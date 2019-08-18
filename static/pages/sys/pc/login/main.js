
var main = function() {
    require([
        'text!pages/sys/pc/login/ejs/main.html',
        ], function(ejs_main) {

        $('body').css('background-color','rgb(126,131,138)');

        $('.site-main').html(new EJS({ text: ejs_main }).render({}));

        var form = $('.login-form');

        form.find('input[name="account"],input[name="password"]').each(function() {
            $(this).keyup(function(event) {
                if (event.keyCode==13) {
                    form.find('.login-btn').click();
                }
            });
        });

        form.find('.login-btn').click(function(event) {
            var validator = form.validate({
                rules: {
                    account: { required: true },
                    password: { required: true },
                },
                messages: {
                    account: { required: 'Account is required' },
                    password: { required: 'Password is required' },
                },
                errorPlacement: function(error, element) {
                    CORE.notify.error(error.text());
                },
            });

            validator.form();
            if (validator.valid()) {
                $('.login-btn').button('loading');
                CORE.ajax.session({
                    url: '/session/login',
                    data: {
                        account: form.find('input[name="account"]').val(),
                        password: form.find('input[name="password"]').val(),
                    },
                    success: function(result) {
                        $('.login-btn').prop('disabled',true);
                        window.location.href = '/manage/dashboard';
                    },
                    fail: function(result) {
                        $('.login-btn').button('reset');
                        CORE.notify.error(result.msg);
                    },
                    error: function(xhr) {
                        $('.login-btn').button('reset');
                        CORE.notify.error('Login Failure');
                    }
                });
            }
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


