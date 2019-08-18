
define([
    'text!pages/www/m/debug/ejs/mqtt.html',
    'text!pages/www/m/debug/ejs/mqtt_topic.html',
    'text!pages/www/m/debug/ejs/mqtt_message.html',
    'crypto-js',
    ], function(ejs_mqtt,ejs_mqtt_topic,ejs_mqtt_message,CryptoJS) {

    var self = this;

    $('.site-main').on('click','.generate-mqtt-clientid-btn',function(event) {
        if ($('.mqtt-connect-broker-btn').hasClass('hidden')) { return false; }

        var mqtt_client_id = 'debug-' + CryptoJS.MD5(window.navigator.userAgent + new Date().getTime() + Math.random());
        $('input[name="mqtt_client_id"]').val(mqtt_client_id);
    });

    $('.site-main').on('click','.mqtt-connect-broker-btn',function(event) {
        $('.mqtt-connect-broker-btn').button('loading');

        var mqtt_host = $('input[name="mqtt_host"]').val();
        var mqtt_port = parseInt($('input[name="mqtt_port"]').val());
        var mqtt_keep_alive = parseInt($('input[name="mqtt_keep_alive"]').val());
        var mqtt_username = $('input[name="mqtt_username"]').val();
        var mqtt_password = $('input[name="mqtt_password"]').val();
        var mqtt_client_id = $('input[name="mqtt_client_id"]').val();
        var mqtt_use_ssl = $('input[name="mqtt_use_ssl"]').is(':checked');
        var mqtt_clean_session = $('input[name="mqtt_clean_session"]').is(':checked');

        var options = {
            host: mqtt_host,
            port: mqtt_port,
            username: mqtt_username,
            password: mqtt_password,
            clientid: mqtt_client_id,

            timeout: 15,    // in seconds
            keepAliveInterval: mqtt_keep_alive,
            useSSL: mqtt_use_ssl,
            cleanSession: mqtt_clean_session,
            context: { host: mqtt_host, port: mqtt_port },

            success: function(responseObject) {
                CORE.notify.info('Client Connected');
                $('.mqtt-connect-broker-btn').button('reset');

                $('input[name="mqtt_host"]').prop('readonly',true);
                $('input[name="mqtt_port"]').prop('readonly',true);
                $('input[name="mqtt_keep_alive"]').prop('readonly',true);
                $('input[name="mqtt_username"]').prop('readonly',true);
                $('input[name="mqtt_password"]').prop('readonly',true);
                $('input[name="mqtt_client_id"]').prop('readonly',true);
                $('input[name="mqtt_clean_session"]').prop('disabled',true);
                $('input[name="mqtt_use_ssl"]').prop('disabled',true);
                $('.toggle-lwt').prop('disabled',true);

                $('input[name="mqtt_will_topic"]').prop('disabled',true);
                $('select[name="mqtt_will_qos"]').prop('disabled',true);
                $('select[name="mqtt_will_retained"]').prop('disabled',true);
                $('textarea[name="mqtt_will_payload"]').prop('disabled',true);

                $('.mqtt-connect-broker-btn').addClass('hidden');
                $('.mqtt-disconnect-broker-btn').removeClass('hidden');

                $('.subscribe-list').html('');
            },

            failure: function(responseObject) {
                CORE.notify.error('Client Connection Failed');
                $('.mqtt-connect-broker-btn').button('reset');
            },

            lost: function(responseObject) {
                $('input[name="mqtt_host"]').prop('readonly',false);
                $('input[name="mqtt_port"]').prop('readonly',false);
                $('input[name="mqtt_keep_alive"]').prop('readonly',false);
                $('input[name="mqtt_username"]').prop('readonly',false);
                $('input[name="mqtt_password"]').prop('readonly',false);
                $('input[name="mqtt_client_id"]').prop('readonly',false);
                $('input[name="mqtt_clean_session"]').prop('disabled',false);
                $('input[name="mqtt_use_ssl"]').prop('disabled',false);
                $('.toggle-lwt').prop('disabled',false);

                $('input[name="mqtt_will_topic"]').prop('disabled',false);
                $('select[name="mqtt_will_qos"]').prop('disabled',false);
                $('select[name="mqtt_will_retained"]').prop('disabled',false);
                $('textarea[name="mqtt_will_payload"]').prop('disabled',false);

                $('.mqtt-connect-broker-btn').removeClass('hidden');
                $('.mqtt-disconnect-broker-btn').addClass('hidden');

                if (responseObject.errorCode==0) {
                    CORE.notify.info(responseObject.errorMessage);
                } else {
                    CORE.notify.error(responseObject.errorMessage);
                }
            },

            delivered: function(message) {
                CORE.notify.info('Message Delivered');
                $('.mqtt-publish-message-btn').button('reset');
            },
        };

        if ($('.toggle-will').is(':checked')) {
            var mqtt_will_topic = $('input[name="mqtt_will_topic"]').val();
            var mqtt_will_qos = parseInt($('select[name="mqtt_will_qos"]').val());
            var mqtt_will_retained = $('select[name="mqtt_will_retained"]').val() == 'Y';
            var mqtt_will_payload = $('textarea[name="mqtt_will_payload"]').val();

            $.extend(options,{
                will: {
                    topic: mqtt_will_topic,
                    qos: mqtt_will_qos,
                    retained: mqtt_will_retained,
                    payload: mqtt_will_payload,
                }
            });
        }

        CORE.mqtt.reconnect = false;
        CORE.mqtt.log = true;
        CORE.mqtt.connect(options);
    });

    $('.site-main').on('click','.mqtt-disconnect-broker-btn',function(event) {
        if (!!CORE.mqtt.client && CORE.mqtt.client.isConnected()) {
            CORE.mqtt.client.disconnect();
        }

        $('input[name="mqtt_host"]').prop('readonly',false);
        $('input[name="mqtt_port"]').prop('readonly',false);
        $('input[name="mqtt_keep_alive"]').prop('readonly',false);
        $('input[name="mqtt_username"]').prop('readonly',false);
        $('input[name="mqtt_password"]').prop('readonly',false);
        $('input[name="mqtt_client_id"]').prop('readonly',false);
        $('input[name="mqtt_clean_session"]').prop('disabled',false);
        $('input[name="mqtt_use_ssl"]').prop('disabled',false);
        $('.toggle-lwt').prop('disabled',false);

        $('input[name="mqtt_will_topic"]').prop('disabled',false);
        $('select[name="mqtt_will_qos"]').prop('disabled',false);
        $('select[name="mqtt_will_retained"]').prop('disabled',false);
        $('textarea[name="mqtt_will_payload"]').prop('disabled',false);

        $('.mqtt-connect-broker-btn').removeClass('hidden');
        $('.mqtt-disconnect-broker-btn').addClass('hidden');

        CORE.notify.info('Client Disconnected');
    });

    $('.site-main').on('click','.mqtt-subscribe-topic-btn',function(event) {
        if (!CORE.mqtt.client || !CORE.mqtt.client.isConnected()) {
            CORE.notify.error('Client Disconnected');
            return false;
        }

        $('.mqtt-subscribe-topic-btn').button('loading');

        var topic = $('input[name="mqtt_subscribe_topic"]').val();
        var qos = parseInt($('select[name="mqtt_subscribe_qos"]').val());
        var timeout = parseInt($('input[name="mqtt_subscribe_timeout"]').val());

        var options = {
            topic: topic,
            qos: qos,
            timeout: timeout,
            context: { topic: topic, timeout: timeout, qos: qos },

            success: function(responseObject) {
                CORE.notify.info('Subscribe Done');
                $('.mqtt-subscribe-topic-btn').button('reset');

                $('.subscribe-item').each(function() {
                    var item = $(this);
                    if (item.find('.subscribe-topic').html()==topic) {
                        item.remove();
                    }
                });

                var ejs_html = new EJS({ text: ejs_mqtt_topic }).render({ topic: topic, qos: qos, timeout: timeout });
                $('.subscribe-list').append(ejs_html);
            },

            failure: function(responseObject) {
                CORE.notify.error('Subscribe Failed');
                $('.mqtt-subscribe-topic-btn').button('reset');
            },

            arrived: function(message) {
                var ejs_html = new EJS({ text: ejs_mqtt_message }).render({ message: message });
                $('.mqtt-history-message-list').prepend(ejs_html);
            },
        };

        CORE.mqtt.subscribe(options);
    });

    $('.site-main').on('click','.mqtt-unsubscribe-topic-btn',function(event) {
        var item = $(event.currentTarget).parents('.subscribe-item');

        if (!CORE.mqtt.client || !CORE.mqtt.client.isConnected()) {
            CORE.notify.error('Client Disconnected');
            return false;
        }

        var topic = item.find('.subscribe-topic').html();

        var options = {
            topic: topic,
            timeout: 5,
            context: { topic: topic },

            success: function(responseObject) {
                CORE.notify.info('Unsubscribe Done');
                item.remove();
            },

            failure: function(responseObject) {
                CORE.notify.error('Unsubscribe Failed');
            }
        };

        CORE.mqtt.unsubscribe(options);
    });

    $('.site-main').on('click','.mqtt-clear-message-btn',function(event) {
        $('.mqtt-history-message-list').html('');
    });

    return function(ctx,next) {
        new EJS({ text: ejs_mqtt }).update(document.querySelector('.site-main'), {});
    };
});



