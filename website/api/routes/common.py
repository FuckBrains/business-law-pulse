# -*- coding: utf-8 -*-

import os,thriftpy

from core.utils.thrift import IDL_DIR
from core.utils.http import service

thriftpy.load(os.path.join(IDL_DIR, 'common.thrift'), module_name='common_thrift')
from common_thrift import ConfigService, GeoService, FeedbackService, DocService
from common_thrift import SmsService, EmailService, PushService, OAuthService

from website.api.views import upload,ueditor


routes = [
    # config
    { 'method': 'POST', 'path': '/common/config/global', 'handler': service(ConfigService,'get_global') },
    { 'method': 'POST', 'path': '/common/config/market/list', 'handler': service(ConfigService,'list_market') },
    { 'method': 'POST', 'path': '/common/config/market/update', 'handler': service(ConfigService,'update_market') },
    { 'method': 'POST', 'path': '/common/config/launch/list', 'handler': service(ConfigService,'list_launch') },
    { 'method': 'POST', 'path': '/common/config/launch/add', 'handler': service(ConfigService,'add_launch') },
    { 'method': 'POST', 'path': '/common/config/launch/remove', 'handler': service(ConfigService,'remove_launch') },

    # geo
    { 'method': 'POST', 'path': '/common/geo/globe', 'handler': service(GeoService,'get_globe') },
    { 'method': 'POST', 'path': '/common/geo/country', 'handler': service(GeoService,'get_country') },

    # upload
    { 'method': 'POST', 'path': '/common/upload/image', 'handler': upload.store_image },
    { 'method': 'POST', 'path': '/common/upload/file', 'handler': upload.store_file },

    # ueditor
    { 'method': '*', 'path': '/common/ueditor/dispatch', 'handler': ueditor.dispatch_action },

    # push
    { 'method': 'POST', 'path': '/common/push/unicast', 'handler': service(PushService,'unicast') },
    { 'method': 'POST', 'path': '/common/push/listcast', 'handler': service(PushService,'listcast') },
    { 'method': 'POST', 'path': '/common/push/broadcast', 'handler': service(PushService,'broadcast') },

    # oauth
    { 'method': 'POST', 'path': '/common/oauth/qq/access/code', 'handler': service(OAuthService,'get_qq_access_by_code') },
    { 'method': 'POST', 'path': '/common/oauth/weixin/access/code', 'handler': service(OAuthService,'get_weixin_access_by_code') },
    { 'method': 'POST', 'path': '/common/oauth/weixin/access/credential', 'handler': service(OAuthService,'get_weixin_access_by_credential') },
    { 'method': 'POST', 'path': '/common/oauth/weixin/jsapi/sign', 'handler': service(OAuthService,'sign_weixin_jsapi') },
    { 'method': 'POST', 'path': '/common/oauth/weixin/userinfo', 'handler': service(OAuthService,'get_weixin_user_info') },
    { 'method': 'POST', 'path': '/common/oauth/qq/userinfo', 'handler': service(OAuthService,'get_qq_user_info') },

    # feedback
    { 'method': 'POST', 'path': '/common/feedback/list', 'handler': service(FeedbackService,'list') },
    { 'method': 'POST', 'path': '/common/feedback/add', 'handler': service(FeedbackService,'add') },
    { 'method': 'POST', 'path': '/common/feedback/{feedback:[0-9a-f]+}/remove', 'handler': service(FeedbackService,'remove') },

    # doc
    { 'method': 'POST', 'path': '/common/doc/module/list', 'handler': service(DocService,'list_modules') },
    { 'method': 'POST', 'path': '/common/doc/module/create', 'handler': service(DocService,'create_module') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/update', 'handler': service(DocService,'update_module') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/remove', 'handler': service(DocService,'remove_module') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/detail', 'handler': service(DocService,'get_module') },

    { 'method': 'POST', 'path': '/common/doc/module/{module}/item/list', 'handler': service(DocService,'list_items') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/item/create', 'handler': service(DocService,'create_item') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/item/{item}/update', 'handler': service(DocService,'update_item') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/item/{item}/remove', 'handler': service(DocService,'remove_item') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/item/{item}/detail', 'handler': service(DocService,'get_item') },
    { 'method': 'POST', 'path': '/common/doc/module/{module}/item/{item}/seq', 'handler': service(DocService,'seq_item') },
]



