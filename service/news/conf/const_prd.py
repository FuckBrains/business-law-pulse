# -*- coding: utf-8 -*-

from core.conf.const import CONST

CONST.update({
    'node': '0',

    'redis': {
        'cache': {'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 50},
        'app': {'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 50},
    },

    'mongo': {
        'edit': {'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 50},
        'edit-primary': {'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 50},

        'crawl': {'db': 'blp_crawl', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 50},
        'crawl-primary': {'db': 'blp_crawl', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 50},
    },
})


