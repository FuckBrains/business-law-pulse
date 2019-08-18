
define([
    'text!common/ejs/loading.html',
    'text!common/ejs/pagination.html',
    'text!pages/sys/pc/chart/ejs/m2.html',
    'text!pages/sys/pc/chart/ejs/empty_data.html',
    'text!pages/sys/pc/chart/ejs/firm_children.html',
    'text!pages/sys/pc/firm/ejs/pick_list.html',
    'chart','bootstrap-multiselect','bootstrap-datetimepicker',
    ], function(ejs_loading, ejs_pagination, ejs_m2, ejs_empty_data, ejs_firm_children, ejs_pick_list, Chart) {

    var self = this;

    self.palette = [];
    for (var i=0;i<256;i++) {
        var r = parseInt(Math.random()*255);
        var g = parseInt(Math.random()*255);
        var b = parseInt(Math.random()*255);
        self.palette.push([r,g,b]);
    }

    self.levels = {
        1: { en: ' < 1 Million USD', cn: '小于百万美元级别' },
        2: { en: ' 1 Million USD', cn: '百万美元级别' },
        3: { en: ' 10 Million USD', cn: '千万美元级别' },
        4: { en: ' 100 Million USD', cn: '亿美元级别'} ,
        5: { en: ' 1 Billion USD', cn: '十亿美元级别' },
        6: { en: ' 10 Billion USD', cn: '百亿美元级别' },
        7: { en: ' 100 Billion USD', cn: '千亿美元级别' },
    };

    var ejs = {
        loading: ejs_loading,
        pagination: ejs_pagination,
        m2: ejs_m2,
        empty_data: ejs_empty_data,
        firm_children: ejs_firm_children,
        pick_list: ejs_pick_list,
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
        $('input[name="firm"]').val(item.find('.firm-id').val());
        $('.firm').val(item.find('.firm-name').val());
        $('#pick_firm_modal').modal('hide');

        CORE.ajax.post({
            url: '/law/firm/' + item.find('.firm-id').val() + '/children',
            success: function(result) {
                var firms = result.data.firms;
                firms.splice(0,0,{ id: item.find('.firm-id').val(), name: item.find('.firm-name').val() });

                var ejs_html = new EJS({ text: ejs.firm_children }).render({ firms: firms });
                $('.firm-children').html(ejs_html);
            }
        });
    });

    $('.site-main').on('click','.render-chart-btn',function(event) {
        var firms = [];
        $('input[name="firm"]').each(function() {
            var firm = $(this);
            if (firm.is(':checked')) {
                firms.push({ id: firm.val() });
            }
        });

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
            url: '/law/stats/m2',
            data: {
                start: self.start,
                end: self.end,
                categories: $('select[name="categories"]').val() || [],
                industries: $('select[name="industries"]').val() || [],
                areas: $('select[name="areas"]').val() || [],
                firms: firms,
            },
            success: function(result) {
                self.stats = result.data;
                console.log(self.stats);
                self.render_month_chart(self.stats.months);
                self.render_level_chart(self.stats.levels);
                self.render_category_chart(self.stats.categories);
                self.render_industry_chart(self.stats.industries);
                self.render_area_chart(self.stats.areas);
            },
            complete: function(result) {
                $('.render-chart-btn').button('reset');
            },
        });
    });

    $('.site-main').on('change','select.month-filter',function(event) {
        if (!self.stats) return false;

        self.stats.months.sort(function(x,y) { return parseInt(x.dimension) > parseInt(y.dimension) ? 1:-1; });

        var step = parseInt($(event.currentTarget).val());

        var months = [];
        for (var i=0;i<self.stats.months.length;i=i+step) {
            var month = {
                dimension: self.stats.months[i].dimension,
                deals: [],
            }
            for (var j=i;j<Math.min(i+step,self.stats.months.length);j++) {
                month.deals = month.deals.concat(self.stats.months[j].deals);
            }

            if (step>1) {
                month.dimension += '-' + self.stats.months[Math.min(i+step,self.stats.months.length)-1].dimension;
            }

            months.push(month);
        }

        self.render_month_chart(months);
    });

    self.search_firm = function() {
        $('.firm-list').html(new EJS({ text: ejs.loading }).render({ padding: '150px', font: '30px' }));

        setTimeout(function() {
            CORE.ajax.post({
                url: '/law/firm/filter',
                data: {
                    page: self.page,
                    keyword: self.keyword,
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

    self.render_month_chart = function(months) {
        months.sort(function(x,y) { return parseInt(x.dimension) > parseInt(y.dimension) ? 1:-1; });

        var labels = [], data = [];
        months.forEach(function(month) {
            labels.push(month.dimension);
            data.push(month.deals.length);
        });

        if (data.reduce(function(sum,item) { return sum+item; },0)==0) {
            var ejs_html = new EJS({ text: ejs.empty_data }).render({});
            $('.month-count-line').html(ejs_html);
        } else {
            var canvas = $('<canvas></canvas>');
            $('.month-count-line').html(canvas);
            new Chart(canvas[0], {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '交易量',
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 3,
                        fill: true,
                    }]
                },
                options: {
                    legend: {
                        display: false,
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    return value == parseInt(value) ? value.toString() : '';
                                }
                            }
                        }]
                    }
                },
            });
        }

        var labels = [], data = [];
        months.forEach(function(month) {
            labels.push(month.dimension);
            data.push(month.deals.reduce(function(volume,deal) { return volume+deal.value; },0));
        });

        if (data.reduce(function(sum,item) { return sum+item; },0)==0) {
            $('.month-volume-bar').html(new EJS({ text: ejs.empty_data }).render({}));
        } else {
            var canvas = $('<canvas></canvas>');
            $('.month-volume-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '交易总金额',
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderWidth: 1,
                    }]
                },
                options: {
                    legend: {
                        display: false,
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    var division = 1000000;
                                    var text = ' Million';
                                    if (parseInt(values[0]/1000000000) > 0) {
                                        division = 1000000000;
                                        text = ' Billion';
                                    }
                                    var tick = parseInt(value/division);
                                    return tick.toString() + (tick == 0 ? '':text);
                                }
                            }
                        }]
                    },
                }
            });
        }
    };

    self.render_level_chart = function(levels) {
        self.palette.sort(function(x,y) { return Math.random()>0.5 ? -1 : 1; });
        var palette = {};
        levels.forEach(function(level,index) {
            palette[level.dimension] = self.palette[index];
        });

        var labels = [], colors = [], data = [];
        levels.sort(function(x,y) { return parseInt(x.dimension) > parseInt(y.dimension) ? 1:-1; });
        levels.forEach(function(level) {
            var label = self.levels[level.dimension];
            labels.push(label.en || labek.cn);
            colors.push(palette[level.dimension]);
            data.push(level.deals.length);
        });

        if (data.reduce(function(sum,item) { return sum+item; },0)==0) {
            var ejs_html = new EJS({ text: ejs.empty_data }).render({});
            $('.level-count-pie').html(ejs_html);
        } else {
            var canvas = $('<canvas></canvas>');
            $('.level-count-pie').html(canvas);
            new Chart(canvas[0], {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors.map(function(color) {
                            return 'rgba(' + color.map(function(i) { return i.toString(); }).join(',') + ',0.3)';
                        }),
                    }]
                },
                options: {
                    cutoutPercentage: 30,
                    legend: {
                        position: 'left',
                    },
                }
            });
        }
    };

    self.render_category_chart = function(categories) {
        self.palette.sort(function(x,y) { return Math.random()>0.5 ? -1 : 1; });
        var palette = {};
        categories.forEach(function(category,index) {
            palette[category.dimension] = self.palette[index];
        });

        categories.forEach(function(category) {
            category.count = category.deals.length;
            category.volume = category.deals.reduce(function(volume,deal) { return volume+deal.value; }, 0);
        });

        var labels = [], colors = [], datasets = [];
        categories.sort(function(x,y) { return parseInt(x.count) < parseInt(y.count) ? 1:-1; });
        categories.forEach(function(category,index) {
            var label = self.categories[category.dimension];
            labels.push(label.en || label.cn);
            colors.push(palette[category.dimension]);

            datasets.push({
                label: label.en || label.cn,
                data: [category.count],
                borderWidth: 1,
                backgroundColor: 'rgba(' + colors[index].join(',') + ',0.2)',
                borderColor: 'rgba(' + colors[index].join(',') + ',0.4)',
            });
        });

        if (datasets.reduce(function(sum,item) { return sum+item.data[0]; },0)==0) {
            var ejs_html = new EJS({ text: ejs.empty_data }).render({});
            $('.category-count-bar').html(ejs_html);
        } else {
            var canvas = $('<canvas></canvas>');
            $('.category-count-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    datasets: datasets
                },
                options: {
                    legend: {
                        position: 'bottom',
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                            categoryPercentage: 1.0,
                            barPercentage: 0.6,
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    return value == parseInt(value) ? value.toString() : '';
                                }
                            }
                        }]
                    }
                }
            });
        }

        var labels = [], colors = [], datasets = [];
        categories.sort(function(x,y) { return parseInt(x.volume) < parseInt(y.volume) ? 1:-1; });
        categories.forEach(function(category,index) {
            var label = self.categories[category.dimension];
            labels.push(label.en || label.cn);
            colors.push(palette[category.dimension]);

            datasets.push({
                label: label.en || label.cn,
                data: [category.volume],
                borderWidth: 1,
                backgroundColor: 'rgba(' + colors[index].join(',') + ',0.2)',
                borderColor: 'rgba(' + colors[index].join(',') + ',0.4)',
            });
        });

        if (datasets.reduce(function(sum,item) { return sum+item.data[0]; },0)==0) {
            $('.category-volume-bar').html(new EJS({ text: ejs.empty_data }).render({}));
        } else {
            var canvas = $('<canvas></canvas>');
            $('.category-volume-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    datasets: datasets
                },
                options: {
                    legend: {
                        position: 'bottom',
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                            ticks: {
                                autoSkip: false,
                            },
                            categoryPercentage: 1.0,
                            barPercentage: 0.6,
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    var division = 1000000;
                                    var text = ' Million';
                                    if (parseInt(values[0]/1000000000) > 0) {
                                        division = 1000000000;
                                        text = ' Billion';
                                    }
                                    var tick = parseInt(value/division);
                                    return tick.toString() + (tick == 0 ? '':text);
                                }
                            }
                        }]
                    }
                }
            });
        }
    };

    self.render_industry_chart = function(industries) {
        self.palette.sort(function(x,y) { return Math.random()>0.5 ? -1 : 1; });
        var palette = {};
        industries.forEach(function(industry,index) {
            palette[industry.dimension] = self.palette[index];
        });

        industries.forEach(function(industry) {
            industry.count = industry.deals.length;
            industry.volume = industry.deals.reduce(function(volume,deal) { return volume+deal.value; }, 0);
        });

        var labels = [], colors = [], datasets = [];
        industries.sort(function(x,y) { return parseInt(x.count) < parseInt(y.count) ? 1:-1; });
        industries.forEach(function(industry,index) {
            var label = self.industries[industry.dimension];
            labels.push(label.en || label.cn);
            colors.push(palette[industry.dimension]);

            datasets.push({
                label: label.en || label.cn,
                data: [industry.count],
                borderWidth: 1,
                backgroundColor: 'rgba(' + colors[index].join(',') + ',0.2)',
                borderColor: 'rgba(' + colors[index].join(',') + ',0.4)',
            });
        });

        if (datasets.reduce(function(sum,item) { return sum+item.data[0]; },0)==0) {
            $('.industry-count-bar').html(new EJS({ text: ejs.empty_data }).render({}));
        } else {
            var canvas = $('<canvas></canvas>');
            $('.industry-count-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    datasets: datasets
                },
                options: {
                    legend: {
                        position: 'bottom',
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                            categoryPercentage: 1.0,
                            barPercentage: 0.6,
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    return value == parseInt(value) ? value.toString() : '';
                                }
                            }
                        }]
                    }
                }
            });
        }

        var labels = [], colors = [], datasets = [];
        industries.sort(function(x,y) { return parseInt(x.volume) < parseInt(y.volume) ? 1:-1; });
        industries.forEach(function(industry,index) {
            var label = self.industries[industry.dimension];
            labels.push(label.en || label.cn);
            colors.push(palette[industry.dimension]);

            datasets.push({
                label: label.en || label.cn,
                data: [industry.volume],
                borderWidth: 1,
                backgroundColor: 'rgba(' + colors[index].join(',') + ',0.2)',
                borderColor: 'rgba(' + colors[index].join(',') + ',0.4)',
            });
        });

        if (datasets.reduce(function(sum,item) { return sum+item.data[0]; },0)==0) {
            $('.industry-volume-bar').html(new EJS({ text: ejs.empty_data }).render({}));
        } else {
            var canvas = $('<canvas></canvas>');
            $('.industry-volume-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    datasets: datasets
                },
                options: {
                    legend: {
                        position: 'bottom',
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                            ticks: {
                                autoSkip: false,
                            },
                            categoryPercentage: 1.0,
                            barPercentage: 0.6,
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    var division = 1000000;
                                    var text = ' Million';
                                    if (parseInt(values[0]/1000000000) > 0) {
                                        division = 1000000000;
                                        text = ' Billion';
                                    }
                                    var tick = parseInt(value/division);
                                    return tick.toString() + (tick == 0 ? '':text);
                                }
                            }
                        }]
                    }
                }
            });
        }
    };

    self.render_area_chart = function(areas) {
        var labels = [], data = [], datasets = [], colors = [];

        self.palette.sort(function(x,y) { return Math.random()>0.5 ? -1 : 1; });
        var palette = {};
        areas.forEach(function(area,index) {
            palette[area.dimension] = self.palette[index];
        });

        areas.forEach(function(area) {
            area.count = area.deals.length;
            area.volume = area.deals.reduce(function(volume,deal) { return volume+deal.value; }, 0);
        });

        var labels = [], colors = [], datasets = [];
        areas.sort(function(x,y) { return parseInt(x.count) < parseInt(y.count) ? 1:-1; });
        areas.forEach(function(area,index) {
            var label = self.areas[area.dimension];
            labels.push(label.en || label.cn);
            colors.push(palette[area.dimension]);

            datasets.push({
                label: label.en || label.cn,
                data: [area.count],
                borderWidth: 1,
                backgroundColor: 'rgba(' + colors[index].join(',') + ',0.2)',
                borderColor: 'rgba(' + colors[index].join(',') + ',0.4)',
            });
        });

        if (datasets.reduce(function(sum,item) { return sum+item.data[0]; },0)==0) {
            $('.area-count-bar').html(new EJS({ text: ejs.empty_data }).render({}));
        } else {
            var canvas = $('<canvas></canvas>');
            $('.area-count-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    datasets: datasets,
                },
                options: {
                    legend: {
                        position: 'bottom',
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                            categoryPercentage: 1.0,
                            barPercentage: 0.6,
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    return value == parseInt(value) ? value.toString() : '';
                                }
                            }
                        }]
                    }
                }
            });
        }

        var labels = [], colors = [], datasets = [];
        areas.sort(function(x,y) { return parseInt(x.volume) < parseInt(y.volume) ? 1:-1; });
        areas.forEach(function(area,index) {
            var label = self.areas[area.dimension];
            labels.push(label.en || label.cn);
            colors.push(palette[area.dimension]);

            datasets.push({
                label: label.en || label.cn,
                data: [area.volume],
                borderWidth: 1,
                backgroundColor: 'rgba(' + colors[index].join(',') + ',0.2)',
                borderColor: 'rgba(' + colors[index].join(',') + ',0.4)',
            });
        });

        if (datasets.reduce(function(sum,value) { return sum+value.data[0]; },0)==0) {
            $('.area-volume-bar').html(new EJS({ text: ejs.empty_data }).render({}));
        } else {
            var canvas = $('<canvas></canvas>');
            $('.area-volume-bar').html(canvas);
            new Chart(canvas[0], {
                type: 'bar',
                data: {
                    datasets: datasets,
                },
                options: {
                    legend: {
                        position: 'bottom',
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false,
                            },
                            ticks: {
                                autoSkip: false,
                            },
                            categoryPercentage: 1.0,
                            barPercentage: 0.6,
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                    var division = 1000000;
                                    var text = ' Million';
                                    if (parseInt(values[0]/1000000000) > 0) {
                                        division = 1000000000;
                                        text = ' Billion';
                                    }
                                    var tick = parseInt(value/division);
                                    return tick.toString() + (tick == 0 ? '':text);
                                }
                            }
                        }]
                    }
                }
            });
        }
    };

    return function(ctx,next) {
        self.load_config(function() {
            $('.site-main').html(new EJS({ text: ejs.m2 }).render({
                categories: self.categories,
                industries: self.industries,
                areas: self.areas,
                ejs: ejs,
            }));

            self.render_components();
        });
    };
});



