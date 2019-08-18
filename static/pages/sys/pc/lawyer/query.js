
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/lawyer/ejs/query.html',
    'text!pages/sys/pc/lawyer/ejs/list.html',
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

    $('.site-main').on('keyup','input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-lawyer-btn').click();
        }
    });

    $('.site-main').on('click','.search-lawyer-btn',function(event) {
        self.keyword = $('input[name="keyword"]').val();
        self.page = { no: 1, size: 20 };
        self.search_lawyer();
    });

    $('.site-main').on('click','.lawyer-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.lawyer-pager');
        self.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_lawyer();
    });

    $('.site-main').on('click','.remove-lawyer-btn',function(event) {
        if (!conlawyer('Are you sure of removing this record ?')) return false;

        var tr = $(event.currentTarget).parents('tr');

        CORE.ajax.post({
            url: '/law/lawyer/' + tr.data('lawyer-id') + '/remove',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            success: function(result) {
                tr.remove();
                CORE.notify.info(result.msg);
            }
        });
    });

    self.search_lawyer = function() {
        $('html,body').animate({scrollTop:0},100);

        $('.lawyer-list').html(new EJS({ text: ejs.loading }).render({ padding: '100px', font: '50px' }));
        $('.lawyer-pagination').html('');

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/lawyer/filter',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    page: self.page,
                    keyword: self.keyword,
                },
                success: function(result) {
                    $('.lawyer-list').html(new EJS({ text: ejs.list }).render({ lawyers: result.data.lawyers }));

                    $('.lawyer-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.page.no,
                        size: self.page.size,
                        total: result.data.total,
                        item: 'lawyer-pager',
                        btn: 'lawyer-pager-btn',
                    }));
                }
            });
        },500);
    };

    return function(ctx,next) {
        $('.site-main').html(new EJS({ text: ejs.query }).render({}));
        self.search_lawyer();
    };
});


