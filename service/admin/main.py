# -*- coding: utf-8 -*-

import os,sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.insert(0, root)

from core.utils.setup import setup_init,setup_redis,setup_mongo
setup_init(__package__)
setup_redis()
setup_mongo()


#######################################################################################


import thriftpy
from core.utils.thrift import IDL_DIR
thriftpy.load(os.path.join(IDL_DIR,'admin.thrift'), module_name='admin_thrift')
import admin_thrift


from core.utils.thrift import ThriftProcessor,ThriftMultiplexedProcessor
processor = ThriftMultiplexedProcessor()


config = {
    'AuthService': 'service.admin.handlers.auth.AuthHandler',
    'ProfileService': 'service.admin.handlers.profile.ProfileHandler',
}

import importlib
for key in config:
    path = config[key]
    pkg_name = '.'.join(path.split('.')[:-1])
    cls_name = path.split('.')[-1]
    svc_name = path.split('.')[-2]

    pkg = importlib.import_module(pkg_name)
    cls = getattr(pkg,cls_name)
    svc = getattr(admin_thrift,key)

    try:
        processor.register_processor(svc_name, ThriftProcessor(svc,cls()))
    except Exception as exc:
        sys.exit(0)


