
define([
    'text!pages/www/pc/generate/ejs/main.html',
    'text!pages/www/pc/generate/ejs/deal_client_list.html',
    'text!pages/www/pc/generate/ejs/deal_firm_list.html',
    'text!pages/www/pc/generate/ejs/deal_lawyer_list.html',
    'text!pages/www/pc/generate/ejs/deal_summary.html',
    'text!pages/www/pc/generate/ejs/update_deal_client.html',
    'text!pages/www/pc/generate/ejs/update_deal_firm.html',
    'text!pages/www/pc/generate/ejs/update_deal_lawyer.html',
    'text!pages/www/pc/generate/ejs/preview.html',
    'bootstrap-multiselect','bootstrap-rating','bootstrap-datetimepicker',
    'ueditor','ueditor-lang',
    ], function(ejs_main,ejs_deal_client_list,ejs_deal_firm_list,ejs_deal_lawyer_list,ejs_deal_summary,
                ejs_update_deal_client,ejs_update_deal_firm,ejs_update_deal_lawyer,ejs_preview) {

    var self = this;
    self.clients = [];
    self.firms = [];
    self.lawyers = [];

    var ejs = {
        main: ejs_main,
        deal_client_list: ejs_deal_client_list,
        deal_firm_list: ejs_deal_firm_list,
        deal_lawyer_list: ejs_deal_lawyer_list,
        deal_summary: ejs_deal_summary,
        update_deal_client: ejs_update_deal_client,
        update_deal_firm: ejs_update_deal_firm,
        update_deal_lawyer: ejs_update_deal_lawyer,
        update_preview: ejs_preview,
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

    CONST.lang = window.localStorage.getItem('blp:lang') || 'en';

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
            }
        });
    };

    self.get_summary = function() {
        var summary = {};

        self.clients.forEach(function(client) {
            if (!!summary[client.party]) {
                summary[client.party].clients.push(client);
            } else {
                summary[client.party] = { clients: [client], firms: [] };
            }
        });

        self.firms.forEach(function(firm) {
            firm.lawyers = [];
            self.lawyers.forEach(function(lawyer) {
                if (lawyer.firm==firm.id) {
                    firm.lawyers.push(lawyer);
                }
            });

            if (!!summary[firm.party]) {
                summary[firm.party].firms.push(firm);
            } else {
                summary[firm.party] = { clients: [], firms: [firm] };
            }
        });

        return summary;
    };

    self.list_client = function() {
        $('.deal-client-list').html(new EJS({text: ejs.deal_client_list }).render({
            industries: self.industries,
            areas: self.areas,
            parties: self.parties,
            clients: self.clients,
        }));

        $('.deal-summary-tab').data('client','Y');
        if ($('.deal-summary-tab').data('client') && $('.deal-summary-tab').data('firm') && $('.deal-summary-tab').data('lawyer')) {
            $('.deal-summary-tab').removeClass('hidden');
        }
    };

    self.list_firm = function() {
        $('.deal-firm-list').html(new EJS({ text: ejs.deal_firm_list }).render({
            parties: self.parties,
            areas: self.areas,
            firms: self.firms,
        }));

        if (CONST.lang=='en') {
            $('select[name="firm"]').html('<option value="">-- Choose --</option>');
        } else {
            $('select[name="firm"]').html('<option value="">-- 选择 --</option>');
        }

        var firm_ids = [];
        self.firms.forEach(function(item) {
            if (firm_ids.indexOf(item.id) == -1) {
                firm_ids.push(item.id);
                var option = $('<option></option>');
                option.attr('value',item.id);
                option.html(item.name);
                $('select[name="firm"]').append(option);
            }
        });

        $('.deal-summary-tab').data('firm','Y');
        if ($('.deal-summary-tab').data('client') && $('.deal-summary-tab').data('firm') && $('.deal-summary-tab').data('lawyer')) {
            $('.deal-summary-tab').removeClass('hidden');
        }
    };

    self.list_lawyer = function() {
        var firms = self.firms.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});

        $('.deal-lawyer-list').html(new EJS({ text: ejs_deal_lawyer_list }).render({
            roles: self.roles,
            lawyers: self.lawyers,
            firms: firms,
        }));

        $('.deal-summary-tab').data('lawyer','Y');
        if ($('.deal-summary-tab').data('client') && $('.deal-summary-tab').data('firm') && $('.deal-summary-tab').data('lawyer')) {
            $('.deal-summary-tab').removeClass('hidden');
        }
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
            nonSelectedText: CONST.lang=='en' ? '-- Choose --':'-- 选择 --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('select[name="party"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('select[name="industries"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            nonSelectedText: CONST.lang=='en' ? '-- Choose --':'-- 选择 --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('select[name="areas"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            nonSelectedText: CONST.lang=='en' ? '-- Choose --':'-- 选择 --',
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
    };

    $('.site-main').on('click','.lang-en-btn',function(event) {
        window.localStorage.setItem('blp:lang', 'en');
        window.location.reload();
    });

    $('.site-main').on('click','.lang-cn-btn',function(event) {
        window.localStorage.setItem('blp:lang', 'cn');
        window.location.reload();
    });

    $('.site-main').on('click','.preview-btn',function(event) {
        var form = $('.add-deal-form');
        self.deal = {
            title: form.find('input[name="title"]').val(),
            categories: form.find('select[name="categories"]').val() || [],
            value: form.find('input[name="value"]').val(),
            value_txt: form.find('input[name="value_txt"]').val(),
            date: form.find('input[name="date"]').val(),
            status: form.find('select[name="status"]').val(),
            clients: self.clients,
            firms: self.firms,
            lawyers: self.lawyers,
            summary: self.get_summary(),
            note: UE.getEditor('note_editor').getContent(),
        };

        $('.preview-content').html(new EJS({ text: ejs.preview }).render({
            categories: self.categories,
            industries: self.industries,
            areas: self.areas,
            parties: self.parties,
            roles: self.roles,
            deal: self.deal,
        }));
        $('#preview_modal').modal('show');

        $('.download-pdf-btn').addClass('hidden');
        $('.export-pdf-btn').removeClass('hidden');
        $('.export-pdf-btn').button('reset');
    });

    $('.site-main').on('click','.export-pdf-btn',function(event) {
        var html = $('.preview-content').html();
        html = html.trim().replace(/\n|\r/g,'').replace(/>\s+</g,'><');

        $('.download-pdf-btn').addClass('hidden');
        $('.export-pdf-btn').button('loading');
        CORE.ajax.post({
            url: (CONST.ssl ? 'https':'http') + '://' + CONST.domain.www + '/generate/pdf',
            data: {
                deal: self.deal,
                lang: CONST.lang,
                title: $('.add-deal-form input[name="title"]').val(),
                header: {
                    left: $('input[name="left"]').val(),
                    center: $('input[name="center"]').val(),
                    right: $('input[name="right"]').val(),
                },
                html: html,
            },
            success: function(result) {
                var btn = $('.download-pdf-btn');
                btn.attr('download', result.data.filename);
                btn.attr('href', result.data.pdf);
                btn.removeClass('hidden');

                $('.export-pdf-btn').addClass('hidden');
            },
            complete: function(xhr) {
                $('.export-pdf-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.add-deal-client-btn',function(event) {
        var form = $('.add-deal-client-form');

        var validator = form.validate({
            rules: {
                name: { required: true },
                party: { required: true },
            },
            messages: {
                name: { required: 'Name is required' },
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            self.clients.push({
                id: new Date().getTime(),
                name: form.find('input[name="name"]').val(),
                party: form.find('select[name="party"]').val(),
                industries: form.find('select[name="industries"]').val() || [],
                areas: form.find('select[name="areas"]').val() || [],
            });

            form[0].reset();
            form.find('select[name="party"],select[name="industries"],select[name="areas"]').multiselect('refresh');

            self.list_client();
            CORE.notify.info('Add Done');
        }
    });

    $('.site-main').on('click','.update-deal-client',function(event) {
        var client_id = $(event.currentTarget).parents('tr').data('client-id');
        var client = null;
        self.clients.forEach(function(item) {
            if (item.id == client_id) {
                client = item;
            }
        });

        $('.update-deal-client-form').html(new EJS({ text: ejs.update_deal_client }).render({
            industries: self.industries,
            areas: self.areas,
            parties: self.parties,
            deal: self.deal,
            client: client,
        }));
        $('.deal-client-list, .update-deal-client-form').toggleClass('hidden');

        $('.update-deal-client-form').find('select[name="party"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('.update-deal-client-form').find('select[name="industries"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            nonSelectedText: CONST.lang=='en' ? '-- Choose --':'-- 选择 --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('.update-deal-client-form').find('select[name="areas"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            nonSelectedText: CONST.lang=='en' ? '-- Choose --':'-- 选择 --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });
    });

    $('.site-main').on('click','.update-deal-client-btn',function(event) {
        var form = $('.update-deal-client-form');

        var validator = form.validate({
            rules: {
                name: { required: true },
                party: { required: true },
            },
            messages: {
                name: { required: 'Name is required' },
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            self.clients.forEach(function(item) {
                if (item.id == data.id) {
                    item = {
                        name: form.find('input[name="name"]').val(),
                        party: form.find('select[name="party"]').val(),
                        industries: form.find('select[name="industries"]').val(),
                        areas: form.find('select[name="areas"]').val(),
                    };
                }
            });

            $('.deal-client-list, .update-deal-client-form').toggleClass('hidden');

            self.list_client();
            CORE.notify.info('Update Done');
        }
    });

    $('.site-main').on('click','.remove-deal-client-btn',function(event) {
        if (CONST=='en') {
            if (!confirm('Are you sure of removing this record ?')) return false;
        } else {
            if (!confirm('确定要删除这条记录吗？')) return false;
        }

        var client_id = $(event.currentTarget).parents('tr').data('client-id');
        self.clients = self.clients.filter(function(client) { return client.id != client_id; });

        self.list_client();
        CORE.notify.info('Remove Done');
    });

    $('.site-main').on('click','.add-deal-firm-btn',function(event) {
        var form = $('.add-deal-firm-form');

        var validator = form.validate({
            rules: {
                name: { required: true },
                party: { required: true },
            },
            messages: {
                name: { required: 'Name is required' },
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            self.firms.push({
                id: new Date().getTime(),
                name: form.find('input[name="name"]').val(),
                party: form.find('select[name="party"]').val(),
                areas: form.find('select[name="areas"]').val() || [],
            });

            form[0].reset();
            form.find('select[name="party"],select[name="areas"]').multiselect('refresh');

            self.list_firm();
            CORE.notify.info('Add Done');
        }
    });

    $('.site-main').on('click','.update-deal-firm',function(event) {
        var firm_id = $(event.currentTarget).parents('tr').data('firm-id');
        var firm = null;
        self.firms.forEach(function(item) {
            if (item.id == firm_id) {
                firm = item;
            }
        });

        $('.update-deal-firm-form').html(new EJS({text: ejs.update_deal_firm }).render({
            parties: self.parties,
            areas: self.areas,
            deal: self.deal,
            firm: firm,
        }));
        $('.deal-firm-list, .update-deal-firm-form').toggleClass('hidden');

        $('.update-deal-firm-form').find('select[name="party"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });

        $('.update-deal-firm-form').find('select[name="areas"]').multiselect({
            maxHeight: 300,
            numberDisplayed: 100,
            nonSelectedText: CONST.lang=='en' ? '-- Choose --':'-- 选择 --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });
    });

    $('.site-main').on('click','.update-deal-firm-btn',function(event) {
        var form = $('.update-deal-firm-form');

        var validator = form.validate({
            rules: {
                name: { required: true },
                party: { required: true },
            },
            messages: {
                name: { required: 'Name is required' },
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            self.firms.forEach(function(item) {
                if (item.id == data.id) {
                    item = {
                        name: form.find('input[name="name"]').val(),
                        party: form.find('select[name="party"]').val(),
                        areas: form.find('select[name="areas"]').val(),
                    };
                }
            });

            $('.deal-firm-list, .update-deal-firm-form').toggleClass('hidden');

            self.list_firm();
            CORE.notify.info('Update Done');
        }
    });

    $('.site-main').on('click','.remove-deal-firm-btn',function(event) {
        if (CONST=='en') {
            if (!confirm('Are you sure of removing this record ?')) return false;
        } else {
            if (!confirm('确定要删除这条记录吗？')) return false;
        }

        var firm_id = $(event.currentTarget).parents('tr').data('firm-id');
        self.firms.forEach(function(firm) { return firm.id != firm_id; });

        self.list_firm();
        CORE.notify.info('Remove Done');
    });

    $('.site-main').on('click','.add-deal-lawyer-btn',function(event) {
        var form = $('.add-deal-lawyer-form');

        var validator = form.validate({
            rules: {
                name: { required: true },
                firm: { required: true },
            },
            messages: {
                name: { required: 'Name is required' },
                firm: { required: 'Firm is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            self.lawyers.push({
                id: new Date().getTime(),
                name: form.find('input[name="name"]').val(),
                firm: form.find('select[name="firm"]').val(),
                role: form.find('select[name="role"]').val(),
            });

            form[0].reset();

            self.list_lawyer();
            CORE.notify.info('Add Done');
        }
    });

    $('.site-main').on('click','.update-deal-lawyer',function(event) {
        var lawyer_id = $(event.currentTarget).parents('tr').data('lawyer-id');
        var lawyer = null;
        self.lawyers.forEach(function(item) {
            if (item.id == lawyer_id) {
                lawyer = item;
            }
        });

        $('.update-deal-lawyer-form').html(new EJS({ text: ejs.update_deal_lawyer }).render({
            roles: self.roles,
            deal: self.deal,
            firms: self.firms,
            lawyer: lawyer,
        }));
        $('.deal-lawyer-list, .update-deal-lawyer-form').toggleClass('hidden');
    });

    $('.site-main').on('click','.update-deal-lawyer-btn',function(event) {
        var form = $('.update-deal-lawyer-form');

        var validator = form.validate({
            rules: {
                name: { required: true },
                firm: { required: true },
            },
            messages: {
                name: { required: 'Name is required' },
                firm: { required: 'Firm is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            self.lawyers.forEach(function(item) {
                if (item.id == data.id) {
                    item = {
                        name: form.find('input[name="name"]').val(),
                        firm: form.find('select[name="firm"]').val(),
                        role: form.find('select[name="role"]').val(),
                    };
                }
            });

            $('.deal-lawyer-list, .update-deal-lawyer-form').toggleClass('hidden');

            self.list_lawyer();
            CORE.notify.info('Update Done');
        }
    });

    $('.site-main').on('click','.remove-deal-lawyer-btn',function(event) {
        if (CONST=='en') {
            if (!confirm('Are you sure of removing this record ?')) return false;
        } else {
            if (!confirm('确定要删除这条记录吗？')) return false;
        }

        var lawyer_id = $(event.currentTarget).parents('tr').data('lawyer-id');
        self.lawyers = self.lawyers.filter(function(lawyer) { return lawyer.id != lawyer_id; });

        self.list_lawyer();
        CORE.notify.info('Remove Done');
    });

    $('.site-main').on('click','.deal-summary-btn',function(event) {
        var summary = self.get_summary();

        $('#deal_summary').html(new EJS({ text: ejs.deal_summary }).render({
            categories: self.categories,
            industries: self.industries,
            areas: self.areas,
            parties: self.parties,
            roles: self.roles,
            deal: self.deal,
            summary: summary,
        }));
    });

    return function(ctx,next) {
        self.load_config(function() {
            $('.site-main').html(new EJS({ text: ejs.main }).render({
                categories: self.categories,
                industries: self.industries,
                areas: self.areas,
                parties: self.parties,
                roles: self.roles,
            }));

            self.render_components();
            self.list_client();
            self.list_firm();
            self.list_lawyer();
        });
    };
});

