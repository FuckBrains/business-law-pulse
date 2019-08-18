
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/deal/ejs/create.html',
    'bootstrap-multiselect', 'bootstrap-rating', 'bootstrap-datetimepicker',
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
                self.industries = result.data.industries.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                self.areas = result.data.areas.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                self.parties = result.data.parties.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                self.roles = result.data.roles.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                callback();
            },
        });
    };

    self.render_components = function() {
        $('.deal-date').datetimepicker({
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

        $('input[name="uniqueness"],input[name="creativity"],input[name="complexity"],input[name="influence"]').rating({
            filled: 'fa fa-star fa-2x text-primary',
            empty: 'fa fa-star-o fa-2x text-muted',
            start: 0,
            stop: 10,
        });

        $('input[name="deduction"]').rating({
            filled: 'fa fa-star fa-2x text-muted',
            empty: 'fa fa-star-o fa-2x text-muted',
            start: 0,
            stop: 10,
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

    $('.site-main').on('keypress','input[name="value"]',function(event) {
        return (/[\d]/.test(String.fromCharCode(event.keyCode)));
    });

    $('.site-main').on('focus','input[name="value"]',function(event) {
        event.currentTarget.value = event.currentTarget.value.replace(/,/gi,'');
    });

    $('.site-main').on('blur','input[name="value"]',function(event) {
        var value = event.currentTarget.value.toString();

        var length = value.length;
        for (var i=1; i<length/3; i++) {
            var temp = value.slice(0, -4*i+1);          //从后往前数，来获取前面的字符串
            value = value.replace(temp,temp+',');       //给前面的字符串后面加一个逗号
        }

        event.currentTarget.value = value;
    });

    $('.site-main').on('click','.clear-date-btn',function(event) {
        $('input[name="date"]').val('');
    });

    $('.site-main').on('click','.create-deal-btn',function(event) {
        $('input[name="note"]').val(UE.getEditor('note_editor').getContent());
        $('input[name="note_cn"]').val(UE.getEditor('note_cn_editor').getContent());
        $('input[name="raw"]').val(UE.getEditor('raw_editor').getContent());

        var form = $('.create-deal-form');

        $.validator.addMethod('either', function(value, element, param) {
            return !!value || !!$(param).val();
        }, 'English title or Chinese title is required');

        var validator = form.validate({
            rules: {
                title: { either: 'input[name="title_cn"]' },
                title_cn: { either: 'input[name="title"]' },
                categories: { required: true },
            },
            messages: {
                categories: { required: 'Categories is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            var date = $('input[name="date"]').val();
            date = !!date ? new Date(date + 'T00:00+08:00').getTime():0;

            $('.create-deal-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/create',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    title: form.find('input[name="title"]').val(),
                    title_cn: form.find('input[name="title_cn"]').val(),
                    categories: form.find('select[name="categories"]').val() || [],
                    value: form.find('input[name="value"]').val() || 0,
                    value_txt: form.find('input[name="value_txt"]').val(),
                    status: form.find('select[name="status"]').val() || 0,
                    date: date,

                    uniqueness: form.find('input[name="uniqueness"]').val(),
                    uniqueness_remark: form.find('input[name="uniqueness_remark"]').val(),
                    creativity: form.find('input[name="creativity"]').val(),
                    creativity_remark: form.find('input[name="creativity_remark"]').val(),
                    complexity: form.find('input[name="complexity"]').val(),
                    complexity_remark: form.find('input[name="complexity_remark"]').val(),
                    influence: form.find('input[name="influence"]').val(),
                    influence_remark: form.find('input[name="influence_remark"]').val(),
                    deduction: form.find('input[name="deduction"]').val(),
                    deduction_remark: form.find('input[name="deduction_remark"]').val(),

                    remark: form.find('input[name="remark"]').val(),
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
                    $('.create-deal-btn').button('reset');
                },
                error: function(xhr) {
                    $('.create-deal-btn').button('reset');
                    CORE.notify.error(xhr.responseText);
                }
            });
        }
    });

    return function(ctx,next) {
        self.load_config(function() {
            var ejs_html = new EJS({ text: ejs.create }).render({
                categories: self.categories,
                industries: self.industries,
                areas: self.areas,
                parties: self.parties,
                roles: self.roles,
            });
            $('.site-main').html(ejs_html);

            self.render_components();
        });
    };
});



