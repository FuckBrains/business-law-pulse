

var main = function() {
    require([
        'text!common/ejs/loading.html',
        'text!pages/www/pc/index/ejs/header.html',
        'text!pages/www/pc/index/ejs/footer.html',
        'page'], function(ejs_loading,ejs_header,ejs_footer,page) {

        var self = this;

        var ejs = {
            loading: ejs_loading,
            header: ejs_header,
            footer: ejs_footer,
        };

        $('.site-header').html(new EJS({ text: ejs.header }).render({}));
        $('.site-footer').html(new EJS({ text: ejs.footer }).render({}));

        var reset = function(ctx,next) {
            $('.site-main').off();
            if ($('body').hasClass('modal-open')) {
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
            }
            next();
        };

        var transition = function(ctx,next) {
            $('.site-main').addClass('site-transition-ease-out');
            setTimeout(function() {
                $('.site-main').removeClass('site-transition-ease-out').html('');
                next();
            },500);
        };

        var loading = function(ctx,next) {
            $('.site-main').html(new EJS({ text: ejs.loading }).render({ padding: '200px', font: '50px' }));
            setTimeout(function() { next(); }, 500);
        };

        page('/', reset, loading, function(ctx,next) {
            require(['pages/www/pc/generate/index'], function(module) {
                module(ctx,next);
            });
        });

        // not found
        page('*', function(ctx, next) {
            page.redirect('/generate');
        });

        page.base('/generate');
        page.start({
            hashbang: false,
            decodeURLComponents: false,
        });
    });
};


require([CONST.require.config], function() {
    require(['domReady','bootstrap','jasny-bootstrap','ejs','core'], function(domReady) {
        domReady(function() {
            CORE.ajax.session({
                url: '/session/sync',
                success: function(result) {
                    CORE.user = result.data.user;
                },
                fail: function(result) { },
                complete: function(xhr) {
                    main();
                }
            });
        });
    });
});



