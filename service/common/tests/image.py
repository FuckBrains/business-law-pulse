# -*- encoding: utf-8 -*-

from core.utils import REDIS
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os,datetime

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestImageService(TestCase):

    def setUp(self):
        self.scene = 'user/avatar'
        self.name = 'qrcode.png'
        self.url = 'http://oss.dev.footballzone.com/static/images/index/qrcode.png'
        self.path = 'images/default/user_avatar.png'

        self.image_service = thrift_connect(service=common_thrift.ImageService)

    def tearDown(self):
        self.image_service.close()

    def test_store(self):
        import requests,tempfile
        response = requests.get(self.url)
        content = tempfile.NamedTemporaryFile()
        for chunk in response.iter_content(chunk_size=1024*512):
            content.write(chunk)

        import uuid
        path = uuid.uuid1().hex + '.' + 'png'
        path = os.path.join('tmp',datetime.datetime.now().strftime('%Y/%m%d/%H%M'), path)

        from core.utils.storage import instantiate_storage
        storage = instantiate_storage()
        save_path = storage.save(content,path,self.name)
        content.close()

        payload = Payload(gid=self.gid,data=dict(scene='user/avatar',path=save_path,name=self.name))
        result = self.image_service.store(payload)
        self.assertEquals(result.err,0)

    def test_download(self):
        payload = Payload(gid=self.gid,data=dict(scene=self.scene,url=self.url))
        result = self.image_service.download(payload)
        self.assertEquals(result.err,0)

    def test_extract(self):
        image_id = ''
        for key in REDIS['cache'].scan_iter('image:*:store'):
            image_id = key.split(':')[1]
            break

        self.assertNotEquals(image_id,'')

        payload = Payload(gid=self.gid,data=dict(id=image_id))
        result = self.image_service.extract(payload)
        self.assertEquals(result.err,0)

    def test_construct(self):
        payload = Payload(gid=self.gid,data=dict(scene=self.scene,path=self.path))
        result = self.image_service.construct(payload)
        self.assertEquals(result.err,0)


