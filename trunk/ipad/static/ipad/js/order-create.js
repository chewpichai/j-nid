$(function() {
  var current_hour = (new Date()).getHours();
  $('.order-form-controls select[name=customer]').val(++current_hour).change(customerChange).change().chosen({
    width: '300px',
    allow_single_deselect: true,
    no_results_text: "ไม่พบลูกค้าชื่อ"
  });

  $('#order-submit-btn').click(orderSubmitClick);

  $('#id-note').val('').data('baskets', {});
});


function customerChange() {
  var customer_id = this.value,
      outstanding = $(this).find('option[value=' + customer_id + ']').data('outstanding');
  
  $('.outstanding').html(Math.abs(outstanding));
  $('.outstanding').removeClass('red');

  if (outstanding < 0) {
    $('.outstanding').addClass('red');
  }
}


function orderSubmitClick() {
  var data = {
        person: $('[name=customer]').val(),
        order_items: [],
        notation: $('#id-note').val()
      };

  $('tr[product-id]').each(function(i, elm) {
    var $tr = $(elm),
        item = {
          is_basket: $tr.attr('product-type-id') == 'basket',
          price_per_unit: parseFloat($tr.find('a[href=#price]').text()),
          unit: parseInt($tr.find('a[href=#unit]').text()),
          product: $tr.attr('product-id'),
          cost_per_unit: parseFloat($tr.attr('cost-per-unit')),
          is_deposit: true
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

  dialog_instance = BootstrapDialog.show({
    title: 'ชำระเงิน',
    message: $('.payment-dialog').clone(),
    buttons: [{
      label: 'บันทึก',
      action: function(dialog) {
        data.paid = parseFloat($(dialog.getMessage()).find('input[name=payment]').val());
        data.paid = isNaN(data.paid)? 0:data.paid;
        $.post('/api/orders/create/', JSON.stringify(data), function(response) {
          dialog.close();
          $('#loading').modal();
          location.reload();
        });
      }
    }],
    onshow: function(dialog) {
      var summary = 0;

      if (data.person <= 24) {
        summary = $(dialog.getMessage()).find('.summary').html();
      }
      
      $(dialog.getMessage()).find('input[name=payment]').val(summary);
    }
  });
}