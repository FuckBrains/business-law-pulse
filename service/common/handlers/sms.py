# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result
from core.utils.thrift import thrift_exempt

import datetime



class SmsHandler(ThriftHandler):
    def __init__(self):
        super(SmsHandler, self).__init__()

        self.config = CONST['sms']

        self.proxies = {
            'http': 'http://%s:%s' % (
                CONST['proxies']['default']['http']['host'],
                CONST['proxies']['default']['http']['port']
            ),
            'https': 'http://%s:%s' % (
                CONST['proxies']['default']['http']['host'],
                CONST['proxies']['default']['http']['port']
            ),
        }

        from service.common.utils.aliyun import AliyunSMS
        self.sms = AliyunSMS(self.config,self.proxies)

    def send_validation(self,request):
        cellphone = request.data['cellphone']
        validation = request.data['validation']
        scene = request.data['scene']

        now = int(datetime.datetime.now().timestamp()*1000)

        # check valid agent
        if not request.device or not self.check_valid_agent(request.device):
            return Result(data=dict(validation=validation,interval=self.config['interval']))

        # check ip frequency
        if not request.device or not self.check_ip_frequency(request.device.ip,now):
            return Result(data=dict(validation=validation,interval=self.config['interval']))

        # check cellphone frequency
        if not self.check_cellphone_frequency(cellphone,now):
            return Result(data=dict(validation=validation,interval=self.config['interval']))

        # check account frequency ( UserID / OpenID )
        account = request.data.get('account')
        if account is not None and not self.check_account_frequency(account,now):
            return Result(data=dict(validation=validation,interval=self.config['interval']))

        if CONST['env'] != 'local':
            # send sms
            payload = self.sms.build_payload(cellphone,params={ 'validation': validation })
            result = self.sms.send(payload,'POST')
            if not result:
                raise BizException('短信验证码发送失败')

        return Result(data=dict(interval=self.config['interval']))

    @thrift_exempt
    def check_valid_agent(self,device):
        if device.platform not in ('android','ios'):
            self.logger.error('[ SMS Error ] 非法的User-Agent')
            return False
        return True

    @thrift_exempt
    def check_ip_frequency(self,ip,now):
        return True
        limit = self.config['limit']['ip']
        key = 'sms:limit:ip:%s' % ip

        stats = []
        for item in REDIS['app'].lrange(key,0,-1) or []:
            if now - int(item) < limit['duration']*1000:
                stats.append(int(item))

        if len(stats) > 0 and now < stats[0]:
            self.logger.error('[ SMS Error ] 非法的系统时间')
            return False

        stats = [now] + stats
        stats = stats[:limit['count']]
        REDIS['app'].delete(key)
        REDIS['app'].lpush(key,*stats)
        REDIS['app'].expire(key, limit['duration'])

        if len(stats) > 1 and stats[0] - stats[1] < limit['duration']*1000:
            self.logger.error('[ SMS Error ] IP接收短信过于频繁')
            return False

        return True

    @thrift_exempt
    def check_cellphone_frequency(self,cellphone,now):
        limit = self.config['limit']['cellphone']
        key = 'sms:limit:cellphone:%s' % cellphone

        stats = []
        for item in REDIS['app'].lrange(key,0,-1) or []:
            if now - int(item) < limit['duration']*1000:
                stats.append(int(item))

        if len(stats) > 0 and now < stats[0]:
            self.logger.error('[ SMS Error ] 非法的系统时间')
            return False

        stats = [now] + stats
        stats = stats[:limit['count']]
        REDIS['app'].delete(key)
        REDIS['app'].lpush(key,*stats)
        REDIS['app'].expire(key, limit['duration'])

        if len(stats) > 1 and stats[0] - stats[1] < limit['duration']*1000:
            self.logger.error('[ SMS Error ] 手机接收短信过于频繁')
            return False

        return True

    @thrift_exempt
    def check_account_frequency(self,account,now):
        limit = self.config['limit']['account']
        key = 'sms:limit:account:%s' % account

        stats = []
        for item in REDIS['app'].lrange(key,0,-1) or []:
            if now - int(item) < limit['duration']*1000:
                stats.append(int(item))

        if len(stats) > 0 and now < stats[0]:
            self.logger.error('[ SMS Error ] 非法的系统时间')
            return False

        stats = [now] + stats
        stats = stats[:limit['count']]
        REDIS['app'].delete(key)
        REDIS['app'].lpush(key,*stats)
        REDIS['app'].expire(key, limit['duration'])

        if len(stats) > 1 and stats[0] - stats[1] < limit['duration']*1000:
            self.logger.error('[ SMS Error ] 帐号接收短信过于频繁')
            return False

        return True




