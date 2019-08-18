
define([
    'text!pages/www/m/debug/ejs/index.html',
    ], function(ejs_index) {

    var self = this;

    $('.site-main').on('click','.debug-on-btn',function(event) {
        window.sessionStorage.setItem('debug','1');
        $('.debug-on-btn').addClass('btn-primary').removeClass('btn-default');
        $('.debug-off-btn').addClass('btn-default').removeClass('btn-primary');
    });

    $('.site-main').on('click','.debug-off-btn',function(event) {
        window.sessionStorage.removeItem('debug');
        $('.debug-on-btn').addClass('btn-default').removeClass('btn-primary');
        $('.debug-off-btn').addClass('btn-primary').removeClass('btn-default');
    });

    return function(ctx,next) {
        $('.site-canvas').css('background-color','#e7e8e9');
        new EJS({ text: ejs_index }).update(document.querySelector('.site-main'), {});
    };
});




