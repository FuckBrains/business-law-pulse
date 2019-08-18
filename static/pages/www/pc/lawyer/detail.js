
define([
    'text!common/ejs/loading.html',
    'text!pages/www/pc/index/ejs/empty_data.html',
    'text!pages/www/pc/lawyer/ejs/detail.html',
    'text!pages/www/pc/lawyer/ejs/career_firms.html',
    'text!pages/www/pc/lawyer/ejs/filter_deals.html',
    'text!pages/www/pc/index/ejs/deals.html',
    'text!pages/www/pc/deal/ejs/feedbacks.html',
    'holder'], function(ejs_loading,ejs_empty_data, ejs_detail,ejs_career_firms,ejs_filter_deals,ejs_deals,ejs_feedbacks,Holder) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        empty_data: ejs_empty_data,
        detail: ejs_detail,
        career_firms: ejs_career_firms,
        filter_deals: ejs_filter_deals,
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

    self.load_recent_deals = function() {
        CORE.ajax.post({
            url: '/law/deal/filter',
            data: {
                lawyer: self.lawyer.id
            },
            success: function(result) {
                $('.recent-deal-list').html(new EJS({ text: ejs.deals }).render({ deals: result.data.deals }));
            }
        });
    };

    self.load_careers = function() {
        CORE.ajax.post({
            url: '/law/lawyer/' + self.lawyer.id + '/career',
            success: function(result) {
                self.career = result.data.career;
                $('.career-firms').html(new EJS({ text: ejs.career_firms }).render({ career: self.career }));
                Holder.run();
            }
        });
    };

    self.load_lawyer_feedback = function() {
        CORE.ajax.post({
            url: '/law/lawyer/' + self.lawyer.id + '/feedback/filter',
            data: {
                page: { size: 10 },
            },
            success: function(result) {
                $('.feedback-list').html(new EJS({ text: ejs.feedbacks }).render({ feedbacks: result.data.feedbacks }));
            }
        });
    };

    $('.site-main').on('click','.list-firm-deal-btn',function(event) {
        var btn = $(event.currentTarget);
        var firm = { id: btn.parents('tr').data('firm-id') };

        $('.firm-deal-list').html(new EJS({ text: ejs.loading }).render({ padding: '50px', font: '30px' }));
        $('#firm_deal_modal').modal('show');

        var deals = [];
        for (var i=0;i<self.career.length;i++) {
            if (self.career[i].firm.id == firm.id) {
                deals = self.career[i].deals;
                break;
            }
        }

        $('.firm-deal-list').html(new EJS({ text: ejs.filter_deals }).render({ deals: deals }));
    });

    return function(ctx,next) {
        self.load_config(function() {
            CORE.ajax.post({
                url: '/law/lawyer/' + ctx.params.lawyer + '/detail',
                success: function(result) {
                    self.lawyer = result.data.lawyer;

                    $('.site-main').html(new EJS({ text: ejs.detail }).render({
                        categories: self.categories,
                        lawyer: self.lawyer,
                        ejs: ejs
                    }));

                    self.load_recent_deals();
                    self.load_careers();
                    self.load_lawyer_feedback();
                }
            });
        });
    };
});


