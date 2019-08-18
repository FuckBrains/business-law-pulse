# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os,datetime
import hashlib

from bson import ObjectId
from mongoengine import Q

import thriftpy
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

from service.admin.models import Admin


class ProfileHandler(ThriftHandler):
    def __init__(self):
        super(ProfileHandler, self).__init__()

        self.permissions = {
            'admin': [
                { 'value': 'create_admin', 'name': 'Create' },
                { 'value': 'reset_admin_password', 'name': 'Reset' },
                { 'value': 'disable_admin', 'name': 'Disable' },
                { 'value': 'update_admin_info', 'name': 'Update info' },
                { 'value': 'update_admin_permission', 'name': 'Update Permission' },
            ],
        }

    @property
    @thrift_exempt
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

    def filter(self,request):
        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        admins = Admin.objects.all()

        if keyword:
            query = Q(realname__contains=keyword) | Q(cellphone=keyword) | Q(email=keyword)
            admins = admins.filter(query)

        total = admins.count()
        start, end = (page.get('no',1)-1)*page['size'], page.get('no',1)*page['size']
        admins = admins.order_by('id')[start:end]

        _admins = [admin.digest() for admin in admins]
        return Result(data=dict(admins=_admins,total=total))

    @check_admin_auth
    def create(self,request):
        admin = Admin(status=1,created=datetime.datetime.now())

        avatar = request.data.get('avatar')
        if avatar:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=avatar))
                result = image_service.extract(payload)
                image = result.data['image']
                admin.avatar = image or self.default_avatar
        else:
            admin.avatar = self.default_avatar

        admin.realname = request.data['realname'].strip()
        admin.gender = request.data.get('gender','').strip()
        admin.email = request.data.get('email','').strip()
        admin.cellphone = request.data.get('cellphone','').strip()

        if not admin.email and not admin.cellphone:
            raise BizException('邮箱和手机不能同时为空')

        if admin.email and Admin.objects.filter(email=admin.email).first():
            raise BizException('邮箱已被注册')

        if admin.cellphone and Admin.objects.filter(cellphone=admin.cellphone).first():
            raise BizException('手机已被注册')

        admin.switch_db('primary').save()
        return Result(msg='创建成功')

    @check_admin_auth
    def get_digest(self,request):
        admin_id = request.data['admin']['id'] if isinstance(request.data['admin'],dict) else request.data['admin']
        admins = Admin.objects.only('realname','cellphone','email','avatar','gender')
        admin = admins.with_id(ObjectId(admin_id or '0'*24))

        _admin = admin.digest() if admin else None
        return Result(data=dict(admin=_admin))

    def get_detail(self,request):
        admin_id = request.data['admin']['id'] if isinstance(request.data['admin'],dict) else request.data['admin']

        auth = request.auth
        if auth.id != admin_id:
            raise BizException('帐号未授权')

        admins = Admin.objects.exclude('password')
        admin = admins.with_id(ObjectId(admin_id or '0'*24))

        _admin = admin.detail() if admin else None

        return Result(data=dict(admin=_admin))

    @check_admin_auth
    def get_multiple(self,request):
        admin_ids = []
        for item in request.data['admins']:
            admin_ids.append(item['id'] if isinstance(item,dict) else item['id'])

        if len(admin_ids) > 100:
            raise BizException('记录数量超过上限')

        admin_ids = [ObjectId(admin_id or '0'*24) for admin_id in admin_ids]
        admins = Admin.objects.only('realname','cellphone','email','avatar','gender')
        bulk = admins.in_bulk(admin_ids)

        _admins = []
        for admin_id in admin_ids:
            admin = bulk.get(admin_id)
            if admin:
                _admins.append(admin.digest())

        return Result(data=dict(admins=_admins))

    @check_admin_auth
    def update_info(self,request):
        auth = request.auth

        admins = Admin.objects.all_fields()
        admin = admins.with_id(ObjectId(auth.id))
        if not admin:
            raise BizException('记录不存在')

        avatar = request.data.get('avatar',None)
        if avatar:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=avatar))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    admin.avatar = image

        realname = request.data.get('realname',None)
        if realname is not None:
            admin.realname = realname.strip()

        gender = request.data.get('gender',None)
        if gender is not None:
            admin.gender = gender.strip()

        email = request.data.get('email',None)
        if email is not None:
            email = email.strip()
            if Admin.objects.filter(id__ne=admin.id,email=email).first():
                raise BizException('邮箱已被注册')
            else:
                admin.email = email

        cellphone = request.data.get('cellphone',None)
        if cellphone is not None:
            cellphone = cellphone.strip()
            if Admin.objects.filter(id__ne=admin.id,cellphone=cellphone).first():
                raise BizException('手机已被注册')
            else:
                admin.cellphone = cellphone

        admin.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_admin_auth
    def update_password(self,request):
        auth = request.auth
        old_password = request.data['old_password']
        new_password = request.data['new_password']

        admins = Admin.objects.only('password')
        admin = admins.with_id(ObjectId(auth.id))
        if not admin:
            raise BizException('记录不存在')

        enc_old_password = hashlib.new('md5', old_password.encode('utf8')).hexdigest()
        if admin.password != enc_old_password:
            raise BizException('旧密码不正确')

        enc_new_password = hashlib.new('md5', new_password.encode('utf8')).hexdigest()
        admin.password = enc_new_password

        admin.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_admin_auth
    def reset_password(self,request):
        admin_id = request.data['admin']
        password = request.data['password']

        admins = Admin.objects.only('password')
        admin = admins.with_id(ObjectId(admin_id))
        if not admin:
            raise BizException('记录不存在')

        enc_password = hashlib.new('md5', password.encode('utf8')).hexdigest()
        Admin.objects.using('primary').filter(id=admin.id).update(password=enc_password)
        return Result(msg='更新成功')

    @check_admin_auth
    def update_status(self,request):
        admin_id = request.data['admin']
        status = int(request.data['status'])

        admins = Admin.objects.only('status')
        admin = admins.with_id(ObjectId(admin_id))
        if not admin:
            raise BizException('记录不存在')

        admin.status = status

        admin.switch_db('primary').save()
        return Result(msg='更新成功')

    @check_admin_auth(permissions=['update_admin_permissions'])
    def update_permission(self,request):
        admin_id = request.data['admin']['id'] if isinstance(request.data['admin'],dict) else request.data['admin']

        admins = Admin.objects.only('permissions')
        admin = admins.with_id(ObjectId(admin_id or '0'*24))
        if not admin:
            raise BizException('记录不存在')

        admin.permissions = request.data.get('permissions',[])

        admin.switch_db('primary').save()
        return Result(msg='修改成功')

    @check_admin_auth
    def load_permissions(self,request):
        return Result(data=dict(permissions=self.permissions))


