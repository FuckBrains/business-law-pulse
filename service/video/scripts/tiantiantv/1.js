
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

    var communicate = function(message) {
        var ua = window.navigator.userAgent.toLowerCase();
        if (new RegExp('android').test(ua)) {
            BRIDGE.communicate(JSON.stringify(message));
        } else if (new RegExp(['iphone','ipad','ipod'].join('|')).test(ua)) {
            window.webkit.messageHandlers.BRIDGE.postMessage(message);
        }
    };

    if (new RegExp('^/player/ck/ck.php').test(window.location.pathname)) {
        var ahead = document.getElementsByClassName('ahead')[0];
        !!ahead && ahead.remove();

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

    } else if (new RegExp('^/channel/.+').test(window.location.pathname)) {
        var timer = setInterval(function() {
            var iframe = document.getElementsByTagName('iframe')[0];
            if (!iframe || !iframe.src) return;
            clearInterval(timer);

            document.body.innerHTML = '';
            window.location.href = iframe.src;
        }, 100);
    }

}, 100);

})();

