var page = require('webpage').create();
var args = require('system').args;

page.paperSize = {
  width: '5.5in',
  height: '8in',
};

page.open(args[1], function() {
  page.render(args[2]);
  phantom.exit();
});