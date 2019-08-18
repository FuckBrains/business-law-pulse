# -*- coding: utf-8 -*-

from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect
from core.utils.http import Response

import logging
logger = logging.getLogger('aiohttp.server')

import os

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



async def store_image(request):
    scene = request.data['scene']
    image = request.data['image']

    with thrift_connect(service=common_thrift.ImageService) as image_service:
        payload = Payload(gid=request.gid,data=dict(scene=scene,path=image['path'],name=image['name']))
        result = image_service.store(payload)

    return Response(msg='上传成功',data=dict(image=result.data['image']))


async def store_file(request):
    file = request.data['file']

    with thrift_connect(service=common_thrift.FileService) as file_service:
        payload = Payload(gid=request.gid,data=dict(path=file['path'],name=file['name']))
        result = file_service.store(payload)

    return Response(msg='上传成功',data=dict(image=result.data['file']))



