
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/firm/ejs/create.html',
    'text!pages/sys/pc/firm/ejs/pick_list.html',
    'bootstrap-multiselect',
    'ueditor','ueditor-lang',
    ], function(ejs_loading, ejs_pagination, ejs_create, ejs_pick_list) {

    var self = this;

    var ejs = {
        loadding: ejs_loading,
        pagination: ejs_pagination,
        create: ejs_create,
        pick_list: ejs_pick_list,
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
        });
    };

    $('.site-main').on('keyup','input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-firm-btn').click();
        }
    });

    $('.site-main').on('click','.search-firm-btn',function(event) {
        self.keyword = $('input[name="keyword"]').val();
        self.page = { no: 1, size: 10 };
        self.search_firm();
    });

    $('.site-main').on('click','.firm-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.firm-pager');
        self.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_firm();
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

    $('.site-main').on('click','.create-firm-btn',function(event) {
        var logo = $('.upload-firm-logo').data('image') || {};
        if (!$.isEmptyObject(logo)) {
            $('input[name="logo"]').val(logo.id);
        }

        $('input[name="note"]').val(UE.getEditor('note_editor').getContent());
        $('input[name="note_cn"]').val(UE.getEditor('note_cn_editor').getContent());
        $('input[name="raw"]').val(UE.getEditor('raw_editor').getContent());

        var form = $('.create-firm-form');

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
            $('.create-firm-btn').button('loading');
            CORE.ajax.post({
                url: '/law/firm/create',
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
                    setTimeout(function() {
                        window.location.reload();
                    },500);
                },
                fail: function(result) {
                    CORE.notify.error(result.msg);
                    $('.create-firm-btn').button('reset');
                },
                error: function(xhr) {
                    $('.create-firm-btn').button('reset');
                    CORE.notify.error(xhr.responseText);
                }
            });
        }
    });

    self.search_firm = function() {
        $('.firm-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/firm/filter',
                data: {
                    keyword: self.keyword,
                    page: self.page,
                },
                success: function(result) {
                    $('.firm-list').html(new EJS({ text: ejs.pick_list }).render({ firms: result.data.firms }));

                    $('.firm-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.page.no,
                        size: self.page.size,
                        total: result.data.total,
                        item: 'firm-pager',
                        btn: 'firm-pager-btn',
                    }));
                }
            });
        },500);
    };

    return function(ctx,next) {
        self.load_config(function() {
            $('.site-main').html(new EJS({ text: ejs.create }).render({ categories: self.categories, areas: self.areas }));
            self.render_components();
        });
    };
});


