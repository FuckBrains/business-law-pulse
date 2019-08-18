
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/admin/ejs/update.html',
    ], function(ejs_loading, ejs_pagination, ejs_update) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        update: ejs_update,
    };

    self.load_permission = function(callback) {
        CORE.ajax.post({
            url: '/admin/permission/load',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {},
            success: function(result) {
                self.permissions = result.data.permissions;
                callback();
            }
        });
    };
    $('.site-main').on('click','.update-profile-btn',function(event) {
        var form = $('.update-profile-form');

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
            $('.update-profile-btn').button('loading');
            CORE.ajax.post({
                url: '/admin/info/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    admin: self.admin.id,
                    realname: form.find('input[name="realname"]').val(),
                    gender: form.find('select[name="gender"]').val(),
                    email: form.find('input[name="email"]').val(),
                    cellphone: form.find('input[name="cellphone"]').val(),
                },
                success: function(result) {
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-profile-btn').button('reset');
                },
            });
        }
    });

    $('.site-main').on('click','.update-permission-btn',function(event) {
        var permssions = [];
        $('input[name="permission"]:checked').each(function() { permissions.push($(this).val()); });

        $('.update-permission-btn').button('loading');
        CORE.ajax.post({
            url: '/admin/permission/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                admin: self.admin.id,
                permissions: permissions,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-permission-btn').button('reset');
            },
        });
    });

    return function(ctx,next) {
        self.load_permission(function() {
            CORE.ajax.post({
                url: '/admin/' + ctx.params.admin + '/detail',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                success: function(result) {
                    self.admin = result.data.admin;

                    $('.site-main').html(new EJS({ text: ejs.update }).render({
                        admin: self.admin,
                        permissions: self.permissions,
                    }));

                    CORE.image.uploader('.upload-admin-avatar');
                },
            });
        });
    };
});




