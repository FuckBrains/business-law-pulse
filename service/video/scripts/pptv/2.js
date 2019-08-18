
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
        var btn = document.getElementsByClassName('p-video-button')[0];
        if (!btn) return;
        clearInterval(timer);

        btn.style.display = 'block';
        btn.click();
    }, 100);

}, 100);

})();

