# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestSmsService(TestCase):

    def setUp(self):
        self.scene = 'bind'
        self.cellphone = '18998901440'
        self.account = 'user-1'
        self.device = common_thrift.Device(agent=self.agents['app'],ip='127.0.0.1',port=0)
        #self.device = common_thrift.Device(agent='',ip='127.0.0.1',port=0)
        self.sms_service = thrift_connect(service=common_thrift.SmsService)

    def tearDown(self):
        self.sms_service.close()

    def test_validation(self):
        payload = Payload(gid=self.gid,data=dict(scene=self.scene,cellphone=self.cellphone,account=self.account),device=self.device)
        result = self.sms_service.send_validation(payload)
        self.assertEquals(result.err,0)
        validation = result.data['validation']

        payload = Payload(gid=self.gid,data=dict(scene=self.scene,cellphone=self.cellphone,validation=validation))
        result = self.sms_service.check_validation(payload)
        self.assertEquals(result.err,0)




