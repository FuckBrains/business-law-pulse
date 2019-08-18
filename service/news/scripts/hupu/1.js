
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

    setTimeout(function() {
        document.body.scrollTop = 0;
    }, 500);

    var timer = setInterval(function() {
        var node = document.body.getElementsByClassName('m-app-info')[0];
        if (!node) return;
        clearInterval(timer);

        var nodes = ['m-app-info','ui-page-tools'];
        for (var i=0;i<nodes.length;i++) {
            var node = document.getElementsByClassName(nodes[i])[0];
            !!node && node.remove();
        }
    }, 100);

    var node = document.getElementsByClassName('button-returnList')[0];
    if (!!node) {
        node.setAttribute('style','padding-left:15px;');
        node.setAttribute('class','');
    }

    var nodes = ['top-nav-right','down-kanApp'];
    for (var i=0;i<nodes.length;i++) {
        var node = document.getElementsByClassName(nodes[i])[0];
        !!node && node.remove();
    }

}, 100);

})();

