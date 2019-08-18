
var main = function() {
    require([
        'text!common/ejs/loading.html',
        'page'], function(ejs_loading,page) {

        var reset = function(ctx,next) {
            $('.site-main').off();
            $('.site-main').css('background-color','white');
            if ($('body').hasClass('modal-open')) {
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
            }
            next();
        };

        var transition = function(ctx,next) {
            $('.site-main').addClass('site-transition-ease-out');
            setTimeout(function() {
                $('.site-main').removeClass('site-transition-ease-out');
                $('.site-main').html('');
                next();
            },500);
        };

        var loading = function(ctx,next) {
            var ejs_html = new EJS({ text: ejs_loading }).render({ padding: '200px', font: '45px' });
            $('.site-main').html(ejs_html);
            setTimeout(function() {
                next();
            }, 500);
        };

        page('/docs', reset, transition, loading, function(ctx,next) {
            if (CONST.env === 'prd') {
                page.redirect('/api/index');
            } else {
                require(['pages/www/pc/debug/docs'], function(module) {
                    module(ctx,next);
                });
            }
        });

        page('/index', reset, transition, loading, function(ctx,next) {
            require(['pages/www/pc/debug/index'], function(module) {
                module(ctx,next);
            });
        });

        // not found
        page('*', function(ctx, next) {
            window.location.href = (CONST.ssl ? 'https':'http') + '://' + CONST.domain.www;
        });

        page.base('/debug');
        page.start({
            hashbang: false,
            decodeURLComponents: false,
        });
    });
};


require([CONST.require.config], function() {
    require(['domReady','bootstrap','jasny-bootstrap','ejs','core'], function(domReady) {
        domReady(function() {
            main();
        });
    });
});




