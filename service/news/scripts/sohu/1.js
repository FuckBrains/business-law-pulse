
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

    var timer = setInterval(function() {
        var body = document.body.innerHTML;
        if (!body) return;

        var icon = document.getElementsByClassName('sprite-icons-back')[0];
        !!icon && icon.remove();

        var banner = document.getElementById('ceans_12448');
        !!banner && banner.remove();

        var wrappers = document.getElementsByClassName('media-wrapper');
        for (var i=0;i<wrappers.length;i++) {
            wrappers[i].remove();
        }

        clearInterval(timer);
    }, 100);
}, 100);

})();

