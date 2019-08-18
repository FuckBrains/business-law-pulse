/*jslint browser:true*/

define([
    'text!common/ejs/loading.html',
    'text!pages/www/pc/debug/ejs/docs.html',
    'text!pages/www/pc/debug/ejs/readme.html',
    'text!pages/www/pc/debug/ejs/doc_module_list.html',
    'text!pages/www/pc/debug/ejs/doc_module_detail.html',
    'text!pages/www/pc/debug/ejs/doc_item_detail.html',
    'ueditor','ueditor-lang'
    ], function(ejs_loading,ejs_docs,ejs_readme,ejs_doc_module_list,ejs_doc_module_detail,ejs_doc_item_detail) {

    var self = this;
    self.module = {};

    var ejs = {
        loading: ejs_loading,
        docs: ejs_docs,
        readme: ejs_readme,
        doc_module_list: ejs_doc_module_list,
        doc_module_detail: ejs_doc_module_detail,
        doc_item_detail: ejs_doc_item_detail,
    };

    $('.site-main').on('click','.show-readme-btn',function(event) {
        self.module = {};
        $('#doc_content_tab').html(new EJS({ text: ejs.readme }).render({}));
        $('.doc-content-tab').tab('show');
    });

    $('.site-main').on('click','.module-btn',function(event) {
        var module_id = $(event.currentTarget).data('module-id');
        $('.doc-content-tab').tab('show');
        if (module_id === self.module.id) { return false; }

        self.module = { id: module_id };
        self.load_module_list();
    });

    $('.site-main').on('click','.create-module-btn',function(event) {
        var form = $('.create-module-form');

        var validator = form.validate({
            rules: {
                code: { required: true },
                name: { required: true },
                remark: { required: true },
            },
            messages: {
                code: { required: 'module code is required' },
                name: { required: 'module name is required' },
                remark: { required: 'module remark is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.create-module-btn').button('loading');
            CORE.ajax.post({
                url: '/common/doc/module/create',
                data: {
                    code: form.find('input[name="code"]').val(),
                    name: form.find('input[name="name"]').val(),
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    $('.create-module-form')[0].reset();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.create-module-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.update-module-modal-btn',function(event) {
        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/detail',
            success: function(result) {
                var module = result.data.module;
                $('.update-module-form input[name="code"]').val(module.code);
                $('.update-module-form input[name="name"]').val(module.name);
                $('.update-module-form textarea[name="remark"]').val(module.remark);
                $('#update_module_modal').modal('show');
            }
        });
    });

    $('.site-main').on('click','.update-module-btn',function(event) {
        var form = $('.update-module-form');

        var validator = form.validate({
            rules: {
                code: { required: true },
                name: { required: true },
                remark: { required: true },
            },
            messages: {
                code: { required: 'module code is required' },
                name: { required: 'module name is required' },
                remark: { required: 'module remark is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.update-module-btn').button('loading');
            CORE.ajax.post({
                url: '/common/doc/module/' + self.module.id + '/update',
                data: {
                    code: form.find('input[name="code"]').val(),
                    name: form.find('input[name="name"]').val(),
                    remark: form.find('textarea[name="remark"]').val(),
                },

                success: function(result) {
                    $('.update-module-form')[0].reset();
                    $('#update_module_modal').modal('hide');
                    self.load_module_list();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-module-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.seq-prev-item-btn',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        var item_id = item_record.data('item-id');

        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + item_id + '/seq',
            data: { action: 'P' },

            success: function(result) {
                var prev_item_record = item_record.prev();
                item_record.insertBefore(prev_item_record);

                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('click','.seq-next-item-btn',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        var item_id = item_record.data('item-id');

        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + item_id + '/seq',
            data: { action: 'N' },

            success: function(result) {
                var next_item_record = item_record.next();
                item_record.insertAfter(next_item_record);

                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('click','.seq-first-item-btn',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        var item_id = item_record.data('item-id');

        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + item_id + '/seq',
            data: { action: 'F' },

            success: function(result) {
                var first_item_record = $('.item-record').first();
                item_record.insertBefore(first_item_record);

                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('click','.seq-last-item-btn',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        var item_id = item_record.data('item-id');

        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + item_id + '/seq',
            data: { action: 'L' },

            success: function(result) {
                var last_item_record = $('.item-record').last();
                item_record.insertAfter(last_item_record);

                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('click','.create-item-tab-btn',function(event) {
        $('.create-item-tab').tab('show');
    });

    $('.site-main').on('click','.create-item-btn',function(event) {
        var data = {
            module: self.module,
            url: $('#create_item_tab').find('input[name="url"]').val(),
            type: $('#create_item_tab').find('select[name="type"]').val(),
            remark: UE.getEditor('create_item_remark_editor').getContent(),
            input: UE.getEditor('create_item_input_editor').getContent(),
            output: UE.getEditor('create_item_output_editor').getContent(),
        };

        if (!data.url) { CORE.notify.error('item url is required'); return false; }
        if (!data.type) { CORE.notify.error('item type is required'); return false; }
        if (!data.remark) { CORE.notify.error('item remark is required'); return false; }
        if (!data.input) { CORE.notify.error('item input is required'); return false; }
        if (!data.output) { CORE.notify.error('item output is required'); return false; }

        $('.create-item-btn').button('loading');
        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/create',
            data: data,

            success: function(result) {
                $('#create_item_tab').find('input[name="url"]').val('');
                $('#create_item_tab').find('select[name="type"]').val('');
                window.UE.getEditor('create_item_remark_editor').setContent('');
                window.UE.getEditor('create_item_input_editor').setContent('');
                window.UE.getEditor('create_item_output_editor').setContent('');

                $('.item-list').append(new EJS({ text: ejs.doc_item_detail }).render({ index: 0, item: result.data.item }));

                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.create-item-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.remove-item-btn',function(event) {
        if (!window.confirm('Sure to remove this item ?')) { return false; }

        var item_record = $(event.currentTarget).parents('.item-record');
        var item_id = item_record.data('item-id');

        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + item_id + '/remove',

            success: function(result) {
                item_record.remove();
            }
        });
    });

    $('.site-main').on('click','.update-item-tab-btn',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        var item_id = item_record.data('item-id');

        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + item_id + '/detail',

            success: function(result) {
                var item = result.data.item;
                $('#edit_item_tab').find('input[name="item_id"]').val(item.id);
                $('#edit_item_tab').find('input[name="url"]').val(item.url);
                $('#edit_item_tab').find('select[name="type"]').val(item.type);
                window.UE.getEditor('update_item_remark_editor').setContent(item.remark);
                window.UE.getEditor('update_item_input_editor').setContent(item.input);
                window.UE.getEditor('update_item_output_editor').setContent(item.output);

                $('.update-item-tab').tab('show');
            }
        });
    });

    $('.site-main').on('click','.update-item-btn',function(event) {
        var data = {
            id: $('#edit_item_tab').find('input[name="item_id"]').val(),
            module: self.module,
            url: $('#edit_item_tab').find('input[name="url"]').val(),
            type: $('#edit_item_tab').find('select[name="type"]').val(),
            remark: window.UE.getEditor('update_item_remark_editor').getContent(),
            input: window.UE.getEditor('update_item_input_editor').getContent(),
            output: window.UE.getEditor('update_item_output_editor').getContent(),
        };

        if (!data.url) { CORE.notify.error('item url is required'); return false; }
        if (!data.type) { CORE.notify.error('item type is required'); return false; }
        if (!data.remark) { CORE.notify.error('item remark is required'); return false; }
        if (!data.input) { CORE.notify.error('item input is required'); return false; }
        if (!data.output) { CORE.notify.error('item output is required'); return false; }

        $('.update-item-btn').button('loading');
        CORE.ajax.post({
            url: '/common/doc/module/' + self.module.id + '/item/' + data.id + '/update',
            data: data,

            success: function(result) {
                CORE.ajax.post({
                    url: '/common/doc/module/' + self.module.id + '/item/' + data.id + '/detail',

                    success: function(result) {
                        $('.item-record').each(function() {
                            var item = $(this);
                            if (item.data('item-id') === data.id) {
                                item.replaceWith(new EJS({ text: ejs.doc_item_detail }).render({ index: 0, item: result.data.item }));
                            }
                        });

                        $('.doc-content-tab').tab('show');
                    }
                });

                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-item-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.item-input-hint',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        item_record.find('.item-input-hint').addClass('hidden');
        item_record.find('.item-input-content').removeClass('hidden');
    });

    $('.site-main').on('click','.item-output-hint',function(event) {
        var item_record = $(event.currentTarget).parents('.item-record');
        item_record.find('.item-output-hint').addClass('hidden');
        item_record.find('.item-output-content').removeClass('hidden');
    });

    self.load_module_list = function() {
        $('html,body').animate({scrollTop: 0},500);

        $('#doc_content_tab').html(new EJS({ text: ejs.loading }).render({ padding: '200px', font: '50px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/common/doc/module/' + self.module.id + '/detail',
                success: function(result) {
                    var module = result.data.module;

                    CORE.ajax.post({
                        url: '/common/doc/module/' + self.module.id + '/item/list',
                        success: function(result) {
                            $('#doc_content_tab').html(new EJS({ text: ejs.doc_module_detail }).render({
                                module: module,
                                items: result.data.items,
                                ejs: ejs,
                            }));
                        }
                    });
                }
            });
        }, 500);
    };

    self.init_editor = function(editor_id) {
        window.UE.delEditor(editor_id);
        window.UE.getEditor(editor_id, {
            customDomain: true,
            pasteplain: true,
            elementPathEnabled: false,
            wordCount: true,
            autoHeightEnabled: false,
            scaleEnabled: false,
            enableAutoSave: false,
            shortcutMenu: false,
            enableContextMenu: true,
            toolbars: [
                ['source','|','undo','redo','|','bold','italic','underline','forecolor','backcolor','removeformat','|',
                'justifyleft','justifycenter','justifyright','|','blockquote','insertunorderedlist','inserttable','link','spechars','|',
                'insertimage','|','template','fullscreen']
            ],
            iframeCssUrl: CONST.require.cdn + 'bootstrap/3.3.7/css/bootstrap.min.css',
            initialStyle: "body { width:780px; margin:10px auto; font-size:12px; font-family:monospace; }",
            serverUrl: (CONST.ssl ? 'https':'http') + '://' + CONST.domain.api + '/common/ueditor/dispatch',
        });
    };

    return function(ctx,next) {
        var ejs_html = new EJS({ text: ejs_docs }).render({});
        $('.site-main').html(ejs_html);

        $(window).resize(function(event) {
            $('.doc-sidebar').css('max-height', $(window).height());
            $('.doc-content').css('max-height', $(window).height());
        });
        $(window).resize();

        CORE.ajax.post({
            url: '/common/doc/module/list',
            success: function(result) {
                self.modules = result.data.modules.reduce(function(dict,item) { dict[item.code] = item; return dict; },{});
                var ejs_html = new EJS({ text: ejs_doc_module_list }).render({ modules: self.modules });
                $('.doc-module-list').html(ejs_html);
            }
        });

        $('#doc_content_tab').html(new EJS({ text: ejs.readme }).render({}));

        self.init_editor('create_item_remark_editor');
        self.init_editor('update_item_remark_editor');

        self.init_editor('create_item_input_editor');
        self.init_editor('update_item_input_editor');

        self.init_editor('create_item_output_editor');
        self.init_editor('update_item_output_editor');
    };
});



