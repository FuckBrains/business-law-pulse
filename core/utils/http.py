# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.exceptions import BizException,ThriftException,HttpException,RestException
from core.utils.thrift import Payload,Device,IDL_DIR
from core.utils.thrift import thrift_connect

from core.utils.storage import instantiate_storage
storage = instantiate_storage()

import asyncio
from aiohttp import web
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_session import session_middleware

import logging
logger = logging.getLogger('aiohttp.server')

import os,json,datetime
import uuid,traceback,tempfile
from bson import ObjectId

import thriftpy
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



def get_request_auth(request):
    if request.headers.get('x-admin-id'):
        return common_thrift.Auth(type='admin', id=request.headers['x-admin-id'], token=request.headers['x-admin-token'])
    if request.headers.get('x-user-id'):
        return common_thrift.Auth(type='user', id=request.headers['x-user-id'], token=request.headers['x-user-token'])
    return None


def get_request_device(request):
    agent = request.headers.get('X-User-Agent','') or request.headers.get('User-Agent','')
    _device = common_thrift.Device(
        ip=request.headers.get('Remote-Addr','0.0.0.0'),
        port=int(request.headers.get('Remote-Port','0')),
        agent=agent,
    )
    return Device(_device)


# basic
async def basic_middleware_factory(app, handler):
    async def middleware_handler(request):
        socket = request.transport.get_extra_info('socket')
        (local_host,local_port) = socket.getsockname()
        (remote_host,remote_port) = socket.getpeername()

        if not request.headers.get('Remote-Addr'):
            if request.headers.get('X-Real-IP'):
                request.headers['Remote-Addr'] = request.headers['X-Real-IP']
            else:
                # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs. Take just the first one.
                request.headers['Remote-Addr'] = request.headers.get('X-Forwarded-For',remote_host).split(',')[0]

        if not request.headers.get('Remote-Port'):
            request.headers['Remote-Port'] = str(remote_port)

        request.gid = str(ObjectId())
        request.auth = get_request_auth(request)
        request.device = get_request_device(request)
        request.data = {}

        if request.method == 'GET':
            request.data = dict(request.query)
        elif request.method == 'POST':
            if request.content_type.startswith('application/x-www-form-urlencoded'):
                post_data = await request.post()
                request.data = dict(post_data)

            elif request.content_type == 'application/json':
                body = await request.text()
                try:
                    request.data = json.loads(body or '{}')
                except:
                    msg = 'Invalid JSON format\n%s' % body
                    return web.Response(status=403, text=msg, content_type='text/html')

            elif request.content_type.startswith('multipart/form-data'):
                reader = await request.multipart()
                while True:
                    field = await reader.next()
                    if not field:
                        break

                    content_type = field.headers.get('Content-Type','empty')
                    if content_type == 'empty':
                        request.data[field.name] = await field.text()
                    elif content_type == 'application/json':
                        request.data[field.name] = await field.json()
                    else:
                        content = tempfile.NamedTemporaryFile()
                        chunk_size = 0    # cannot rely on Content-Length if transfer is chunked
                        while True:
                            chunk = await field.read_chunk()
                            if not chunk:
                                break
                            chunk_size += len(chunk)
                            content.write(chunk)

                        extension = os.path.splitext(field.filename)[-1]
                        path = uuid.uuid1().hex + extension
                        path = os.path.join('tmp',datetime.datetime.now().strftime('%Y/%m%d/%H%M'), path)
                        temp_path = storage.save(content,path,field.filename)
                        content.close()

                        request.data[field.name] = {
                            'content_type': content_type,
                            'name': field.filename,
                            'size': chunk_size,
                            'path': temp_path
                        }

            else:
                msg = 'Forbidden Content-Type\n%s' % request.content_type
                return web.Response(status=403, text=msg, content_type='text/html')

        response = await handler(request)
        response.headers['Access-Control-Expose-Headers'] = ','.join([
            'Connection','Content-Encoding','Content-Length','Content-Type','Date','Server','Transfer-Encoding','X-Request-Id',
        ])
        return response
    return middleware_handler


