# -*- coding: utf-8 -*-

from core.conf import CONST


CONST.update({
    'node': '0',

    'redis': {
        'cache': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 10 },
        'app': { 'host': 'localhost', 'port': 6379, 'password': 'foobared', 'db': 1, 'maxsize': 10 },
    },

    'mongo': {
        'default': { 'db': 'blp_default', 'host': 'localhost', 'port': 20000, 'username': 'blp', 'password': 'blp', 'maxsize': 10 },
        'primary': { 'db': 'blp_default', 'host': 'localhost', 'port': 20000, 'username': 'blp', 'password': 'blp', 'maxsize': 10 },
    },

    'umeng': {
        'auth': {
            'android': { 'APP_KEY': '574b97c267e58e406b0028f5', 'APP_SECRET': 'qaxtx5umo9lolniixrqv3f1uqvem8tdd' },
            'ios': { 'APP_KEY': '55064389fd98c57c53000653', 'APP_SECRET': 'ovz1vxi5kudujkk4ps1lpnatlfb1rvrp' },
        },
        'production_mode': False,
    },

    'sms': {
        'key_id': 'eSau2EHwOxnz8TFs',
        'key_secret': '3w7auEqmenQPGqLDjQjm9OirYrgOxX',
        'url': 'https://sms.aliyuncs.com/',
        'signname': '足球地带',
        'templatecode': 'SMS_52090122',

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



