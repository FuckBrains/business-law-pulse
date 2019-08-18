# -*- coding: utf-8 -*-

from core.conf import CONST


CONST.update({
    'node': '0',

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'minsize': 10, 'maxsize': 50 },
    },
})

CONST['static']['cache'] = '1.0.0'


