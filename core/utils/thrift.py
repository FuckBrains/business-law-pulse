# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.exceptions import BizException,ThriftException

import os,re,uuid,traceback,pickle

import logging
logger = logging.getLogger('thriftpy')

from functools import wraps

import thriftpy
from thriftpy.transport import TTransportException
from thriftpy.thrift import TProcessor,TMultiplexedProcessor,TClient,TApplicationException
from thriftpy.transport import TBufferedTransportFactory,TSocket
from thriftpy.protocol import TBinaryProtocolFactory,TMultiplexedProtocolFactory

IDL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'idl'))

thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift



class Device(common_thrift.Device):
    MARKETS = {
        'AppStore'      : 'AppStore',
        'Alpha'         : 'Alpha',
        'Tencent'       : '腾讯应用宝',
        'Wandoujia'     : '豌豆荚',
        'Qihoo'         : '奇虎360',
        'Baidu'         : '百度手机助手',
        'PP'            : 'PP助手',
        'Xiaomi'        : '小米',
        'Meizu'         : '魅族',
        'Huawei'        : '华为',
        'Vivo'          : 'vivo',
        'Oppo'          : 'OPPO',
        'Lenovo'        : '联想',
        'Letv'          : '乐视',
        'Gionee'        : '金立',
        'HiMarket'      : '安卓市场',
        'GooglePlay'    : '谷歌市场',
    }

    def __init__(self, device=None):
        self.agent = ''
        self.ip = '0.0.0.0'
        self.port = 0

        if device:
            self.agent = device.agent
            self.ip = device.ip
            self.port = device.port

    @property
    def is_mobile(self):
        features = ['Android', 'iPhone', 'iPad', 'iPod', 'Windows Phone', 'Symbian', 'BlackBerry']
        matcher = re.search('|'.join(features), self.agent, re.I)
        return True if matcher else False

    @property
    def is_weixin(self):
        matcher = re.search('MicroMessenger', self.agent, re.I)
        return True if matcher else False

    @property
    def platform(self):
        # ios / android / web / unknown
        if self.agent.startswith(CONST['name']):
            if re.search('iPhone|iPad|iPod', self.agent, re.I):
                return 'ios'
            elif re.search('Android', self.agent, re.I):
                return 'android'
        elif re.search('Mozilla', self.agent, re.I):
            return 'web'

        return 'unknown'

    @property
    def channel(self):
        # app / web / unknown
        platform = self.platform
        if platform in ('ios','android'):
            return 'app'

        return platform

    @property
    def version(self):
        regexp = '%s\/(?P<x>\d{1,3})\.(?P<y>\d{1,3})\.(?P<z>\d{1,3})' % CONST['name']
        matcher = re.search(regexp, self.agent)
        if matcher:
            pattern = matcher.groupdict()
            return (int(pattern['x']),int(pattern['y']),int(pattern['z']))

        return (0,0,0)

    @property
    def market(self):
        regexp = 'Market\/(?P<market>[A-Za-z0-9]+)'
        matcher = re.search(regexp, self.agent, re.I)
        if matcher:
            pattern = matcher.groupdict()
            return pattern['market']

        return ''

    def __str__(self):
        return 'Device(agent=\'%s\', ip=\'%s\', port=%s)' % (self.agent,self.ip,self.port)

    def __repr__(self):
        return self.__str__()



class Upstream(common_thrift.Upstream):
    def __init__(self, app='', host='', ip='0.0.0.0', mac=''):
        self.app = app
        self.host = host
        self.ip = ip
        self.mac = mac

    def __str__(self):
        return 'Upstream(app=\'%s\', host=\'%s\', ip=\'%s\', mac=\'%s\')' % (self.app,self.host,self.ip,self.mac)

    def __repr__(self):
        return self.__str__()



class Payload(common_thrift.Payload):
    def __init__(self, gid, upstream=None, device=None, auth=None, data={}):
        self.auth = None
        self.upstream = None
        self.device = None
        self._data = {}

        if not gid:
            raise BizException('Payload gid is empty')

        self.gid = gid
        self.sid = uuid.uuid1().hex[:16]

        if auth:
            if isinstance(auth,common_thrift.Auth):
                self.auth = auth
            elif auth.__class__.__module__ == 'common' and auth.__class__.__name__ == 'Auth':
                self.auth = auth
            elif isinstance(auth,dict):
                self.auth = common_thrift.Auth(type=auth['type'], id=auth['id'], token=auth['token'])

        if device:
            if isinstance(auth,dict):
                self.device = common_thrift.Device(agent=device['agent'],ip=device['ip'],port=device['port'])
            elif isinstance(device,Device):
                self.device = common_thrift.Device(agent=device.agent,ip=device.ip,port=device.port)
            elif isinstance(device,common_thrift.Device):
                self.device = device

        if upstream:
            self.upstream = upstream

        if data:
            assert isinstance(data,dict)
            self._data = data

        encode_data = pickle.dumps(self._data)
        super(Payload, self).__init__(gid=self.gid,sid=self.sid, upstream=self.upstream, auth=self.auth,device=self.device, data=encode_data)

    def __str__(self):
        return 'Payload(gid=\'%s\', sid=\'%s\', upstream=\'%s\', auth=%s, device=%s, data=%s)' % (self.gid,self.sid,self.upstream,self.auth,self.device,self._data)

    def __repr__(self):
        return self.__str__()


