# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result

import json,datetime
import uuid,hashlib,base64,traceback
from Crypto.Cipher import AES
from paho.mqtt import publish



class MqttHandler(ThriftHandler):

    def __init__(self):
        super(MqttHandler, self).__init__()
        self.config = CONST['mqtt']['admin']

    def push(self,request):
        topic = request.data['topic']
        body = request.data['body']

        payload = {
            'mid': uuid.uuid1().hex,
            'timestamp': int(datetime.datetime.now().timestamp()*1000),
            'data': body,
        }

        try:
            publish.single(
                topic=topic, payload=json.dumps(payload),qos=0, retain=False,
                hostname=self.config['host'], port=self.config['port'],
                auth=dict(username=self.config['username'], password=self.config['password']),
                client_id='python-'+uuid.uuid1().hex)
        except Exception as exc:
            log = traceback.format_exc()
            self.logger.error(log)
            raise BizException('推送失败',log=log)

        return Result(msg='推送成功')

    def encrypt(self,request):
        origin_text = request.data['text']
        origin_key = request.data['key']

        # PKCS7Padding
        pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

        md5_hex = hashlib.new('md5', origin_key.encode('utf8')).hexdigest()
        key, iv = md5_hex[:16], md5_hex[16:]

        padded_text = pad(origin_text)
        cipher_text = AES.new(key,AES.MODE_CBC,iv).encrypt(padded_text.encode('utf8'))
        base64_text = base64.b64encode(cipher_text).decode('utf8')

        self.logger.info('########## ENCRYPTED TEXT ##########')
        self.logger.info(base64_text)
        return Result(data={ 'text': base64_text })

    def decrypt(self,request):
        base64_text = request.data['text']
        origin_key = request.data['key']

        # PKCS7Padding
        unpad = lambda s: s[0:-ord(s[-1])]

        md5_hex = hashlib.new('md5', origin_key.encode('utf8')).hexdigest()
        key, iv = md5_hex[:16], md5_hex[16:]

        cipher_text = base64.b64decode(base64_text.encode('utf8'))
        padded_text = AES.new(key,AES.MODE_CBC,iv).decrypt(cipher_text).decode('utf8')
        origin_text = unpad(padded_text)

        self.logger.info('########## DECRYPTED TEXT ##########')
        self.logger.info(origin_text)
        return Result(data={ 'text': origin_text })
