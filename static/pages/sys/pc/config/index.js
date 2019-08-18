
define([
    'text!common/ejs/loading.html',
    'text!pages/sys/pc/config/ejs/index.html',
    'text!pages/sys/pc/config/ejs/item.html',
    'bootstrap-multiselect', 'bootstrap-datetimepicker',
    ], function(ejs_loading, ejs_index, ejs_item) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        index: ejs_index,
        item: ejs_item,
    };

    var multiselect_templates = {
        button: '<div class="multiselect dropdown-toggle" data-toggle="dropdown"><span class="multiselect-selected-text"></span></div>',
        ul: '<ul class="multiselect-container dropdown-menu" style="min-width:300px;margin:6px 0px 0px -8px;"></ul>',
    };

    self.load_config = function(callback) {
        CORE.ajax.post({
            url: '/law/config/load',
            data: {
                keys: ['categories','industries','areas','parties','roles','formula','homepage'],
            },
            success: function(result) {
                self.categories = result.data.categories;
                self.industries = result.data.industries;
                self.parties = result.data.parties;
                self.roles = result.data.roles;
                self.areas = result.data.areas;
                self.formula = result.data.formula || {};
                self.homepage = result.data.homepage || {};
                callback();
            }
        });
    };

    self.render_components = function() {
        $('.start-date').datetimepicker({
            language:  'zh-CN',
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 2,
            maxView: 4,
            forceParse: 0,
            showMeridian: 1,
            format: 'yyyy-mm-dd',
            linkField: 'start_date',
            linkFormat: 'yyyy-mm-dd',
            initialDate: !!homepage.start_date ? new Date(homepage.start_date) : new Date('2016-01-01T00:00:00+08:00'),
        });

        $('.end-date').datetimepicker({
            language:  'zh-CN',
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 2,
            maxView: 4,
            forceParse: 0,
            showMeridian: 1,
            format: 'yyyy-mm-dd',
            linkField: 'end_date',
            linkFormat: 'yyyy-mm-dd',
            initialDate: !!homepage.end_date ? new Date(homepage.end_date) : new Date('2016-12-31T00:00:00+08:00'),
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

    $('.site-main').on('click','.add-config-btn',function(event) {
        var tr = $(event.currentTarget).parents('.config-item');
        tr.find('.add-config-btn').addClass('hidden');
        tr.find('.remove-config-btn').removeClass('hidden');
        var tbody = tr.parents('tbody');
        var ejs_html = new EJS({ text: ejs.item }).render({ config: { id: tbody.find('tr').length+1 }, saved: 0 });
        tbody.append(ejs_html);
    });

    $('.site-main').on('click','.remove-config-btn',function(event) {
        if ($(event.currentTarget).data('saved')=='1') return false;
        if (!confirm('确定要删除此记录吗？')) return false;
        var tr = $(event.currentTarget).parents('.config-item');
        var tbody = tr.parents('tbody');
        tr.remove();
        var trs = tbody.find('tr');
        for (var i=0;i<trs.length;i++) {
            $(trs[i]).find('.config-id').html(i+1);
        }
    });

    $('.site-main').on('click','.update-category-btn',function(event) {
        var categories = [];
        $('#category').find('tbody > tr').each(function() {
            var item = $(this);
            var category = {
                id: parseInt(item.find('.config-id').html()),
                en: item.find('input[name="en"]').val().trim(),
                cn: item.find('input[name="cn"]').val().trim(),
            };

            if (category.en || category.cn) {
                categories.push(category);
            }
        });

        $('.update-category-btn').button('loading');
        CORE.ajax.post({
            url: '/law/config/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                key: 'categories',
                value: categories,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-category-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.update-industry-btn',function(event) {
        var industries = [];
        $('#industry').find('tbody > tr').each(function() {
            var item = $(this);
            var industry = {
                id: parseInt(item.find('.config-id').html()),
                en: item.find('input[name="en"]').val().trim(),
                cn: item.find('input[name="cn"]').val().trim(),
            };

            if (industry.en || industry.cn) {
                industries.push(industry);
            }
        });

        $('.update-industry-btn').button('loading');
        CORE.ajax.post({
            url: '/law/config/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                key: 'industries',
                value: industries,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-industry-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.update-area-btn',function(event) {
        var areas = [];
        $('#area').find('tbody > tr').each(function() {
            var item = $(this);
            var area = {
                id: parseInt(item.find('.config-id').html()),
                en: item.find('input[name="en"]').val().trim(),
                cn: item.find('input[name="cn"]').val().trim(),
            };

            if (area.en || area.cn) {
                areas.push(area);
            }
        });

        $('.update-area-btn').button('loading');
        CORE.ajax.post({
            url: '/law/config/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                key: 'areas',
                value: areas,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-area-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.update-party-btn',function(event) {
        var parties = [];
        $('#party').find('tbody > tr').each(function() {
            var item = $(this);
            var party = {
                id: parseInt(item.find('.config-id').html()),
                en: item.find('input[name="en"]').val().trim(),
                cn: item.find('input[name="cn"]').val().trim(),
            };

            if (party.en || !party.cn) {
                parties.push(party);
            }
        });

        $('.update-party-btn').button('loading');
        CORE.ajax.post({
            url: '/law/config/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                key: 'parties',
                value: parties,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-party-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.update-role-btn',function(event) {
        var roles = [];
        $('#role').find('tbody > tr').each(function() {
            var item = $(this);
            var role = {
                id: parseInt(item.find('.config-id').html()),
                en: item.find('input[name="en"]').val().trim(),
                cn: item.find('input[name="cn"]').val().trim(),
            };

            if (role.en || role.cn) {
                roles.push(role);
            }
        });

        $('.update-role-btn').button('loading');
        CORE.ajax.post({
            url: '/law/config/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                key: 'roles',
                value: roles,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-role-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.update-formula-btn',function(event) {
        var form = $('.update-formula-form');
        var formula = {
            std_volume: parseFloat(form.find('input[name="std_volume"]').val()),
            std_avg_volume: parseFloat(form.find('input[name="std_avg_volume"]').val()),
            std_score: parseFloat(form.find('input[name="std_score"]').val()),
            std_avg_score: parseFloat(form.find('input[name="std_avg_score"]').val()),
            std_number: parseFloat(form.find('input[name="std_number"]').val()),
        };

        if (formula.std_volume+formula.std_avg_volume+formula.std_score+formula.std_avg_score+formula.std_number != 100) {
            CORE.notify.error('Sum of weights should be 100%');
            return false;
        }

        $('.update-formula-btn').button('loading');
        CORE.ajax.post({
            url: '/law/config/update',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                key: 'formula',
                value: formula,
            },
            success: function(result) {
                CORE.notify.info(result.msg);
            },
            complete: function(xhr) {
                $('.update-formula-btn').button('reset');
            }
        });
    });

    $('.site-main').on('click','.update-homepage-btn',function(event) {
        var form = $('.update-homepage-form');

        var validator = form.validate({
            rules: {
                curve_title: { required: true },
                bar_title: { required: true },
                start_date: { required: true },
                end_date: { required: true },
                categories: { required: true },
                industries: { required: true },
                areas: { required: true },
            },
            messages: {
                curve_title: { required: 'Curve title is required' },
                bar_title: { required: 'Bar title is required' },
                start_date: { required: 'Start date is required' },
                end_date: { required: 'End date is required' },
                categories: { required: 'Categories is required' },
                industries: { required: 'Industries is required' },
                areas: { required: 'Areas is required' },
            },
            errorPlacement: function(error, element) {
                CORE.notify.error(error.text());
            },
        });

        validator.form();
        if (validator.valid()) {
            var categories = form.find('select[name="categories"]').val();
            var industries = form.find('select[name="industries"]').val();
            var areas = form.find('select[name="areas"]').val();

            $('.update-homepage-btn').button('loading');
            CORE.ajax.post({
                url: '/law/config/update',
                headers: {
                    'x-admin-id': CORE.admin.id,
                    'x-admin-token': CORE.admin.token,
                },
                data: {
                    key: 'homepage',
                    value: {
                        curve_title: form.find('input[name="curve_title"]').val(),
                        bar_title: form.find('input[name="bar_title"]').val(),
                        start_date: new Date(form.find('input[name="start_date"]').val()+'T00:00:00+08:00').getTime(),
                        end_date: new Date(form.find('input[name="start_date"]').val()+'T00:00:00+08:00').getTime(),
                        categories: categories.reduce(function(list,item) { list.push(parseInt(item)); return list; },[]),
                        industries: industries.reduce(function(list,item) { list.push(parseInt(item)); return list; },[]),
                        areas: areas.reduce(function(list,item) { list.push(parseInt(item)); return list; },[]),
                    },
                },
                success: function(result) {
                    CORE.notify.info(result.msg);
                },
                complete: function(xhr) {
                    $('.update-homepage-btn').button('reset');
                }
            });
        }
    });

    return function(ctx,next) {
        self.load_config(function() {
            $('.site-main').html(new EJS({ text: ejs.index }).render({
                categories: self.categories,
                industries: self.industries,
                areas: self.areas,
                parties: self.parties,
                roles: self.roles,
                formula: self.formula,
                homepage: self.homepage,
                ejs: ejs,
            }));

            self.render_components();
        });
    };
});



