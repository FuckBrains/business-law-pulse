
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/firm/ejs/update.html',
    'text!pages/sys/pc/firm/ejs/pick_list.html',
    'text!pages/sys/pc/firm/ejs/deals.html',
    'text!pages/sys/pc/deal/ejs/feedbacks.html',
    'bootstrap-multiselect','bootstrap-rating','bootstrap-datetimepicker',
    'ueditor','ueditor-lang',
    ], function(ejs_loading, ejs_pagination, ejs_update, ejs_pick_list, ejs_deals, ejs_feedbacks) {

    var self = this;
    self.search = {
        firm: { keyword: '', page: { no: 1, size: 20 } },
        deal: { keyword: '', page: { no: 1, size: 20 } },
        feedback: { keyword: '', page: { no: 1, size: 20 } },
    };

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        update: ejs_update,
        pick_list: ejs_pick_list,
        deals: ejs_deals,
        feedbacks: ejs_feedbacks,
    };

    var multiselect_templates = {
        button: '<div class="multiselect dropdown-toggle" data-toggle="dropdown"><span class="multiselect-selected-text"></span></div>',
        ul: '<ul class="multiselect-container dropdown-menu" style="min-width:300px;margin:6px 0px 0px -8px;"></ul>',
    };

    var ueditor_options = {
        toolbars: [
            ['source','|','undo','redo','|','bold','italic','underline','forecolor','backcolor','removeformat','|',
            'justifyleft','justifycenter','justifyright','|','blockquote','insertunorderedlist','inserttable','link','spechars','|',
            'insertimage','|','template','fullscreen']
        ],
        iframeCssUrl: CONST.require.cdn + 'bootstrap/3.3.7/css/bootstrap.min.css',
        initialStyle: "body { width:960px; margin:10px auto; font-size:14px; font-family:'Microsoft YaHei','Helvetica Neue',Helvetica,Arial; }",
        serverUrl: (CONST.ssl ? 'https':'http') + '://' + CONST.domain.api + '/common/ueditor/dispatch',
    };

    self.load_config = function(callback) {
        CORE.ajax.post({
            url: '/law/config/load',
            success: function(result) {
                self.categories = result.data.categories.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                self.areas = result.data.areas.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                callback();
            },
        });
    };

    self.render_components = function() {
        CORE.image.uploader('.upload-firm-logo');

        $('select[name="categories"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            nonSelectedText: '-- Choose --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('select[name="area"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        UE.delEditor('note_editor');
        UE.getEditor('note_editor', {
            customDomain: true,
            pasteplain: true,
            elementPathEnabled: false,
            wordCount: true,
            autoHeightEnabled: false,
            scaleEnabled: false,
            enableAutoSave: false,
            shortcutMenu: false,
            enableContextMenu: true,
            toolbars: ueditor_options.toolbars,
            iframeCssUrl: ueditor_options.iframeCssUrl,
            initialStyle: ueditor_options.initialStyle,
            serverUrl: ueditor_options.serverUrl,
        }).addListener('ready', function() {
            this.setContent(self.firm.note);
        });

        UE.delEditor('note_cn_editor');
        UE.getEditor('note_cn_editor', {
            customDomain: true,
            pasteplain: true,
            elementPathEnabled: false,
            wordCount: true,
            autoHeightEnabled: false,
            scaleEnabled: false,
            enableAutoSave: false,
            shortcutMenu: false,
            enableContextMenu: true,
            toolbars: ueditor_options.toolbars,
            iframeCssUrl: ueditor_options.iframeCssUrl,
            initialStyle: ueditor_options.initialStyle,
            serverUrl: ueditor_options.serverUrl,
        }).addListener('ready', function() {
            this.setContent(self.firm.note_cn);
        });


        UE.delEditor('raw_editor');
        UE.getEditor('raw_editor', {
            customDomain: true,
            pasteplain: true,
            elementPathEnabled: false,
            wordCount: true,
            autoHeightEnabled: false,
            scaleEnabled: false,
            enableAutoSave: false,
            shortcutMenu: false,
            enableContextMenu: true,
            toolbars: ueditor_options.toolbars,
            iframeCssUrl: ueditor_options.iframeCssUrl,
            initialStyle: ueditor_options.initialStyle,
            serverUrl: ueditor_options.serverUrl,
        }).addListener('ready', function() {
            this.setContent(self.firm.raw);
        });

        $('.feedback-created').datetimepicker({
            language:  'zh-CN',
            todayBtn:  1,
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 2,
            maxView: 4,
            forceParse: 0,
            showMeridian: 1,
            format: 'yyyy-mm-dd',
        });

        $('input[name="rating"]').rating({
            filled: 'fa fa-star fa-2x text-primary',
            empty: 'fa fa-star-o fa-2x text-muted',
            start: 0,
            stop: 10,
        });
    };

    $('.site-main').on('keyup','#pick_parent_modal input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-firm-btn').click();
        }
    });

    $('.site-main').on('click','.search-firm-btn',function(event) {
        self.search.firm.keyword = $('#pick_parent_modal input[name="keyword"]').val();
        self.search.firm.page = { no: 1, size: 10 };
        search_firm();
    });

    $('.site-main').on('click','.firm-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.firm-pager');
        self.search.firm.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        search_firm();
    });

    $('.site-main').on('click','.pick-firm-btn',function(event) {
        var item = $(event.currentTarget);
        $('input[name="parent"]').val(item.find('.firm-id').val());
        $('.firm-parent').val(item.find('.firm-name').val());
        $('#pick_parent_modal').modal('hide');
    });

    $('.site-main').on('click','.remove-parent-btn',function(event) {
        $('input[name="parent"]').val('');
        $('.firm-parent').val('');
    });

    $('.site-main').on('click','.update-firm-btn',function(event) {
        var logo = $('.upload-firm-logo').data('image') || {};
        if (!$.isEmptyObject(logo)) {
            $('input[name="logo"]').val(logo.id);
        }

        $('input[name="note"]').val(UE.getEditor('note_editor').getContent());
        $('input[name="note_cn"]').val(UE.getEditor('note_cn_editor').getContent());
        $('input[name="raw"]').val(UE.getEditor('raw_editor').getContent());

        var form = $('.update-firm-form');

        $.validator.addMethod('either', function(value, element, param) {
            return !!value || !!$(param).val();
        }, 'English name or Chinese name is required');

        var validator = form.validate({
            rules: {
                name: { either: 'input[name="name_cn"]' },
                name_cn: { either: 'input[name="name"]' },
                website: { url: true },
                opened: { range: [1900,new Date().getFullYear()] },
                closed: { range: [1900,new Date().getFullYear()] },
            },
            messages: {
                categories: { required: 'Categories is required' },
                area: { required: 'Areas is required' },
                website: { url: 'Website url invalid' },
                opened: { range: 'Year of opened should between 1900 to current year' },
                closed: { range: 'Year of closed should between 1900 to current year' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.update-firm-btn').button('loading');
            CORE.ajax.post({
                url: '/law/firm/' + self.firm.id + '/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    logo: form.find('input[name="logo"]').val(),
                    name: form.find('input[name="name"]').val(),
                    name_cn: form.find('input[name="name_cn"]').val(),
                    parent: form.find('input[name="parent"]').val(),
                    categories: form.find('select[name="categories"]').val() || [],
                    website: form.find('input[name="website"]').val(),
                    phone: form.find('input[name="phone"]').val(),
                    opened: form.find('input[name="opened"]').val() || 0,
                    closed: form.find('input[name="closed"]').val() || 0,
                    area: form.find('select[name="area"]').val() || 0,
                    status: form.find('select[name="status"]').val() || 0,
                    raw: form.find('input[name="raw"]').val(),
                    note: form.find('input[name="note"]').val(),
                    note_cn: form.find('input[name="note_cn"]').val(),
                },
                success: function(result) {
                    CORE.notify.info(result.msg);
                },
                fail: function(result) {
                    CORE.notify.error(result.msg);
                },
                error: function(xhr) {
                    CORE.notify.error(xhr.responseText);
                },
                complete: function(xhr) {
                    $('.update-firm-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('keyup','#deals_tab input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-deal-btn').click();
        }
    });

    $('.site-main').on('click','.search-deal-btn',function(event) {
        self.search.deal.keyword = $('#deals_tab input[name="keyword"]').val();
        self.search.deal.page = { no: 1, size: 10 };
        self.search_deal();
    });

    $('.site-main').on('click','.deal-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.deal-pager');
        self.search.deal.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_deal();
    });

    $('.site-main').on('keyup','#feedbacks_tab input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-feedback-btn').click();
        }
    });

    $('.site-main').on('click','.search-feedback-btn',function(event) {
        self.search.feedback.keyword = $('#feedbacks_tab input[name="keyword"]').val();
        self.search.feedback.page = { no: 1, size: 10 };
        self.search_feedback();
    });

    $('.site-main').on('click','.feedback-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.feedback-pager');
        self.search.feedback.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_feedback();
    });

    $('.site-main').on('click','.create-feedback-btn',function(event) {
        var form = $('.create-feedback-form');

        var created = form.find('input[name="created"]').val();
        created = !!created ? new Date(created + 'T00:00+08:00').getTime():0;

        $('.create-feedback-btn').button('loading');
        CORE.ajax.post({
            url: '/law/firm/' + self.firm.id + '/feedback/create',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                name: form.find('input[name="name"]').val(),
                content: form.find('textarea[name="content"]').val(),
                name_cn: form.find('input[name="name_cn"]').val(),
                content_cn: form.find('textarea[name="content_cn"]').val(),
                created: created,
                rating: form.find('input[name="rating"]').val(),
            },
            success: function(result) {
                CORE.notify.info(result.msg);

                form[0].reset();
                form.find('input[name="rating"]').rating('rate','');
                $('.search-feedback-btn').click();
            },
            fail: function(result) {
                CORE.notify.error(result.msg);
            },
            error: function(xhr) {
                CORE.notify.error(xhr.responseText);
            },
            complete: function(xhr) {
                $('.create-feedback-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.remove-feedback-btn',function(event) {
        if (!confirm('Sure to remove this record ?')) return false;

        var tr = $(event.currentTarget).parents('tr');

        CORE.ajax.post({
            url: '/law/firm/' + self.firm.id + '/feedback/remove',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                feedback: tr.data('feedback-id'),
            },
            success: function(result) {
                CORE.notify.info(result.msg);
                tr.remove();
            },
            fail: function(result) {
                CORE.notify.error(result.msg);
            },
            error: function(xhr) {
                CORE.notify.error(xhr.responseText);
            }
        });
    });

    var search_firm = function() {
        $('.firm-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/firm/filter',
                data: {
                    keyword: self.search.firm.keyword,
                    page: self.search.firm.page,
                },
                success: function(result) {
                    $('.firm-list').html(new EJS({ text: ejs.pick_list }).render({ firms: result.data.firms }));

                    $('.firm-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.search.firm.page.no,
                        size: self.search.firm.page.size,
                        total: result.data.total,
                        item: 'firm-pager',
                        btn: 'firm-pager-btn',
                    }));
                }
            });
        },500);
    };

    self.search_deal = function() {
        $('.deal-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/deal/filter',
                data: {
                    firm: self.firm.id,
                    keyword: self.search.deal.keyword,
                    page: self.search.deal.page,
                },
                success: function(result) {
                    $('.deal-list').html(new EJS({ text: ejs.deals }).render({ deals: result.data.deals }));

                    $('.deal-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.search.deal.page.no,
                        size: self.search.deal.page.size,
                        total: result.data.total,
                        item: 'deal-pager',
                        btn: 'deal-pager-btn',
                    }));
                }
            });
        },500);
    };

    self.search_feedback = function() {
        $('.feedback-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/firm/' + self.firm.id + '/feedback/filter',
                data: {
                    keyword: self.search.feedback.keyword,
                    page: self.search.feedback.page,
                },
                success: function(result) {
                    $('.feedback-list').html(new EJS({ text: ejs.feedbacks }).render({ feedbacks: result.data.feedbacks }));

                    $('.feedback-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.search.feedback.page.no,
                        size: self.search.feedback.page.size,
                        total: result.data.total,
                        item: 'feedback-pager',
                        btn: 'feedback-pager-btn',
                    }));
                }
            });
        },500);
    };

    return function(ctx,next) {
        self.load_config(function() {
            CORE.ajax.post({
                url: '/law/firm/' + ctx.params.firm + '/detail',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                success: function(result) {
                    self.firm = result.data.firm;

                    $('.site-main').html(new EJS({ text: ejs.update }).render({
                        categories: self.categories,
                        areas: self.areas,
                        firm: self.firm,
                    }));

                    self.render_components();
                    self.search_deal();
                    self.search_feedback();
                }
            });
        });
    };
});



