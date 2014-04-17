RegExp.quote = function(str) {
  return (str+'').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
};


function CommaFormatted(amount) {
  amount = '' + amount;
  var delimiter = ',';

  if (amount.indexOf('.') != -1) {
   var a = amount.split('.', 2);
   var d = a[1];
  } else {
    var a = [amount];
    var d = '';
  }
  var i = parseInt(a[0]);
  
  if (isNaN(i)) { return ''; }
  
  var minus = '';
  
  if (i < 0) { minus = '-'; }
  
  i = Math.abs(i);
  var n = new String(i);
  var a = [];
  
  while(n.length > 3) {
    var nn = n.substr(n.length-3);
    a.unshift(nn);
    n = n.substr(0, n.length-3);
  }
  
  if (n.length > 0) { a.unshift(n); }
  
  n = a.join(delimiter);
  
  if (d.length < 1) { amount = n; }
  else { amount = n + '.' + d; }
  
  amount = minus + amount;
  return amount;
}


var dialog_instance;


$(function() {
  
});