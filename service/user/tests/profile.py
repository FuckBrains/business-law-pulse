# -*- encoding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift

from service.user.models import User



class TestProfileService(TestCase):

    def setUp(self):
        self.profile_service = thrift_connect(service=user_thrift.ProfileService)

    def tearDown(self):
        self.profile_service.close()

    def test_filter(self):
        auth = self.admin_login()
        payload = Payload(gid=self.gid,data=dict(keyword='18998901440'),auth=auth)
        result = self.profile_service.filter(payload)
        self.assertEquals(result.err,0)

    def test_get_digest(self):
        user = User.objects.all().first()
        payload = Payload(gid=self.gid,data=dict(user=str(user.id)))
        result = self.profile_service.get_digest(payload)
        self.assertEquals(result.err,0)

    def test_get_detail(self):
        auth = self.user_login()
        payload = Payload(gid=self.gid,data=dict(user=str(auth.id)),auth=auth)
        result = self.profile_service.get_detail(payload)
        self.assertEquals(result.err,0)

    def test_get_multiple(self):
        user = User.objects.all().first()
        payload = Payload(gid=self.gid,data=dict(users=[str(user.id)]))
        result = self.profile_service.get_multiple(payload)
        self.assertEquals(result.err,0)
        self.assertEquals(len(result.data['users']),1)

    def test_update_info(self):
        auth = self.user_login()

        user = User.objects.filter(id=auth.id).first()
        self.assertNotEquals(user,None)

        old_gender = user.gender
        new_gender = 'F'

        payload = Payload(gid=self.gid,data=dict(gender=new_gender),auth=auth)
        result = self.profile_service.update_info(payload)
        self.assertEquals(result.err,0)
        user.reload()
        self.assertEquals(user.gender,new_gender)

        payload = Payload(gid=self.gid,data=dict(gender=old_gender),auth=auth)
        result = self.profile_service.update_info(payload)
        self.assertEquals(result.err,0)
        user.reload()
        self.assertEquals(user.gender,old_gender)

    def test_update_password(self):
        auth = self.user_login()

        old_password = self.auth['user']['password']
        new_password = 'helloworld'

        payload = Payload(gid=self.gid,data=dict(old_password=old_password,new_password=new_password),auth=auth)
        result = self.profile_service.update_password(payload)
        self.assertEquals(result.err,0)

        payload = Payload(gid=self.gid,data=dict(old_password=new_password,new_password=old_password),auth=auth)
        result = self.profile_service.update_password(payload)
        self.assertEquals(result.err,0)

    def test_update_bind(self):
        auth = self.user_login()

        user = User.objects.filter(id=auth.id).first()
        old_cellphone = user.cellphone
        new_cellphone = '18998901441'

        payload = Payload(gid=self.gid,data=dict(cellphone=new_cellphone),auth=auth)
        result = self.profile_service.update_bind(payload)
        self.assertEquals(result.err,0)
        user.reload()
        self.assertEquals(user.cellphone,new_cellphone)

        payload = Payload(gid=self.gid,data=dict(cellphone=old_cellphone),auth=auth)
        result = self.profile_service.update_bind(payload)
        self.assertEquals(result.err,0)
        user.reload()
        self.assertEquals(user.cellphone,old_cellphone)

    def test_update_status(self):
        auth = self.admin_login()

        user = User.objects.all().first()
        old_status = user.status
        new_status = 0

        payload = Payload(gid=self.gid,data=dict(user=str(user.id),status=new_status),auth=auth)
        result = self.profile_service.update_status(payload)
        self.assertEquals(result.err,0)
        user.reload()
        self.assertEquals(user.status,new_status)

        payload = Payload(gid=self.gid,data=dict(user=str(user.id),status=old_status),auth=auth)
        result = self.profile_service.update_status(payload)
        self.assertEquals(result.err,0)
        user.reload()
        self.assertEquals(user.status,old_status)



