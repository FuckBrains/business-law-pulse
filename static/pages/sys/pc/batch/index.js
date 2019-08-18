
define([
    'text!common/ejs/loading.html',
    'text!pages/sys/pc/batch/ejs/index.html',
    ], function(ejs_loading, ejs_index) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        index: ejs_index,
    };

    $('.site-main').on('click','.add-config-btn',function(event) {
    });

    return function(ctx,next) {
        $('.site-main').html(new EJS({ text: ejs.index }).render({}));
    };
});




