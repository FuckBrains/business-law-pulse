
(function() {

var ua = window.navigator.userAgent.toLowerCase();
if (new RegExp('android').test(ua)) {
    if (!document.body.innerHTML || !!window.injected) return;
} else if (new RegExp(['iphone','ipad','ipod'].join('|')).test(ua)) {
    if (!!window.injected) return;
}

window.injected = true;

clearInterval(window.timer);
window.timer = setInterval(function() {
    if (!document.body) return;
    clearInterval(window.timer);

    var meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0';
    document.getElementsByTagName('head')[0].appendChild(meta);

    var communicate = function(message) {
        var ua = window.navigator.userAgent.toLowerCase();
        if (new RegExp('android').test(ua)) {
            BRIDGE.communicate(JSON.stringify(message));
        } else if (new RegExp(['iphone','ipad','ipod'].join('|')).test(ua)) {
            window.webkit.messageHandlers.BRIDGE.postMessage(message);
        }
    };

    window.ajax_callback = function(content) {
        if (new RegExp('<video.+video>').test(content)) {
            document.body.innerHTML = new RegExp('<video.+video>').exec(content)[0];
            var video = document.getElementsByTagName('video')[0];

            communicate({
                topic: 'video/stream',
                body: {
                    stream: video.src
                }
            });

        } else if (new RegExp('<iframe.+iframe>').test(content)) {
            document.body.innerHTML = new RegExp('<iframe.+iframe>').exec(content)[0];
            var iframe = document.getElementsByTagName('iframe')[0];
            iframe.width = window.innerWidth;
            iframe.height = window.innerHeight;

            /*
            if (new RegExp('^http://minisite.letv.com/').test(iframe.src)) {
                document.body.innerHTML = '';
                communicate({
                    topic: 'common/navigate',
                    body: {
                        url: iframe.src,
                        target: 'self',
                    }
                });
                return;
            }
            */

            communicate({
                topic: 'common/ajax',
                body: {
                    type: 'GET',
                    url: iframe.src,
                    headers: {
                        'referer': window.location.href,
                        'user-agent': window.navigator.userAgent
                    },
                    callback: 'ajax_callback'
                }
            });
        }
    };

    var timer = setInterval(function() {
        var iframe = document.getElementsByTagName('iframe')[0];
        if (!iframe || !iframe.src) return;
        clearInterval(timer);

        var content = new RegExp('<iframe.+iframe>').exec(document.body.innerHTML)[0];
        window.ajax_callback(content);
    }, 100);

}, 100);

})();

