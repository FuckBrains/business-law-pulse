# -*- coding: utf-8 -*-

from core.conf import CONST


CONST.update({
    'node': '0',

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 20 },
        'app': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 20 },
    },

    'mongo': {
        'default': { 'db': 'blp_default', 'host': 'localhost', 'port': 20000, 'username': 'blp', 'password': 'blp', 'maxsize': 20 },
        'primary': { 'db': 'blp_default', 'host': 'localhost', 'port': 20000, 'username': 'blp', 'password': 'blp', 'maxsize': 20 },
    },

    'umeng': {
        'auth': {
            'android': { 'APP_KEY': '', 'APP_SECRET': '' },
            'ios': { 'APP_KEY': '', 'APP_SECRET': '' },
        },
        'production_mode': False,
    },

    'sms': {
        'key_id': '',
        'key_secret': '',
        'url': 'https://sms.aliyuncs.com/',
        'signname': '',
        'templatecode': '',

        'limit': {
            'cellphone': { 'count': 3, 'duration': 60 },
            'account': { 'count': 3, 'duration': 60 },
            'ip': { 'count': 100, 'duration': 60 },
        },
    },

    'email': {
        'service': {
            'smtp': 'smtp.exmail.qq.com',
            'username': 'service@footballzone.com',
            'password': 'Fbz2507',
            'display': '足球地带',
        },
    },
})



