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

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift



async def sync(request):
    session = await get_session(request)
    user = session.get('user',{})
    if not user:
        raise BizException('用户未登录')

    with thrift_connect(user_thrift.AuthService) as auth_service:
        payload = Payload(gid=request.gid, data=dict(id=user['id'],token=user['token']))
        result = auth_service.validate_token(payload)
        if result.err:
            raise BizException('用户未登录')

    with thrift_connect(user_thrift.ProfileService) as profile_service:
        payload = Payload(gid=request.gid, data=dict(id=user['id']))
        result = profile_service.get_digest(payload)
        _user = result.data['user']

    user.update(_user)
    session['user'] = user

    return Response(msg='同步成功',data=dict(user=user))


async def login(request):
    account = request.data.get('account','')
    password = request.data.get('password','')

    with thrift_connect(user_thrift.AuthService) as auth_service:
        payload = Payload(gid=request.gid, data=dict(account=account,password=password),device=request.device)
        result = auth_service.create_token(payload)
        if result.err:
            raise BizException(result.msg)

    user = result.data['user']
    auth = common_thrift.Auth(type='user',id=user['id'],token=user['token'])

    with thrift_connect(user_thrift.ProfileService) as profile_service:
        payload = Payload(gid=request.gid, data=dict(user=auth.id), auth=auth)
        result = profile_service.get_digest(payload)
        user = result.data['user']

    user.update({ 'token': auth.token })

    session = await get_session(request)
    session['user'] = user

    return Response(msg='登录成功')


async def logout(request):
    session = await get_session(request)
    user = session.get('user',{})
    if not user:
        return Response(msg='帐号已退出')

    with thrift_connect(user_thrift.AuthService) as auth_service:
        auth = common_thrift.Auth(type='user',id=user['id'],token=user['token'])
        payload = Payload(gid=request.gid, data=dict(), auth=auth, device=request.device)
        result = auth_service.destroy_token(payload)
        if not result.err:
            session['user'] = None

    return Response(msg='退出成功')


