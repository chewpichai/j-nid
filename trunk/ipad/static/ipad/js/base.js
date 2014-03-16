var dialog_instance;

$(function() {
  $('#add-product-btn').click(addProductBtnClick);

  $('body').on('click', '.product-list li a', productClick);

  $('.order-form').on('click', 'a[href=#qty]', quantityClick);
  $('.order-form').on('click', 'a[href=#unit]', unitClick);
  $('.order-form').on('click', 'a[href=#price]', priceClick);
  $('.order-form').on('click', 'a.remove-product-btn', removeBtnClick);

  var current_hour = (new Date()).getHours();
  $('select[name=customer]').val(++current_hour).change(customerChange).change().combobox();

  $('#order-submit-btn').click(orderSubmitClick);

  $('#id-note').val('').data('baskets', {});
});


function initProductTypeList() {
  var width = 0;

  $('.product-type-list li').each(function(i, elm) {
    width += $(elm).outerWidth(true);
  });

  $('.product-type-list').width(width);

  $('body').on('click', '.product-type-list li a', productTypeClick);
}


function addProductBtnClick() {
  dialog_instance = BootstrapDialog.show({
    title: 'เพิ่มรายการสินค้า',
    message: $('.product-dialog').clone(),
    onshow: function() {
      setTimeout(initProductTypeList, 300);
    }
  });
}


function productTypeClick() {
  var product_type_id = $(this).attr('product-type-id');
  $('.product-list li').hide();
  $('.product-list li[product-type-id=' + product_type_id + ']').fadeIn();
  return false;
}


function productClick() {
  dialog_instance.close();

  var product_type_id = $(this).closest('[product-type-id]').attr('product-type-id');

  if (product_type_id == 'basket') {
    BootstrapDialog.basket_confirm(this);
    return false;
  }
  
  addProduct(this);

  return false;
}


function addProduct(elm, is_pledge) {
  var is_pledge = typeof is_pledge !== 'undefined' ? is_pledge : false;
      product_id = $(elm).attr('product-id'),
      product_type_id = $(elm).closest('[product-type-id]').attr('product-type-id'),
      name = $(elm).text(),
      unit = parseFloat($(elm).attr('unit')),
      price_per_unit = parseFloat($(elm).attr('price-per-unit')),
      cost_per_unit = parseFloat($(elm).attr('cost-per-unit')),
      total = unit * price_per_unit,
      $existed_tr = $('.order-form tbody tr[product-id=' + product_id + '][product-type-id=' + product_type_id + ']'),
      output = [];

  if (product_type_id == 'basket' && !is_pledge) {
    var note_txt = $('#id-note').val(),
        re = new RegExp(RegExp.quote(name) + ' x \\d+', 'm'),
        existed = re.exec(note_txt),
        qty,
        basket = {
          is_basket: true,
          price_per_unit: price_per_unit,
          unit: unit,
          product_id: product_id
        };

    if (existed) {
      qty = parseInt(existed[0].split(' x ')[1]);
      qty++;
      note_txt = note_txt.replace(existed[0], name + ' x ' + qty);
      $('#id-note').data('baskets')[name]['unit'] = qty;
    } else {
      if (note_txt.length > 0) note_txt += '\n';
      note_txt += name + ' x 1';
      $('#id-note').data('baskets')[name] = basket;
    }

    $('#id-note').val(note_txt);

    return;
  }
  
  if ($existed_tr.length) {
    var qty = parseFloat($existed_tr.find('a[href=#qty]').text()),
        price = parseFloat($existed_tr.find('a[href=#price]').text()),
        unit = parseFloat($existed_tr.find('a[href=#unit]').text()),
        default_unit = parseFloat($existed_tr.find('a[href=#unit]').attr('default'));
    
    if (product_type_id != 'basket') qty++;
    unit += default_unit;
    $existed_tr.find('a[href=#qty]').text(qty);
    $existed_tr.find('a[href=#unit]').text(unit);
    $existed_tr.find('.total').text(unit * price);
  } else {
    output.push('<tr product-type-id="' + product_type_id + '" product-id="' + product_id + '" cost-per-unit="' + cost_per_unit + '">');
    
    if (product_type_id == 'basket') output.push('<td>0</td>');
    else output.push('<td><a href="#qty">1</a></td>');

    output.push('<td class="name">' + name + '</td>');
    output.push('<td><a href="#unit" default="' + unit + '">' + unit + '</a></td>');
    output.push('<td><a href="#price" default="' + price_per_unit + '">' + price_per_unit + '</a></td>');
    output.push('<td><div class="total-wrapper"><span class="total">' + total + '</span><div class="remove-product-btn-wrapper"><a href="#remove" class="remove-product-btn"><span class="glyphicon glyphicon-remove-circle"></span></a></div></div></td>');
    output.push('</tr>');

    $(output.join('')).appendTo('.order-form tbody').addClass('animated pulse').swipe({
      allowPageScroll: 'vertical',
      swipe: function(event, direction, distance, duration, fingerCount) {
        var $tr = $(event.currentTarget);

        if (direction == 'left') {
          $tr.find('.remove-product-btn-wrapper').show();
          $tr.find('.remove-product-btn').addClass('animated bounceInRight');  
        } else if (direction == 'right') {
          if ($tr.find('.remove-product-btn').hasClass('bounceInRight')) {
            $tr.find('.remove-product-btn').addClass('animated bounceOutRight').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
              $tr.find('.remove-product-btn-wrapper').hide();
              $(this).removeClass('animated bounceOutRight bounceInRight');
            });
          }
        }
      },
    });
  }
  
  updateSummary();
}


