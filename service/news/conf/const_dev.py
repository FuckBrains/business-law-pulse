# -*- coding: utf-8 -*-

from core.conf.const import CONST

CONST.update({
    'node': '0',

    'redis': {
        'cache': {'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 20},
        'app': {'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 20},
    },

    'mongo': {
        'edit': {'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 20},
        'edit-primary': {'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 20},

        'crawl': {'db': 'blp_crawl', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 20},
        'crawl-primary': {'db': 'blp_crawl', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 20},
    },
})


