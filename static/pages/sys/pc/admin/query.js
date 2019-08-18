
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/admin/ejs/query.html',
    'text!pages/sys/pc/admin/ejs/list.html',
    ], function(ejs_loading, ejs_pagination, ejs_query, ejs_list) {

    var self = this;
    self.page = { no: 1, size: 20 };
    self.keyword = '';

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        query: ejs_query,
        list: ejs_list,
    };

    self.search_admin = function() {
        $('html,body').animate({scrollTop:0},100);

        $('.admin-list').html(new EJS({ text: ejs.loading }).render({ padding: '100px', font: '50px' }));
        $('.admin-pagination').html('');

        setTimeout(function() {
            CORE.ajax.post({
                url: '/admin/filter',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    page: self.page,
                    keyword: self.keyword,
                },
                success: function(result) {
                    $('.admin-list').html(new EJS({ text: ejs.list }).render({ admins: result.data.admins }));
                    $('.admin-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.page.no,
                        size: self.page.size,
                        total: result.data.total,
                        item: 'admin-pager',
                        btn: 'admin-pager-btn',
                    }));
                }
            });
        },500);
    };

    $('.site-main').on('keyup','input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-admin-btn').click();
        }
    });

    $('.site-main').on('click','.search-admin-btn',function(event) {
        self.keyword = $('input[name="keyword"]').val();
        self.page = { no: 1, size: 20 };
        self.search_admin();
    });

    $('.site-main').on('click','.admin-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.admin-pager');
        self.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_admin();
    });

    $('.site-main').on('click','.reset-admin-btn',function(event) {
        var tr = $(event.currentTarget).parents('tr');
        var form = $('.reset-password-form');
        form[0].reset();
        form.find('input[name="admin_id"]').val(tr.data('admin-id'));
        form.find('.admin-name').html(tr.find('.admin-name').html());
        $('#reset_password_modal').modal('show');
    });

    $('.site-main').on('click','.submit-password-btn',function(event) {
        var form = $('.reset-password-form');

        var validator = form.validate({
            rules: {
                password: { required: true },
                confirm_password: { equalTo: 'input[name="password"]' },
            },
            messages: {
                password: { required: 'Password is required' },
                confirm_password: { equalTo: 'Two passwords should be indentical' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            CORE.ajax.post({
                url: '/admin/password/reset',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    admin: form.find('input[name="admin_id"]').val(),
                    password: form.find('input[name="password"]').val(),
                },
                success: function(result) {
                    CORE.notify.info(result.msg);
                    $('#reset_password_modal').modal('hide');
                }
            });
        }
    });

    $('.site-main').on('click','.disable-admin-btn',function(event) {
        if (!confirm('Are you sure of disabling this admin ?')) return false;
        var tr = $(event.currentTarget).parents('tr');
        CORE.ajax.post({
            url: '/admin/status/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                admin: tr.data('admin-id'),
                status: 0,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            }
        });
    });

    return function(ctx,next) {
        $('.site-main').html(new EJS({ text: ejs.query }).render({}));
        self.search_admin();
    };
});


