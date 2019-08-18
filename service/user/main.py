# -*- coding: utf-8 -*-

import os,sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.insert(0, root)

from core.utils.setup import setup_init,setup_redis,setup_mongo
setup_init(__package__)
setup_redis()
setup_mongo()


#######################################################################################


import importlib
import thriftpy
from core.utils.thrift import IDL_DIR
thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift


from core.utils.thrift import ThriftProcessor,ThriftMultiplexedProcessor
processor = ThriftMultiplexedProcessor()


config = {
    'AuthService': 'service.user.handlers.auth.AuthHandler',
    'ProfileService': 'service.user.handlers.profile.ProfileHandler',
}

for key in config:
    path = config[key]
    pkg_name = '.'.join(path.split('.')[:-1])
    cls_name = path.split('.')[-1]
    svc_name = path.split('.')[-2]

    pkg = importlib.import_module(pkg_name)
    cls = getattr(pkg,cls_name)
    svc = getattr(user_thrift,key)
    processor.register_processor(svc_name, ThriftProcessor(svc,cls()))
    


