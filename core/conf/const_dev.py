# -*- coding: utf-8 -*-

import os,logging

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))

CONST = {
    'gunicorn': {
        'workers': 1,
        'timeout': 300,
    },

    'code': 'blp',
    'name': 'businesslawpulse',

    'env': 'dev',
    'debug': False,
    'ssl': False,

    'domain': {
        'default': 'blp.liangyongxiong.cn',
        'oss': 'oss.blp.liangyongxiong.cn',
        'api': 'api.blp.liangyongxiong.cn',
        'www': 'www.blp.liangyongxiong.cn',
    },

    'root': ROOT,

    'static': {
        'base': os.path.join(ROOT, 'static'),
        'url': 'http://oss.blp.liangyongxiong.cn/static/',
        'cache': '1.0.1',
    },

    'media': {
        'base': os.path.join(ROOT, 'media'),
        'url': 'http://oss.blp.liangyongxiong.cn/media/',
        'storage': 'core.utils.storage.LocalStorage',
    },

    'certificate': {
        'local': { 'private': '', 'public': '' },
        'remove': { 'website': {}, 'service': {} },
    },

    'auth_public_key': os.path.join(ROOT,'core/certs/public.pem'),

    'thrift': {
        'common_thrift': {
            'host': 'localhost',
            'port': 9000,
            'service': {
                'ConfigService': { 'multiplex': 'config' },
                'ImageService': { 'multiplex': 'image' },
                'FileService': { 'multiplex': 'file' },
                'GeoService': { 'multiplex': 'geo' },
                'PushService': { 'multiplex': 'push' },
                'MqttService': { 'multiplex': 'mqtt' },
                'SmsService': { 'multiplex': 'sms' },
                'EmailService': { 'multiplex': 'email' },
                'UEditorService': { 'multiplex': 'ueditor' },
                'FeedbackService': { 'multiplex': 'feedback' },
                'DocService': { 'multiplex': 'doc' },
            },
        },

        'admin_thrift': {
            'host': 'localhost',
            'port': 9020,
            'service': {
                'AuthService': { 'multiplex': 'auth' },
                'ProfileService': { 'multiplex': 'profile' },
            },
        },

        'user_thrift': {
            'host': 'localhost',
            'port': 9010,
            'service': {
                'AuthService': { 'multiplex': 'auth' },
                'ProfileService': { 'multiplex': 'profile' },
            },
        },

        'news_thrift': {
            'host': 'localhost',
            'port': 9040,
            'service': {
                'CrawlService': {'multiplex': 'crawl'},
                'EditService': {'multiplex': 'edit'},
                'NewsService': {'multiplex': 'news'},
            },
        },

        'video_thrift': {
            'host': 'localhost',
            'port': 9050,
            'service': {
                'VideoService': {'multiplex': 'video'},
            },
        },

        'law_thrift': {
            'host': 'localhost',
            'port': 9060,
            'service': {
                'ConfigService': {'multiplex': 'config'},
                'ClientService': {'multiplex': 'client'},
                'FirmService': {'multiplex': 'firm'},
                'LawyerService': {'multiplex': 'lawyer'},
                'DealService': {'multiplex': 'deal'},
                'StatsService': {'multiplex': 'stats'},
            },
        },
    },

    'oauth': {
        'qq': {
            'app': { 'id': '', 'secret': '' },
            'web': { 'id': '', 'secret': '' },
        },
        'weixin': {
            'app': { 'id': '', 'secret': '' },
            'web': { 'id': '', 'secret': '' },
            'mp': { 'id': '', 'secret': '' },
        },
        'weibo': {
            'app': { 'id': '', 'secret': '' },
        },
    },

    'proxies': {
        'default': {
            'http': { 'host': 'localhost', 'port': 3128 },
            'https': { 'host': 'localhost', 'port': 3128 },
            'socks5': { 'host': 'localhost', 'port': 1080 },
        },
        '7m': {
            'http': { 'host': '7m.proxy.fbz', 'port': 3128 },
        },
    },

    'oss': {
        'host': 'oss-cn-shenzhen.aliyuncs.com',
        'bucket': 'businesslawpulse',
        'key_id': '',
        'key_secret': '',
        'cache_age': 60*60*24*30,   # 30 days
    },

    'mqtt': {
        'admin': {
            'host': 'mqtt.blp.liangyongxiong.cn',
            'port': 1885,   # tcp
            'username': 'businesslawpulse/admin',
            'password': 'admin',
            'ssl': False,
        },
        'app': {
            'host': 'mqtt.blp.liangyongxiong.cn',
            'port': 1883,   # tcp
            'username': 'businesslawpulse/app',
            'password': 'app',
            'ssl': False,
        },
        'web': {
            'host': 'mqtt.blp.liangyongxiong.cn',
            'port': 8883,   # ws
            'username': 'businesslawpulse/web',
            'password': 'web',
            'ssl': False,
        },
    },

    'test': {
        'admin': { 'email': '331338391@qq.com', 'password': '123456' },
        'user': { 'cellphone': '18998901440', 'password': '123456' },
    },

    'timezone': 'Asia/Shanghai',

    'logging': {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'verbose': { 'format': '[%(asctime)s] [%(process)d %(thread)d] [%(levelname)s] %(message)s' },
            'simple': { 'format': '[%(asctime)s] [%(levelname)s] %(message)s' }
        },

        'handlers': {
            'null': {
                'level': logging.DEBUG,
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': logging.DEBUG,
                'formatter': 'simple',
                'class': 'logging.StreamHandler',
            },
            'syslog': {
                'level': logging.DEBUG,
                'formatter': 'simple',
                'class': 'logging.handlers.SysLogHandler',
                'facility': 'local7',
                'address': '/dev/log',
            },
            'common': {
                'level': logging.DEBUG,
                'formatter': 'simple',
                'class': 'logging.handlers.WatchedFileHandler',
                'encoding': 'utf8',
                'filename': 'log/common.log',
            },
        },

        'loggers': {
            'aiohttp.server': { 'handlers': ['console','common'], 'level': logging.INFO, 'propagate': False },
            'thriftpy': { 'handlers': ['console','common'], 'level': logging.INFO, 'propagate': False },
            'command': { 'handlers': ['console','common'], 'level': logging.INFO, 'propagate': False },
        },
    },
}
