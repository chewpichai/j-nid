$(function() {
    $('input[name$=date]').datepicker({dateFormat: 'dd-mm-yy'});

    $('.order-list tr[order-id]').click(showOrder);

    $('.payment-list tr[payment-id]').click(showPayment);

    // $('.menu-btn a').click(function() {
    //  $('.main-menu').slideToggle();
    // });

    $('.menu-btn a').sidr();

    $('ul.product-list li.product a').click(showPriceEditor);

    $('#price-editor form').submit(priceEditorSubmit);
});

function showOrder() {
    var order_id = $(this).attr('order-id');
    $.get('/web/order/' + order_id + '/', function(response) {
        $('#dialog').html(response);
        $('#dialog').dialog({
            title: $('#dialog .order-wrapper').attr('name'),
            modal: true,
            width: 600
        });
    });
}

function showPayment() {
    var payment_id = $(this).attr('payment-id');
    $.get('/web/payment/' + payment_id + '/', function(response) {
        $('#dialog').html(response);
        $('#dialog').dialog({
            title: $('#dialog .payment-wrapper').attr('name'),
            modal: true,
            width: 600
        });
    });
}

function showPriceEditor() {
    var $li = $(this).closest('li'),
        pk = $li.attr('product-id'),
        price = $li.find('.price').attr('value'),
        cost = $li.find('.cost').attr('value'),
        name = $li.find('h3').text();

    $('#price-editor').attr('title', name);

    $('#price-editor').dialog({
        modal: true,
        open: function(event, ui) {
            $('#price-editor').find('input[name=pk]').val(pk);
            $('#price-editor').find('input[name=price]').val(price);
            $('#price-editor').find('input[name=cost]').val(cost);
        },
        close: function(event, ui) {
            $('#price-editor form').submit();
        }
    });
    return false;
}

function priceEditorSubmit() {
    var data = $(this).serialize(),
        pk = this['pk'].value;

    $('#loading').dialog({modal: true});

    $.post('/api/products/' + pk + '/', data, function(response) {
        var $li = $('li.product[product-id=' + response.pk + ']');

        $li.find('.price').attr('value', response.price).text(response.formated_price);
        $li.find('.cost').attr('value', response.cost).text(response.formated_cost);
        $li.hide().fadeIn();
        $('#loading').dialog('close');
    });
    return false;
}
