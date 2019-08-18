# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result



class PushHandler(ThriftHandler):
    def __init__(self):
        super(PushHandler, self).__init__()

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

        from service.common.utils.umeng import UMengPush
        self.umeng = UMengPush(logger=self.logger,proxies=self.proxies)

    def unicast(self,request):
        title = request.data['title']
        content = request.data.get('content','')
        url = request.data.get('url','')
        platform = request.data['platform']
        token = request.data['token']

        start_time = request.data.get('start_time')
        expire_time = request.data.get('expire_time')
        max_send_num = request.data.get('max_send_num')

        policy = self.umeng.construct_policy(platform,start_time,expire_time,max_send_num)

        custom = { 'type': 'info', 'url': url }
        feedback = self.umeng.submit_push(
                    type='unicast',platform=platform,
                    title=title,content=content,custom=custom,
                    policy=policy,tokens=[token])

        if feedback['result']['ret'] == 'SUCCESS':
            msg = '%s 提交成功' % ('Android' if platform=='android' else 'iOS')
        else:
            msg = feedback['result']['data']['error_text']

        return Result(msg=msg,data=feedback)

    def listcast(self,request):
        title = request.data['title']
        content = request.data.get('content','')
        url = request.data.get('url','')
        platform = request.data['platform']
        tokens = request.data['tokens']

        start_time = request.data.get('start_time')
        expire_time = request.data.get('expire_time')
        max_send_num = request.data.get('max_send_num')

        # maximum of 500 tokens
        if len(tokens) > 500:
            raise BizException('设备数量不能超过500')

        policy = self.umeng.construct_policy(platform,start_time,expire_time,max_send_num)

        custom = { 'type': 'info', 'url': url }
        feedback = self.umeng.submit_push(
                    type='listcast',platform=platform,
                    title=title,content=content,custom=custom,
                    policy=policy,tokens=tokens)

        if feedback['result']['ret'] == 'SUCCESS':
            msg = '%s 提交成功' % ('Android' if platform=='android' else 'iOS')
        else:
            msg = feedback['result']['data']['error_text']

        return Result(msg=msg,data=feedback)

    def broadcast(self,request):
        title = request.data['title']
        content = request.data.get('content','')
        url = request.data.get('url','')
        platform = request.data['platform']

        start_time = request.data.get('start_time')
        expire_time = request.data.get('expire_time')
        max_send_num = request.data.get('max_send_num')

        # prevent duplicate pushing
        key = 'push:broadcast:info:url:%s' % url
        if url and REDIS['app'].hget(key,platform):
            raise BizException('不能重复推送')

        policy = self.umeng.construct_policy(platform,start_time,expire_time,max_send_num)

        custom = { 'type': 'info', 'url': url }
        feedback = self.umeng.submit_push(
                    type='broadcast',platform=platform,
                    title=title,content=content,custom=custom,
                    policy=policy)

        if feedback['result']['ret'] == 'SUCCESS':
            REDIS['app'].hset(key, platform, request.gid)
            REDIS['app'].expire(key, 60*60)
            msg = '%s 提交成功' % ('Android' if platform=='android' else 'iOS')
        else:
            msg = feedback['result']['data']['error_text']

        return Result(msg=msg,data=feedback)


