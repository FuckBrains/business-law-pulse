
(function() {
    var HYBRID = {
        communicate: function(message) {
            var user_agent = window.navigator.userAgent.toLowerCase();

            if (new RegExp(['android'].join('|')).test(user_agent)) {
                if (!window.BRIDGE) { return false; }
                window.BRIDGE.communicate(JSON.stringify(message));
            } else if (new RegExp(['iphone','ipad','ipod'].join('|')).test(user_agent)) {
                if (!window.webkit || !window.webkit.messageHandlers || !window.webkit.messageHandlers.BRIDGE) { return false; }
                window.webkit.messageHandlers.BRIDGE.postMessage(message);
            } else {
                return false;
            }

            return true;
        },

        comment: {},
        callback: {},
    };

    window.HYBRID = HYBRID;

}(window));


