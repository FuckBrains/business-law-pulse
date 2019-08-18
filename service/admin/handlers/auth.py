# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result
from core.utils.thrift import thrift_exempt
from core.utils.decorators import check_admin_auth

import datetime
import hashlib,uuid,base64

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5

from mongoengine import Q

from service.admin.models import Admin


class AuthHandler(ThriftHandler):
    def __init__(self):
        super(AuthHandler,self).__init__()

        with open(CONST['auth_private_key'], 'r') as f:
            self.private_key = RSA.importKey(f.read())

    def validate_token(self,request):
        admin_id = request.data['id']
        admin_token = request.data['token']

        admin = Admin.objects.filter(id=admin_id).first()
        if not admin:
            raise BizException('记录不存在')

        key = 'auth:admin:%s:token:%s' % (admin_id,admin_token)
        if not REDIS['app'].exists(key):
            raise BizException('无效的Token',err=-2)

        permissions = admin.permissions
        expire = datetime.datetime.now() + datetime.timedelta(seconds=60*10)
        expire = int(expire.timestamp()*1000)
        message = ':'.join(['admin',admin_id,admin_token,'|'.join(permissions),str(expire)])
        digest = SHA.new(message.encode('utf8'))
        signer = Signature_PKCS1_v1_5.new(self.private_key)
        signature = signer.sign(digest)
        signature = base64.b64encode(signature).decode('utf8')

        return Result(data=dict(permissions=permissions,expire=expire,signature=signature))

    def create_token(self,request):
        channel = request.device.channel
        if channel == 'unknown':
            raise BizException('无法识别的客户端')

        identifier = request.data['identifier']
        password = request.data['password']
        enc_password = hashlib.new('md5', password.encode('utf8')).hexdigest()
        admin = Admin.objects.filter(status=1).filter(Q(email=identifier) | Q(cellphone=identifier)).filter(password=enc_password).first()
        if not admin:
            raise BizException('帐号或密码有误')

        # delete existing token
        pattern = 'auth:admin:%s:token:*' % str(admin.id)
        for key in REDIS['app'].scan_iter(match=pattern):
            info = REDIS['app'].hgetall(key)
            if info['channel'] == channel:
                REDIS['app'].delete(key)

        token = self.generate_token(str(admin.id),request.device)
        return Result(data=dict(admin={ 'id': str(admin.id), 'token': token }))

    def destroy_token(self,request):
        auth = request.auth
        channel = request.device.channel
        if channel == 'unknown':
            raise BizException('无法识别的客户端')

        pattern = 'auth:admin:%s:token:*' % auth.id
        for key in REDIS['app'].scan_iter(match=pattern):
            info = REDIS['app'].hgetall(key)
            if info['channel'] == channel:
                REDIS['app'].delete(key)
                break

        return Result(msg='注销Token成功')

    @thrift_exempt
    def generate_token(self,id,device):
        value = {
            'channel': device.channel,
            'agent': device.agent,
            'ip': device.ip,
            'port': device.port,
            'created': int(datetime.datetime.now().timestamp()*1000),
        }

        token = uuid.uuid1().hex
        key = 'auth:admin:%s:token:%s' % (id,token)
        REDIS['app'].hmset(key,value)
        return token


