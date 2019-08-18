# -*- coding: utf-8 -*-

from core.conf import CONST


CONST.update({
    'node': '0',

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'minsize': 10, 'maxsize': 20 },
        'session': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'minsize': 10, 'maxsize': 20 },
    },

    'require': {
        'cdn': CONST['static']['url'] + 'vendor/',
        'source': CONST['static']['url'] + 'vendor/require.js/2.3.4/require.js',
        'config': CONST['static']['url'] + 'common/config.js?_v=' + CONST['static']['cache'],
    },
})

CONST['static']['cache'] = '1.0.3'


