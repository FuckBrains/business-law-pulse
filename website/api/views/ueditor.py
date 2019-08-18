# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.exceptions import BizException
from core.utils.thrift import Payload,IDL_DIR
from core.utils.thrift import thrift_connect

from core.utils.storage import instantiate_storage
storage = instantiate_storage()

from aiohttp import web

import logging
logger = logging.getLogger('aiohttp.server')

import os,datetime,json,uuid,base64,traceback

import thriftpy

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift




async def dispatch_action(request):
    actions = {
        'config' : get_config,
        'uploadfile' : upload_file,
        'uploadimage' : upload_image,
        'uploadscrawl' : upload_scrawl,
        'uploadvideo' : upload_video,
        'catchimage' : catch_image,
        'listfile' : list_file,
        'listimage' : list_image,
    }

    action = request.query.get('action','')
    if action not in actions.keys():
        raise BizException('Invalid UEditor Action')

    try:
        return await actions[action](request)
    except Exception as e:
        logger.error(traceback.format_exc())

    return web.json_response(dict(state='ERROR'))

async def get_config(request):
    api_prefix = '%s://%s' % ('https' if CONST['ssl'] else 'http', CONST['domain']['api'])
    if request.headers.get('Referer','').startswith(api_prefix):
        return web.json_response(UEditorUploadSettings)

    callback = request.query.get('callback','cb')
    jsonp = '%s(%s);' % (callback,json.dumps(UEditorUploadSettings))
    return web.Response(text=jsonp)

async def upload_image(request):
    upfile = request.data.get(UEditorUploadSettings['imageFieldName'])
    if not upfile:
        return web.json_response(dict(state='ERROR'))

    with thrift_connect(service=common_thrift.ImageService) as image_service:
        payload = Payload(gid=request.gid,data=dict(scene='ueditor/picture',path=upfile['path'],name=upfile['name']))
        result = image_service.store(payload)
        image = result.data['image']

    url = image['thumbnails'][0]['url']
    return web.json_response(dict(state='SUCCESS',url=url))

async def upload_scrawl(request):
    upfile = await request.post().get(UEditorUploadSettings['scrawlFieldName'])
    content = base64.b64decode(upfile)
    filename = 'scrawl_%s.jpg' % datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    path = uuid.uuid1().hex + '.' + 'png'
    path = os.path.join('tmp',datetime.datetime.now().strftime('%Y/%m%d/%H%M'), path)
    save_path = storage.save(content,path,filename)

    with thrift_connect(service=common_thrift.ImageService) as image_service:
        payload = Payload(gid=request.gid,data=dict(scene='ueditor/picture',path=save_path,name=upfile.name))
        result = image_service.store(payload)
        image = result.data['image']

    return web.json_response(dict(state='SUCCESS',url=image['thumbnails'][0].url))

async def upload_video(request):
    upfile = request.data.get(UEditorUploadSettings['videoFieldName'])
    if not upfile:
        return web.json_response(dict(state='ERROR'))

    return web.json_response(dict(state='ERROR'))

async def upload_file(request):
    upfile = request.data.get(UEditorUploadSettings['fileFieldName'])
    if not upfile:
        return web.json_response(dict(state='ERROR'))

    path = uuid.uuid1().hex + '.' + 'png'
    path = os.path.join('tmp',datetime.datetime.now().strftime('%Y/%m%d/%H%M'), path)
    save_path = storage.save(upfile.file,path,upfile.name)

    with thrift_connect(service=common_thrift.FileService) as file_service:
        payload = Payload(gid=request.gid,data=dict(path=save_path,name=upfile.name))
        result = file_service.store(payload)
        file = result.data['file']

    return web.json_response(dict(state='SUCCESS',url=file['url']))

async def catch_image(request):
    source = await request.post().get(UEditorUploadSettings['catcherFieldName']+'[]',[])
    if not isinstance(source,list):
        source = [source]

    images = [{
        'source': item,         # pre-catch url
        'url': item,            # post-catch url
        'state': 'SUCCESS',
    } for item in source]

    return web.json_response(dict(state='DONE',list=images))

async def list_image(request):
    start = int(request.query.get('start','0') or '0')
    size = int(request.query.get('size','30') or '30')
    images = [{'url': 'https://www.baidu.com/img/bdlogo.png'}]
    return web.json_response(dict(state='SUCCESS',list=images))

