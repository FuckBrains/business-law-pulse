
define([
    'text!pages/www/pc/debug/ejs/debug.html',
    'text!pages/www/pc/debug/ejs/ajax_param.html',
    'text!pages/www/pc/debug/ejs/mqtt_topic.html',
    'text!pages/www/pc/debug/ejs/mqtt_message.html',
    'holder','crypto-js'], function(ejs_debug,ejs_ajax_param,ejs_mqtt_topic,ejs_mqtt_message,Holder,CryptoJS) {

    var self = this;

    var ejs = {
        debug: ejs_debug,
        ajax_param: ejs_ajax_param,
        mqtt_topic: ejs_mqtt_topic,
        mqtt_message: ejs_mqtt_message,
    };

    $('.site-main').on('click','.x-debug',function(event) {
        var node = $(event.currentTarget);
        node.toggleClass('fa-toggle-on').toggleClass('fa-toggle-off');
        node.toggleClass('text-primary').toggleClass('text-muted');
        if (node.hasClass('fa-toggle-on')) {
            window.sessionStorage.setItem('debug','1');
        } else {
            window.sessionStorage.removeItem('debug');
        }
    });

    $('.site-main').on('click','.add-ajax-querystring-param-btn',function(event) {
        $('.ajax-querystring').append(new EJS({ text: ejs.ajax_param }).render({}));
    });

    $('.site-main').on('click','.add-ajax-headers-param-btn',function(event) {
        $('.ajax-headers').append(new EJS({ text: ejs.ajax_param }).render({}));
    });

    $('.site-main').on('click','.remove-ajax-param-btn',function(event) {
        var btn = $(event.currentTarget);
        if (btn.parents('.ajax-param-list').find('.ajax-param-item').length>1) {
            btn.parents('.ajax-param-item').remove();
        }
    });

    $('.site-main').on('click','.submit-ajax-btn',function(event) {
        $('#ajax .request-error').html('');
        $('#ajax .response-header').html('');
        $('#ajax .output-text').html('');

        var url = $('.api-url').val().trim();
        var method = $('.api-method').val();

        var headers = {};
        $('.ajax-headers').find('.ajax-param-item').each(function() {
            var name = $(this).find('.param-name').val();
            var value = $(this).find('.param-value').val();
            if (!!name && !!value) {
                headers[name] = value;
            }
        });

        var querystring = [];
        $('.ajax-querystring').find('.ajax-param-item').each(function() {
            var name = $(this).find('.param-name').val();
            var value = $(this).find('.param-value').val();
            if (!!name && !!value) {
                querystring.push(name + '=' + value);
            }
        });

        var data = {};
        if (!!$('.param-json').val().trim()) {
            try {
                data = JSON.parse($('.param-json').val());
            } catch(e) {
                CORE.notify.error('Illegal JSON');
                return false;
            }
        }

        if (!!CORE.ajax.xhr) { CORE.ajax.xhr.abort(); }
        $('#ajax .submit-ajax-btn').button('loading');

        if (method != 'POST') {
            CORE.notify.error(method + ' is unsupported');
            $('#ajax .submit-ajax-btn').button('reset');
            return false;
        }

        CORE.ajax.post({
            url: querystring.length==0 ? url : url + '?' + querystring.join('&'),
            headers: headers,
            data: data,
            success: function(result,xhr) {
                console.log(result);
                CORE.notify.info('Submit Done');
                var output = JSON.stringify(result, null, 4).replace(/\n/g, '<br>').replace(/\s/g,'&nbsp;');
                $('#ajax .output-text').html(output);
            },
            fail: function(result) {
                console.log(result);
                CORE.notify.error('Submit Failed');
                var output = JSON.stringify(result, null, 4).replace(/\n/g, '<br>').replace(/\s/g,'&nbsp;');
                $('#ajax .output-text').html(output);
            },
            error: function(xhr) {
                CORE.notify.error(xhr.status + ' - ' + xhr.statusText);
            },
            complete: function(xhr) {
                $('#ajax .submit-ajax-btn').button('reset');
                $('#ajax .request-error').html(xhr.state() + ' - ' + xhr.status + ' - ' + xhr.statusText);
                self.output_response_header('#ajax',xhr);
            }
        });
    });

    $('.site-main').on('click','.submit-upload-image-btn',function(event) {
        $('#upload .request-error').html('');
        $('#upload .response-header').html('');
        $('#upload .output-text').html('');

        var file_input = $('#upload input[name="image"]')[0];
        if (!file_input.files || file_input.files.length==0) {
            CORE.notify.error('Choose an image');
            return false;
        }

        if (file_input.files[0].size>1024*1024*5) {
            CORE.notify.error('Image file size exceeds');
            return false;
        }

        $('#upload .submit-upload-image-btn').button('loading');

        require(['jquery-form' ],function() {
            $('#upload_image_form').ajaxSubmit({
                url: (CONST.ssl ? 'https':'http') + '://' + CONST.domain.api + '/common/upload/image',
                type: 'POST',
                dataType: 'json',
                success: function(result) {
                    console.log(result);
                    $('#upload_image_form .fileinput').fileinput('clear');
                    var output = JSON.stringify(result, null, 4).replace(/\n/g, '<br>').replace(/\s/g,'&nbsp;');
                    $('#upload .output-text').html(output);

                    if (result.err) {
                        CORE.notify.error(result.msg);
                    } else {
                        CORE.notify.info(result.msg);
                    }
                },
                complete: function(xhr) {
                    $('#upload .submit-upload-image-btn').button('reset');
                    $('#upload .request-error').html(xhr.state() + ' - ' + xhr.status + ' - ' + xhr.statusText);
                    CORE.ajax.xhr = xhr;
                    self.output_response_header('#upload',xhr);
                }
            });
        });
    });

    $('.site-main').on('click','.upload-file',function(event) {
        $('input[name="file"]')[0].click();
    });

    $('.site-main').on('change','input[name="file"]',function(event) {
        if (!!$('input[name="file"]').val()) {
            $('.upload-file').val($('input[name="file"]')[0].files[0].name);
        } else {
            $('.upload-file').val('-- Click to choose --');
        }
    });

    $('.site-main').on('click','.submit-upload-file-btn',function(event) {
        $('#upload .request-error').html('');
        $('#upload .response-header').html('');
        $('#upload .output-text').html('');

        var file_input = $('#upload input[name="file"]')[0];
        if (!file_input.files || file_input.files.length==0) {
            CORE.notify.error('Choose a file');
            return false;
        }

        if (file_input.files[0].size>1024*1024*20) {
            CORE.notify.error('File size exceeds');
            return false;
        }

        $('#upload .submit-upload-file-btn').button('loading');

        require(['jquery-form' ],function() {
            $('#upload_file_form').ajaxSubmit({
                url: (CONST.ssl ? 'https':'http') + '://' + CONST.domain.api + '/common/file/upload',
                type: 'POST',
                dataType: 'json',

                success: function(result) {
                    console.log(result);
                    var output = JSON.stringify(result, null, 4).replace(/\n/g, '<br>').replace(' ','&nbsp;');
                    $('#upload .output-text').html(output);

                    if (result.err) {
                        CORE.notify.error(result.msg);
                    } else {
                        CORE.notify.info(result.msg);
                        $('#upload_file_form')[0].reset();
                    }
                },

                complete: function(xhr) {
                    $('#upload .submit-upload-file-btn').button('reset');
                    $('#upload .request-error').html(xhr.state()+' - '+xhr.status+' - '+xhr.statusText);
                    CORE.ajax.xhr = xhr;
                    self.output_response_header('#upload',xhr);
                }
            });
        });
    });

    $('.site-main').on('click','.generate-mqtt-clientid-btn',function(event) {
        if ($('.mqtt-connect-broker-btn').hasClass('hidden')) return false;

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
                    if (item.find('.subscribe-topic').html() == topic) {
                        item.remove();
                    }
                });

                $('.subscribe-list').append(new EJS({ text: ejs.mqtt_topic }).render({ topic: topic, qos: qos, timeout: timeout }));
            },

            failure: function(responseObject) {
                CORE.notify.error('Subscribe Failed');
                $('.mqtt-subscribe-topic-btn').button('reset');
            },

            arrived: function(message) {
                $('.mqtt-history-message-list').prepend(new EJS({ text: ejs.mqtt_message }).render({ message: message }));
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

    $('.site-main').on('click','.mqtt-publish-message-btn',function(event) {
        if (!CORE.mqtt.client || !CORE.mqtt.client.isConnected()) {
            CORE.notify.error('Client Disconnected');
            return false;
        }

        $('.mqtt-publish-message-btn').button('loading');

        var topic = $('input[name="mqtt_publish_topic"]').val();
        var qos = parseInt($('select[name="mqtt_publish_qos"]').val());
        var retained = $('select[name="mqtt_publish_retained"]').val() == 'Y';
        var payload = $('textarea[name="mqtt_publish_payload"]').val();

        var options = {
            payload: payload,
            topic: topic,
            qos: qos,
            retained: retained,
        };

        CORE.mqtt.publish(options);

        $('.mqtt-send-message-btn').button('reset');
    });

    $('.site-main').on('click','.mqtt-clear-message-btn',function(event) {
        $('.mqtt-history-message-list').html('');
    });

    self.output_response_header = function(el,xhr) {
        $(el+' .response-header').html(xhr.getAllResponseHeaders().replace(new RegExp('\n','g'),'<br>'));
    };

    return function(ctx,next) {
        $('title').html('接口调试 - 足球地带');

        $('.site-main').html(new EJS({ text: ejs.debug }).render({ ejs_ajax_param: ejs_ajax_param }));

        Holder.run();

        if (window.sessionStorage.getItem('debug')=='1') {
            $('.x-debug').removeClass('fa-toggle-off').removeClass('text-muted');
            $('.x-debug').addClass('fa-toggle-on').addClass('text-primary');
        }
    };
});


