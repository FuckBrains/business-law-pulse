# -*- coding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.http import Response

import logging
logger = logging.getLogger('aiohttp.server')

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'user.thrift'), module_name='user_thrift')
import user_thrift



async def login_by_password(request):
    with thrift_connect(user_thrift.ProfileService) as profile_service:
        payload = Payload(gid=request.gid, data=request.data,auth=request.auth)
        result = profile_service.validate_token(payload)
    return Response(err=result.err,msg=result.msg,data=result.data,log=result.log)

