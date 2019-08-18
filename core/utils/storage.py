# -*- coding: utf-8 -*-

import os,time
import random,importlib,tempfile
from urllib.parse import quote

import logging
logger = logging.getLogger('thriftpy')

from core.conf import CONST

from core.utils.exceptions import BizException



def instantiate_storage():
    segs = CONST['media']['storage'].split('.')
    module_path = '.'.join(segs[:-1])
    class_name = segs[-1]
    storage = getattr(importlib.import_module(module_path),class_name)
    return storage()


class LocalStorage:
    def save(self, content, name, origin=''):
        saved_name = self.get_available_name(name)

        access_name = self.path(saved_name)
        dir_name = os.path.dirname(access_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        def chuncks(content,chunk_size=1024*512):
            content.seek(0)
            while True:
                data = content.read(chunk_size)
                if not data:
                    break
                yield data

        with open(access_name,'wb') as fp:
            for chunk in chuncks(content):
                fp.write(chunk)

        return saved_name

    def path(self, name):
        if not os.path.exists(CONST['media']['base']):
            raise BizException('media base not exists')

        return os.path.join(CONST['media']['base'],name)

    def url(self, name):
        if name.startswith('http'):
            return name
        elif name.startswith('images'):
            return CONST['static']['url'] + name

        return CONST['media']['url'] + name

    def exists(self, name):
        return os.path.exists(self.path(name))

    def size(self, name):
        if not self.exists(name):
            return 0

        return os.path.getsize(self.path(name))

    def open(self, name):
        if not self.exists(name):
            return None

        def chunks(fp, chunk_size=1024*512):
            while True:
                data = fp.read(chunk_size)
                if not data:
                    break
                yield data

        content = tempfile.NamedTemporaryFile()
        with open(self.path(name),'rb') as fp:
            for chunk in chunks(fp):
                content.write(chunk)

        return content

    def delete(self, name):
        if not self.exists(name):
            return

        os.remove(self.path(name))

    def get_available_name(self, name, max_length=None):
        (dir_name, file_name) = os.path.split(name)
        (file_root, file_ext) = os.path.splitext(file_name)

        random.seed(time.time())
        while self.exists(name):
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            random_string = ''.join([random.choice(chars) for i in range(0,8)])
            name= os.path.join(dir_name, "%s_%s%s" % (file_root, random_string, file_ext))

        return name


class AliyunStorage:
    def __init__(self):
        import oss2
        self.config = CONST['oss']
        auth = oss2.Auth(self.config['key_id'],self.config['key_secret'])
        self.bucket = oss2.Bucket(auth, 'http://%s' % self.config['host'], self.config['bucket'])

    def save(self, content, name, origin=''):
        filename = quote(origin or os.path.basename(name), safe='?!@#$&()[]/\\+-*=_.:,;~%\'"')
        headers = {
            'Cache-Control': 'max-age=%d' % self.config['cache_age'],
            'Content-Disposition': 'inline;filename=%s' % filename,
            #'Content-Disposition': 'attachment;filename=%s' % filename,
        }

        saved_name = self.get_available_name(name)

        # 当无法确定待上传的数据长度时，progress_callback的第二个参数（total_bytes）为None
        percentage = 0
        def callback(consumed_bytes, total_bytes):
            if total_bytes:
                percentage = int((float(consumed_bytes)/float(total_bytes))*100)

        content.seek(0)
        access_name = self.path(saved_name)
        res = self.bucket.put_object(access_name,content,headers=headers,progress_callback=callback)
        if res.status != 200:
            message = ''.join([seg.decode('utf8') for seg in res.readlines()])
            raise BizException(message)

        return saved_name

    def path(self, name):
        return os.path.join('media',name)

    def url(self, name):
        if name.startswith('http'):
            return name
        elif name.startswith('images'):
            return CONST['static']['url'] + name

        return CONST['media']['url'] + name

    def exists(self, name):
        flag = self.bucket.object_exists(self.path(name))
        return flag

    def size(self, name):
        res = self.bucket.head_object(self.path(name))
        headers = dict([item for item in res.headers.raw_items()])
        return int(headers.get('Content-Length','0'))

    def open(self, name):
        name = os.path.join('media',name)
        res = self.bucket.get_object(name)

        content = tempfile.NamedTemporaryFile()
        content.write(res.read())
        content.seek(0)
        return content

    def delete(self, name):
        self.bucket.delete_object(self.path(name))

    def get_available_name(self, name, max_length=None):
        (dir_name, file_name) = os.path.split(name)
        (file_root, file_ext) = os.path.splitext(file_name)

        random.seed(time.time())
        while self.exists(name):
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            random_string = ''.join([random.choice(chars) for i in range(0,8)])
            name= os.path.join(dir_name, "%s_%s%s" % (file_root, random_string, file_ext))

        return name


