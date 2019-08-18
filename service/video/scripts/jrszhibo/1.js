
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

    setTimeout(function() {
        var iframe = document.getElementsByTagName('iframe')[0];
        if (!!iframe) {
            document.body.innerHTML = '';
            window.location.href = iframe.src;
        } else {
            var timer = setInterval(function() {
                var video = document.getElementsByTagName('video')[0];
                if (!video || !video.src || video.src=='#') return;
                clearInterval(timer);

                communicate({
                    topic: 'video/stream',
                    body: {
                        stream: video.src
                    }
                });
            }, 100);
        }
    }, 500);

}, 100);

})();

