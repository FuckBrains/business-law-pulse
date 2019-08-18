
define([
    'text!common/ejs/loading.html',
    'text!pages/www/pc/deal/ejs/detail.html',
    'text!pages/www/pc/deal/ejs/summary.html',
    ], function(ejs_loading,ejs_detail,ejs_summary) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        detail: ejs_detail,
        summary: ejs_summary,
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

    self.render_deal_relation = function() {
        CORE.ajax.post({
            url: '/law/deal/' + self.deal.id +'/relation',
            success: function(result) {
                self.clients = result.data.clients;
                self.firms = result.data.firms;
                self.lawyers = result.data.lawyers;

                self.summary = {};
                self.clients.forEach(function(client) {
                    if (!!self.summary[client.party]) {
                        self.summary[client.party].clients.push(client);
                    } else {
                        self.summary[client.party] = { clients: [client], firms: [] };
                    }
                });

                self.firms.forEach(function(firm) {
                    firm.lawyers = [];
                    self.lawyers.forEach(function(lawyer) {
                        if (lawyer.firm.id == firm.id) {
                            firm.lawyers.push(lawyer);
                        }
                    });

                    if (!!self.summary[firm.party]) {
                        self.summary[firm.party].firms.push(firm);
                    } else {
                        self.summary[firm.party] = { clients: [], firms: [firm] };
                    }
                });

                $('.deal-summary').html(new EJS({ text: ejs.summary }).render({
                        categories: self.categories, industries: self.industries,
                        areas: self.areas, parties: self.parties, roles: self.roles,
                        deal: self.deal, summary: summary,
                }));
            }
        });
    };

    return function(ctx,next) {
        CORE.ajax.post({
            url: '/law/deal/' + ctx.params.deal + '/detail',
            success: function(result) {
                self.deal = result.data.deal;

                self.load_config(function() {
                    $('.site-main').html(new EJS({ text: ejs.detail }).render({
                        categories: self.categories,
                        industries: self.industries,
                        areas: self.areas,
                        deal: self.deal,
                        ejs: ejs,
                    }));

                    self.render_deal_relation();
                });
            }
        });
    };
});