class Result(common_thrift.Result):
    def __init__(self, data={}, err=0, msg='', log=''):
        assert isinstance(err,int)
        assert isinstance(msg,str)
        assert isinstance(log,str)
        assert isinstance(data,dict)
        self._data = data
        encode_data = pickle.dumps(self._data)
        super(Result, self).__init__(err=err,data=encode_data,msg=msg,log=log)

    def __str__(self):
        return 'Result(err=%s, msg=\'%s\', data=%s, log=%s)' % (self.err,self.msg,self._data,self.log)

    def __repr__(self):
        return self.__str__()


class ThriftLogger(object):
    def __init__(self,gid):
        self.gid = gid
        self.sid = '0'*16

    def update(self,gid,sid):
        self.gid = gid
        self.sid = sid

    def debug(self,msg):
        logger.debug('[%s:%s] %s' % (self.gid,self.sid,msg))

    def info(self,msg):
        logger.info('[%s:%s] %s' % (self.gid,self.sid,msg))

    def warn(self,msg):
        logger.warn('[%s:%s] %s' % (self.gid,self.sid,msg))

    def error(self,msg):
        logger.error('[%s:%s] %s' % (self.gid,self.sid,msg))

    def critical(self,msg):
        logger.critical('[%s:%s] %s' % (self.gid,self.sid,msg))

    def __str__(self):
        return 'ThriftLogger(gid=\'%s\', sid=\'%s\')' % (self.gid,self.sid)

    def __repr__(self):
        return self.__str__()


