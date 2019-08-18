
var main = function() {
    require([
        'text!common/ejs/loading.html',
        'text!pages/www/pc/index/ejs/header.html',
        'text!pages/www/pc/index/ejs/footer.html',
        'text!pages/www/pc/index/ejs/main.html',
        'text!pages/www/pc/index/ejs/empty_data.html',
        'text!pages/www/pc/index/ejs/firms.html',
        'text!pages/www/pc/index/ejs/deals.html',
        'text!pages/www/pc/index/ejs/news.html',
        'text!pages/www/pc/index/ejs/tags.html',
        'text!pages/www/pc/index/ejs/ads.html',
        'holder','chart'
        ], function(ejs_loading,ejs_header,ejs_footer,ejs_main,ejs_empty_data,
        ejs_firms,ejs_deals,ejs_news,ejs_tags,ejs_ads,Holder,Chart) {

        var self = this;

        var ejs = {
            loading: ejs_loading,
            header: ejs_header,
            footer: ejs_footer,
            main: ejs_main,
            empty_data: ejs_empty_data,
            firms: ejs_firms,
            deals: ejs_deals,
            news: ejs_news,
            tags: ejs_tags,
        };

        $('.site-header').html(new EJS({ text: ejs.header }).render({}));
        $('.site-footer').html(new EJS({ text: ejs.footer }).render({}));

        $('.site-main').html(new EJS({ text: ejs.main }).render({ ejs: ejs }));
        $('.carousel').carousel({ interval: 1000*5 });

        $('.news').html(new EJS({ text: ejs_news }).render({}));
        $('.tags').html(new EJS({ text: ejs_tags }).render({}));
        $('.ads').html(new EJS({ text: ejs_ads }).render({}));
        Holder.run();

        self.load_config = function(callback) {
            CORE.ajax.post({
                url: '/law/config/load',
                success: function(result) {
                    categories = result.data.categories.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                    industries = result.data.industries.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                    areas = result.data.areas.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                    parties = result.data.parties.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                    roles = result.data.roles.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                    callback();
                }
            });
        };

        self.render_month_chart = function(months) {
            months.sort(function(x,y) { return parseInt(x.dimension) > parseInt(y.dimension) ? 1:-1; });

            var labels = [], data = [];
            for (var i=0;i<months.length;i++) {
                labels.push(months[i].dimension.substr(4,6));
                data.push(months[i].count);
            }

            if (data.reduce(function(sum,item) { return sum+item; },0)==0) {
                var ejs_html = new EJS({ text: ejs_empty_data }).render({});
                $('.month-count-line').html(ejs_html);
            } else {
                var canvas = $('<canvas></canvas>');
                $('.month-count-line').html(canvas);
                new Chart(canvas[0], {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Number',
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
                labels.push(month.dimension.substr(4,6));
                data.push(month.volume);
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
                            label: 'Volume',
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

        self.load_config(function() {
            CORE.ajax.post({
                url: '/law/stats/custom',
                success: function(result) {
                    self.render_month_chart(result.data.stats);
                }
            });

            CORE.ajax.post({
                url: '/law/stats/ranking/firm',
                success: function(result) {
                    var prc_firms = result.data.prc_firms;
                    var global_firms = result.data.global_firms;

                    var ejs_html = new EJS({ text: ejs.firms }).render({ firms: prc_firms });
                    $('.prc-firm-list').html(ejs_html);

                    var ejs_html = new EJS({ text: ejs.firms }).render({ firms: global_firms });
                    $('.global-firm-list').html(ejs_html);

                    Holder.run();
                }
            });

            CORE.ajax.post({
                url: '/law/stats/ranking/deal',
                success: function(result) {
                    var ejs_html = new EJS({ text: ejs_deals }).render({ deals: result.data.deals });
                    $('.recent-deal-list').html(ejs_html);
                }
            });
        });

    });
};


require([CONST.require.config], function() {
    require(['domReady','bootstrap','jasny-bootstrap','ejs','core'], function(domReady) {
        domReady(function() {
            CORE.ajax.session({
                url: '/session/sync',
                success: function(result) {
                    CORE.user = result.data.user;
                },
                fail: function(result) { },
                complete: function(xhr) {
                    main();
                }
            });
        });
    });
});


