# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestGeoService(TestCase):

    def setUp(self):
        self.geo_service = thrift_connect(service=common_thrift.GeoService)

    def tearDown(self):
        self.geo_service.close()

    def test_get_globe(self):
        payload = Payload(gid=self.gid)
        result = self.geo_service.get_globe(payload)
        self.assertEquals(result.err,0)

    def test_get_nation(self):
        payload = Payload(gid=self.gid)
        result = self.geo_service.get_nation(payload)
        self.assertEquals(result.err,0)

    def test_parse(self):
        payload = Payload(gid=self.gid,data=dict(province='广东',city='深圳'))
        result = self.geo_service.parse(payload)
        self.assertEquals(result.err,0)



