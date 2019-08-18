# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'admin.thrift'), module_name='admin_thrift')
import admin_thrift

from service.admin.models import Admin



class TestProfileService(TestCase):

    def setUp(self):
        self.profile_service = thrift_connect(service=admin_thrift.ProfileService)

    def tearDown(self):
        self.profile_service.close()

    def test_get_digest(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,data=dict(admin=auth.id),auth=auth)
        result = self.profile_service.get_digest(payload)
        self.assertEquals(result.err,0)

    def test_get_detail(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,data=dict(admin=auth.id),auth=auth)
        result = self.profile_service.get_detail(payload)
        self.assertEquals(result.err,0)

    def test_get_multiple(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,data=dict(admins=[auth.id]),auth=auth)
        result = self.profile_service.get_multiple(payload)
        self.assertEquals(result.err,0)
        self.assertEquals(len(result.data['admins']),1)

    def test_update_info(self):
        auth = self.admin_login()

        admin = Admin.objects.filter(id=auth.id).first()
        self.assertNotEquals(admin,None)

        old_realname = admin.realname
        new_realname = '测试'

        payload = Payload(gid=self.gid,data=dict(realname=new_realname),auth=auth)
        result = self.profile_service.update_info(payload)
        self.assertEquals(result.err,0)
        admin.reload()
        self.assertEquals(admin.realname,new_realname)

        payload = Payload(gid=self.gid,data=dict(realname=old_realname),auth=auth)
        result = self.profile_service.update_info(payload)
        self.assertEquals(result.err,0)
        admin.reload()
        self.assertEquals(admin.realname,old_realname)

    def test_update_password(self):
        auth = self.admin_login()

        old_password = self.auth['admin']['password']
        new_password = 'test'

        payload = Payload(gid=self.gid,data=dict(old_password=old_password,new_password=new_password),auth=auth)
        result = self.profile_service.update_password(payload)
        self.assertEquals(result.err,0)

        payload = Payload(gid=self.gid,data=dict(old_password=new_password,new_password=old_password),auth=auth)
        result = self.profile_service.update_password(payload)
        self.assertEquals(result.err,0)


