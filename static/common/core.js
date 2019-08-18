
(function(window) {
    var CONST = window.CONST;
    var $ = window.$;

    Number.prototype.shorten = Number.prototype.shorten || function(float_count) {
        var counter = 0;
        var number = this;
        if (number >= 1000000000) {
            number /= 1000000000;
            counter = 9;
        } else if (number >= 1000000) {
            number /= 1000000;
            counter = 6;
        }
        var fix = float_count !== undefined ? float_count : 2;
        var str = number.toFixed(fix);

        while(str.charAt(str.length - 1) === '0') { str = str.substring(0, str.length - 1); }
        if(str.charAt(str.length - 1) === '.') { str = str.substring(0, str.length - 1); }
        return str + (counter === 6 ? ' million' : (counter === 9 ? ' billion' : ''));
    };

    String.prototype.truncate = String.prototype.truncate || function(length,suffix) {
        var after_truncate_str = '';
        var char_length = 0;
        for (var i=0;i<this.length;i++) {
            var char_code = this.charCodeAt(i);
            if　(char_code >= 33 && char_code <= 126) {
                char_length = char_length + 1;
            } else {
                char_length = char_length + 2;
            }

            if (char_length > length*2) { break; }
            after_truncate_str = after_truncate_str + this.substr(i,1);
        }

        suffix = !suffix ? '...':suffix;
        return after_truncate_str + (after_truncate_str === this ? '':suffix);
    };

    Date.prototype.format = Date.prototype.format || function(format) {
        var options = {
            'm+': this.getMonth()+1,                    //month
            'd+': this.getDate(),                       //day
            'h+': this.getHours(),                      //hour
            'i+': this.getMinutes(),                    //minute
            's+': this.getSeconds(),                    //second
            'q+': Math.floor((this.getMonth()+3)/3),    //quarter
            'S': this.getMilliseconds()                 //millisecond
        };

        if (/(y+)/.test(format)) {
            format = format.replace(RegExp.$1,(this.getFullYear().toString()).substr(4 - RegExp.$1.length));
        }

        for (var k in options) {
            if (options.hasOwnProperty(k)) {
                if(new RegExp('('+ k +')').test(format)) {
                    format = format.replace(RegExp.$1,RegExp.$1.length === 1 ? options[k] : ('00'+ options[k]).substr(options[k].toString().length));
                }
            }
        }

        return format;
    };

    Date.prototype.humanize = Date.prototype.humanize || function(default_format,flag) {
        var gap = (Date.parse(new Date())-Date.parse(this))/1000;
        var text = '';
        if (gap < 60) {
            text = '刚刚';
        } else if (gap < 3600) {
            text =  Math.floor(gap/60).toString() + '分钟前';
        } else if (gap < 86400) {
            text = Math.floor(gap/3600).toString() + '小时前';
        } else if (gap < 86400 * 2) {
            text = '昨天';
        } else if (gap < 86400 * 3) {
            text = '前天';
        } else if (flag) {
            text = this.format(default_format || 'yyyy-mm-dd');
        } else if (gap < 86400 * 30) {
            text = Math.floor(gap/86400).toString() + '天前';
        } else if (gap < 86400 * 30 * 6) {
            text = Math.floor(gap/86400/30).toString() + '个月前';
        } else {
            text = this.format(default_format || 'yyyy-mm-dd');
        }
        return text;
    };

    //////////////////////////////////////////////////////////////////////////////////////////

    var CORE = {
        debug: {
            enable: false,
            timer: null,
            trace: function(callback) {
                var self = this;
                self.enable = true;
                self.timer = setInterval(function() {
                    if (self.enable) { return; }
                    clearInterval(self.timer);
                    callback();
                },1000);
            },
        },

        notify: {
            info: function(message,delay) {
                this.alert(message,delay,'info');
            },
            error: function(message,delay) {
                this.alert(message,delay,'danger');
            },
            alert: function(message,delay,type) {
                $('.notifications').html('');
                require(['bootstrap-notify'],function() {
                    $('.notifications').notify({
                        message: message,
                        type: type,
                        fadeOut: { enabled: true, delay: delay || (1000 * 3) },    // delay in milliseconds
                    }).show();
                });
            }
        },

        ajax: {
            xhr: null,          // XMLHttpRequest
            result: null,       // AJAX请求返回值

            get: function(args) {
                var url = args.url;
                if (url.slice(0,4) !== 'http') {
                    url = (CONST.ssl ? 'https':'http') + '://' + window.location.host + args.url;
                }

                var options = {
                    url: url,
                    type: 'GET',
                    data: args.data || {},
                    contentType: 'text/html',
                    dataType: 'json',
                    cache: args.cache || false,
                    timeout: args.timeout || 0,
                };

                var headers = args.headers || {};

                var callback = {
                    success: args.success,
                    fail: args.fail,
                    error: args.error,
                    complete: args.complete,
                };

                var self = this;
                self.xhr = self.request(options,headers,callback);
                return self.xhr;
            },

            post: function(args) {
                var url = args.url;
                if (url.slice(0,4) !== 'http') {
                    url = (CONST.ssl ? 'https':'http') + '://' + window.location.host + '/api' + args.url;
                }

                var options = {
                    url: url,
                    type: 'POST',
                    data: JSON.stringify(args.data) || '{}',
                    contentType: 'application/json',
                    dataType: 'json',
                    cache: args.cache || false,
                    timeout: args.timeout || 0,
                };

                var headers = args.headers || {};

                var callback = {
                    success: args.success,
                    fail: args.fail,
                    error: args.error,
                    complete: args.complete,
                };

                var self = this;
                return self.request(options,headers,callback);
            },

            session: function(args) {
                var options = {
                    url: args.url,
                    type: 'POST',
                    data: JSON.stringify(args.data) || '{}',
                    contentType: 'application/json',
                    dataType: 'json',
                    cache: args.cache || false,
                    timeout: args.timeout || 0,
                };

                var headers = args.headers || {};

                var callback = {
                    success: args.success,
                    fail: args.fail,
                    error: args.error,
                    complete: args.complete,
                };

                var self = this;
                return self.request(options,headers,callback);
            },

            request: function(options,headers,callback) {
                var self = this;
                self.xhr = $.ajax({
                    url: options.url,
                    type: options.type,
                    data: options.data,
                    contentType: options.contentType,
                    dataType: 'json',
                    cache: options.cache,
                    timeout: options,
                    beforeSend: function(xhr) {
                        if (!!window.sessionStorage && window.sessionStorage.getItem('debug') === '1') {
                            xhr.setRequestHeader('X-Debug', '1');
                        }

                        headers = headers || {};
                        for (var key in headers) {
                            if (headers.hasOwnProperty(key)) {
                                xhr.setRequestHeader(key, headers[key]);
                            }
                        }
                    }
                });

                self.xhr.done(function(result, ts, xhr) {
                    self.result = result;

                    if (result.err === 0) {
                        if (!!callback.success) { callback.success(result); }
                    } else if (!!callback.fail) {
                        callback.fail(result);
                    } else if (result.err === -1) {
                        CORE.notify.error('系统繁忙，请稍后重试');
                    } else if (result.err === -2) {
                        CORE.notify.error('帐号异常，请重新登录');
                    } else {
                        CORE.notify.error(result.msg);
                    }

                    if (!!callback.complete) { callback.complete(xhr); }

                }).fail(function(xhr) {
                    console.log(xhr);
                    if (!!callback.error) { callback.error(xhr); }
                    if (!!callback.complete) { callback.complete(xhr); }
                });

                return self.xhr;
            },
        },

        geo: {
            storage: null,
            bind: function(options) {
                var self = this;
                var callback = function() {
                    $(options.province.selector).html('<option value="0">' + options.province.label + '</option>');

                    var provinces = self.storage;
                    provinces.forEach(function(province) {
                        var option = $('<option></option>');
                        option.prop('value',province.id);
                        option.html(province.name);
                        $(options.province.selector).append(option);
                    });

                    $(options.city.selector).unbind('change');
                    $(options.city.selector).bind('change',function() {
                        if (!!options.city.change) { options.city.change(); }
                    });

                    $(options.province.selector).unbind('change');
                    $(options.province.selector).bind('change',function() {
                        $(options.city.selector).html('<option value="0">' + options.city.label + '</option>');

                        var province = provinces.filter(function(province) {
                            return province.id === $(options.province.selector).val();
                        });

                        province.cities.forEach(function(city) {
                            var option = $('<option></option>');
                            option.prop('value',city.id);
                            option.html(city.name);
                            $(options.city.selector).append(option);
                        });

                        if (!!options.city.value) {
                            $(options.city.selector).val(options.city.value);
                            options.city.value = null;
                        }

                        if (province.cities.length === 1) {
                            $(options.city.selector).val(province.cities[0].id);
                        }

                        if (!!options.province.change) { options.province.change(); }

                        $(options.city.selector).change();
                    });

                    if (!!options.province.value) {
                        $(options.province.selector).val(options.province.value);
                    }

                    $(options.province.selector).change();
                };

                if (!!self.storage) {
                    callback();
                } else {
                    CORE.ajax.post({
                        url: '/common/geo/all',
                        type: 'POST',
                        contentType: 'application/json',
                        dataType: 'json',
                        cache: true,

                        success: function(result) {
                            self.storage = result.data.storage;
                            callback();
                        },
                    });
                }
            }
        },

        image: {
            uploader: function(element,callback) {
                element = typeof element === 'string' ? $(element) : element;
                element.addClass('thumbnail');
                element.attr('align','center');
                element.css('margin','0px');
                element.css('padding','0px');
                element.css('display','block');
                element.css('line-height',element.css('height'));

                var empty = $('<i class="image-empty fa fa-plus text-muted"></i>');
                var loading = $('<i class="image-loading fa fa-spinner fa-spin text-muted hidden"></i>');

                var img = $('<img style="max-width:95%;max-height:95%;display:inline;"/>');
                var exist = $('<div class="image-exist" style="width:100%;height:100%;font-size:0;"></div>');
                exist.append(img);

                var form = $('<form class="image-form hidden"><input name="scene"><input name="image" type="file"></form>');
                var input = form.find('input[type="file"]');
                input.change(function() {
                    form.find('input[name="scene"]').val(element.data('scene'));
                    var files = input[0].files;

                    if (files.length === 0) {
                        CORE.notify.error('请选择图片');
                        return false;
                    }

                    if (files[0].size > 1024*1024*10) {
                        $('.add-tag-logo input[type="file"]').val('');
                        CORE.notify.error('请选择 10M 以下的图片');
                        return false;
                    }

                    exist.addClass('hidden');
                    empty.addClass('hidden');
                    loading.removeClass('hidden');

                    require(['jquery-form' ],function() {
                        form.ajaxSubmit({
                            url: (CONST.ssl ? 'https':'http') + '://' + CONST.domain.api + '/common/upload/image',
                            type: 'POST',
                            dataType: 'json',

                            beforeSend: function(xhr) {
                                if (!!window.sessionStorage && window.sessionStorage.getItem('debug') === '1') {
                                    xhr.setRequestHeader('X-Debug', '1');
                                }
                            },

                            success: function(result) {
                                if (result.err !== 0) {
                                    if (!img.attr('src')) {
                                        empty.removeClass('hidden');
                                    } else {
                                        exist.removeClass('hidden');
                                    }

                                    CORE.notify.error(result.msg);
                                    return false;
                                }

                                var image = result.data.image;
                                img.attr('src', image.thumbnails[0].url);
                                exist.removeClass('hidden');

                                element.data('image',image);
                                if (!!callback) { callback(image); }

                                CORE.notify.info(result.msg);
                                console.log(result);
                            },

                            error: function(xhr) {
                                if (!img.attr('src')) {
                                    empty.removeClass('hidden');
                                } else {
                                    exist.removeClass('hidden');
                                }
                                CORE.notify.error('上传失败');
                                console.log(xhr);
                            },

                            complete: function() {
                                form.resetForm();
                                loading.addClass('hidden');
                            },
                        });
                    });
                });

                element.append(empty).append(loading).append(exist).append(form);
                if (!!element.data('exist')) {
                    empty.addClass('hidden');
                    img.attr('src',element.data('exist'));
                } else {
                    exist.addClass('hidden');
                }

                element.click(function() {
                    input[0].click();
                });
            }
        },

        video: {
            duration: function(seconds) {
                var hour = Math.floor(seconds/3600);
                var minute = Math.floow((seconds % 3600) / 60);
                var second = seconds % 60;

                var duration_str = '';
                if (hour>0) {
                    duration_str += hour + ':';
                }

                if (minute<10) {
                    duration_str += '0' + minute + ':';
                } else {
                    duration_str += minute + ':';
                }

                if (second<10) {
                    duration_str += '0' + second;
                } else {
                    duration_str += second;
                }

                return duration_str;
            }
        },

        weixin: {
            init: false,
            inside: new RegExp('micromessenger').test(window.navigator.userAgent.toLowerCase()),
            share: function(options) {
                if (CONST.env === 'local') { return; }

                var defaults = {
                    title: $('title').html(),
                    link: window.location.href,
                    imgUrl: CONST.static.url+'images/index/footballzone_icon.png',
                    desc: '我在看 ' + $('title').html() + '，分享给你，快来看！',
                    success: function() { return; },
                    fail: function() { return; },
                    complete: function() { return; },
                    cancel: function() { return; },
                    trigger: function() { return; },
                };

                options = $.extend(defaults,options || {});

                var self = this;
                if (!!self.init) {
                    window.wx.ready(function() {
                        window.wx.onMenuShareTimeline(options);
                        window.wx.onMenuShareAppMessage(options);
                        window.wx.onMenuShareQQ(options);
                        window.wx.onMenuShareQZone(options);
                        window.wx.onMenuShareWeibo(options);
                    });
                } else {
                    if (self.inside) { return; }

                    // load js api module for weixin browser
                    require(['http://res.wx.qq.com/open/js/jweixin-1.1.0.js'], function() {
                        // http://mp.weixin.qq.com/wiki/7/aaa137b55fb2e0456bf8dd9148dd613f.html
                        CORE.ajax.post({
                            url: '/user/oauth/weixin/jsapi',
                            data: {
                                url: window.location.href,
                            },
                            success: function(result) {
                                var config = result.data.config;

                                window.wx.config({
                                    // 开启调试模式,调用的所有api的返回值会在客户端alert出来
                                    //debug: CONST.env=='dev',
                                    debug: false,
                                    appId: CONST.oauth.weixin,
                                    timestamp: config.timestamp,
                                    nonceStr: config.nonceStr,
                                    signature: config.signature,
                                    jsApiList: [
                                        'onMenuShareTimeline',
                                        'onMenuShareAppMessage',
                                        'onMenuShareQQ',
                                        'onMenuShareQZone',
                                        'onMenuShareWeibo',
                                    ],
                                });

                                window.wx.ready(function() {
                                    self.init = true;
                                    window.wx.onMenuShareTimeline(options);
                                    window.wx.onMenuShareAppMessage(options);
                                    window.wx.onMenuShareQQ(options);
                                    window.wx.onMenuShareQZone(options);
                                    window.wx.onMenuShareWeibo(options);
                                });

                                window.wx.error(function(res){
                                    console.log(res);
                                });
                            }
                        });
                    });
                }
            }
        },

        mqtt: {
            client: null,
            config: null,
            last: null,
            reconnect: true,
            log: false,
            topics: {},

            connect: function(options) {
                var self = this;

                require(['paho-mqtt'], function() {
                    var uri = options.uri || '';
                    var host = options.host || '';
                    var port = options.port || 0;
                    var path = options.path || '';
                    var clientid = options.clientid || '';

                    if (!!self.client && self.client.isConnected()) {
                        self.client.disconnect();
                    }

                    if (!!uri) {
                        self.client = new window.Paho.MQTT.Client(uri,clientid);
                    } else {
                        self.client = new window.Paho.MQTT.Client(host,port,path,clientid);
                    }

                    var willMessage = null;
                    if (!!options.will) {
                        willMessage = new window.Paho.MQTT.Message(options.will.payload);
                        willMessage.destinationName = options.will.topic;
                        willMessage.qos = options.will.qos || 0;
                        willMessage.retained = options.will.retained || false;
                    }

                    self.config = {
                        timeout: options.timeout || 15,                         // in seconds
                        keepAliveInterval: options.keepAliveInterval || 60,     // in seconds
                        mqttVersion: options.mqttVersion || 4,                  // 3 for MQTT 3.1,  4 for MQTT 3.1.1
                        cleanSession: options.hasOwnProperty('cleanSession') ? options.cleanSession : true,
                        useSSL: options.useSSL || false,
                        invocationContext: options.context || null,
                        willMessage: willMessage,

                        onSuccess: function(responseObject) {
                            // responseObject = { invocationContext: xxx }
                            if (self.log) { console.log(responseObject); }

                            try {
                                if (!!options.success) { options.success(responseObject); }
                            } catch(e) {
                                console.log(e);
                            }
                        },

                        onFailure: function(responseObject) {
                            // responseObject = { invocationContext: xxx, errorCode: xxx, errorMessage: xxx }
                            if (self.log) { console.log(responseObject); }

                            setTimeout(function() {
                                if (self.reconnect) { self.client.connect($.extend({},self.config)); }
                            },1000*5);

                            try {
                                if (!!options.failure) { options.failure(responseObject); }
                            } catch(e) {
                                console.log(e);
                            }
                        }
                    };

                    if (!!options.username && !!options.password) {
                        $.extend(self.config,{
                            userName: options.username,
                            password: options.password,
                        });
                    }

                    self.client.onConnectionLost = function(responseObject) {
                        self.topics = {};

                        // responseObject = { errorCode: xxx, errorMessage: xxx }
                        if (self.log) { console.log(responseObject); }

                        setTimeout(function() {
                            if (self.reconnect) { self.client.connect($.extend({},self.config)); }
                        },1000*5);

                        try {
                            if (!!options.lost) { options.lost(responseObject); }
                        } catch(e) {
                            console.log(e);
                        }
                    };

                    self.client.onMessageArrived = function(message) {
                        var pako = require('pako');
                        var _message = {
                            destinationName: message.destinationName,
                            //payloadString: pako.inflate(message.payloadBytes, { to: 'string' }),
                            payloadString: message.payloadString,
                            qos: message.qos,
                            retained: message.retained,
                            duplicate: message.duplicate,
                        };

                        self.last = _message;
                        if (self.log) { console.log(_message); }

                        if (self.topics.hasOwnProperty(_message.destinationName)) {
                            try {
                                self.topics[_message.destinationName].arrived(_message);
                            } catch(e) {
                                console.log(e);
                            }
                        }
                    };

                    self.client.onMessageDelivered = function(message) {
                        try {
                            if (!!options.delivered) { options.delivered(message); }
                        } catch(e) {
                            console.log(e);
                        }
                    };

                    self.client.connect($.extend({},self.config));
                });
            },

            subscribe: function(options) {
                var self = this;
                if (!self.client || !self.client.isConnected()) {
                    return false;
                }

                self.client.subscribe(options.topic, {
                    timeout: options.timeout || 5,      // in seconds
                    qos: options.qos || 0,
                    invocationContext: options.context || null,

                    onSuccess: function(responseObject) {
                        self.topics[options.topic] = options;

                        // responseObject = { invocationContext: xxx, grantedQos: xxx }
                        if (self.log) { console.log(responseObject); }

                        try {
                            if (!!options.success) { options.success(responseObject); }
                        } catch(e) {
                            console.log(e);
                        }
                    },

                    onFailure: function(responseObject) {
                        // responseObject = { invocationContext: xxx, errorCode: xxx }
                        if (self.log) { console.log(responseObject); }

                        try {
                            if (!!options.failure) { options.failure(responseObject); }
                        } catch(e) {
                            console.log(e);
                        }
                    }
                });

                return true;
            },

            unsubscribe: function(options) {
                var self = this;
                if (!self.client || !self.client.isConnected()) {
                    return false;
                }

                self.client.unsubscribe(options.topic, {
                    timeout: options.timeout || 5,  // in seconds
                    invocationContext: options.context || null,

                    onSuccess: function(responseObject) {
                        if (self.topics.hasOwnProperty(options.topic)) {
                            delete self.topics[options.topic];
                        }

                        // responseObject = { invocationContext: xxx }
                        if (self.log) { console.log(responseObject); }

                        try {
                            if (!!options.success) { options.success(responseObject); }
                        } catch(e) {
                            console.log(e);
                        }
                    },

                    onFailure: function(responseObject) {
                        // responseObject = { invocationContext: xxx, errorCode: xxx, errorMessage: xxx }
                        if (self.log) { console.log(responseObject); }

                        try {
                            if (!!options.failure) { options.failure(responseObject); }
                        } catch(e) {
                            console.log(e);
                        }
                    }
                });

                return true;
            },

            publish: function(options) {
                var self = this;
                if (!self.client || !self.client.isConnected()) {
                    return false;
                }

                var message = new window.Paho.MQTT.Message(options.payload);
                message.destinationName = options.topic;
                message.qos = options.qos || 0;
                message.retained = options.retained || false;

                self.client.send(message);
                return true;
            },
        }
    };

    window.CORE = CORE;

}(window));



