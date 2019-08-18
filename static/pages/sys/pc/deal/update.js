
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/deal/ejs/update.html',
    'text!pages/sys/pc/deal/ejs/relation.html',
    'text!pages/sys/pc/deal/ejs/summary.html',

    'text!pages/sys/pc/deal/ejs/deal_client_list.html',
    'text!pages/sys/pc/deal/ejs/deal_firm_list.html',
    'text!pages/sys/pc/deal/ejs/deal_lawyer_list.html',
    'text!pages/sys/pc/deal/ejs/update_deal_client.html',
    'text!pages/sys/pc/deal/ejs/update_deal_firm.html',
    'text!pages/sys/pc/deal/ejs/update_deal_lawyer.html',
    'text!pages/sys/pc/deal/ejs/pick_client_list.html',
    'text!pages/sys/pc/deal/ejs/pick_firm_list.html',
    'text!pages/sys/pc/deal/ejs/pick_lawyer_list.html',

    'bootstrap-multiselect', 'bootstrap-rating', 'bootstrap-datetimepicker',
    'ueditor','ueditor-lang',
    ], function(ejs_loading, ejs_pagination, ejs_update, ejs_relation, ejs_summary,
        ejs_deal_client_list, ejs_deal_firm_list, ejs_deal_lawyer_list,
        ejs_update_deal_client, ejs_update_deal_firm, ejs_update_deal_lawyer,
        ejs_pick_client_list, ejs_pick_firm_list, ejs_pick_lawyer_list) {

    var self = this;
    self.search = {
        client: { keyword: '', page: { no: 1, size: 10 } },
        firm: { keyword: '', page: { no: 1, size: 10 } },
        lawyer: { keyword: '', page: { no: 1, size: 10 } },
    };

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        update: ejs_update,
        relation: ejs_relation,
        summary: ejs_summary,
        deal_client_list: ejs_deal_client_list,
        deal_firm_list: ejs_deal_firm_list,
        deal_lawyer_list: ejs_deal_lawyer_list,
        update_deal_client: ejs_update_deal_client,
        update_deal_firm: ejs_update_deal_firm,
        update_deal_lawyer: ejs_update_deal_lawyer,
        pick_client_list: ejs_pick_client_list,
        pick_firm_list: ejs_pick_firm_list,
        pick_lawyer_list: ejs_pick_lawyer_list,
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

    self.render_profile_components = function() {
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
            initialDate: self.deal.date ? new Date(self.deal.date):'',
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
        }).addListener('ready', function() {
            this.setContent(self.deal.note);
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
            this.setContent(self.deal.note_cn);
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
            this.setContent(self.deal.raw);
        });
    };

    self.render_relation_components = function() {
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
            nonSelectedText: '-- Choose --',
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
            nonSelectedText: '-- Choose --',
            delimiterText: '　|　',
            enableFiltering: true,
            allSelectedText: false,
            buttonContainer: '<div></div>',
            buttonClass: '',
            templates: multiselect_templates,
        });
    };

    //////////////////////////////////////////////////////////////////////////////////////////////////////////

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

    $('.site-main').on('click','.update-deal-btn',function(event) {
        $('input[name="note"]').val(UE.getEditor('note_editor').getContent());
        $('input[name="note_cn"]').val(UE.getEditor('note_cn_editor').getContent());
        $('input[name="raw"]').val(UE.getEditor('raw_editor').getContent());

        var form = $('.update-deal-form');

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

            $('.update-deal-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id + '/update',
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
                    date: date || 0,

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
                },
                fail: function(result) {
                    CORE.notify.error(result.msg);
                },
                error: function(xhr) {
                    CORE.notify.error(xhr.responseText);
                },
                complete: function(xhr) {
                    $('.create-deal-btn').button('reset');
                }
            });
        }
    });

    //////////////////////////////////////////////////////////////////////////////////////////////////////////

    $('.site-main').on('click','.add-deal-client-btn',function(event) {
        var form = $('.add-deal-client-form');

        var validator = form.validate({
            rules: {
                client: { required: true },
                party: { required: true },
            },
            messages: {
                client: { required: 'Client is required' },
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.add-deal-client-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id +'/client/add',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    client: form.find('input[name="client"]').val(),
                    party: form.find('select[name="party"]').val() || 0,
                    major: form.find('select[name="major"]').val() || 0,
                    industries: form.find('select[name="industries"]').val() || [],
                    areas: form.find('select[name="areas"]').val() || [],
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    form[0].reset();
                    form.find('select[name="party"]').multiselect('refresh');
                    form.find('select[name="industries"]').multiselect('refresh');
                    form.find('select[name="areas"]').multiselect('refresh');
                    self.list_client();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.add-deal-client-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.update-deal-client',function(event) {
        var client_id = $(event.currentTarget).parents('tr').data('client-id');
        var client = null;
        for (var i=0;i<self.clients.length;i++) {
            if (self.clients[i].id == client_id) {
                client = self.clients[i];
                break;
            }
        }

        $('.update-deal-client-form').html(new EJS({ text: ejs.update_deal_client }).render({
            parties: self.parties,
            industries: self.industries,
            areas: self.areas,
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
            nonSelectedText: '-- Choose --',
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
            nonSelectedText: '-- Choose --',
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
                party: { required: true },
            },
            messages: {
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.update-deal-client-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id + '/client/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    client: form.find('input[name="client"]').val(),
                    party: form.find('select[name="party"]').val() || 0,
                    major: form.find('select[name="major"]').val() || 0,
                    industries: form.find('select[name="industries"]').val() || [],
                    areas: form.find('select[name="areas"]').val() || [],
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    $('.deal-client-list, .update-deal-client-form').toggleClass('hidden');
                    self.list_client();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-deal-client-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.remove-deal-client-btn',function(event) {
        if (!confirm('Are you sure of removing this record ?')) return false;

        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/client/remove',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                client: $(event.currentTarget).parents('.deal-client-item').data('client-id'),
            },
            success: function(result) {
                self.list_client();
                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('click','.add-deal-firm-btn',function(event) {
        var form = $('.add-deal-firm-form');

        var validator = form.validate({
            rules: {
                firm: { required: true },
                party: { required: true },
            },
            messages: {
                firm: { required: 'Firm is required' },
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.add-deal-firm-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id +'/firm/add',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    firm: form.find('input[name="firm"]').val(),
                    party: form.find('select[name="party"]').val() || 0,
                    areas: form.find('select[name="areas"]').val() || [],
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    form[0].reset();
                    form.find('select[name="party"]').multiselect('refresh');
                    form.find('select[name="areas"]').multiselect('refresh');
                    self.list_firm();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.add-deal-firm-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.update-deal-firm',function(event) {
        var firm_id = $(event.currentTarget).parents('tr').data('firm-id');
        var firm = null;
        for (var i=0;i<self.firms.length;i++) {
            if (self.firms[i].id == firm_id) {
                firm = self.firms[i];
                break;
            }
        }

        $('.update-deal-firm-form').html(new EJS({ text: ejs.update_deal_firm }).render({
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
            nonSelectedText: '-- Choose --',
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
                party: { required: true },
            },
            messages: {
                party: { required: 'Party is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.update-deal-firm-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id + '/firm/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    firm: form.find('input[name="firm"]').val(),
                    party: form.find('select[name="party"]').val() || 0,
                    areas: form.find('select[name="areas"]').val() || [],
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    $('.deal-firm-list, .update-deal-firm-form').toggleClass('hidden');
                    self.list_firm();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-deal-firm-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.remove-deal-firm-btn',function(event) {
        if (!confirm('Are you sure of removing this record ?')) return false;

        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/firm/remove',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                firm: $(event.currentTarget).parents('.deal-firm-item').data('firm-id'),
            },
            success: function(result) {
                self.list_firm();
                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('click','.add-deal-lawyer-btn',function(event) {
        var form = $('.add-deal-lawyer-form');

        var validator = form.validate({
            rules: {
                lawyer: { required: true },
                firm: { required: true },
            },
            messages: {
                lawyer: { required: 'Lawyer is required' },
                firm: { required: 'Firm is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.add-deal-lawyer-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id +'/lawyer/add',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    lawyer: form.find('input[name="lawyer"]').val(),
                    firm: form.find('select[name="firm"]').val(),
                    role: form.find('select[name="role"]').val() || 0,
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    form[0].reset();
                    self.list_lawyer();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.add-deal-lawyer-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.update-deal-lawyer',function(event) {
        var lawyer_id = $(event.currentTarget).parents('tr').data('lawyer-id');
        var lawyer = null;
        for (var i=0;i<self.lawyers.length;i++) {
            if (self.lawyers[i].id == lawyer_id) {
                lawyer = self.lawyers[i];
                break;
            }
        }

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
                firm: { required: true },
            },
            messages: {
                firm: { required: 'Firm is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            $('.update-deal-lawyer-btn').button('loading');
            CORE.ajax.post({
                url: '/law/deal/' + self.deal.id + '/lawyer/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    lawyer: form.find('input[name="lawyer"]').val(),
                    firm: form.find('select[name="firm"]').val(),
                    role: form.find('select[name="role"]').val() || 0,
                    remark: form.find('textarea[name="remark"]').val(),
                },
                success: function(result) {
                    $('.deal-lawyer-list, .update-deal-lawyer-form').toggleClass('hidden');
                    self.list_lawyer();
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-deal-lawyer-btn').button('reset');
                }
            });
        }
    });

    $('.site-main').on('click','.remove-deal-lawyer-btn',function(event) {
        if (!confirm('Are you sure of removing this record ?')) return false;

        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/lawyer/remove',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                lawyer: $(event.currentTarget).parents('.deal-lawyer-item').data('lawyer-id'),
            },
            success: function(result) {
                self.list_lawyer();
                CORE.notify.info(result.msg);
            }
        });
    });

    $('.site-main').on('keyup','#pick_client_modal input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-client-btn').click();
        }
    });

    $('.site-main').on('click','.search-client-btn',function(event) {
        self.search.client.keyword = $('#pick_client_modal input[name="keyword"]').val();
        self.search.client.page = { no: 1, size: 10 };
        self.search_client();
    });

    $('.site-main').on('click','.client-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.client-pager');
        self.search.client.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_client();
    });

    $('.site-main').on('click','.pick-client-btn',function(event) {
        var item = $(event.currentTarget);
        $('input[name="client"]').val(item.find('.client-id').val());
        $('.deal-client').val(item.find('.client-name').val());
        $('#pick_client_modal').modal('hide');
    });

    $('.site-main').on('keyup','#pick_firm_modal input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-firm-btn').click();
        }
    });

    $('.site-main').on('click','.search-firm-btn',function(event) {
        self.search.firm.keyword = $('#pick_firm_modal input[name="keyword"]').val();
        self.search.firm.page = { no: 1, size: 10 };
        self.search_firm();
    });

    $('.site-main').on('click','.firm-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.firm-pager');
        self.search.firm.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_firm();
    });

    $('.site-main').on('click','.pick-firm-btn',function(event) {
        var item = $(event.currentTarget);
        $('input[name="firm"]').val(item.find('.firm-id').val());
        $('.deal-firm').val(item.find('.firm-name').val());
        $('#pick_firm_modal').modal('hide');
    });

    $('.site-main').on('keyup','#pick_lawyer_modal input[name="keyword"]',function(event) {
        if (event.keyCode==13) {
            $('.search-lawyer-btn').click();
        }
    });

    $('.site-main').on('click','.search-lawyer-btn',function(event) {
        self.search.lawyer.keyword = $('#pick_lawyer_modal input[name="keyword"]').val();
        self.search.lawyer.page = { no: 1, size: 10 };
        self.search_lawyer();
    });

    $('.site-main').on('click','.lawyer-pager-btn',function(event) {
        var pager = $(event.currentTarget).parents('.lawyer-pager');
        self.search.firm.page = {
            no: parseInt(pager.data('page-no')),
            size: parseInt(pager.data('page-size')),
        };
        self.search_lawyer();
    });

    $('.site-main').on('click','.pick-lawyer-btn',function(event) {
        var item = $(event.currentTarget);
        $('input[name="lawyer"]').val(item.find('.lawyer-id').val());
        $('.deal-lawyer').val(item.find('.lawyer-name').val());
        $('#pick_lawyer_modal').modal('hide');
    });

    $('.site-main').on('click','.deal-summary-btn',function(event) {
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
                if (lawyer.firm.id==firm.id) {
                    firm.lawyers.push(lawyer);
                }
            });

            if (!!summary[firm.party]) {
                summary[firm.party].firms.push(firm);
            } else {
                summary[firm.party] = { clients: [], firms: [firm] };
            }
        });

        $('#deal_summary').html(new EJS({ text: ejs.summary }).render({
            categories: self.categories,
            industries: self.industries,
            areas: self.areas,
            parties: self.parties,
            roles: self.roles,
            deal: self.deal,
            summary: summary,
        }));
    });

    self.list_client = function() {
        $('.deal-client-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/client/list',
            success: function(result) {
                self.clients = result.data.clients;
                $('.deal-client-list').html(new EJS({ text: ejs.deal_client_list }).render({
                    parties: self.parties,
                    industries: self.industries,
                    areas: self.areas,
                    clients: self.clients,
                }));

                $('.deal-summary-tab').data('client','Y');
                if ($('.deal-summary-tab').data('client') && $('.deal-summary-tab').data('firm') && $('.deal-summary-tab').data('lawyer')) {
                    $('.deal-summary-tab').removeClass('hidden');
                }
            }
        });
    };

    self.list_firm = function() {
        var ejs_html = new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' });
        $('.deal-firm-list').html(ejs_html);

        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/firm/list',
            success: function(result) {
                self.firms = result.data.firms;
                $('.deal-firm-list').html(new EJS({ text: ejs_deal_firm_list }).render({
                    parties: self.parties,
                    areas: self.areas,
                    firms: self.firms,
                }));

                $('select[name="firm"]').html('<option value="">-- Choose --</option>');

                var firm_ids = [];
                self.firms.forEach(function(firm) {
                    if (firm_ids.indexOf(firm.id) == -1) {
                        firm_ids.push(firm.id);

                        var option = $('<option></option>');
                        option.attr('value',firm.id);
                        option.html(firm.name || firm.name_cn);
                        $('select[name="firm"]').append(option);
                    }
                });

                $('.deal-summary-tab').data('firm','Y');
                if ($('.deal-summary-tab').data('client') && $('.deal-summary-tab').data('firm') && $('.deal-summary-tab').data('lawyer')) {
                    $('.deal-summary-tab').removeClass('hidden');
                }
            }
        });
    };

    self.list_lawyer = function() {
        $('.deal-lawyer-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/lawyer/list',
            success: function(result) {
                self.lawyers = result.data.lawyers;
                $('.deal-lawyer-list').html(new EJS({ text: ejs.deal_lawyer_list }).render({
                    roles: self.roles,
                    lawyers: self.lawyers,
                }));

                $('.deal-summary-tab').data('lawyer','Y');
                if ($('.deal-summary-tab').data('client') && $('.deal-summary-tab').data('firm') && $('.deal-summary-tab').data('lawyer')) {
                    $('.deal-summary-tab').removeClass('hidden');
                }
            }
        });
    };

    self.search_client = function() {
        $('.client-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/client/filter',
                data: {
                    keyword: self.search.client.keyword,
                    page: self.search.client.page,
                },
                success: function(result) {
                    $('.client-list').html(new EJS({ text: ejs.pick_client_list }).render({ clients: result.data.clients }));

                    $('.client-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.search.client.page.no,
                        size: self.search.client.page.size,
                        total: result.data.total,
                        item: 'client-pager',
                        btn: 'client-pager-btn',
                    }));
                }
            });
        },500);
    };

    self.search_firm = function() {
        $('.firm-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/firm/filter',
                data: {
                    keyword: self.search.firm.keyword,
                    page: self.search.firm.page,
                },
                success: function(result) {
                    $('.firm-list').html(new EJS({ text: ejs.pick_firm_list }).render({ firms: result.data.firms }));

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

    self.search_lawyer = function() {
        $('.lawyer-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/lawyer/filter',
                data: {
                    keyword: self.search.lawyer.keyword,
                    page: self.search.lawyer.page,
                },
                success: function(result) {
                    $('.lawyer-list').html(new EJS({ text: ejs.pick_lawyer_list }).render({ lawyers: result.data.lawyers }));

                    $('.lawyer-pagination').html(new EJS({ text: ejs.pagination }).render({
                        no: self.search.lawyer.page.no,
                        size: self.search.lawyer.page.size,
                        total: result.data.total,
                        item: 'lawyer-pager',
                        btn: 'lawyer-pager-btn',
                    }));
                }
            });
        },500);
    };

    return function(ctx,next) {
        self.load_config(function() {
            CORE.ajax.post({
                url: '/law/deal/' + ctx.params.deal + '/detail',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                success: function(result) {
                    self.deal = result.data.deal;

                    $('.site-main').html(new EJS({ text: ejs.update }).render({
                        categories: self.categories,
                        industries: self.industries,
                        areas: self.areas,
                        parties: self.parties,
                        roles: self.roles,
                        deal: self.deal,
                    }));

                    $('#relation_tab').html(new EJS({ text: ejs.relation }).render({
                        categories: self.categories,
                        industries: self.industries,
                        areas: self.areas,
                        parties: self.parties,
                        roles: self.roles,
                        deal: self.deal,
                    }));

                    self.render_profile_components();
                    self.render_relation_components();

                    self.list_client();
                    self.list_firm();
                    self.list_lawyer();
                }
            });
        });
    };
});



