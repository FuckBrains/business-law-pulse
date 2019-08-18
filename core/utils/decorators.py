# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException,ThriftException
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect

import logging
logger = logging.getLogger('thriftpy')

import os,json,datetime,time
import hashlib,uuid,base64,traceback

from functools import wraps

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'admin.thrift'), module_name='admin_thrift')
import admin_thrift

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift

with open(CONST['auth_public_key'],'r') as f:
    PUBLIC_KEY = RSA.importKey(f.read())



def check_admin_auth(handler_func=None,permissions=[]):
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapped_func(self, request):
            auth = request.auth
            if not auth:
                raise BizException('帐号未授权',err=-2)

            auth_permissions = auth.permissions or []
            if auth.expire and datetime.datetime.fromtimestamp(auth.expire/1000) > datetime.datetime.now():
                message = ':'.join(['admin',auth.id,auth.token,'|'.join(auth_permissions),str(auth.expire)])
                digest = SHA.new(message.encode('utf8'))
                verifier = Signature_PKCS1_v1_5.new(PUBLIC_KEY)
                flag = verifier.verify(digest, base64.b64decode(auth.signature.encode('utf8') or ''))
                if flag and set(permissions).issubset(set(auth_permissions)):
                    return handler_func(self, request)

            with thrift_connect(service=admin_thrift.AuthService) as auth_service:
                payload = request.new_payload(auth=None,data=dict(id=auth.id, token=auth.token))
                result = auth_service.validate_token(payload)
                if result.err == -2:
                    raise BizException('帐号未授权',err=-2)

            auth.permissions = result.data['permissions']
            auth.expire = result.data['expire']
            auth.signature = result.data['signature']
            return handler_func(self, request)

        return wrapped_func

    if not handler_func:
        def _decorator(handler_func):
            return decorator(handler_func)
        return _decorator

    return decorator(handler_func)


def check_user_auth(handler_func=None,permissions=[]):
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapped_func(self, request):
            auth = request.auth
            if not auth:
                raise BizException('帐号未授权',err=-2)

            auth_permissions = auth.permissions or []
            if auth.expire and datetime.datetime.fromtimestamp(auth.expire/1000) > datetime.datetime.now():
                message = ':'.join(['user',auth.id,auth.token,'|'.join(auth_permissions),str(auth.expire)])
                digest = SHA.new(message.encode('utf8'))
                verifier = Signature_PKCS1_v1_5.new(PUBLIC_KEY)
                flag = verifier.verify(digest, base64.b64decode(auth.signature.encode('utf8') or ''))
                if flag and set(permissions).issubset(set(auth_permissions)):
                    return handler_func(self, request)

            with thrift_connect(service=user_thrift.AuthService) as auth_service:
                payload = request.new_payload(auth=None,data=dict(id=auth.id, token=auth.token))
                result = auth_service.validate_token(payload)
                if result.err == -2:
                    raise BizException('帐号未授权',err=-2)

            auth.permissions = result.data['permissions']
            auth.expire = result.data['expire']
            auth.signature = result.data['signature']
            return handler_func(self, request)

        return wrapped_func

    if not handler_func:
        def _decorator(handler_func):
            return decorator(handler_func)
        return _decorator

    return decorator(handler_func)
