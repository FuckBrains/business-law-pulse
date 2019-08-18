# -*- encoding: utf-8 -*-

from core.conf import CONST
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect

import os
import unittest

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

thriftpy.load(os.path.join(IDL_DIR,'admin.thrift'), module_name='admin_thrift')
import admin_thrift

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift



class TestCase(unittest.TestCase):
    def __init__(self, methodName='thriftTest'):
        self.agents = {
            'pc': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'm': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
            'app': 'footballzone/1.0.0 (iPhone 6s; iOS 10.3.2; Scale/2) AFNetworking/3.0 Market/AppStore NetType/WiFi Language/zh-Hans-CN',
        }

        self.auth = {
            'admin': {
                'device': common_thrift.Device(agent=self.agents['pc'],ip='127.0.0.1',port=0),
                'email': CONST['test']['admin']['email'],
                'password': CONST['test']['admin']['password']
            },
            'user': {
                'device': common_thrift.Device(agent=self.agents['pc'],ip='127.0.0.1',port=0),
                'cellphone': CONST['test']['user']['cellphone'],
                'password': CONST['test']['user']['password']
            },
        }

        self.gid = 'testcase'

    def admin_login(self,email=None,password=None,device=None):
        email = email or self.auth['admin']['email']
        password = password or self.auth['admin']['password']
        device = device or self.auth['admin']['device']
        payload = Payload(gid=self.gid,data=dict(email=email,password=password),device=device)

        auth_service = thrift_connect(service=admin_thrift.AuthService)
        result = auth_service.create_token(payload)
        auth_service.close()
        self.assertEquals(result.err,0)

        admin = result.data['admin']
        return common_thrift.Auth(type='admin',id=admin['id'],token=admin['token'])

    def user_login(self,cellphone=None,password=None,device=None):
        cellphone = cellphone or self.auth['user']['cellphone']
        password = password or self.auth['user']['password']
        device = device or self.auth['user']['device']
        payload = Payload(gid=self.gid,data=dict(type='account',account=cellphone,password=password),device=device)

        auth_service = thrift_connect(service=user_thrift.AuthService)
        result = auth_service.create_token(payload)
        auth_service.close()
        self.assertEquals(result.err,0)

        user = result.data['user']
        return common_thrift.Auth(type='user',id=user['id'],token=user['token'])


