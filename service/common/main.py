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
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift


from core.utils.thrift import ThriftProcessor,ThriftMultiplexedProcessor
processor = ThriftMultiplexedProcessor()


config = {
    'ConfigService': 'service.common.handlers.config.ConfigHandler',
    'ImageService': 'service.common.handlers.image.ImageHandler',
    'FileService': 'service.common.handlers.file.FileHandler',
    'GeoService': 'service.common.handlers.geo.GeoHandler',
    'PushService': 'service.common.handlers.push.PushHandler',
    'MqttService': 'service.common.handlers.mqtt.MqttHandler',
    'SmsService': 'service.common.handlers.sms.SmsHandler',
    'EmailService': 'service.common.handlers.email.EmailHandler',
    'OAuthService': 'service.common.handlers.oauth.OAuthHandler',
    'UEditorService': 'service.common.handlers.ueditor.UEditorHandler',
    'DocService': 'service.common.handlers.doc.DocHandler',
}

for key in config:
    path = config[key]
    pkg_name = '.'.join(path.split('.')[:-1])
    cls_name = path.split('.')[-1]
    svc_name = path.split('.')[-2]

    pkg = importlib.import_module(pkg_name)
    cls = getattr(pkg,cls_name)
    svc = getattr(common_thrift,key)
    processor.register_processor(svc_name, ThriftProcessor(svc,cls()))



