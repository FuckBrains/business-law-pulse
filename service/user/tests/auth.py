# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift

from service.user.models import User



class TestAuthService(TestCase):

    def setUp(self):
        self.auth_service = thrift_connect(service=user_thrift.AuthService)

    def tearDown(self):
        self.auth_service.close()

    def test_create_token(self):
        user = self.auth['user']
        payload = Payload(gid=self.gid,data=dict(type='account',account=user['cellphone'],password=user['password']),device=user['device'])
        result = self.auth_service.create_token(payload)
        self.assertEquals(result.err,0)

    def test_validate_token(self):
        auth = self.user_login()
        payload = Payload(gid=self.gid,data=dict(id=auth.id, token=auth.token))
        result = self.auth_service.validate_token(payload)
        self.assertEquals(result.err,0)

    def test_destroy_token(self):
        auth = self.user_login()
        payload = Payload(gid=self.gid,auth=auth,device=self.auth['user']['device'])
        result = self.auth_service.destroy_token(payload)
        self.assertEquals(result.err,0)

    def test_access_token(self):
        self.assertEquals(0,0)




