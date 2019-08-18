
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/chart/ejs/m1.html',
    'text!pages/sys/pc/chart/ejs/empty_data.html',
    'text!pages/sys/pc/chart/ejs/filter_deals.html',
    'text!pages/sys/pc/chart/ejs/ranking_deals.html',
    'text!pages/sys/pc/chart/ejs/ranking_firms.html',
    'text!pages/sys/pc/chart/ejs/ranking_lawyers.html',
    'bootstrap-multiselect', 'bootstrap-datetimepicker',
    ], function(ejs_loading, ejs_pagination, ejs_m1, ejs_empty_data, ejs_filter_deals, ejs_ranking_deals, ejs_ranking_firms, ejs_ranking_lawyers) {

    var self = this;

    self.palette = [];
    for (var i=0;i<256;i++) {
        var r = parseInt(Math.random()*255);
        var g = parseInt(Math.random()*255);
        var b = parseInt(Math.random()*255);
        self.palette.push([r,g,b]);
    }

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        m1: ejs_m1,
        empty_data: ejs_empty_data,
        filter_deals: ejs_filter_deals,
        ranking_deals: ejs_ranking_deals,
        ranking_firms: ejs_ranking_firms,
        ranking_lawyers: ejs_ranking_lawyers,
    };

    var multiselect_templates = {
        button: '<div class="multiselect dropdown-toggle" data-toggle="dropdown"><span class="multiselect-selected-text"></span></div>',
        ul: '<ul class="multiselect-container dropdown-menu" style="min-width:300px;margin:6px 0px 0px -8px;"></ul>',
    };

    self.load_config = function(callback) {
        CORE.ajax.post({
            url: '/law/config/load',
            success: function(result) {
                self.categories = result.data.categories.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                self.industries = result.data.industries.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                self.areas = result.data.areas.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                callback();
            }
        });
    };

    self.render_components = function() {
        $('.chart-start-time').datetimepicker({
            language:  'zh-CN',
            autoclose: 1,
            todayHighlight: 1,
            startView: 4,
            minView: 3,
            maxView: 4,
            forceParse: 0,
            showMeridian: 1,
            format: 'mm / yyyy',
            linkField: 'chart_start_time',
            linkFormat: 'yyyy-mm',
            initialDate: new Date('2016-01-01T00:00:00+08:00'),
        });

        $('.chart-end-time').datetimepicker({
            language:  'zh-CN',
            autoclose: 1,
            todayHighlight: 1,
            startView: 4,
            minView: 3,
            maxView: 4,
            forceParse: 0,
            showMeridian: 1,
            format: 'mm / yyyy',
            linkField: 'chart_end_time',
            linkFormat: 'yyyy-mm',
            initialDate: new Date('2016-12-01T00:00:00+08:00'),
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

    $('.site-main').on('click','.render-chart-btn',function(event) {
        if (!$('input[name="start"]').val() || !$('input[name="end"]').val()) {
            CORE.notify.error('请选择起止时间');
            return false;
        }

        self.start = new Date($('input[name="start"]').val()+'-01T00:00+08:00').getTime();
        self.end = new Date($('input[name="end"]').val()+'-01T00:00+08:00').getTime();

        $('.render-chart-btn').button('loading');

        var ejs_html = new EJS({ text: ejs.loading }).render({ padding: '50px', font: '50px' });
        $('.month-count-line').html(ejs_html);
        $('.month-volume-bar').html(ejs_html);
        $('.level-count-pie').html(ejs_html);
        $('.category-count-bar').html(ejs_html);
        $('.category-volume-bar').html(ejs_html);
        $('.industry-count-bar').html(ejs_html);
        $('.industry-volume-bar').html(ejs_html);
        $('.area-count-bar').html(ejs_html);
        $('.area-volume-bar').html(ejs_html);

        $('select.month-filter').val(1);

        CORE.ajax.post({
            url: '/law/stats/m1',
            data: {
                start: self.start,
                end: self.end,
                categories: $('select[name="categories"]').val() || [],
                industries: $('select[name="industries"]').val() || [],
                areas: $('select[name="areas"]').val() || [],
            },
            success: function(result) {
                self.deals = result.data.deals;
                self.firms = result.data.firms;
                self.lawyers = result.data.lawyers;

                $('.ranking-deal-list').html(new EJS({ text: ejs.ranking_deals }).render({ deals: self.deals }));
                $('.ranking-firm-list').html(new EJS({ text: ejs.ranking_firms }).render({ deals: self.firms }));
                $('.ranking-lawyer-list').html(new EJS({ text: ejs.ranking_lawyers }).render({ deals: self.lawyers }));
            },
            complete: function(result) {
                $('.render-chart-btn').button('reset');
            },
        });
    });

    $('.site-main').on('click','.list-firm-deal-btn',function(event) {
        var btn = $(event.currentTarget);
        var review = parseInt(btn.data('review'));
        var firm_id = btn.parents('tr').data('firm-id');

        $('.firm-deal-list').html(new EJS({ text: ejs.loading }).render({ padding: '50px', font: '30px' }));
        $('#firm_deal_modal').modal('show');

        var firm = self.firms.filter(function(firm) { return firm.id == firm_id; }).pop();
        var deals = [];
        if (firm) {
            if (review==0) {
                deals = firm.deals.filter(function(deal) { return dael.value == 0; });
            } else {
                deals = firm.deals.filter(function(deal) { return deal.review == review; });
            }
        }

        $('.firm-deal-list').html(new EJS({ text: ejs.filter_deals }).render({ deals: deals }));
    });

    $('.site-main').on('click','.list-lawyer-deal-btn',function(event) {
        var btn = $(event.currentTarget);
        var review = parseInt(btn.data('review'));
        var lawyer_id = btn.parents('tr').data('lawyer-id');

        var ejs_html = new EJS({ text: ejs.loading }).render({ padding: '50px', font: '30px' });
        $('.lawyer-deal-list').html(ejs_html);
        $('#lawyer_deal_modal').modal('show');

        var lawyer = self.lawyers.filter(function(lawyer) { return lawyer.id == lawyer_id; }).pop();
        var deals = [];
        if (lawyer) {
            if (review==0) {
                deals = lawyer.deals.filter(function(deal) { return dael.value == 0; });
            } else {
                deals = lawyer.deals.filter(function(deal) { return deal.review == review; });
            }
        }

        $('.lawyer-deal-list').html(new EJS({ text: ejs.filter_deals }).render({ deals: deals }));
    });

    return function(ctx,next) {
        self.load_config(function() {
            $('.site-main').html(new EJS({ text: ejs.m1 }).render({
                categories: self.categories,
                industries: self.industries,
                areas: self.areas,
                ejs: ejs,
            }));
            self.render_components();
        });
    };
});



