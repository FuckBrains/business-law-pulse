
(function(window) {
    require.config({
        baseUrl: CONST.static.url,
        waitSeconds: 0,
        paths: {
            'domReady': CONST.require.cdn + 'require-domReady/2.0.1/domReady.min',
            'text': CONST.require.cdn + 'require-text/2.0.12/text.min',
            'css': CONST.require.cdn + 'require-css/0.1.10/css.min',

            'crypto-js': CONST.require.cdn + 'crypto-js/3.1.9/crypto-js.min',

            'jquery': CONST.require.cdn + 'jquery/1.12.4/jquery.min',
            'jquery-form': CONST.require.cdn + 'jquery.form/4.2.2/jquery.form.min',
            'jquery-validate': CONST.require.cdn + 'jquery-validate/1.17.0/jquery.validate.min',
            'jquery-cookie': CONST.require.cdn + 'jquery-cookie/1.4.1/jquery.cookie',
            'jquery-qrcode': CONST.require.cdn + 'jquery.qrcode/1.0/jquery.qrcode.min',
            'jquery-sortable': CONST.require.cdn + 'jquery-sortable/0.9.13/jquery-sortable-min',

            'tiny-color-picker': CONST.require.cdn + 'tinyColorPicker/1.1.1/jqColorPicker.min',
            'zabuto-calendar': CONST.require.cdn + 'zabuto_calendar/1.2.1/zabuto_calendar',

            'bootstrap': CONST.require.cdn + 'bootstrap/3.3.7/js/bootstrap.min',
            'jasny-bootstrap': CONST.require.cdn + 'jasny-bootstrap/3.1.3/js/jasny-bootstrap.min',

            'bootstrap-notify': CONST.require.cdn + 'bootstrap-notify/0.1.0/js/bootstrap-notify',
            'bootstrap-multiselect': CONST.require.cdn + 'bootstrap-multiselect/0.9.13/js/bootstrap-multiselect',
            'bootstrap-rating': CONST.require.cdn + 'bootstrap-rating/1.4.0/bootstrap-rating.min',
            'bootstrap-switch': CONST.require.cdn + 'bootstrap-switch/js/3.3.4/bootstrap-switch.min',
            'bootstrap-wysiwyg': 'vendor/bootstrap-rating/js/bootstrap-wysiwyg',
            'bootstrap-datetimepicker': 'vendor/bootstrap-datetimepicker/js/bootstrap-datetimepicker.min',
            'bootstrap-datetimepicker-lang': 'vendor/bootstrap-datetimepicker/js/locales/bootstrap-datetimepicker.zh-CN',

            'page': CONST.require.cdn + 'page.js/1.7.1/page.min',
            'holder': CONST.require.cdn + 'holder/2.9.4/holder.min',
            'paho-mqtt': CONST.require.cdn + 'paho-mqtt/1.0.2/mqttws31',
            'pako': CONST.require.cdn + 'pako/pako.min',
            'chart': CONST.require.cdn + 'Chart.js/2.6.0/Chart.min',
            'ejs': 'vendor/ejs/ejs_production',

            'ueditor': 'vendor/ueditor/ueditor.all.min',
            'ueditor-lang': 'vendor/ueditor/lang/zh-cn/zh-cn',

            'core': 'common/core',
            'hybrid': 'common/hybrid',
        },
        shim: {
            'jquery-form': {
                deps: ['jquery'],
            },
            'jquery-validator': {
                deps: ['jquery'],
            },
            'zabuto-calendar': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'zabuto_calendar/1.2.1/zabuto_calendar.min.css',
                ],
            },
            'bootstrap': {
                deps: [
                    'jquery',
                    'css!' + CONST.require.cdn + 'bootstrap/3.3.7/css/bootstrap.min.css',
                    'css!' + CONST.require.cdn + 'font-awesome/4.7.0/css/font-awesome.min.css',
                ],
            },
            'jasny-bootstrap': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css',
                ],
            },
            'bootstrap-notify': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'bootstrap-notify/0.1.0/css/bootstrap-notify.css',
                ],
            },
            'bootstrap-multiselect': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'bootstrap-multiselect/0.9.13/css/bootstrap-multiselect.css',
                ],
            },
            'bootstrap-rating': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'bootstrap-rating/1.4.0/bootstrap-rating.css',
                ],
            },
            'bootstrap-switch': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'bootstrap-switch/3.3.4/css/bootstrap3/bootstrap-switch.min.css',
                ],
            },
            'bootstrap-wysiwyg': {
                deps: ['bootstrap'],
            },
            'bootstrap-datetimepicker': {
                deps: [
                    'bootstrap',
                    'css!' + CONST.require.cdn + 'bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css',
                ],
            },
            'bootstrap-datetimepicker-lang': {
                deps: ['bootstrap-datetimepicker'],
            },
            'ueditor': {
                deps: [ 'vendor/ueditor/third-party/zeroclipboard/ZeroClipboard.min', 'vendor/ueditor/ueditor.config' ],
                exports: 'UE',
                init: function(ZeroClipboard){
                    window.ZeroClipboard = ZeroClipboard;
                },
            },
            'ueditor-lang': {
                deps: [
                    'ueditor',
                ],
            },
            'core': {
                deps: ['jquery', 'jquery-validate', 'css!common/core.css'],
                init: function(){
                    document.body.style.display = '';
                },
            },
        },
        config: {
            'text': {
                useXhr: function (url, protocol, hostname, port) {
                    // allow cross-domain requests
                    // remote server allows CORS
                    return true;
                },
            },
            'ueditor-config': {
                UEDITOR_HOME_URL: CONST.static.url + 'ueditor/',
            },
        },
        urlArgs: function(id, url) {
            if (new RegExp('^'+CONST.require.cdn).test(url)) {
                return '';
            }

            if (url.indexOf('?_v=') != -1) {
                return '';
            }

            return (url.indexOf('?') == -1 ? '?' : '&') + '_v=' + (CONST.env == 'local' ? new Date().getTime() : CONST.static.cache);
        },
    });

}(window));


