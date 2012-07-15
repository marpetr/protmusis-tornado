$(function() {
  $('#container').tabs();
  setInterval(function() {
    $('#status').load('/dashboard/status');
  }, 2000);
});
