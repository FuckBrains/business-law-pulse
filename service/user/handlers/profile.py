# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException,ThriftException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth,check_user_auth

import os,sys,json,time,datetime,pytz
import uuid,random,hashlib

from mongoengine import Q

import thriftpy

thriftpy.load(os.path.join(IDL_DIR, 'common.thrift'), module_name='common_thrift')
import common_thrift

thriftpy.load(os.path.join(IDL_DIR, 'user.thrift'), module_name='user_thrift')
import user_thrift

from service.user.models import User



class ProfileHandler(ThriftHandler):

    @thrift_exempt
    @property
    def default_avatar(self):
        if hasattr(self,'_default_avatar'):
            return self._default_avatar

        module,app = self.__class__.__module__.split('.')[:2]
        name = self.__class__.__name__
        gid = '%s.%s.%s' % (module,app,name)
        with thrift_connect(service=common_thrift.ImageService) as image_service:
            payload = Payload(gid=gid,data=dict(scene='user/avatar',path='images/default/user_avatar.png'))
            result = image_service.construct(payload)
            self._default_avatar = result.data['image']
            
        return self._default_avatar

    @check_admin_auth
    def filter(self,request):
        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        users = User.objects.all()

        if keyword:
            query = Q(nickname__icontains=keyword) | Q(email__icontains=keyword) | Q(cellphone__contains=keyword)
            users = users.filter(query)

        total = users.count()
        start, end = (page.get('no',1)-1)*page['size'], page.get('no',1)*page['size']
        users = users.order_by('id')[start:end]

        _users = []
        for user in users:
            _user = user.digest()
            if user.status == -1:
                _user.update({ 'nickname': '足球流氓', 'avatar': self.blacklist_avatar })

            _users.append(_user)

        return Result(data=dict(users=_users,total=total))


    def with_identifier(self, request):
        identifier = request.data['identifier']
        mode = request.data['mode']

        user = None
        if mode == 'nickname':
            user = User.objects.filter(nickname=identifier).first()
        elif mode == 'cellphone':
            user = User.objects.filter(cellphone=identifier).first()
        elif mode == 'email':
            user = User.objects.filter(email=identifier).first()
        elif mode == 'qq':
            user = User.objects.filter(qq_openid=identifier).first()
        elif mode == 'weixin':
            user = User.objects.filter(Q(weixin_openid=identifier) | Q(weixin_unionid=identifier)).first()

        _user = user.digest() if user else None
        return Result(data=dict(user=_user))


    def get_digest(self, request):
        user_id = request.data['user']['id'] if isinstance(request.data['user'],dict) else request.data['user']
        user = User.objects.filter(id=user_id or '0'*24).first()

        _user = user.digest() if user else None
        if user and user.status == -1:
            _user.update({ 'nickname': '足球流氓', 'avatar': self.blacklist_avatar })

        return Result(data=dict(user=_user))

    def get_detail(self, request):
        user_id = request.data['user']['id'] if isinstance(request.data['user'],dict) else request.data['user']
        user = User.objects.filter(id=user_id or '0'*24).first()

        _user = None
        if user:
            if request.auth and request.auth.id == str(user.id):
                _user = user.detail()
            else:
                _user = user.digest()

        return Result(data=dict(user=_user))

    def get_multiple(self, request):
        user_ids = []
        for item in request.data['users']:
            user_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(user_ids) > 100:
            raise BizException('记录数量超过上限')

        users = User.objects.filter(id__in=user_ids)

        _users = []
        for user in users:
            _user = user.digest()
            if user.status == -1:
                _user.update({ 'nickname': '足球流氓', 'avatar': self.blacklist_avatar })

            _users.append(_user)

        return Result(data=dict(users=_users))

    @check_admin_auth
    def random_sockpuppet(self, request):
        users = User.objects.filter(type=0)
        user = users[random.randint(0,users.count()-1)]
        _user = user.digest()
        if user.status == -1:
            _user.update({ 'nickname': '足球流氓', 'avatar': self.blacklist_avatar })

        token = ''

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

        _user.update({ 'token': token })

        return Result(data=dict(user=_user))

    def create(self,request):
        #now = pytz.timezone(CONST['timezone']).normalize(datetime.datetime.now().astimezone(pytz.utc))
        user = User(type=1,avatar=self.default_avatar,status=1,created=datetime.datetime.now())

        cellphone = request.data.get('cellphone')
        if cellphone is not None:
            identifier = cellphone['identifier']
            validation = cellphone['validation']

            if User.objects.filter(cellphone=identifier).first():
                raise BizException('手机号已被注册')
            else:
                with thrift_connect(service=user_thrift.AuthService) as auth_service:
                    payload = Payload(gid=request.gid,data=dict(scene='register',mode='cellphone',identifier=identifier,validation=validation))
                    result = auth_service.check_otp(payload)

                if result.err:
                    raise BizException('手机验证码校验失败')
                else:
                    user.cellphone = identifier

        email = request.data.get('email')
        if email is not None:
            identifier = email['identifier']
            validation = email['validation']

            if User.objects.filter(email=identifier).first():
                raise BizException('邮箱已被注册')
            else:
                with thrift_connect(service=user_thrift.AuthService) as auth_service:
                    payload = Payload(gid=request.gid,data=dict(scene='register',mode='email',identifier=identifier,validation=validation))
                    result = auth_service.check_otp(payload)

                if result.err:
                    raise BizException('邮件验证码校验失败')
                else:
                    user.email = identifier

        qq = request.data.get('qq')
        if qq is not None:
            openid = qq['openid']
            if User.objects.filter(qq_openid=openid).first():
                raise BizException('ＱＱ已被注册')

            with thrift_connect(service=common_thrift.OAuthService) as oauth_service:
                payload = Payload(gid=request.gid,device=request.device,data=dict(access=qq))
                result = oauth_service.check_qq_access(payload)

            if result.err:
                raise BizException('ＱＱ验证失败')

            user.qq_openid = openid
            with thrift_connect(service=common_thrift.OAuthService) as oauth_service:
                payload = Payload(gid=request.gid,device=request.device,data=dict(access=qq))
                result = oauth_service.get_qq_user_info(payload)

            profile = result.data['profile']
            user.gender = profile['gender']

            if profile['avatar']:
                with thrift_connect(service=common_thrift.ImageService) as image_service:
                    payload = Payload(gid=request.gid,data=dict(scene='user/avatar',url=profile['avatar']))
                    result = image_service.download(payload)
                    image = result.data['image']
                    if image:
                        user.avatar = image

        weixin = request.data.get('weixin')
        if weixin is not None:
            openid = weixin['openid']
            unionid = weixin.get('unionid')
            if User.objects.filter(Q(weixin_openid=openid) | Q(weixin_unionid__ne=None) & Q(weixin_unionid__ne='') & Q(weixin_unionid=unionid)).first():
                raise BizException('微信已被注册')

            with thrift_connect(service=common_thrift.OAuthService) as oauth_service:
                payload = Payload(gid=request.gid,device=request.device,data=dict(access=weixin))
                result = oauth_service.check_weixin_access(payload)

            if result.err:
                raise BizException('微信验证失败')

            user.weixin_openid = openid
            user.weixin_unionid = unionid

            with thrift_connect(service=common_thrift.OAuthService) as oauth_service:
                payload = Payload(gid=request.gid,device=request.device,data=dict(access=weixin))
                result = oauth_service.get_weixin_user_info(payload)

            profile = result.data['profile']
            user.gender = profile['gender']

            if profile['avatar']:
                with thrift_connect(service=common_thrift.ImageService) as image_service:
                    payload = Payload(gid=request.gid,data=dict(scene='user/avatar',url=profile['avatar']))
                    result = image_service.download(payload)
                    image = result.data['image']
                    if image:
                        user.avatar = image

        nickname = request.data['nickname'].strip()
        if User.objects.filter(nickname=nickname).first():
            raise BizException('昵称已被注册')
        else:
            user.nickname = nickname

        password = request.data.get('password')
        if password:
            if len(password) < 6:
                raise BizException('密码长度不得小于6位')

            user.password = hashlib.new('md5', password.encode('utf8')).hexdigest()

        gender = request.data.get('gender')
        if gender is not None:
            user.gender = gender.strip()

        avatar = request.data.get('avatar')
        if avatar:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=avatar))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    user.avatar = image

        user.switch_db('primary').save()

        _user = user.digest()

        token = self.generate_token(user,request.device)
        _user.update({ 'token': token})

        return Result(msg='注册成功',data=dict(user=_user))

    @check_user_auth
    def update_info(self,request):
        user = User.objects.filter(id=request.auth.id).first()
        if not user:
            raise BizException('用户记录不存在')

        avatar = request.data.get('avatar')
        if avatar:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=avatar))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    user.avatar = image

        nickname = request.data.get('nickname')
        if nickname is not None:
            nickname = nickname.strip()
            if User.objects.filter(id__ne=request.auth.id,nickname=nickname).first():
                raise BizException('昵称已被注册')
            else:
                user.nickname = nickname

        gender = request.data.get('gender')
        if gender is not None:
            user.gender = gender.strip()

        division_id = ''
        city_id = '' 
        if request.device.channel == 'app' and request.device.version < (2,0,0):
            province = request.data.get('province')
            city = request.data.get('city')
            if province is not None and city is not None:
                division_id = province['id']
                city_id = city['id']
        else:
            geo = request.data.get('geo')
            if geo is not None:
                division_id = geo['division']
                city_id = geo['city']

        if division_id and city_id:
            with thrift_connect(service=common_thrift.GeoService) as geo_service:
                payload = Payload(gid=request.gid,data=dict(division=division_id,city=city_id))
                result = geo_service.parse(payload)
            
            user.geo = { 'division': result.data['division'], 'city': result.data['city'] }

        qq_account = request.data.get('qq_account')
        if qq_account is not None:
            user.qq_account = qq_account.strip()

        weixin_account = request.data.get('weixin_account')
        if weixin_account is not None:
            user.weixin_account = weixin_account.strip()

        weibo_account = request.data.get('weibo_account')
        if weibo_account is not None:
            user.weibo_account = weibo_account.strip()

        user.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_user_auth
    def update_password(self,request):
        user = User.objects.filter(id=request.auth.id).first()
        if not user:
            raise BizException('用户记录不存在')

        if not user.type:
            raise BizException('用户类型不支持')

        old_password = request.data['old_password']
        new_password = request.data['new_password']

        if len(new_password) < 6:
            raise BizException('新密码长度不得少于6位')

        if not user.cellphone and not user.email:
            raise BizException('请先绑定手机或邮箱')

        if not user.password and old_password:
            raise BizException('旧密码有误')

        enc_old_password = hashlib.new('md5', old_password.encode('utf8')).hexdigest()
        if user.password and user.password != enc_old_password:
            raise BizException('旧密码有误')

        enc_new_password = hashlib.new('md5', new_password.encode('utf8')).hexdigest()
        user.password = enc_new_password

        user.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_user_auth
    def reset_password(self,request):
        user = User.objects.filter(id=request.auth.id).first()
        if not user:
            raise BizException('用户记录不存在')

        if not user.type:
            raise BizException('用户类型不支持')

        password = request.data['password']

        if len(password) < 6:
            raise BizException('新密码长度不得少于6位')

        if not user.cellphone and not user.email:
            raise BizException('请先绑定手机或邮箱')

        enc_password = hashlib.new('md5', password.encode('utf8')).hexdigest()
        user.password = enc_password

        user.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_user_auth
    def update_bind(self,request):
        user = User.objects.filter(id=request.auth.id).first()
        if not user:
            raise BizException('用户记录不存在')

        mode = request.data['mode']
        toggle = request.data['toggle']
        if mode == 'cellphone':
            if toggle == 1:
                cellphone = request.data['cellphone']
                identifier = cellphone['identifier']
                validation = cellphone['validation']
                with thrift_connect(service=user_thrift.AuthService) as auth_service:
                    payload = Payload(gid=request.gid,data=dict(scene='bind',mode='cellphone',identifier=identifier,validation=validation))
                    result = auth_service.check_otp(payload)

                if result.err:
                    return Result(err=result.err,msg=result.msg,log=result.log)

                user.cellphone = cellphone['identifier']
            else:
                if not user.email:
                    raise BizException('请先绑定邮箱')

                user.cellphone = None

        elif mode == 'email':
            if toggle == 1:
                email = request.data['email']
                identifier = email['identifier']
                validation = email['validation']
                with thrift_connect(service=user_thrift.AuthService) as auth_service:
                    payload = Payload(gid=request.gid,data=dict(scene='bind',mode='email',identifier=identifier,validation=validation))
                    result = auth_service.check_otp(payload)

                if result.err:
                    return Result(err=result.err,msg=result.msg,log=result.log)

                user.email = email['identifier']
            else:
                if not user.cellphone:
                    raise BizException('请先绑定手机')

                user.email = None

        elif mode == 'weixin':
            if toggle == 1:
                weixin = request.data['weixin']
                with thrift_connect(service=common_thrift.OAuthService) as oauth_service:
                    payload = Payload(gid=request.gid,data=dict(access=weixin))
                    result = oauth_service.check_weixin_access(payload)

                if result.err:
                    return Result(err=result.err,msg=result.msg,log=result.log)

                user.weixin_openid = weixin['openid']
                user.weixin_unionid = weixin.get('unionid')
            else:
                user.weixin_openid = None
                user.weixin_unionid = None

        elif mode == 'qq':
            if toggle == 1:
                qq = request.data['qq']
                with thrift_connect(service=common_thrift.OAuthService) as oauth_service:
                    payload = Payload(gid=request.gid,data=dict(access=qq))
                    result = oauth_service.check_qq_access(payload)

                if result.err:
                    return Result(err=result.err,msg=result.msg,log=result.log)

                user.qq_openid = qq['openid']
            else:
                user.qq_openid = None

        user.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_admin_auth
    def update_status(self,request):
        user_id = request.data['user']['id'] if isinstance(request.data['user'],dict) else request.data['user']
        user = User.objects.filter(id=user_id or '0'*24).first()
        if not user:
            raise BizException('用户记录不存在')

        status = request.data['status']
        user.status = status

        user.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_admin_auth(permissions=['update_user_permissions'])
    def update_permissions(self,request):
        user_id = request.data['user']['id'] if isinstance(request.data['user'],dict) else request.data['user']
        user = User.objects.filter(id=user_id or '0'*24).first()
        if not user:
            raise BizException('记录不存在')

        user.permissions = request.data.get('permissions',[])

        user.switch_db('primary').save()
        return Result(msg='修改成功')


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