# session
async def session_middleware_factory(app, handler):
    pool = app['redis'].get('session')
    storage = RedisStorage(pool,cookie_name='SESSION',domain=CONST['domain']['default'],secure=False,httponly=True)
    return await session_middleware(storage)(app,handler)


# logging
async def logging_middleware_factory(app, handler):
    async def middleware_handler(request):
        # skip static & media files
        if request.path.startswith('/static') or request.path.startswith('/media'):
            response = await handler(request)
            return response

        logger.info('[%s] req >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' % request.gid)
        logger.info('[%s] path: %s %s' % (request.gid, request.method, str(request.url)))

        if request.method == 'POST':
            logger.info('[%s] body: %s' % (request.gid, json.dumps(request.data,ensure_ascii=False)))

        headers = dict(request.headers.items())
        excludes = ['Connection','Accept','Accept-Encoding','Accept-Language']
        for key in excludes:
            if headers.get(key):
                del headers[key]

        logger.info('[%s] headers: %s' % (request.gid, json.dumps(headers,ensure_ascii=False)))

        view_handler = request.match_info.handler
        logger.info('[%s] handler: %s.%s' % (request.gid, view_handler.__module__, view_handler.__name__))

        response = await handler(request)

        logger.info('[%s] res <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<' % request.gid)

        if response.status != 200:
            logger.info('[%s] status: %s' % (response.status, request.gid))
            return response

        if request.method == 'POST':
            result = json.loads(response.text)

            if result.get('err'):
                logger.info('[%s] err: %s' % (request.gid, result['err']))

            if result.get('msg'):
                logger.info('[%s] msg: %s' % (request.gid, result['msg']))

            if result.get('log'):
                logger.info('[%s] log: %s' % (request.gid, result['log']))

            if result.get('data'):
                logger.debug('[%s] data: %s' % (request.gid, result['data']))

        elif request.method == 'GET':
            logger.info('[%s] %s - %s' % (request.gid, response.status, response.reason))

        elif request.method == 'HEAD':
            logger.info('[%s] %s - %s' % (request.gid, response.status, response.reason))

        elif request.method == 'OPTIONS':
            logger.info('[%s] options feedback' % request.gid)

        response.headers['X-Request-Id'] = request.gid
        return response
    return middleware_handler


