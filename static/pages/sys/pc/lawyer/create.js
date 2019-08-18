
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/lawyer/ejs/create.html',
    'bootstrap-multiselect',
    'ueditor','ueditor-lang',
    ], function(ejs_loading, ejs_pagination, ejs_create) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        create: ejs_create,
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

    $('.site-main').on('click','.create-lawyer-btn',function(event) {
        var avatar = $('.upload-lawyer-avatar').data('image') || {};
        if (!$.isEmptyObject(avatar)) {
            $('input[name="avatar"]').val(avatar.id);
        }

        $('input[name="note"]').val(UE.getEditor('note_editor').getContent());
        $('input[name="note_cn"]').val(UE.getEditor('note_cn_editor').getContent());
        $('input[name="raw"]').val(UE.getEditor('raw_editor').getContent());

        var form = $('.create-lawyer-form');

        $.validator.addMethod('either', function(value, element, param) {
            return !!value || !!$(param).val();
        }, 'English name or Chinese name is required');

        var validator = form.validate({
            rules: {
                name: { either: 'input[name="name_cn"]' },
                name_cn: { either: 'input[name="name"]' },
            },
            messages: {
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.create-lawyer-btn').button('loading');
            CORE.ajax.post({
                url: '/law/lawyer/create',
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
                    title: form.find('input[name="title"]').val(),
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
                    $('.create-lawyer-btn').button('reset');
                },
                error: function(xhr) {
                    $('.create-lawyer-btn').button('reset');
                    CORE.notify.error(xhr.responseText);
                }
            });
        }
    });

    return function(ctx,next) {
        self.load_config(function() {
            $('.site-main').html(new EJS({ text: ejs.create }).render({ categories: self.categories }));
            self.render_components();
        });
    };
});