async def list_file(request):
    start = int(request.query.get('start','0') or '0')
    size = int(request.query.get('size','30') or '30')
    files = [{'url': 'https://www.baidu.com/img/bdlogo.png', 'original': '百度Logo'}]
    return web.json_response(dict(state='SUCCESS',list=files))


# 请参阅php文件夹里面的 config.json 进行配置
UEditorUploadSettings = {
    # 上传图片配置项
    'imageActionName': 'uploadimage',       # 执行上传图片的action名称
    'imageMaxSize': 1024*1024*10,           # 上传大小限制，单位B，默认10M
    'imageFieldName': 'upfile',             # 提交的图片表单名称
    'imageUrlPrefix': '',
    'imagePathFormat': '',
    'imageAllowFiles': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],

    # 涂鸦图片上传配置项
    'scrawlActionName': 'uploadscrawl',     # 执行上传涂鸦的action名称
    'scrawlFieldName': 'upfile',            # 提交的图片表单名称
    'scrawlMaxSize': 1024*1024*10,          # 上传大小限制，单位B，默认10M
    'scrawlUrlPrefix': '',
    'scrawlPathFormat': '',

    # 截图工具上传
    'snapscreenActionName': 'uploadimage',  # 执行上传截图的action名称
    'snapscreenPathFormat': '',
    'snapscreenUrlPrefix': '',

    # 上传视频配置
    'videoActionName': 'uploadvideo',       # 执行上传视频的action名称
    'videoPathFormat': '',
    'videoFieldName': 'upfile',             # 提交的视频表单名称
    'videoMaxSize': 1024*1024*100,          # 上传大小限制，单位B，默认100MB
    'videoUrlPrefix': '',
    'videoAllowFiles': [
        '.flv', '.swf', '.mkv', '.avi', '.rm', '.rmvb', '.mpeg', '.mpg',
        '.ogg', '.ogv', '.mov', '.wmv', '.mp4', '.webm', '.mp3', '.wav', '.mid',
    ],

    # 上传文件配置
    'fileActionName': 'uploadfile',         # 执行上传视频的action名称
    'filePathFormat': '',
    'fileFieldName': 'upfile',              # 提交的文件表单名称
    'fileMaxSize': 1024*1024*200,           # 上传大小限制，单位B，默认200MB
    'fileUrlPrefix': '',                    # 文件访问路径前缀
    'fileAllowFiles': [
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.md', '.xml',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif', '.psd',
        '.rar', '.zip', '.tar', '.gz', '.7z', '.bz2', '.cab', '.iso',
        '.flv', '.swf', '.mkv', '.avi', '.rm', '.rmvb', '.mpeg', '.mpg',
        '.ogg', '.ogv', '.mov', '.wmv', '.mp4', '.webm', '.mp3', '.wav', '.mid',
        '.exe', '.com', '.dll', '.msi'
    ], # 上传文件格式显示

    # 列出指定目录下的图片
    'imageManagerActionName': 'listimage',  # 执行图片管理的action名称
    'imageManagerListPath': '',
    'imageManagerListSize': 30,             # 每次列出文件数量
    'imageManagerUrlPrefix': '',            # 图片访问路径前缀
    'imageManagerAllowFiles': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],

    # 列出指定目录下的文件
    'fileManagerActionName': 'listfile',    # 执行文件管理的action名称
    'fileManagerListPath': '',
    'fileManagerUrlPrefix': '',
    'fileManagerListSize': 30,              # 每次列出文件数量
    'fileManagerAllowFiles': [
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.md', '.xml',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif', '.psd',
        '.rar', '.zip', '.tar', '.gz', '.7z', '.bz2', '.cab', '.iso',
        '.flv', '.swf', '.mkv', '.avi', '.rm', '.rmvb', '.mpeg', '.mpg',
        '.ogg', '.ogv', '.mov', '.wmv', '.mp4', '.webm', '.mp3', '.wav', '.mid',
        '.exe', '.com', '.dll', '.msi'
    ],

    # 抓取远程图片配置
    'catcherLocalDomain': ['127.0.0.1', 'localhost', 'img.baidu.com'],
    'catcherPathFormat': '',
    'catcherActionName': 'catchimage',      # 执行抓取远程图片的action名称
    'catcherFieldName': 'source',           # 提交的图片列表表单名称
    'catcherMaxSize': 1024*1024*10,         # 上传大小限制，单位B，默认10M
    'catcherAllowFiles': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    'catcherUrlPrefix': '',
}



