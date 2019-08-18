
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/admin/ejs/create.html',
    ], function(ejs_loading, ejs_pagination, ejs_create) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        create: ejs_create,
    };

    $('.site-main').on('click','.create-admin-btn',function(event) {
        var form = $('.create-admin-form');

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
            $('.create-admin-btn').button('loading');
            CORE.ajax.post({
                url: '/admin/create',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    realname: form.find('input[name="realname"]').val(),
                    gender: form.find('select[name="gender"]').val(),
                    email: form.find('input[name="email"]').val(),
                    cellphone: form.find('input[name="cellphone"]').val(),
                },
                success: function(result) {
                    CORE.notify.info(result.msg);
                    window.location.reload();
                },
                fail: function(result) {
                    CORE.notify.error(result.msg);
                    $('.create-admin-btn').button('reset');
                },
            });
        }
    });

    return function(ctx,next) {
        $('.site-main').html(new EJS({ text: ejs.create }).render({}));
        CORE.image.uploader('.upload-admin-avatar');
    };
});



