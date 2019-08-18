
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/lawyer/ejs/update.html',
    'text!pages/sys/pc/lawyer/ejs/deals.html',
    'text!pages/sys/pc/lawyer/ejs/career.html',
    'text!pages/sys/pc/lawyer/ejs/filter_deals.html',
    'text!pages/sys/pc/deal/ejs/feedbacks.html',
    'bootstrap-multiselect','bootstrap-rating','bootstrap-datetimepicker',
    'ueditor','ueditor-lang',
    ], function(ejs_loading, ejs_pagination, ejs_update, ejs_deals, ejs_career, ejs_filter_deals, ejs_feedbacks) {

    var self = this;
    self.search = {
        deal: { keyword: '', page: { no: 1, size: 20 } },
        feedback: { keyword: '', page: { no: 1, size: 20 } },
    };

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        update: ejs_update,
        deals: ejs_deals,
        career: ejs_career,
        filter_deals: ejs_filter_deals,
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
                callback();
            },
        });
    };

    self.render_components = function() {
        CORE.image.uploader('.upload-lawyer-avatar');

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
            this.setContent(self.lawyer.note);
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
            this.setContent(self.lawyer.note_cn);
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
            this.setContent(self.lawyer.raw);
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

    $('.site-main').on('click','.update-lawyer-btn',function(event) {
        var avatar = $('.upload-lawyer-avatar').data('image') || {};
        if (!$.isEmptyObject(avatar)) {
            $('input[name="avatar"]').val(avatar.id);
        }

        $('input[name="note"]').val(UE.getEditor('note_editor').getContent());
        $('input[name="note_cn"]').val(UE.getEditor('note_cn_editor').getContent());
        $('input[name="raw"]').val(UE.getEditor('raw_editor').getContent());

        var form = $('.update-lawyer-form');

        $.validator.addMethod('either', function(value, element, param) {
            return !!value || !!$(param).val();
        }, 'English name or Chinese name is required');

        var validator = form.validate({
            rules: {
                name: { either: 'input[name="name_cn"]' },
                name_cn: { either: 'input[name="name"]' },
                categories: { required: true },
                area: { required: true },
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
            $('.update-lawyer-btn').button('loading');
            CORE.ajax.post({
                url: '/law/lawyer/' + self.lawyer.id + '/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    avatar: form.find('input[name="avatar"]').val(),
                    name: form.find('input[name="name"]').val(),
                    name_cn: form.find('input[name="name_cn"]').val(),
                    categories: form.find('select[name="categories"]').val() || [],
                    gender: form.find('select[name="gender"]').val(),
                    position: form.find('input[name="position"]').val(),
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
                    $('.update-lawyer-btn').button('reset');
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
            url: '/law/lawyer/' + self.lawyer.id + '/feedback/create',
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
            url: '/law/lawyer/' + self.lawyer.id + '/feedback/remove',
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

    $('.site-main').on('click','.list-firm-deal-btn',function(event) {
        var btn = $(event.currentTarget);
        var firm = { id: btn.parents('tr').data('firm-id') };

        $('.firm-deal-list').html(new EJS({ text: ejs.loading }).render({ padding: '50px', font: '30px' }));
        $('#firm_deal_modal').modal('show');

        var deals = [];
        for (var i=0;i<self.career.length;i++) {
            if (self.career[i].firm.id == firm.id) {
                deals = self.career[i].deals;
                break;
            }
        }

        $('.firm-deal-list').html(new EJS({ text: ejs.filter_deals }).render({ deals: deals }));
    });

    self.load_career = function() {
        CORE.ajax.post({
            url: '/law/lawyer/' + self.lawyer.id + '/career',
            success: function(result) {
                self.career = result.data.career;
                $('.career').html(new EJS({ text: ejs.career }).render({ career: self.career }));
            }
        });
    };

    self.search_deal = function() {
        $('.deal-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/deal/filter',
                data: {
                    lawyer: self.lawyer.id,
                    keyword: self.search.deal.keyword,
                    page: self.search.deal.page,
                },
                success: function(result) {
                    $('.deal-list').html(new EJS({ text: ejs.deals}).render({ deals: result.data.deals }));

                    var ejs_html = new EJS({ text: ejs.pagination }).render({
                        no: self.search.deal.page.no,
                        size: self.search.deal.page.size,
                        total: result.data.total,
                        item: 'deal-pager',
                        btn: 'deal-pager-btn',
                    });
                    $('.deal-pagination').html(ejs_html);
                }
            });
        },500);
    };

    self.search_feedback = function() {
        $('.feedback-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/lawyer/' + self.lawyer.id + '/feedback/filter',
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
                url: '/law/lawyer/' + ctx.params.lawyer + '/detail',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                success: function(result) {
                    self.lawyer = result.data.lawyer;

                    $('.site-main').html(new EJS({ text: ejs.update }).render({
                        categories: self.categories,
                        lawyer: self.lawyer,
                    }));

                    self.render_components();

                    self.load_career();
                    self.search_deal();
                    self.search_feedback();
                }
            });
        });
    };
});



