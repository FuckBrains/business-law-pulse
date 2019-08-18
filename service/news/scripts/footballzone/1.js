
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

    var timer = setInterval(function() {
        var content = document.getElementsByClassName('article-content')[0];
        if (!content) return;
        clearInterval(timer);

        var nodes = content.getElementsByTagName('a');
        for (var i=0;i<nodes.length;i++) {
            var node = nodes[i];
            if (!node.href || new RegExp('^javascript').test(node.href)) return;
            node.target = '_self';
            node.onclick = function(event) {
                communicate({
                    topic: 'common/navigate',
                    body: {
                        url: this.href,
                        target: 'new'
                    }
                });
                return false;
            };
        }
    }, 100);
}, 100);

})();

