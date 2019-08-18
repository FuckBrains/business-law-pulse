# -*- encoding: utf-8 -*-

from core.utils import REDIS
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.test import TestCase

import os,datetime

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class TestFileService(TestCase):

    def setUp(self):
        self.name = 'qrcode.png'
        self.url = 'http://oss.dev.footballzone.com/static/files/index/qrcode.png'
        self.path = 'files/default/user_avatar.png'

        self.file_service = thrift_connect(service=common_thrift.FileService)

    def tearDown(self):
        self.file_service.close()

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

        payload = Payload(gid=self.gid,data=dict(path=save_path,name=self.name))
        result = self.file_service.store(payload)
        self.assertEquals(result.err,0)

    def test_extract(self):
        file_id = ''
        for key in REDIS['cache'].scan_iter('file:*:store'):
            file_id = key.split(':')[1]
            break

        self.assertNotEquals(file_id,'')

        payload = Payload(gid=self.gid,data=dict(id=file_id))
        result = self.file_service.extract(payload)
        self.assertEquals(result.err,0)



