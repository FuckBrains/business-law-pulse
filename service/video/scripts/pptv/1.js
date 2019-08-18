
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

    if (window.location.hostname=='player.aplus.pptv.com') {
        var timer = setInterval(function() {
            var btn = document.getElementsByClassName('p-video-button')[0];
            if (!btn) return;

            btn.style.display = 'block';
            btn.click();

            var video = document.getElementsByTagName('video')[0];
            if (!video || !video.src || video.src=='#') return;
            clearInterval(timer);

            communicate({
                topic: 'video/stream',
                body: {
                    stream: video.src,
                    page: window.location.href
                }
            });
        }, 1000);

    } else {
        var timer = setInterval(function() {
            var iframe = document.getElementById('ifr_player');
            if (!iframe || !iframe.src) return;
            clearInterval(timer);

            document.body.innerHTML = '';
            window.location.href = iframe.src;
        }, 1000);
    }

}, 100);

})();

