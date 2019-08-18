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
thriftpy.load(os.path.join(IDL_DIR,'law.thrift'), module_name='law_thrift')
import law_thrift


from core.utils.thrift import ThriftProcessor,ThriftMultiplexedProcessor
processor = ThriftMultiplexedProcessor()


config = {
    'ConfigService': 'service.law.handlers.config.ConfigHandler',
    'ClientService': 'service.law.handlers.client.ClientHandler',
    'FirmService': 'service.law.handlers.firm.FirmHandler',
    'LawyerService': 'service.law.handlers.lawyer.LawyerHandler',
    'DealService': 'service.law.handlers.deal.DealHandler',
    'StatsService': 'service.law.handlers.stats.StatsHandler',
}

import importlib
for key in config:
    path = config[key]
    pkg_name = '.'.join(path.split('.')[:-1])
    cls_name = path.split('.')[-1]
    svc_name = path.split('.')[-2]

    pkg = importlib.import_module(pkg_name)
    cls = getattr(pkg,cls_name)
    svc = getattr(law_thrift,key)

    try:
        processor.register_processor(svc_name, ThriftProcessor(svc,cls()))
    except Exception as exc:
        sys.exit(0)


