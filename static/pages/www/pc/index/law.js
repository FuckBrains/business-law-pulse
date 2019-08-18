
var main = function() {
    require([
        'text!pages/www/pc/index/ejs/header.html',
        'text!pages/www/pc/index/ejs/footer.html',
        'page'], function(ejs_header,ejs_footer,page) {

        var self = this;

        var ejs = {
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
                $('.site-main').removeClass('site-transition-ease-out');
                $('.site-main').html('');
                next();
            },500);
        };

        // law deal
        page('/deal/:deal/detail', reset, transition, function(ctx,next) {
            require(['pages/www/pc/deal/detail'], function(module) {
                module(ctx,next);
            });
        });

        // law firm
        page('/firm/:firm/detail', reset, transition, function(ctx,next) {
            require(['pages/www/pc/firm/detail'], function(module) {
                module(ctx,next);
            });
        });

        // law lawyer
        page('/lawyer/:lawyer/detail', reset, transition, function(ctx,next) {
            require(['pages/www/pc/lawyer/detail'], function(module) {
                module(ctx,next);
            });
        });

        // not found
        page('*', function(ctx, next) {
            window.location.href = (CONST.ssl ? 'https':'http') + '://' + COST.domain.www;
        });

        page.base('/law');
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
                fail: function(xhr) { },
                complete: function(xhr) {
                    main();
                }
            });
        });
    });
});


