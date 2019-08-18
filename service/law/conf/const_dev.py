# -*- coding: utf-8 -*-

import os
from core.conf import CONST


CONST.update({
    'node': '0',

    'auth_private_key': os.path.join(CONST['root'],'service/admin/certs/private.pem'),

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 20 },
        'app': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 20 },
    },

    'mongo': {
        'default': { 'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 20 },
        'primary': { 'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 20 },
    },
})



