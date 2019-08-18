# -*- coding: utf-8 -*-

from core.conf import CONST


CONST.update({
    'node': '0',

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'minsize': 10, 'maxsize': 100 },
        'session': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'minsize': 10, 'maxsize': 100 },
    },

    'require': {
        'cdn': 'http://cdn.bootcss.com/',
        'source': 'http://cdn.bootcss.com/require.js/2.3.4/require.js',
        'config': CONST['static']['url'] + 'common/config.js?_v=' + CONST['static']['cache'],
    },
})

CONST['static']['cache'] = '1.0.1'


