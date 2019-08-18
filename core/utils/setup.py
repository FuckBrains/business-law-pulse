# -*- coding: utf-8 -*-

import os,sys
import importlib


def setup_init(package):
    import signal
    def sigint_handler(signum, frame):
        print('\n########## SIGNAL [ %s ] ##########\n' % signum, flush=True)
        sys.exit(0)

    signal.signal(signal.SIGHUP, sigint_handler)    # SIGHUP = 1
    signal.signal(signal.SIGINT, sigint_handler)    # SIGINT = 2
    signal.signal(signal.SIGTERM, sigint_handler)   # SIGTERM = 15

    module = importlib.import_module(package + '.' + 'conf.const')
    CONST = module.CONST

    module,app = package.split('.')
    filename = os.path.join(CONST['root'], 'log/%s.%s.%s.log' % (module,app,CONST['node']))
    CONST['logging']['handlers']['common'].update({ 'filename': os.path.abspath(filename) })
    from logging.config import dictConfig
    dictConfig(CONST['logging'])


def setup_redis():
    import redis
    from core.conf import CONST
    from core.utils import REDIS
    for key in CONST.get('redis',{}):
        value = CONST['redis'][key]
        pool = redis.ConnectionPool(
                        host=value['host'],port=value['port'],
                        password=value['password'],db=value['db'],
                        max_connections=value['maxsize'],
                        decode_responses=True)
        REDIS[key] = redis.StrictRedis(connection_pool=pool)


def setup_mongo():
    import mongoengine
    from core.conf import CONST
    for key in CONST.get('mongo',{}):
        value = CONST['mongo'][key]
        mongoengine.register_connection(
                        alias=key,
                        name=value['db'], host=value['host'], port=value['port'],
                        username=value['username'], password=value['password'],
                        maxpoolsize=value['maxsize'])