# cors
async def cors_middleware_factory(app, handler):
    ACCESS_CONTROL_MAX_AGE = 60     # in seconds

    def validate_crossdomain_request(request):
        return request.headers.get('Origin','').endswith(CONST['domain']['default'])

    async def middleware_handler(request):
        if request.method == 'OPTIONS' and 'Access-Control-Request-Method' in request.headers:
            if validate_crossdomain_request(request):
                response = web.Response(status=200, content_type='text/html')
                response.headers['Access-Control-Max-Age'] = str(ACCESS_CONTROL_MAX_AGE)
                response.headers['Access-Control-Allow-Origin'] =  request.headers.get('Origin','')
                response.headers['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
                response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers','')
                #response.headers['Access-Control-Allow-Credentials'] = 'true'
                return response

        response = await handler(request)

        if not request.headers.get('Origin','').endswith(request.host) and validate_crossdomain_request(request):
            response.headers['Access-Control-Allow-Origin'] =  request.headers.get('Origin','')

        return response

    return middleware_handler


# override
def override_http_status(app):
    async def handle_404(request, response):
        return response

    async def handle_500(request, response):
        return response

    overrides = {
        404: handle_404,
        500: handle_500,
    }

    async def override_middleware_factory(app, handler):
        async def middleware_handler(request):
            try:
                response = await handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return response
                else:
                    return await override(request, response)

            except Exception as exc:
                if isinstance(exc,web.HTTPException):
                    response = exc
                elif isinstance(exc,(BizException,ThriftException,HttpException,RestException)):
                    return web.json_response({ 'err': exc.err, 'msg': exc.msg, 'log': exc.log })
                #elif isinstance(exc,asyncio.CancelledError):
                #    text = 'Ignored premature client disconnection'
                elif isinstance(exc,asyncio.TimeoutError):
                    return web.json_response({ 'err': -1, 'msg': 'Request Handler Timeout' })
                else:
                    return web.json_response({ 'err': -1, 'msg': 'Internal Error', 'log': traceback.format_exc() })

                override = overrides.get(response.status)
                if override is None:
                    raise
                else:
                    return await override(request, response)

        return middleware_handler
    return override_middleware_factory


def setup_startup(app,startup=[]):
    import logging
    logger = logging.getLogger('aiohttp.server')

    async def init_redis(app):
        import aioredis
        app['redis'] = {}
        for key in CONST['redis']:
            logger.info('Starting redis connection of %s ...' % key)
            value = CONST['redis'][key]
            app['redis'][key] = await aioredis.create_pool(
                loop=app.loop,
                address=(value['host'],value['port']),
                password=value['password'],db=value['db'],
                minsize=value['minsize'],maxsize=value['maxsize'])

    app.on_startup.append(init_redis)

    for func in startup:
        app.on_startup.append(func)


def setup_shutdown(app,shutdown=[]):
    import logging
    logger = logging.getLogger('aiohttp.server')

    async def close_redis(app):
        for key in CONST['redis']:
            logger.info('Closing redis connection of %s ...' % key)
            if app['redis'][key]:
                app['redis'][key].close()
                await app['redis'][key].wait_closed()
                del app['redis'][key]

    app.on_shutdown.append(close_redis)

    for func in shutdown:
        app.on_shutdown.append(func)


def setup_cleanup(app,cleanup):
    import logging
    logger = logging.getLogger('aiohttp.server')

    async def terminate_background_tasks(app):
        logger.info('Terminating background tasks')

    app.on_cleanup.append(terminate_background_tasks)

    for func in cleanup:
        app.on_cleanup.append(func)


def setup_prepare(app,prepare):
    async def on_prepare(request, response):
        #response.headers['key'] = 'value'
        pass

    app.on_response_prepare.append(on_prepare)

    for func in prepare:
        app.on_response_prepare.append(func)


def create_app(loop=None,
                middlewares=None,routes=None,templates=None,
                prepare=[],startup=[],shutdown=[],cleanup=[]):

    app = web.Application(loop=loop,debug=CONST['debug'])

    setup_startup(app,startup)
    setup_shutdown(app,shutdown)
    setup_cleanup(app,cleanup)

    setup_prepare(app,prepare)

    if middlewares:
        middlewares(app)

    if routes:
        routes(app)

    if templates:
        templates(app)

    return app


class Response(web.Response):
    def __init__(self, err=0,msg='',data={},log=''):
        result = dict(err=0,msg='',data={},log='')
        result.update({ 'err': err, 'msg': msg, 'data': data, 'log': log })
        super(Response,self).__init__(text=json.dumps(result),content_type='application/json')


def service(service_module,api_name):
    async def handler(request):
        if request.method == 'GET':
            data = {}
        elif request.method == 'POST':
            data = request.data
        else:
            data ={}

        data.update(request.match_info or {})

        try:
            with thrift_connect(service_module) as service_client:
                payload = Payload(gid=request.gid,auth=request.auth,device=request.device,data=data)
                api_invoker = getattr(service_client,api_name)
                result = api_invoker(payload)
            return Response(err=result.err,msg=result.msg,data=result.data,log=result.log)
        except ThriftException as exc:
            return web.json_response({ 'err': exc.err, 'msg': exc.msg, 'log': exc.log })
        except Exception as exc:
            return web.json_response({ 'err': -1, 'msg': 'Internal Error', 'log': traceback.format_exc() })

    return handler


