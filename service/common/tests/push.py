# -*- encoding: utf-8 -*-

from core.utils import REDIS
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestPushService(TestCase):

    def setUp(self):
        self.title = 'Title'
        self.content = 'Content'
        self.url = 'https://www.baidu.com/'
        self.device = 'android'
        self.token = 'abcdefghijklmnopqrstnvwxyz'

        self.push_service = thrift_connect(service=common_thrift.PushService)

    def tearDown(self):
        self.push_service.close()

    def test_unicast(self):
        data = dict(title=self.title,content=self.content,url=self.url,device=self.device,token=self.token)
        payload = Payload(gid=self.gid,data=data)
        result = self.push_service.unicast(payload)
        self.assertEquals(result.err,0)

    def test_listcast(self):
        data = dict(title=self.title,content=self.content,url=self.url,device=self.device,tokens=[self.token])
        payload = Payload(gid=self.gid,data=data)
        result = self.push_service.listcast(payload)
        self.assertEquals(result.err,0)

    def test_broadcast(self):
        REDIS['app'].delete('push:broadcast:info:device:%s:url:%s' % (self.device,self.url))

        data = dict(title=self.title,content=self.content,url=self.url,device=self.device)
        payload = Payload(gid=self.gid,data=data)
        result = self.push_service.broadcast(payload)
        self.assertEquals(result.err,0)



