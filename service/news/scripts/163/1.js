
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

    var nodes = ['sub-box','js-wakeupclient','js-share','u-layer-newsapp'];
    for (var i=0;i<nodes.length;i++) {
        var node = document.getElementsByClassName(nodes[i])[0];
        !!node && node.remove();
    }

}, 100);

})();

