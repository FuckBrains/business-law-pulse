# -*- coding: utf-8 -*-

import os,thriftpy

from core.utils.thrift import IDL_DIR
from core.utils.http import service

thriftpy.load(os.path.join(IDL_DIR, 'common.thrift'), module_name='common_thrift')
from common_thrift import OAuthService

thriftpy.load(os.path.join(IDL_DIR, 'admin.thrift'), module_name='admin_thrift')
from admin_thrift import AuthService,ProfileService

from website.api.views import admin


routes = [
    # token
    { 'method': 'POST', 'path': '/admin/token/validate', 'handler': service(AuthService,'validate_token') },
    { 'method': 'POST', 'path': '/admin/token/create', 'handler': service(AuthService,'create_token') },
    { 'method': 'POST', 'path': '/admin/token/destroy', 'handler': service(AuthService,'destroy_token') },

    # profile
    { 'method': 'POST', 'path': '/admin/filter', 'handler': service(ProfileService,'filter') },
    { 'method': 'POST', 'path': '/admin/create', 'handler': service(ProfileService,'create') },
    { 'method': 'POST', 'path': '/admin/{admin:[0-9a-f]+}/detail', 'handler': service(ProfileService,'get_detail') },
    { 'method': 'POST', 'path': '/admin/info/update', 'handler': service(ProfileService,'update_info') },
    { 'method': 'POST', 'path': '/admin/password/update', 'handler': service(ProfileService,'update_password') },
    { 'method': 'POST', 'path': '/admin/password/reset', 'handler': service(ProfileService,'reset_password') },
    { 'method': 'POST', 'path': '/admin/status/update', 'handler': service(ProfileService,'update_status') },
    { 'method': 'POST', 'path': '/admin/permission/update', 'handler': service(ProfileService,'update_permissions') },
    { 'method': 'POST', 'path': '/admin/permission/load', 'handler': service(ProfileService,'load_permissions') },

    # login
    { 'method': 'POST', 'path': '/admin/login/password', 'handler': admin.login_by_password },
]


