$(function() {
  $('.order-search-form select[name=customer]').chosen({
    width: '100%',
    allow_single_deselect: true,
    no_results_text: 'ไม่พบลูกค้าชื่อ'
  });

  $('.order-form').on('click', 'a.remove-product-btn', removeBtnClick);

  $('#add-product-btn').click(addProductBtnClick);

  $('body').on('click', '.product-list li a', productClick);

  $('.order-form').on('click', 'a[href=#qty]', quantityClick);
  $('.order-form').on('click', 'a[href=#unit]', unitClick);
  $('.order-form').on('click', 'a[href=#price]', priceClick);

  $('body').on('click', '[name=quantity],[name=unit],[name=price],[name=payment]', function() {
    this.select();
  });

  $('input.date').datepicker({language: 'th', format: 'dd/mm/yyyy', autoclose: 'true'});
});


function addProductBtnClick() {
  $('#product-dialog').modal().on('shown.bs.modal', function(e) {
    initProductTypeList();
  });
}


function initProductTypeList() {
  var width = 2;

  $('.product-type-list li').each(function(i, elm) {
    width += $(elm).outerWidth(true);
  });

  $('.product-type-list').width(width);

  $('body').on('click', '.product-type-list li a', productTypeClick);
}


function productTypeClick() {
  var product_type_id = $(this).attr('product-type-id');
  $('.product-list li').hide();
  $('.product-list li[product-type-id=' + product_type_id + ']').fadeIn();
  return false;
}


function productClick() {
  $('#product-dialog').modal('hide');

  var product_type_id = $(this).closest('[product-type-id]').attr('product-type-id');

  if (product_type_id == 'basket') {
    BootstrapDialog.basket_confirm($(this));
    return false;
  }

  showProductComfirmDialog(this, false);

  return false;
}

function showProductComfirmDialog(elm, is_deposit) {
  var $dialog = $('.quantity-price-dialog').clone(),
      $elm = $(elm).clone();

  $dialog.find('[name=quantity]').val('1');
  $dialog.find('[name=price]').val(parseFloat($elm.attr('price-per-unit')));
  BootstrapDialog.product_confirm($elm, $dialog, is_deposit);
}


function addProduct(elm, is_deposit) {
  var product_id = $(elm).attr('product-id'),
      product_type_id = $(elm).closest('[product-type-id]').attr('product-type-id'),
      name = $(elm).text(),
      quantity = parseFloat($(elm).attr('quantity')),
      quantity = isNaN(quantity) ? 1 : quantity,
      default_unit = parseFloat($(elm).attr('unit')),
      unit = default_unit * quantity,
      price_per_unit = parseFloat($(elm).attr('price-per-unit')),
      cost_per_unit = parseFloat($(elm).attr('cost-per-unit')),
      total = CommaFormatted(unit * price_per_unit),
      $existed_tr = $('.order-form tbody tr[product-id=' + product_id + '][product-type-id=' + product_type_id + ']'),
      output = [];

  if (product_type_id == 'basket' && !is_deposit) {
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
      qty += quantity;
      note_txt = note_txt.replace(existed[0], name + ' x ' + qty);
      $('#id-note').data('baskets')[name]['unit'] = qty;
    } else {
      if (note_txt.length > 0) note_txt += '\n';
      note_txt += name + ' x ' + quantity;
      $('#id-note').data('baskets')[name] = basket;
    }

    $('#id-note').val(note_txt);

    return;
  }

  if ($existed_tr.length && !$existed_tr.hasClass('deleted')) {
    var qty = parseFloat($existed_tr.find('a[href=#qty]').text()),
        price = parseFloat($existed_tr.find('a[href=#price]').text()),
        unit = parseFloat($existed_tr.find('a[href=#unit]').text()),
        default_unit = parseFloat($existed_tr.find('a[href=#unit]').attr('default'));

    if (product_type_id != 'basket') qty++;

    unit += default_unit;
    $existed_tr.find('a[href=#qty]').text(qty);
    $existed_tr.find('a[href=#unit]').text(unit);
    $existed_tr.find('.total').text(CommaFormatted(unit * price));
  } else {
    output.push('<tr product-type-id="' + product_type_id + '" product-id="' + product_id + '" cost-per-unit="' + cost_per_unit + '">');

    if (product_type_id == 'basket') output.push('<td>0</td>');
    else output.push('<td><a href="#qty">' + quantity + '</a></td>');

    output.push('<td class="name">' + name + '</td>');
    output.push('<td><a href="#unit" default="' + default_unit + '">' + unit + '</a></td>');
    output.push('<td><a href="#price" default="' + price_per_unit + '">' + price_per_unit + '</a></td>');
    output.push('<td><div class="total-wrapper"><span class="total">' + total + '</span><div class="remove-product-btn-wrapper"><a href="#remove" class="remove-product-btn"><span class="glyphicon glyphicon-remove-circle"></span></a></div></div></td>');
    output.push('</tr>');

    $(output.join('')).appendTo('.order-form tbody').addClass('animated pulse').swipe({
      allowPageScroll: 'vertical',
      swipe: orderItemSwipe,
    });
  }

  updateSummary();
}


