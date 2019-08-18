
define([
    'text!common/ejs/loading.html',
    'text!pages/www/m/index/ejs/empty_data.html',
    'text!pages/www/m/firm/ejs/detail.html',
    'text!pages/www/m/firm/ejs/recent_lawyers.html',
    'text!pages/www/m/index/ejs/deals.html',
    'text!pages/www/m/deal/ejs/feedbacks.html',
    'holder','chart'], function(ejs_loading,ejs_empty_data, ejs_detail,ejs_recent_lawyers,ejs_deals,ejs_feedbacks,Holder,Chart) {

    Chart.defaults.global.defaultFontSize = 9;

    var self = this;

    var ejs = {
        loading: ejs_loading,
        empty_data: ejs_empty_data,
        detail: ejs_detail,
        recent_lawyers: ejs_recent_lawyers,
        deals: ejs_deals,
        feedbacks: ejs_feedbacks,
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
            }
        });
    };

    self.load_firm_recent_stats = function() {
        CORE.ajax.post({
            url: '/law/stats/firm/' + self.firm.id + '/recent',
            success: function(result) {
                render_month_chart(result.data.stats);

                new EJS({ text: ejs.deals }).update(document.querySelector('.recent-deal-list'), { deals: result.data.deals });
                new EJS({ text: ejs.recent_lawyers }).update(document.querySelector('.recent-lawyer-list'), { lawyers: result.data.lawyers });
            }
        });
    };

    self.load_firm_feedback = function() {
        CORE.ajax.post({
            url: '/law/firm/' + self.firm.id + '/feedback/filter',
            data: {
                page: { size: 10 },
            },
            success: function(result) {
                new EJS({ text: ejs.feedbacks }).update(document.querySelector('.feedback-list'), { feedbacks: result.data.feedbacks });
            }
        });
    };

    var render_month_chart = function(months) {
        months.sort(function(x,y) { return parseInt(x.dimension) > parseInt(y.dimension) ? 1:-1; });

        var labels = [], data = [];
        for (var i=0;i<months.length;i++) {
            labels.push(months[i].dimension.substr(4,6));
            data.push(months[i].count);
        }

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

    return function(ctx,next) {
        self.load_config(function() {
            CORE.ajax.post({
                url: '/law/firm/' + ctx.params.firm + '/detail',
                success: function(result) {
                    self.firm = result.data.firm;

                    new EJS({ text: ejs.detail }).update(document.querySelector('.site-main'), {
                        categories: self.categories,
                        areas: self.areas,
                        firm: self.firm,
                        ejs: ejs,
                    });
                    Holder.run();

                    self.load_firm_recent_stats();
                    self.load_firm_feedback();
                }
            });
        });
    };
});


