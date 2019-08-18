# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.thrift import ThriftHandler,Result
from core.utils.decorators import check_admin_auth

import json

from service.common.utils.launch import get_launch



class ConfigHandler(ThriftHandler):

    def get_global(self,request):
        markets = dict([(market['code'],market) for market in json.loads(REDIS['app'].get('config:markets') or '[]')])
        market = markets.get(request.device.market,{})
        market_version = tuple([int(num) for num in market.get('version','0.0.0').split('.')])
        fake = True if request.device.version > market_version else False
        fake_url = '%s://%s/fake/' % ('https' if CONST['ssl'] else 'http',CONST['domain']['www'])

        if request.device.platform == 'android':
            folder = 'release' if CONST['env'] == 'prd' else 'development'
            download_url = 'http://footballzone.oss-cn-shenzhen.aliyuncs.com/download/%s/latest/footballzone-%s.apk' % (folder,request.device.market or 'Alpha')
        elif request.device.platform == 'ios':
            download_url = 'https://itunes.apple.com/us/app/zu-qiu-de-dai/id1114039638'
        else:
            download_url = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.footballzone.android'

        upgrade = {
            'type': 'upgrade',
            'version': market.get('version','0.0.0'),
            'force': market.get('force',0),
            'title': '发现新版本 v%s' % market.get('version','0.0.0'),
            'content': market.get('content',''),
            'url': download_url,
        }

        launch = get_launch()

        config = {
            'fake': fake_url if fake else '',
            'upgrade': upgrade,
            'launch': launch,
            'mqtt': CONST['mqtt']['app'],
            'push': { 'upgrade': upgrade, 'launch': launch },   # deprecated
        }

        return Result(data={ 'config': config })

    @check_admin_auth
    def list_market(self,request):
        markets = json.loads(REDIS['app'].get('config:markets') or '[]')
        return Result(data={ 'markets': markets })

    @check_admin_auth
    def update_market(self,request):
        markets = request.data['markets']
        REDIS['app'].set('config:markets', json.dumps(markets))
        return Result(msg='更新成功')


