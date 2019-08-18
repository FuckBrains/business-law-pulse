
define([
    'text!common/ejs/loading.html',
    'text!pages/sys/pc/profile/ejs/index.html',
    ], function(ejs_loading, ejs_index) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        index: ejs_index,
    };

    $('.site-main').on('click','.update-info-btn',function(event) {
        var form = $('.update-info-form');

        $.validator.addMethod('either', function(value, element, param) {
            return !!value || !!$(param).val();
        }, 'Either email or cellphone is required');

        var validator = form.validate({
            rules: {
                realname: { required: true },
                email: { either: 'input[name="cellphone"]' },
                cellphone: { either: 'input[name="email"]' },
            },
            messages: {
                realname: { required: 'Name is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            var avatar = $('.upload-admin-avatar').data('image');

            $('.update-info-btn').button('loading');
            CORE.ajax.post({
                url: '/admin/info/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    admin: CORE.admin.id,
                    avatar: !!avatar ? avatar.id : '',
                    realname: form.find('input[name="realname"]').val(),
                    gender: form.find('select[name="gender"]').val(),
                    email: form.find('input[name="email"]').val(),
                    cellphone: form.find('input[name="cellphone"]').val(),
                },
                success: function(result) {
                    CORE.notify.info(result.msg);

                    CORE.ajax.session({
                        url: '/session/sync',
                        success: function(result) {
                            CORE.admin = result.data.admin;
                            $('.admin-realname').html(CORE.admin.realname);
                        }
                    });
                },
                complete: function(xhr) {
                    $('.update-info-btn').button('reset');
                },
            });
        }
    });

    $('.site-main').on('click','.update-password-btn',function(event) {
        var form = $('.update-password-form');

        var validator = form.validate({
            rules: {
                new_password: { required: true },
                confirm_new_password: { equalTo: 'input[name="new_password"]' },
            },
            messages: {
                new_password: { required: 'New password is required' },
                confirm_new_password: { equalTo: 'Two new passwords should be indentical' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.update-password-btn').button('loading');
            CORE.ajax.post({
                url: '/admin/password/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    old_password: form.find('input[name="old_password"]').val(),
                    new_password: form.find('input[name="new_password"]').val(),
                },
                success: function(result) {
                    form[0].reset();

                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-password-btn').button('reset');
                },
            });
        }
    });

    return function(ctx,next) {
        CORE.ajax.post({
            url: '/admin/' + CORE.admin.id + '/detail',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            success: function(result) {
                $('.site-main').html(new EJS({ text: ejs.index }).render({ admin: result.data.admin }));
                CORE.image.uploader('.upload-admin-avatar');
            }
        });
    };
});



