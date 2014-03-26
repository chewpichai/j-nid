$(function() {
  $('table.order-form > tbody > tr[product-id]').swipe({
    allowPageScroll: 'vertical',
    swipe: orderItemSwipe,
  });

  $('#order-delete-btn').click(function() {
    BootstrapDialog.order_delete_confirm(this);    
  });

  updateSummary();
});


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