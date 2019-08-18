# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.thrift import ThriftHandler,Result
from core.utils.decorators import check_admin_auth

import json

from service.law.utils.stats import compute_firm_ranking
from service.law.models import LawConfig



class ConfigHandler(ThriftHandler):
    def __init__(self):
        super(ConfigHandler,self).__init__()

    def load(self,request):
        keys = request.data.get('keys',[])
        if not keys:
            keys = ['categories','industries','areas','parties','roles']

        config = dict([(
            key,json.loads(REDIS['app'].get('law:config:%s' % key) or 'null')
        ) for key in keys])

        return Result(data=config)

    @check_admin_auth(permissions=['update_law_config'])
    def update(self,request):
        key = request.data.get('key','')
        value = request.data.get('value',None)

        config = LawConfig.objects.filter(key='law:config:%s' % key).first()
        if not config:
            config = LawConfig(key='law:config:%s' % key)

        config.value = value
        config.switch_db('primary').save()

        REDIS['app'].set('law:config:%s' % key, json.dumps(value))

        if key == 'formula' and value:
            compute_firm_ranking()

        return Result(msg='修改成功')



