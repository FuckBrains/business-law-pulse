
var main = function() {
    require([
        'text!common/ejs/loading.html',
        'text!pages/www/m/index/ejs/navmenu.html',
        'text!pages/www/m/index/ejs/footer.html',
        'page'], function(ejs_loading,ejs_navmenu,ejs_footer,page) {

        new EJS({ text: ejs_navmenu }).update(document.querySelector('.site-navmenu'), {});
        new EJS({ text: ejs_footer }).update(document.querySelector('.site-footer'), {});

        var reset = function(ctx,next) {
            $('.site-main').off();
            $('.site-canvas').css('background-color','white');
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
            new EJS({ text: ejs_loading }).update(document.querySelector('.site-main'), { padding: '10em', font: '2em' });
            setTimeout(next, 500);
        };

        page('/debug', reset, transition, loading, function(ctx,next) {
            require(['pages/www/m/debug/index'], function(module) {
                module(ctx,next);
            });
        });

        page('/config', reset, transition, loading, function(ctx,next) {
            require(['pages/www/m/debug/config'], function(module) {
                module(ctx,next);
            });
        });

        page('/mqtt', reset, transition, loading, function(ctx,next) {
            require(['pages/www/m/debug/mqtt'], function(module) {
                module(ctx,next);
            });
        });
        page.exit('/mqtt', function(ctx,next) {
            if (CORE.mqtt.client.isConnected()) {
                CORE.mqtt.client.disconnect();
            }
            next();
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




