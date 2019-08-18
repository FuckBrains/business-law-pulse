
define([
    'text!common/ejs/loading.html',
    'text!pages/sys/pc/dashboard/ejs/index.html',
    ], function(ejs_loading, ejs_index) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        index: ejs_index,
    };

    return function(ctx,next) {
        $('.site-main').html(new EJS({ text: ejs.index }).render({}));
    };
});


