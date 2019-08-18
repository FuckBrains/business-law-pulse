# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestUEditorService(TestCase):

    def setUp(self):
        self.ueditor_service = thrift_connect(service=common_thrift.UEditorService)

    def tearDown(self):
        self.ueditor_service.close()

    def test_list_image(self):
        payload = Payload(gid=self.gid,data=dict(page={ 'size': 10, 'no': 1 }))
        result = self.ueditor_service.list_image(payload)
        self.assertEquals(result.err,0)

    def test_list_file(self):
        payload = Payload(gid=self.gid,data=dict(page={ 'size': 10, 'no': 1 }))
        result = self.ueditor_service.list_file(payload)
        self.assertEquals(result.err,0)



