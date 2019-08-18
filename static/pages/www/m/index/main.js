
var main = function() {
    require([
        'text!common/ejs/loading.html',
        'text!pages/www/m/index/ejs/navmenu.html',
        'text!pages/www/m/index/ejs/footer.html',
        'text!pages/www/m/index/ejs/main.html',
        'text!pages/www/m/index/ejs/empty_data.html',
        'text!pages/www/m/index/ejs/firms.html',
        'text!pages/www/m/index/ejs/deals.html',
        'holder','chart'
        ], function(ejs_loading,ejs_navmenu,ejs_footer,ejs_main,ejs_empty_data, ejs_firms,ejs_deals,Holder,Chart) {

        var self = this;

        var ejs = {
            loading: ejs_loading,
            navmenu: ejs_navmenu,
            footer: ejs_footer,
            main: ejs_main,
            empty_data: ejs_empty_data,
            firms: ejs_firms,
            deals: ejs_deals,
        };

        new EJS({ text: ejs.navmenu }).update(document.querySelector('.site-navmenu'), {});
        new EJS({ text: ejs.footer }).update(document.querySelector('.site-footer'), {});
        new EJS({ text: ejs.main }).update(document.querySelector('.site-main'), {});

        Holder.run();
        Chart.defaults.global.defaultFontSize = 9;

        CORE.ajax.post({
            url: '/law/config/load',
            success: function(result) {
                categories = result.data.categories.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                industries = result.data.industries.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                areas = result.data.areas.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                parties = result.data.parties.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});
                roles = result.data.roles.reduce(function(dict,item) { dict[item.id] = item; return dict; },{});

                CORE.ajax.post({
                    url: '/law/stats/custom',
                    success: function(result) {
                        render_month_chart(result.data.stats);
                    }
                });

                CORE.ajax.post({
                    url: '/law/stats/ranking/firm',
                    success: function(result) {
                        var prc_firms = result.data.prc_firms;
                        var global_firms = result.data.global_firms;

                        new EJS({ text: ejs.firms }).update(document.querySelector('.prc-firm-list'), { firms: prc_firms });
                        new EJS({ text: ejs.firms }).update(document.querySelector('.global-firm-list'), { firms: global_firms });

                        Holder.run();
                    }
                });

                CORE.ajax.post({
                    url: '/law/stats/ranking/deal',
                    success: function(result) {
                        new EJS({ text: ejs.deals }).update(document.querySelector('.recent-deal-list'), { deals: result.data.deals });
                    }
                });
            }
        });

        var render_month_chart = function(months) {
            months.sort(function(x,y) { return parseInt(x.dimension) > parseInt(y.dimension) ? 1:-1; });

            var labels = [], data = [];
            months.forEach(function(month) {
                labels.push(month.dimension.substr(4,6));
                data.push(month.count);
            });

            if (data.reduce(function(sum,item) { return sum+item; },0)==0) {
                new EJS({ text: ejs.empty_data }).update(document.querySelector('.month-count-line'), {});
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
                new EJS({ text: ejs.empty_data }).update(document.querySelector('.month-volume-bar'), {});
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


