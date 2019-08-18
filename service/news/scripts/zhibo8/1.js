
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
        var ad = document.getElementById('m_adv');
        if (!ad) return;
        ad.remove();

        var right = document.getElementsByClassName('float_right')[0];
        !!right && right.remove();

        var download = document.querySelector('a[href="http://m.zhibo8.cc/download/"]');
        !!download && download.remove();

        var login = document.getElementById('logindiv');
        !!login && login.remove();

        var info = document.getElementById('nouserinfo');
        !!info && info.remove();

        document.body.style.marginTop = 0;

        clearInterval(timer);
    }, 100);

}, 100);

})();


