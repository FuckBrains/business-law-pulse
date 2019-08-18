
define([
    'text!pages/www/m/debug/ejs/config.html',
    ], function(ejs_config) {

    var self = this;

    $('.site-main').on('click','.submit-ajax-btn',function(event) {
        var market = $('select[name="market"]').val();
        var version = $('input[name="version"]').val();
        var agent = '';
        if (market=='AppStore') {
            agent = 'footballzone/' + version + ' (iPhone 6s; iOS 10.3.2; Scale/2) AFNetworking/3.0 Market/AppStore NetType/WiFi Language/zh-Hans-CN';
        } else {
            agent = 'footballzone/' + version + ' (Linux; Android 6.0; Meizu Build/MRA58K) OKHttpClient/3.4.2 Market/' + market + ' NetType/WiFi Language/zh_CN';
        }

        $('.submit-ajax-btn').button('loading');
        $('.ajax-result').html('Loading ...');

        setTimeout(function() {
            CORE.ajax.post({
                url: '/common/config/global',
                headers: {
                    'x-user-agent': agent,
                },
                data: { },
                success: function(result) {
                    CORE.notify.info('Submit Done');
                    $('.ajax-result').html(JSON.stringify(result, null, 4).replace(/\n/g,'<br>').replace(/\s/g,'&nbsp;'));
                },
                fail: function(result) {
                    CORE.notify.info('Submit Failed');
                    $('.ajax-result').html(JSON.stringify(result, null, 4));
                },
                error: function(xhr) {
                    CORE.notify.error(xhr.status + ' - ' + xhr.statusText);
                    $('.ajax-result').html('No Result');
                },
                complete: function(xhr) {
                    $('.submit-ajax-btn').button('reset');
                }
            });
        }, 500);
    });

    return function(ctx,next) {
        $('.site-canvas').css('background-color','#f1f2f3');
        new EJS({ text: ejs_config }).update(document.querySelector('.site-main'), {});
    };
});



