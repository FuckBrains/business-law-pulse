
var main = function() {
    require([
        'text!common/ejs/loading.html',
        'text!pages/sys/pc/dashboard/ejs/header.html',
        'text!pages/sys/pc/dashboard/ejs/footer.html',
        'page'], function(ejs_loading,ejs_header,ejs_footer,page) {

        $('.site-header').html(new EJS({ text: ejs_header }).render({}));
        $('.site-footer').html(new EJS({ text: ejs_footer }).render({}));

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

        var loading = function(ctx,next) {
            var ejs_html = new EJS({ text: ejs_loading }).render({ padding: '200px', font: '50px' });
            $('.site-main').html(ejs_html);
            setTimeout(function() { next(); }, 500);
        };

        // dashboard
        page('/', reset, transition, function(ctx,next) {
            page('/dashboard');
        });

        page('/dashboard', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/dashboard/index'], function(module) {
                module(ctx,next);
            });
        });

        page.exit('/dashboard', function(ctx,next) {
            next();
        });

        // profile
        page('/profile', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/profile/index'], function(module) {
                module(ctx,next);
            });
        });

        // logout
        page('/logout', reset, transition, function(ctx,next) {
            CORE.ajax.session({
                url: '/session/logout',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                success: function(result) {
                    window.location.href = '/';
                },
                fail: function(result) {
                    CORE.notify.error(result.msg);
                },
                error: function(xhr) {
                    CORE.notify.error('退出失败');
                }
            });
        });

        // admin
        page('/admin/query', reset, transition, function(ctx,next) {
            require(['pages/sys/pc/admin/query'], function(module) {
                module(ctx,next);
            });
        });
        page('/admin/create', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/admin/create'], function(module) {
                module(ctx,next);
            });
        });
        page('/admin/:admin/update', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/admin/update'], function(module) {
                module(ctx,next);
            });
        });

        // law deal
        page('/law/deal/query', reset, transition, function(ctx,next) {
            require(['pages/sys/pc/deal/query'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/deal/create', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/deal/create'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/deal/:deal/update', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/deal/update'], function(module) {
                module(ctx,next);
            });
        });

        // law client
        page('/law/client/query', reset, transition, function(ctx,next) {
            require(['pages/sys/pc/client/query'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/client/create', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/client/create'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/client/:client/update', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/client/update'], function(module) {
                module(ctx,next);
            });
        });

        // law firm
        page('/law/firm/query', reset, transition, function(ctx,next) {
            require(['pages/sys/pc/firm/query'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/firm/create', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/firm/create'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/firm/:firm/update', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/firm/update'], function(module) {
                module(ctx,next);
            });
        });

        // lawyer
        page('/law/lawyer/query', reset, transition, function(ctx,next) {
            require(['pages/sys/pc/lawyer/query'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/lawyer/create', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/lawyer/create'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/lawyer/:lawyer/update', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/lawyer/update'], function(module) {
                module(ctx,next);
            });
        });

        // law config
        page('/law/config', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/config/index'], function(module) {
                module(ctx,next);
            });
        });

        // law batch
        page('/law/batch', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/batch/index'], function(module) {
                module(ctx,next);
            });
        });

        // law chart
        page('/law/chart/m1', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/chart/m1'], function(module) {
                module(ctx,next);
            });
        });
        page('/law/chart/m2', reset, transition, loading, function(ctx,next) {
            require(['pages/sys/pc/chart/m2'], function(module) {
                module(ctx,next);
            });
        });

        // not found
        page('*', function(ctx, next) {
            page.redirect('/manage/dashboard');
        });

        page.base('/manage');
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
                    CORE.admin = result.data.admin;
                    main();
                },
                fail: function(result) {
                    window.location.href = '/';
                },
                error: function(xhr) {
                    window.location.href = '/';
                }
            });
        });
    });
});


