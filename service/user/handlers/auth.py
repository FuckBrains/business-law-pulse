# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os,datetime,time
import random,hashlib,uuid,base64

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5

from mongoengine import Q

import thriftpy
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

from service.user.models import User



class AuthHandler(ThriftHandler):
    def __init__(self):
        super(AuthHandler,self).__init__()

        with open(CONST['auth_private_key'], 'r') as f:
            self.private_key = RSA.importKey(f.read())

    def validate_token(self,request):
        user_id = request.data['id']
        user_token = request.data['token']

        user = User.objects.filter(id=user_id).first()
        if not user:
            raise BizException('记录不存在')

        key = 'auth:user:%s:token:%s' % (user_id,user_token)
        if not REDIS['app'].exists(key):
            raise BizException('无效的Token')

        permissions = user.permissions
        expire = datetime.datetime.now() + datetime.timedelta(seconds=60*10)
        expire = int(expire.timestamp()*1000)
        message = ':'.join(['user',user_id,user_token,'|'.join(permissions),str(expire)])
        digest = SHA.new(message.encode('utf8'))
        signer = Signature_PKCS1_v1_5.new(self.private_key)
        signature = signer.sign(digest)
        signature = base64.b64encode(signature).decode('utf8')

        return Result(data=dict(permissions=permissions,expire=expire,signature=signature))

    def create_token(self,request):
        channel = request.device.channel
        if channel == 'unknown':
            raise BizException('无法识别的客户端')

        users = User.objects.filter(status=1)
        user = None

        type = request.data.get('type','account')
        identifier = request.data['identifier']

        if type == 'account':
            password = request.data['password']
            enc_password = hashlib.new('md5', password.encode('utf8')).hexdigest()
            user = users.filter(Q(email=identifier) | Q(cellphone=identifier)).filter(password=enc_password).first()
        elif type == 'weixin':
            user = users.filter(weixin_openid=identifier).first()
        elif type == 'qq':
            user = users.filter(qq_openid=identifier).first()

        if not user:
            raise BizException('帐号或密码有误')

        # check existing token
        pattern = 'auth:user:%s:token:*' % str(user.id)
        for key in REDIS['app'].scan_iter(match=pattern):
            info = REDIS['app'].hgetall(key)
            if info['channel'] == channel:
                REDIS['app'].delete(key)

        token = self.generate_token(user,request.device)
        return Result(data=dict(user={ 'id': str(user.id), 'token': token }))

    def destroy_token(self,request):
        auth = request.auth
        channel = request.device.channel
        if channel == 'unknown':
            raise BizException('无法识别的客户端')

        pattern = 'auth:user:%s:token:*' % auth.id
        for key in REDIS['app'].scan_iter(match=pattern):
            info = REDIS['app'].hgetall(key)
            if info['channel'] == channel:
                REDIS['app'].delete(key)
                break

        return Result(msg='注销Token成功')

    @check_admin_auth
    def admin_access(self,request):
        user_id = request.data['user']['id'] if isinstance(request.data['user'],dict) else request.data['user']
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise BizException('用户记录不存在')

        token = ''
        channel = 'app' if request.device.platform in ('ios','android') else 'web'

        # get existing token
        pattern = 'auth:user:%s:token:*' % str(user.id)
        for key in REDIS['app'].scan_iter(match=pattern):
            info = REDIS['app'].hgetall(key)
            if info['channel'] == channel:
                token = key.split(':')[-1]
                break

        # no existing token
        if not token:
            token = self.generate_token(user,request.device)

        return Result(data=dict(user={ 'id': str(user.id), 'token': token }))

    def otp_access(self,request):
        user = None

        mode = request.data['mode']
        if mode == 'cellphone':
            scene = request.data['scene']
            if scene not in ('retrieve','login'):
                raise BizException('无法识别的场景')

            cellphone = request.data['cellphone']
            identifier = cellphone['identifier']
            validation = cellphone['validation']

            key = 'otp:%s:cellphone:%s' % (scene,identifier)
            info = REDIS['app'].hgetall(key)
            if not info or info['validation'] != validation:
                raise BizException('手机验证码校验失败')

            REDIS['app'].delete(key)
            user = User.objects.filter(cellphone=identifier).first()

        elif mode == 'email':
            scene = request.data['scene']
            if scene not in ('retrieve','login'):
                raise BizException('无法识别的场景')

            identifier = cellphone['identifier']
            validation = cellphone['validation']

            key = 'otp:%s:email:%s' % (scene,identifier)
            info = REDIS['app'].hgetall(key)
            if not info or info['validation'] != validation:
                raise BizException('邮件验证码校验失败')

            REDIS['app'].delete(key)
            user = User.objects.filter(email=identifier).first()

        elif mode == 'qq':
            qq = request.data['qq']
            with thrift_connect(common_thrift.OAuthService) as oauth_service:
                payload = Payload(gid=request.gid, data=dict(access=qq))
                result = oauth_service.check_qq_access(payload)
                if result.err:
                    raise BizException('ＱＱ验证失败')

            openid = qq['openid']
            user = User.objects.filter(qq_openid=openid).first()

        elif mode == 'weixin':
            weixin = request.data['weixin']
            with thrift_connect(common_thrift.OAuthService) as oauth_service:
                payload = Payload(gid=request.gid, data=dict(access=weixin))
                result = oauth_service.check_weixin_access(payload)
                if result.err:
                    raise BizException('微信验证失败')

            openid = weixin['openid']
            unionid = weixin.get('unionid')
            user = User.objects.filter(Q(weixin_openid=openid) | Q(weixin_unionid__ne=None) & Q(weixin_unionid__ne='') & Q(weixin_unionid=unionid)).first()

        if not user:
            raise BizException('用户记录不存在')

        token = ''
        channel = 'app' if request.device.platform in ('ios','android') else 'web'

        # get existing token
        pattern = 'auth:user:%s:token:*' % str(user.id)
        for key in REDIS['app'].scan_iter(match=pattern):
            info = REDIS['app'].hgetall(key)
            if info['channel'] == channel:
                token = key.split(':')[-1]
                break

        # no existing token
        if not token:
            token = self.generate_token(user,request.device)

        return Result(data=dict(user={ 'id': str(user.id), 'token': token }))

    def create_otp(self,request):
        scene = request.data['scene']
        mode = request.data['mode']
        identifier = request.data['identifier']

        if mode == 'cellphone':
            user = User.objects.filter(cellphone=identifier).first()
            if scene in ('register','bind') and user:
                raise BizException('手机号已注册')
            elif scene in ('retrieve','login') and not user:
                raise BizException('手机号未注册')

            random.seed(time.time())
            validation = ''.join([str(random.randint(0,9)) for i in range(0,6)])
        elif mode == 'email':
            user = User.objects.filter(email=identifier).first()
            if scene in ('register','bind') and user:
                raise BizException('邮箱已注册')
            elif scene in ('retrieve','login') and not user:
                raise BizException('邮箱未注册')

            validation = uuid.uuid1().hex

        key = 'otp:%s:%s:%s' % (scene,mode,identifier)
        REDIS['app'].hset(key, 'validation', validation)
        REDIS['app'].hset(key, 'try', 0)
        REDIS['app'].expire(key,CONST['otp'][mode][scene])

        if mode == 'cellphone':
            with thrift_connect(common_thrift.SmsService) as sms_service:
                payload = Payload(gid=request.gid,device=request.device,data=dict(cellphone=identifier,validation=validation,scene=scene))
                result = sms_service.send_validation(payload)

            interval = result.data['interval']
            msg = '验证码已发送'

        elif mode == 'email':
            with thrift_connect(common_thrift.EmailService) as email_service:
                payload = Payload(gid=request.gid,device=request.device,data=dict(email=identifier,validation=validation,scene=scene))
                result = email_service.send_validation(payload)

            interval = 0
            msg = '验证邮件已发送'

        return Result(msg=msg,data=dict(interval=interval))

    def check_otp(self,request):
        scene = request.data['scene']
        mode = request.data['mode']
        identifier = request.data['identifier']
        validation = request.data['validation']

        key = 'otp:%s:%s:%s' % (scene,mode,identifier)
        info = REDIS['app'].hgetall(key)

        # validation not exists
        if not info:
            raise BizException('验证码不存在')

        # over tries
        if int(info['try']) > 5:
            REDIS['app'].delete(key)
            raise BizException('验证码尝试次数过多')

        # check validation
        if validation != info['validation']:
            REDIS['app'].hincrby(key, 'try', amount=1)
            raise BizException('验证码有误')

        REDIS['app'].delete(key)
        return Result(msg='校验成功')

    @thrift_exempt
    def generate_token(self,user,device):
        value = {
            'channel': device.channel,
            'agent': device.agent,
            'ip': device.ip,
            'port': device.port,
            'created': int(datetime.datetime.now().timestamp()*1000),
        }

        user_token = uuid.uuid1().hex
        key = 'auth:user:%s:token:%s' % (str(user.id),user_token)
        REDIS['app'].hmset(key,value)
        return user_token


