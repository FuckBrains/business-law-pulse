# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.http import Response

from aiohttp_session import get_session

import logging
logger = logging.getLogger('aiohttp.server')

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

thriftpy.load(os.path.join(IDL_DIR,'admin.thrift'), module_name='admin_thrift')
import admin_thrift

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift


async def sync(request):
    session = await get_session(request)
    admin = session.get('admin',{})
    if not admin:
        raise BizException('用户未登录')

    with thrift_connect(admin_thrift.AuthService) as auth_service:
        payload = Payload(gid=request.gid, data=dict(id=admin['id'],token=admin['token']),device=request.device)
        result = auth_service.validate_token(payload)
        if result.err:
            raise BizException('用户未登录')

    with thrift_connect(admin_thrift.ProfileService) as profile_service:
        auth = common_thrift.Auth(type='admin',id=admin['id'],token=admin['token'])
        payload = Payload(gid=request.gid, data=dict(admin=admin['id']),auth=auth,device=request.device)
        result = profile_service.get_digest(payload)
        _admin = result.data['admin']

    admin.update(_admin)
    session['admin'] = admin

    return Response(msg='同步成功',data=dict(admin=admin))


async def login(request):
    account = request.data.get('account','')
    password = request.data.get('password','')

    with thrift_connect(admin_thrift.AuthService) as auth_service:
        payload = Payload(gid=request.gid,data=dict(identifier=account,password=password),device=request.device)
        result = auth_service.create_token(payload)
        if result.err:
            raise BizException(result.msg)

    admin = result.data['admin']
    auth = common_thrift.Auth(type='admin',id=admin['id'],token=admin['token'])

    with thrift_connect(admin_thrift.ProfileService) as profile_service:
        payload = Payload(gid=request.gid,data=dict(admin=auth.id),auth=auth,device=request.device)
        result = profile_service.get_digest(payload)
        admin = result.data['admin']

    admin.update({ 'token': auth.token })

    session = await get_session(request)
    session['admin'] = admin

    return Response(msg='登录成功')


async def logout(request):
    session = await get_session(request)
    admin = session.get('admin',{})
    if not admin:
        return Response(msg='帐号已退出')

    with thrift_connect(admin_thrift.AuthService) as auth_service:
        auth = common_thrift.Auth(type='admin',id=admin['id'],token=admin['token'])
        payload = Payload(gid=request.gid,data=dict(),auth=auth,device=request.device)
        result = auth_service.destroy_token(payload)
        if not result.err:
            session['admin'] = None

    return Response(msg='退出成功')


async def switch_user(request):
    user = request.data['user']

    session = await get_session(request)
    admin = session.get('admin',{})
    if not admin:
        raise BizException('管理员未登录')

    with thrift_connect(user_thrift.AuthService) as auth_service:
        auth = common_thrift.Auth(type='admin',id=admin['id'],token=admin['token'])
        payload = Payload(gid=request.gid,data=dict(user=user),auth=auth,device=request.device)
        result = auth_service.access_token(payload)
        user = result.data['user']

    with thrift_connect(user_thrift.ProfileService) as profile_service:
        auth = common_thrift.Auth(type='user',id=user['id'],token=user['token'])
        payload = Payload(gid=request.gid,data=dict(user=user['id']),auth=auth,device=request.device)
        result = profile_service.get_digest(payload)
        user.update(result.data['user'])

    session['user'] = user
    return Response(msg='切换成功',data=dict(user=user))


async def detach_user(request):
    session = await get_session(request)
    admin = session.get('admin',{})
    if not admin:
        raise BizException('管理员未登录')

    session['admin'] = None

    return Response(msg='退出成功')


