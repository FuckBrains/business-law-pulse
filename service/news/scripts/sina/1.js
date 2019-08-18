
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

    if (window.location.href == 'http://sports.sina.cn/?vt=4&urlHistory=sports') {
        communicate({ topic: 'webview/close' });
    } else {
        var navigation = document.getElementsByClassName('icon_navigation')[0];
        !!navigation && navigation.remove();

        var user = document.getElementsByClassName('icon_user')[0];
        !!user && user.remove();

        var ad = document.querySelector('div[sax-type="sax_5"]');
        if (!ad) return;
        ad.remove();

        if (window.location.href.indexOf('china') != -1) {
            var figures = document.getElementsByTagName('figure');
            for (var i=0;i<figures.length;i++) {
                if (figures[i].className != 'art_video') {
                    figures[i].remove();
                }
            }
        }

        var timer = setInterval(function() {
            var btn = document.getElementById('pageJumpBtn');
            if (!btn) return;
            btn.remove();

            var comment = document.getElementsByClassName('j_cmnt_bottom')[0];
            !!comment && comment.remove();

            clearInterval(timer);
        }, 1000);
    }

}, 100);

})();

