# -*- coding: utf-8 -*-

import os,thriftpy

from core.utils.thrift import IDL_DIR
from core.utils.http import service

thriftpy.load(os.path.join(IDL_DIR, 'common.thrift'), module_name='common_thrift')
from common_thrift import OAuthService

thriftpy.load(os.path.join(IDL_DIR, 'user.thrift'), module_name='user_thrift')
from user_thrift import AuthService,ProfileService

from website.api.views import user 


routes = [
    # token
    { 'method': 'POST', 'path': '/user/token/random', 'handler': service(ProfileService,'random_sockpuppet') },
    { 'method': 'POST', 'path': '/user/token/get', 'handler': service(AuthService,'access_token') },
    { 'method': 'POST', 'path': '/user/token/validate', 'handler': service(AuthService,'validate_token') },
    { 'method': 'POST', 'path': '/user/token/destroy', 'handler': service(AuthService,'destroy_token') },

    # profile
    { 'method': 'POST', 'path': '/user/filter', 'handler': service(ProfileService,'filter') },
    { 'method': 'POST', 'path': '/user/update/info', 'handler': service(ProfileService,'update_info') },
    { 'method': 'POST', 'path': '/user/update/password', 'handler': service(ProfileService,'update_password') },
    { 'method': 'POST', 'path': '/user/{user:[0-9a-f]+}/detail', 'handler': service(ProfileService,'get_detail') },

    # oauth
    { 'method': 'POST', 'path': '/user/oauth/qq/code', 'handler': service(OAuthService,'get_qq_access_by_code') },
    { 'method': 'POST', 'path': '/user/oauth/weixin/code', 'handler': service(OAuthService,'get_weixin_access_by_code') },
    { 'method': 'POST', 'path': '/user/oauth/weixin/credential', 'handler': service(OAuthService,'get_weixin_access_by_credential') },
    { 'method': 'POST', 'path': '/user/oauth/weixin/jsapi', 'handler': service(OAuthService,'sign_weixin_jsapi') },
]