function removeBtnClick() {
  var $tr = $(this).closest('tr');

  if ($tr.attr('order-item-id')) {
    $tr.addClass('deleted');
    $tr.find('.remove-product-btn').addClass('animated bounceOutRight').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
      $tr.find('.remove-product-btn-wrapper').hide();
      $(this).removeClass('animated bounceOutRight bounceInRight');
    });
    updateSummary();
  } else {
    $tr.addClass('animated bounceOut').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
      $(this).remove();
      updateSummary();
    });
  }

  return false;
}


function orderItemSwipe(event, direction, distance, duration, fingerCount) {
  var $tr = $(event.currentTarget);

  if ($tr.hasClass('deleted')) {
    $tr.removeClass('deleted');
    return;
  }

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
        $total.text(CommaFormatted(price * unit));

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
        $total.text(CommaFormatted(price * val));

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
        $total.text(CommaFormatted(unit * val));

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
    if (i == 0 || $(tr).hasClass('deleted')) return;

    if ($(tr).find('a[href=#qty]').length)
      quantity += parseFloat($(tr).find('a[href=#qty]').text());

    summary += parseFloat($(tr).find('.total').text().replace(',', ''));
  });

  $td.html(CommaFormatted(summary) + '<br/><br/>' + CommaFormatted(quantity));
  $('.payment-dialog .summary').html(summary);
  $('.payment-dialog .quantity').html(quantity);
}


BootstrapDialog.product_confirm = function($elm, $dialog, is_deposit) {
  new BootstrapDialog({
    title: $elm.text(),
    message: $dialog,
    closable: false,
    data: {elm: $elm, is_deposit: is_deposit},
    buttons: [{
      label: 'ตกลง',
      action: function(dialog) {
        var price = $(dialog.getMessage()).find('input[name=price]').val(),
            quantity = $(dialog.getMessage()).find('input[name=quantity]').val(),
            $elm = dialog.getData('elm'),
            is_deposit = dialog.getData('is_deposit');

        $elm.attr('price-per-unit', price);
        $elm.attr('quantity', quantity);
        addProduct($elm[0], is_deposit);
        dialog.close();
      }
    }],
    onshow: function(dialog) {
      dialog.getModalDialog().find('.form-field').swipe({swipe: numberSwipe, threshold: 0});
    }
  }).open();
};


BootstrapDialog.basket_confirm = function($elm) {
  var $dialog = $('.quantity-dialog').clone();
  $dialog.find('[name=quantity]').val('1');

  new BootstrapDialog({
    title: 'ชนิดของตระกร้า',
    message: $dialog,
    closable: false,
    data: {elm: $elm},
    buttons: [{
      label: 'มัดจำ',
      action: function(dialog) {
        var $elm = dialog.getData('elm'),
            quantity = $(dialog.getMessage()).find('input[name=quantity]').val();

        $elm.attr('quantity', quantity);
        addProduct($elm[0], true);
        dialog.close();
      }
    }, {
      label: 'ไม่มัดจำ',
      action: function(dialog) {
        var $elm = dialog.getData('elm'),
            quantity = $(dialog.getMessage()).find('input[name=quantity]').val();
            
        $elm.attr('quantity', quantity);
        addProduct($elm[0], false);
        dialog.close();
      }
    }],
    onshow: function(dialog) {
      dialog.getModalDialog().swipe({swipe: numberSwipe});
    }
  }).open();
};


function numberSwipe(event, direction, distance, duration, fingerCount) {
  var $input = $(event.currentTarget).find('input[type=number]'),
      num = $input.val();

  if (direction == 'up') {
    $input.val(++num);
  } else if (direction == 'down') {
    $input.val(--num);
  }
}
