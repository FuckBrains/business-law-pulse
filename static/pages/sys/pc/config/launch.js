
define([
    'text!common/ejs/loading.html',
    'text!pages/sys/pc/config/ejs/launch.html',
    'text!pages/sys/pc/config/ejs/launch_list.html',
    'bootstrap-datetimepicker','bootstrap-datetimepicker-lang',
    ], function(ejs_loading, ejs_launch, ejs_launch_list) {

    var self = this;

    var ejs = {
        loading: ejs_loading,
        launch: ejs_launch,
        launch_list: ejs_launch_list,
    };

    self.render_components = function() {
        CORE.image.uploader($('.upload-launch-image'));

        $('.start-date').datetimepicker({
            language:  'zh-CN',
            todayBtn:  1,
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 0,
            maxView: 4,
            minuteStep: 1,
            forceParse: 0,
            showMeridian: 1,
            format: 'yyyy-mm-dd hh:ii',
        });

        $('.end-date').datetimepicker({
            language:  'zh-CN',
            todayBtn:  1,
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 0,
            maxView: 4,
            minuteStep: 1,
            forceParse: 0,
            showMeridian: 1,
            format: 'yyyy-mm-dd hh:ii',
        });
    };

    $('.site-main').on('change','input[name="countdown"]',function(event) {
        var countdown = $('#launch input[name="countdown"]').val();
        if (isNaN(countdown) || countdown != parseInt(countdown).toString() || parseInt(countdown)<0) {
            $('#launch input[name="countdown"]').val(0);
        }
    });

    $('.site-main').on('click','.create-launch-btn',function(event) {
        var btn = $(event.currentTarget);

        var start = $('input[name="start"]').val();
        var end = $('input[name="end"]').val();
        if (!start || !end) {
            CORE.notify.error('请指定生效和失效时间');
            return false;
        }

        var data = {
            image: $('.upload-launch-image').data('image').id,
            countdown: parseInt($('input[name="countdown"]').val()),
            start: new Date(start.replace(' ','T') + '+08:00').getTime(),
            end: new Date(end.replace(' ','T') + '+08:00').getTime(),
            url: $('input[name="url"]').val(),
        };

        btn.button('loading');
        CORE.ajax.post({
            url: '/common/config/launch/create',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: data,
            success: function(result) {
                CORE.notify.info(result.msg);
                window.location.reload();
            },
            complete: function(xhr) {
                btn.button('reset');
            }
        });
    });

    $('.site-main').on('click','.remove-launch-btn',function(event) {
        var item = $(event.currentTarget).parents('.launch-item');

        if (!confirm('确认删除此启动图吗？')) return false;

        CORE.ajax.post({
            url: '/common/config/launch/remove',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            data: {
                image: item.data('image'),
            },
            success: function(result) {
                CORE.notify.info(result.msg);
                item.remove();
            }
        });
    });

    return function(ctx,next) {
        var ejs_html = new EJS({ text: ejs.launch }).render({ ejs_loading: ejs_loading });
        $('.site-main').html(ejs_html);

        self.render_components();

        CORE.ajax.post({
            url: '/common/config/launch/list',
            headers: {
                'x-admin-id': CORE.admin.id,
                'x-admin-token': CORE.admin.token,
            },
            success: function(result) {
                $('.launch-list').html(new EJS({ text: ejs.launch_list }).render({ launches: result.data.launches }));
            }
        });


    };
});





