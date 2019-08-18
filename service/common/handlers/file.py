# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.thrift import ThriftHandler,Result
from core.utils.thrift import thrift_exempt

import os,json,datetime,uuid

import requests
requests.packages.urllib3.disable_warnings()



class FileHandler(ThriftHandler):
    storage = None

    def __init__(self):
        super(FileHandler, self).__init__()
        from core.utils.storage import instantiate_storage
        self.storage = instantiate_storage()

    def store(self,request):
        path = request.data['path']
        name = request.data.get('name','')

        content = self.storage.open(path)
        file_info = self.save(content,name)
        self.storage.delete(path)

        REDIS['cache'].set('file:%s:store' % file_info['id'], json.dumps(file_info), ex=60*60*1)
        return Result(data={ 'file': file_info })

    def extract(self,request):
        file_id = request.data['id']
        file_info = json.loads(REDIS['cache'].get('file:%s:store' % file_id))
        return Result(data={ 'file': file_info })

    @thrift_exempt
    def save(self,content,name):
        _, ext = os.path.splitext(name)
        ext = ext[1:].lower()
        origin_path = uuid.uuid1().hex + '.' + ext
        origin_path = os.path.join('attachment',datetime.datetime.now().strftime('%Y/%m%d/%H%M'), origin_path)

        path = self.storage.save(content,origin_path,name)

        file = {
            'id': uuid.uuid1().hex,
            'name': name,
            'url': self.storage.url(path),
            'size': self.storage.size(path),
            'created': int(datetime.datetime.now().timestamp()*1000),
        }

        content.close()
        return file



