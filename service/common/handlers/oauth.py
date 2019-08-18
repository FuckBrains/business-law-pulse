# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result

import json,datetime,time,re,random,hashlib

import requests
requests.packages.urllib3.disable_warnings()




class OAuthHandler(ThriftHandler):
    def __init__(self):
        super(OAuthHandler,self).__init__()

        config = CONST['proxies']['default']
        self.proxies = {
            'http': 'http://%s:%s' % (config['http']['host'], config['http']['port']),
            'https': 'http://%s:%s' % (config['http']['host'], config['http']['port']),
        }

    def check_qq_access(self,request):
        access = request.data['access']

        # http://wiki.open.qq.com/wiki/website/获取用户OpenID_OAuth2.0
        params = { 'access_token': access['token'] }
        response = requests.get('https://graph.qq.com/oauth2.0/me', params=params, proxies=self.proxies, verify=False)
        if response.status_code != 200:
            raise BizException('网络异常')

        pattern = re.search('callback\((?P<value>.+)\);', response.text).groupdict()
        result = json.loads(pattern['value'])
        if result.get('error'):
            return Result(err=1,msg='ＱＱ验证失败',data=result)

        return Result(msg='验证成功')

    def check_weixin_access(self,request):
        access = request.data['access']

        # https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&id=open1419316518
        params = { 'access_token': access['token'], 'openid': access['openid'] }
        response = requests.get('https://api.weixin.qq.com/sns/auth', params=params, proxies=self.proxies, verify=False)
        if response.status_code != 200:
            raise BizException('网络异常')

        result = json.loads(response.text)
        if result['errcode']:
            return Result(err=1,msg='微信验证失败',data=result)

        return Result(msg='验证成功')

    def get_qq_access_by_code(self,request):
        code = request.data['code']
        redirect = request.data['redirect']

        config = CONST['oauth']['qq']['web']
        key = 'qq:%s:oauth:code' % config['id']

        info = REDIS['app'].hgetall(key)
        if not info:
            params = {
                'client_id': config['id'],
                'client_secret': config['secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect,
            }

            # http://wiki.open.qq.com/wiki/website/使用Authorization_Code获取Access_Token
            response = requests.get('https://graph.qq.com/oauth2.0/token', params=params, proxies=self.proxies, verify=False)
            if response.status_code != 200:
                raise BizException('网络异常')

            content = response.text.strip().strip(';')
            if re.search('callback\((?P<data>.*)\)',content):
                result = eval(content)
                raise BizException(result['error_description'])

            info = dict([param.split('=') for param in content.split('&')])
            REDIS['app'].hmset(key, info)
            REDIS['app'].expire(key, int(info['expires_in'])-60)

        # http://wiki.open.qq.com/wiki/website/获取用户OpenID_OAuth2.0
        params = { 'access_token': info['access_token'] }
        response = requests.get('https://graph.qq.com/oauth2.0/me', params=params, proxies=self.proxies, verify=False)
        if response.status_code != 200:
            raise BizException('网络异常')

        result = eval(response.text.strip().strip(';'))
        if result.get('error'):
            raise BizException(result['error_description'])

        access = {
            'openid': result['openid'],
            'token': result['access_token'],
        }

        return Result(data=dict(access=access))

    def get_weixin_access_by_code(self,request):
        code = request.data['code']

        config = CONST['oauth']['weixin']['mp' if request.device.is_weixin else 'web']
        key = 'weixin:%s:oauth:code' % config['id']

        info = REDIS['app'].hgetall(key)
        if not info:
            params = {
                'appid': config['id'],
                'secret': config['secret'],
                'code': code,
                'grant_type': 'authorization_code',
            }

            # http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
            response = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token', params=params, proxies=self.proxies, verify=False)
            if response.status_code != 200:
                raise BizException('网络异常')

            info = json.loads(response.text)
            if not info.get('openid'):
                raise BizException(json.dumps(info))

            REDIS['app'].hmset(key, info)
            REDIS['app'].expire(key, int(info['expires_in'])-60)

        access = {
            'openid': info['openid'],
            'token': info['access_token'],
        }

        return Result(data=dict(access=access))

    def get_weixin_access_by_credential(self,request):
        config = CONST['oauth']['weixin']['mp']
        key = 'weixin:%s:oauth:credential' % config['id']

        info = REDIS['app'].hgetall(key)
        if not info:
            params = {
                'appid': config['id'],
                'secret': config['secret'],
                'grant_type': 'client_credential',
            }

            # https://mp.weixin.qq.com/wiki?id=mp1421140183
            response = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=params, proxies=self.proxies, verify=False)
            if response.status_code != 200:
                raise BizException('网络异常')

            info = json.loads(response.text)
            REDIS['app'].hmset(key, info)
            REDIS['app'].expire(key, int(info['expires_in'])-60)

        access = {
            'token': info['access_token'],
        }

        return Result(data=dict(access=access))

    def sign_weixin_jsapi(self,request):
        config = CONST['oauth']['weixin']['mp']
        key = 'weixin:%s:oauth:credential' % config['id']

        access = REDIS['app'].hgetall(key)
        if not access:
            params = {
                'appid': config['id'],
                'secret': config['secret'],
                'grant_type': 'client_credential',
            }

            # http://mp.weixin.qq.com/wiki/15/54ce45d8d30b6bf6758f68d2e95bc627.html
            requests.packages.urllib3.disable_warnings()
            response = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=params, proxies=self.proxies, verify=False)
            if response.status_code != 200:
                raise BizException('网络异常')

            access = json.loads(response.text)
            REDIS['app'].hmset(key, access)
            REDIS['app'].expire(key, int(access['expires_in'])-60)

        key = 'weixin:%s:oauth:jsapi' % config['id']
        ticket = REDIS['app'].hgetall(key)
        if not ticket:
            params = {
                'access_token': access['access_token'],
                'type': 'jsapi',
            }

            self.logger.info('getticket: %s' % params)

            # https://mp.weixin.qq.com/wiki?id=mp1421141115
            response = requests.get('https://api.weixin.qq.com/cgi-bin/ticket/getticket', params=params, proxies=self.proxies, verify=False)
            if response.status_code != 200:
                raise BizException('网络异常')

            ticket = json.loads(response.text)
            REDIS['app'].hmset(key, ticket)
            REDIS['app'].expire(key, int(ticket['expires_in'])-60)

        sample = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        random.seed(time.time())
        nonceStr = ''.join([random.choice(sample) for i in range(0,16)])
        timestamp = int(datetime.datetime.now().timestamp())

        url = request.data['url']
        content = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (ticket['ticket'],nonceStr,timestamp,url)
        signature = hashlib.sha1(content.encode('utf8')).hexdigest()

        config = {
            'timestamp': timestamp,
            'nonceStr': nonceStr,
            'signature': signature,
        }

        return Result(data=dict(config=config))

    def get_qq_user_info(self,request):
        access = request.data['access']

        params = {
            'oauth_consumer_key': CONST['oauth']['qq'][request.device.channel]['id'],
            'access_token': access['token'],
            'openid': access['openid'],
            'format': 'json',
        }

        # http://wiki.open.qq.com/wiki/website/OpenAPI调用说明_OAuth2.0
        # http://wiki.connect.qq.com/get_user_info
        response = requests.get('https://graph.qq.com/user/get_user_info', params=params, proxies=self.proxies, verify=False)
        if response.status_code != 200:
            raise BizException('网络异常')

        result = json.loads(response.text)
        if result['ret'] != 0:
            return Result(err=1,msg='无法ＱＱ资料',data=result)

        avatar = result.get('figureurl_qq_2') or result.get('figureurl_qq_1') or result.get('figureurl_2') or result.get('figureurl_1')

        profile = {
            'nickname': result['nickname'],
            'gender': 'M' if result.get('gender','男')=='男' else 'F',
            'avatar': avatar,
            'openid': access['openid'],
        }

        return Result(data=dict(profile=profile))

    def get_weixin_user_info(self,request):
        access = request.data['access']

        params = {
            'access_token': access['token'],
            'openid': access['openid'],
        }

        # https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&id=open1419316518
        response = requests.get('https://api.weixin.qq.com/sns/userinfo', params=params, proxies=self.proxies, verify=False)
        if response.status_code != 200:
            raise BizException('网络异常')

        response.encoding = 'utf8'
        result = json.loads(response.text)
        if not result.get('openid',''):
            return Result(err=1,msg='无法微信资料',data=result)

        avatar = result.get('headimgurl')

        profile = {
            'nickname': result['nickname'],
            'gender': 'M' if result.get('sex',1)==1 else 'F',
            'avatar': avatar,
            'openid': result['openid'],
            'unionid': result.get('unionid',''),
        }

        return Result(data=dict(profile=profile))



