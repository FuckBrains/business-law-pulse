
var main = function() {
    require([
        'text!pages/www/m/index/ejs/navmenu.html',
        'text!pages/www/m/index/ejs/footer.html',
        'page'], function(ejs_navmenu,ejs_footer,page) {

        new EJS({ text: ejs_navmenu }).update(document.querySelector('.site-navmenu'), {});
        new EJS({ text: ejs_footer }).update(document.querySelector('.site-footer'), {});

        var reset = function(ctx,next) {
            $('.site-main').off();
            if ($('body').hasClass('modal-open')) {
                $('.modal-backdrop').remove();
                $('body').removeClass('modal-open');
            }
            next();
        }

        var transition = function(ctx,next) {
            $('.site-main').addClass('site-transition-ease-out');
            setTimeout(function() {
                $('.site-main').removeClass('site-transition-ease-out');
                $('.site-main').html('');
                next();
            },500);
        }

        // law deal
        page('/deal/:deal/detail', reset, transition, function(ctx,next) {
            require(['pages/www/m/deal/detail'], function(module) {
                module(ctx,next);
            });
        });

        // law firm
        page('/firm/:firm/detail', reset, transition, function(ctx,next) {
            require(['pages/www/m/firm/detail'], function(module) {
                module(ctx,next);
            });
        });

        // law lawyer
        page('/lawyer/:lawyer/detail', reset, transition, function(ctx,next) {
            require(['pages/www/m/lawyer/detail'], function(module) {
                module(ctx,next);
            });
        });

        // not found
        page('*', function(ctx, next) {
            window.location.href = (CONST.ssl ? 'https':'http') + '://' + COST.domain.www;
        })

        page.base('/law');
        page.start({
            hashbang: false,
            decodeURLComponents: false,
        });
    });
}

require([CONST.require.config], function() {
    require(['domReady','bootstrap','jasny-bootstrap','ejs','core'], function(domReady) {
        domReady(function() {
            CORE.ajax.session({
                url: '/session/sync',
                success: function(result) {
                    CORE.user = result.data.user;
                },
                fail: function(xhr) { },
                complete: function(xhr) {
                    main();
                }
            });
        });
    });
});


