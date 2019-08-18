# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestMqttService(TestCase):

    def setUp(self):
        self.text = 'test'
        self.key = '1234567890123456789012'
        self.mqtt_service = thrift_connect(service=common_thrift.MqttService)

    def tearDown(self):
        self.mqtt_service.close()

    def test_push(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,data=dict(topic='test',body={ 'key': 'value' }),auth=auth)
        result = self.mqtt_service.push(payload)
        self.assertEquals(result.err,0)

    def test_encrypt_and_decrypt(self):
        payload = Payload(gid=self.gid,data=dict(text=self.text,key=self.key))
        result = self.mqtt_service.encrypt(payload)
        self.assertEquals(result.err,0)
        base64_text = result.data['text']

        payload = Payload(gid=self.gid,data=dict(text=base64_text,key=self.key))
        result = self.mqtt_service.decrypt(payload)
        self.assertEquals(result.err,0)
        origin_text = result.data['text']

        self.assertEquals(origin_text,self.text)


