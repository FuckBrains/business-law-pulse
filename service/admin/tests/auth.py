# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'admin.thrift'), module_name='admin_thrift')
import admin_thrift


class TestAuthService(TestCase):

    def setUp(self):
        self.auth_service = thrift_connect(service=admin_thrift.AuthService)

    def tearDown(self):
        self.auth_service.close()

    def test_create_token(self):
        admin = self.auth['admin']
        payload = Payload(gid=self.gid,data=dict(email=admin['email'],password=admin['password']),device=admin['device'])
        result = self.auth_service.create_token(payload)
        self.assertEquals(result.err,0)

    def test_validate_token(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,data=dict(id=auth.id, token=auth.token))
        result = self.auth_service.validate_token(payload)
        self.assertEquals(result.err,0)

    def test_destroy_token(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,auth=auth,device=self.auth['admin']['device'])
        result = self.auth_service.destroy_token(payload)
        self.assertEquals(result.err,0)



