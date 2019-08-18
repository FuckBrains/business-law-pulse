# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestConfigService(TestCase):

    def setUp(self):
        self.config_service = thrift_connect(service=common_thrift.ConfigService)

    def tearDown(self):
        self.config_service.close()

    def test_get_global(self):
        device = common_thrift.Device(agent=self.agents['app'],ip='127.0.0.1',port=0)
        payload = Payload(gid=self.gid,device=device)
        result = self.config_service.get_global(payload)
        self.assertEquals(result.err,0)

    def test_list_market(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,auth=auth)
        result = self.config_service.list_market(payload)
        self.assertEquals(result.err,0)

    def test_update_market(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,auth=auth)
        result = self.config_service.list_market(payload)
        self.assertEquals(result.err,0)
        markets = result.data['markets']
        self.assertNotEquals(len(markets),0)

        appstore = markets[0]
        old_version = appstore['version']
        new_version = '1.0.0'

        appstore['version'] = new_version

        payload = Payload(gid=self.gid,data=dict(markets=markets),auth=auth)
        result = self.config_service.update_market(payload)
        self.assertEquals(result.err,0)
        payload = Payload(gid=self.gid,auth=auth)
        result = self.config_service.list_market(payload)
        self.assertEquals(result.err,0)
        markets = result.data['markets']
        self.assertNotEquals(len(markets),0)
        appstore = markets[0]
        self.assertEquals(appstore['version'],new_version)

        appstore['version'] = old_version

        payload = Payload(gid=self.gid,data=dict(markets=markets),auth=auth)
        result = self.config_service.update_market(payload)
        self.assertEquals(result.err,0)
        payload = Payload(gid=self.gid,auth=auth)
        result = self.config_service.list_market(payload)
        self.assertEquals(result.err,0)
        markets = result.data['markets']
        self.assertNotEquals(len(markets),0)
        appstore = markets[0]
        self.assertEquals(appstore['version'],old_version)


