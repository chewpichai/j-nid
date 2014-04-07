$(function() {
  $('table.order-form > tbody > tr[product-id]').swipe({
    allowPageScroll: 'vertical',
    swipe: orderItemSwipe,
  });

  $('#order-delete-btn').click(function() {
    BootstrapDialog.order_delete_confirm(this);    
  });

  var baskets = eval($('#id-note').data('baskets'));
  $('#id-note').data('baskets', baskets);

  $('#order-submit-btn').click(orderSubmitClick);

  updateSummary();
});


function orderSubmitClick() {
  var data = {
        order_items: [],
        notation: B64.encode($('#id-note').val())
      },
      url = $(this).attr('url');

  $('tr[product-id]').each(function(i, elm) {
    var $tr = $(elm),
        item = {
          id: $tr.attr('order-item-id'),
          is_basket: $tr.attr('product-type-id') == 'basket',
          price_per_unit: parseFloat($tr.find('a[href=#price]').text()),
          unit: parseInt($tr.find('a[href=#unit]').text()),
          product: $tr.attr('product-id'),
          cost_per_unit: parseFloat($tr.attr('cost-per-unit')),
          is_deposit: true,
          is_deleted: $tr.hasClass('deleted')
        };
    data.order_items.push(item);
  });

  if (data.order_items.length == 0) return;

  $.each($('#id-note').data('baskets'), function(name, basket) {
    var re = new RegExp(RegExp.quote(name) + ' x (\\d+)', 'm'),
        match = re.exec($('#id-note').val());
    if (match) {
      var item = {
            is_basket: true,
            price_per_unit: parseFloat(basket.price_per_unit),
            unit: parseInt(match[1]),
            product: basket.product_id,
            is_deposit: false
          };
      data.order_items.push(item);
    }
  });

  $('#order-submit-btn, #order-delete-btn').hide().nextAll('img').removeClass('hide');

  $.post(url, JSON.stringify(data), function(response) {
    location.reload();
  });
}


BootstrapDialog.order_delete_confirm = function(elm) {
  new BootstrapDialog({
    type: BootstrapDialog.TYPE_DANGER,
    title: 'ลบรายการขาย',
    message: 'ต้องการลบรายการขายนี้?',
    closable: false,
    data: {
      'elm': elm
    },
    buttons: [{
      label: 'ใช่',
      cssClass: 'btn-danger',
      action: function(dialog) {
        dialog.close();
        $('#order-submit-btn, #order-delete-btn').hide().nextAll('img').removeClass('hide');
        $.post($(elm).data('url'), function(response) {
          if (response.status == 'success')
            location = response.url;
        }, 'json');
      }
    }, {
      label: 'ไม่ใช่',
      cssClass: 'btn-primary',
      action: function(dialog) {
        dialog.close();
      }
    }]
  }).open();
};