class ThriftHandlerMeta(type):
    class Request(object):
        def __init__(self, handler, payload):
            self.handler = handler
            self.gid = payload.gid
            self.sid = payload.sid
            self.upstream = payload.upstream
            self.auth = payload.auth

            if payload.device:
                self.device = Device(payload.device)
            else:
                self.device = None

            self.raw_data = payload.data
            self.data = pickle.loads(self.raw_data)

        def new_payload(self, auth=None, data={}):
            cls = self.handler.__class__
            app = '%s.%s' % (cls.__module__,cls.__name__)
            upstream = Upstream(app=app,host=self.handler.hostname,ip=self.handler.ip,mac=self.handler.mac)
            payload = Payload(gid=self.gid,auth=auth or self.auth,upstream=upstream,device=self.device,data=data)
            return payload

        def __str__(self):
            return 'Request(handler=%s, gid=\'%s\', sid=\'%s\', auth=%s, upstream=\'%s\', device=%s, data=%s)' % (
                    self.handler,self.gid,self.sid,self.auth,self.upstream,self.device,self.data)

        def __repr__(self):
            return self.__str__()

    @classmethod
    def wrap_func(cls, func):
        def pre_handle_logging(handler,request):
            handler.logger.info('REQ <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

            handler.logger.info('upstream : %s' % request.upstream)

            if request.auth:
                handler.logger.info('auth : %s' % request.auth)

            if request.device:
                handler.logger.info('device : %s' % request.device)

            if request.data:
                handler.logger.info('data : %s' % request.data)

            handler.logger.info('handler : %s' % func.__qualname__)

        def post_handle_logging(handler,request,result):
            handler.logger.info('RES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

            if result.err:
                handler.logger.info('err : %s' % result.err)

            if result.msg:
                handler.logger.info('msg : %s' % result.msg)

            if result.log:
                handler.logger.info('log : %s' % result.log)

        def call(handler,func,request):
            try:
                result = func(handler,request)
            except Exception as exc:
                if isinstance(exc,(BizException,ThriftException)):
                    result = common_thrift.Result(err=exc.err,msg=exc.msg,log=exc.log)
                else:
                    log = traceback.format_exc()
                    result = common_thrift.Result(err=-1,msg='Internal Error',log=log)

            return result

        def decorator(func):
            @wraps(func)
            def wrapped_func(self,*_args,**_kwargs):
                # ignore thrift_exempt functions
                if getattr(func,'thrift_exempt',False):
                    return func(self,*_args,**_kwargs)

                arg = _args[0]
                if isinstance(arg,cls.Request):
                    # internal invocation
                    request = arg
                    result = call(self,func,request)
                else:
                    # external invocation
                    request = cls.Request(self,arg)
                    self.logger.update(request.gid, request.sid)

                    pre_handle_logging(self,request)
                    result = call(self,func,request)
                    post_handle_logging(self,request,result)

                return result
            return wrapped_func
        return decorator(func)

    def __new__(cls, clsname, superclasses, attributedict):
        for key in attributedict:
            if not key.startswith('_') and hasattr(attributedict[key], '__call__'):
                method = attributedict[key]
                attributedict[key] = cls.wrap_func(method)
        return type.__new__(cls, clsname, superclasses, attributedict)


class ThriftHandler(object, metaclass=ThriftHandlerMeta):
    def __init__(self):
        cls = self.__class__
        self.logger = ThriftLogger(gid='%s.%s.__init__' % (cls.__module__,cls.__name__))

        import socket
        self.hostname = socket.getfqdn(socket.gethostname())

        import fcntl,struct
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        request = 0x8915    # SIOCGIFADDR
        packed = struct.pack('256s', 'eth0'.encode('utf8'))
        result = fcntl.ioctl(sock.fileno(), request, packed)[20:24]
        self.ip = socket.inet_ntoa(result)

        import uuid
        hexstr = uuid.UUID(int=uuid.getnode()).hex[-12:]
        self.mac = ':'.join([hexstr[x:x+2] for x in range(0,11,2)])

    def __str__(self):
        return '%s()' % self.__class__.__name__

    def __repr__(self):
        return self.__str__()


class ThriftProcessor(TProcessor):
    def __init__(self, service, handler):
        super(ThriftProcessor, self).__init__(service, handler)

    def process_in(self, iprot):
        api, seqid, result, call = super(ThriftProcessor, self).process_in(iprot)
        remote = iprot.trans.sock.getpeername()
        logger.debug('[ %s ] : %s' % (api,remote))
        return api, seqid, result, call


class ThriftMultiplexedProcessor(TMultiplexedProcessor):
    def register_processor(self, service_name, processor):
        super(ThriftMultiplexedProcessor, self).register_processor(service_name, processor)

    def process_in(self, iprot):
        api, seqid, result, call = super(ThriftMultiplexedProcessor, self).process_in(iprot)
        if isinstance(result,TApplicationException):
            if result.type == TApplicationException.UNKNOWN_METHOD:
                logger.error('Service with %s not registered in processors' % api)

        remote = iprot.trans.sock.getpeername()
        logger.debug('[ %s ] : %s' % (api,remote))
        return api, seqid, result, call


class ThriftClient(TClient):
    class _Result(object):
        def __init__(self, result):
            self.err = result.err
            self.msg = result.msg
            self.log = result.log
            self._data = result.data
            self.data = {}
            if self._data:
                self.data = pickle.loads(self._data)

    def __init__(self, service, multiplex='', timeout=60*5):
        self.service = service
        self.thrift_module = self.service.__module__
        self.service_name = self.service.__name__

        config = CONST['thrift'].get(self.thrift_module)

        if not config:
            raise Exception('Empty config for thrift module : %s' % self.thrift_module)

        if not config['service'].get(self.service_name,{}):
            raise Exception('Empty config for service name : %s.%s' % (self.thrift_module,self.service_name))

        self.host = config['host']
        self.port = config['port']
        self.multiplex = config['service'][self.service_name].get('multiplex','')

        timeout = timeout if timeout is None else timeout*1000  # in ms
        socket = TSocket(self.host, self.port, socket_timeout=timeout)

        trans_factory = TBufferedTransportFactory()
        transport = trans_factory.get_transport(socket)

        proto_factory = TBinaryProtocolFactory()
        if self.multiplex:
            proto_factory = TMultiplexedProtocolFactory(proto_factory,service_name=self.multiplex)

        protocol = proto_factory.get_protocol(transport)

        try:
            transport.open()
        except TTransportException as exc:
            msg = '%s.%s connection failure' % (self.thrift_module,self.service_name)
            log = traceback.format_exc()
            raise ThriftException(err=-1,msg=msg,log=log)

        self.sockname = socket.sock.getsockname()
        super(ThriftClient, self).__init__(self.service,protocol)

    def _req(self, _api, *_args, **_kwargs):
        logger.debug('[ %s.%s ] api : %s' % (self.thrift_module,self.service_name,_api))
        logger.debug('[ %s.%s ] sockname : %s' % (self.thrift_module,self.service_name,self.sockname))
        logger.debug('[ %s.%s ] args : %s' % (self.thrift_module,self.service_name,_args))
        logger.debug('[ %s.%s ] kwargs : %s' % (self.thrift_module,self.service_name,_kwargs))

        result = None
        try:
            result = super(ThriftClient, self)._req(_api, *_args, **_kwargs)
        except TTransportException as exc:
            msg = '%s.%s invocation failure' % (self.thrift_module,self.service_name)
            log = traceback.format_exc()
            raise ThriftException(err=-1,msg=msg,log=log)

        if not result:
            return result

        thrift_result = self._Result(result)
        if thrift_result.err:
            raise ThriftException(thrift_result)

        return thrift_result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        if exc_type is None:
            return

    def __str__(self):
        return 'ThriftClient(service=%s, sockname=%s)' % (self.service, self.sockname)

    def __repr__(self):
        return self.__str__()


def thrift_connect(service, multiplex='', timeout=60*5):
    return ThriftClient(service, multiplex=multiplex, timeout=timeout)


def thrift_exempt(func):
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        wrapped_func.thrift_exempt = True
        return wrapped_func
    return decorator(func)


