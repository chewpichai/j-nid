$(function() {
    $('input[name$=date]').datepicker({dateFormat: 'dd-mm-yy'});

    $('.order-list tr[order-id]').click(showOrder);

    $('.payment-list tr[payment-id]').click(showPayment);

    // $('.menu-btn a').click(function() {
    //  $('.main-menu').slideToggle();
    // });

    $('.menu-btn a').sidr();
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
