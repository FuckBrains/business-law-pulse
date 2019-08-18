# -*- coding: utf-8 -*-

import os
from core.conf import CONST


CONST.update({
    'node': '0',

    'auth_private_key': os.path.join(CONST['root'],'service/admin/certs/private.pem'),

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 10 },
        'app': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 10 },
    },

    'mongo': {
        'default': {'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 10},
        'primary': {'db': 'blp_default', 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'maxsize': 10},
    },

    'otp': {
        'cellphone': {
            'register': 60*10,      # 秒
            'retrieve': 60*10,      # 秒
            'bind': 60*10,          # 秒
            'login': 60*10,         # 秒
        },
        'email': {
            'register': 3600*24*7,  # 秒
            'retrieve': 3600*24*7,  # 秒
            'bind': 3600*24*7,      # 秒
            'login': 3600*24,       # 秒
        },
    },
})
