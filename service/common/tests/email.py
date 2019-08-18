# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestEmailService(TestCase):

    def setUp(self):
        self.scene = 'bind'
        self.email = '331338391@qq.com'
        self.user = 'Michael'

        self.email_service = thrift_connect(service=common_thrift.EmailService)

    def tearDown(self):
        self.email_service.close()

    def test_validation(self):
        payload = Payload(gid=self.gid,data=dict(scene=self.scene,email=self.email,user=self.user))
        result = self.email_service.send_validation(payload)
        self.assertEquals(result.err,0)

        validation = result.data['validation']

        payload = Payload(gid=self.gid,data=dict(validation=validation))
        result = self.email_service.get_validation(payload)
        self.assertEquals(result.err,0)