function quantityClick() {
  var $tr = $(this).closest('tr'),
      $dialog = $('.quantity-dialog').clone(),
      val = $(this).text(),
      $qty = $(this);

  $dialog.find('input[name=quantity]').val(val);

  dialog_instance = BootstrapDialog.show({
    title: $tr.find('.name').text(),
    message: $dialog,
    buttons: [{
      label: 'ตกลง',
      action: function(dialog) {
        val = $(dialog.getMessage()).find('input[name=quantity]').val();
        
        var $unit = $tr.find('a[href=#unit]'),
            unit = parseFloat($unit.attr('default')) * parseFloat(val),
            $total = $tr.find('.total'),
            price = parseFloat($tr.find('a[href=#price]').text());
        
        $qty.text(val);
        $unit.text(unit);
        $total.text(price * unit);

        updateSummary();
        dialog.close();
      }
    }],
    onshow: function(dialog) {
      dialog.getModalDialog().swipe({swipe: numberSwipe});
    }
  });
  return false;
}


function unitClick() {
  var $tr = $(this).closest('tr'),
      $dialog = $('.unit-dialog').clone(),
      val = $(this).text(),
      $unit = $(this);

  $dialog.find('input[name=unit]').val(val);

  dialog_instance = BootstrapDialog.show({
    title: $tr.find('.name').text(),
    message: $dialog,
    buttons: [{
      label: 'ตกลง',
      action: function(dialog) {
        val = $(dialog.getMessage()).find('input[name=unit]').val();
        
        var $qty = $tr.find('a[href=#qty]'),
            qty = Math.ceil(parseFloat(val) / parseFloat($unit.attr('default'))),
            $total = $tr.find('.total'),
            price = parseFloat($tr.find('a[href=#price]').text());
        
        $unit.text(val);
        $qty.text(qty);
        $total.text(price * val);
        
        updateSummary();
        dialog.close();
      }
    }],
    onshow: function(dialog) {
      dialog.getModalDialog().swipe({swipe: numberSwipe});
    }
  });
  return false;
}

function priceClick() {
  var $tr = $(this).closest('tr'),
      $dialog = $('.price-dialog').clone(),
      val = $(this).text(),
      $price = $(this);

  $dialog.find('input[name=price]').val(val);

  dialog_instance = BootstrapDialog.show({
    title: $tr.find('.name').text(),
    message: $dialog,
    buttons: [{
      label: 'ตกลง',
      action: function(dialog) {
        val = $(dialog.getMessage()).find('input[name=price]').val();
        
        var unit = parseFloat($tr.find('a[href=#unit]').text()),
            $total = $tr.find('.total');
        
        $price.text(val);
        $total.text(unit * val);

        updateSummary();
        dialog.close();
      }
    }],
    onshow: function(dialog) {
      dialog.getModalDialog().swipe({swipe: numberSwipe});
    }
  });
  return false;
}


function updateSummary() {
  var $td = $('.order-form tfoot .summary'),
      quantity = 0, summary = 0;

  $('.order-form tbody tr').each(function(i, tr) {
    if (i == 0) return;

    if ($(tr).find('a[href=#qty]').length)
      quantity += parseFloat($(tr).find('a[href=#qty]').text());

    summary += parseFloat($(tr).find('.total').text());
  });

  $td.html(summary + '<br/><br/>' + quantity);
  $('.payment-dialog .summary').html(summary);
  $('.payment-dialog .quantity').html(quantity);
}


BootstrapDialog.basket_confirm = function(elm) {
  new BootstrapDialog({
    title: 'ชนิดของตระกร้า',
    message: '',
    closable: false,
    data: {
      'elm': elm
    },
    buttons: [{
      label: 'มัดจำ',
      action: function(dialog) {
        addProduct(dialog.getData('elm'), true);
        dialog.close();
      }
    }, {
      label: 'ไม่มัดจำ',
      action: function(dialog) {
        addProduct(dialog.getData('elm'), false);
        dialog.close();
      }
    }]
  }).open();
};


function removeBtnClick() {
  $(this).closest('tr').addClass('animated bounceOut').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
    $(this).remove();
  });
  return false;
}


function customerChange() {
  var customer_id = this.value,
      outstanding = $(this).find('option[value=' + customer_id + ']').data('outstanding');
  
  $('.outstanding').html(Math.abs(outstanding));
  $('.outstanding').removeClass('red');

  if (outstanding < 0) {
    $('.outstanding').addClass('red');
  }
}


function numberSwipe(event, direction, distance, duration, fingerCount) {
  var $input = $(event.currentTarget).find('input[type=number]'),
      num = $input.val();
  
  if (direction == 'up') {
    $input.val(++num);
  } else if (direction == 'down') {
    $input.val(--num);
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
        $.post('/api/orders/create/', JSON.stringify(data), function(response) {
          // dialog.close();
          location.reload();
        });
      }
    }],
    onshow: function(dialog) {
      if (data.person <= 24) {
        var summary = $(dialog.getMessage()).find('.summary').html();
        $(dialog.getMessage()).find('input[name=payment]').val(summary);
      }
    }
  });
}


RegExp.quote = function(str) {
  return (str+'').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
};