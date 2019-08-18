# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.thrift import ThriftHandler,Result
from core.utils.thrift import thrift_exempt

import json



class GeoHandler(ThriftHandler):

    def get_globe(self,request):
        continents = json.loads(REDIS['app'].get('geo:globe') or '[]')
        return Result(data=dict(globe=continents))

    def get_country(self,request):
        country_code = request.data.get('country', 'CN')
        divisions = json.loads(REDIS['app'].get('geo:country:%s' % country_code) or '[]')
        return Result(data=dict(storage=divisions))

    def parse(self,request):
        country = self.get_china()
        divisions = json.loads(REDIS['app'].get('geo:country:%s' % country['code']) or '[]')
        division = dict([(item['name'],item) for item in divisions]).get(request.data['division']) or { 'cities': [] }
        city = dict([(item.name,item) for item in division['cities']]).get(request.data['city'])
        return Result(data=dict(division={ 'id': division['id'], 'name': division['name'] }, city=city))

    @thrift_exempt
    def get_china(self):
        continents = json.loads(REDIS['app'].get('geo:globe') or '[]')
        continent = dict([(item.name,item) for item in continents]).get('亚洲') or { 'countries': [] }
        country = dict([(item.name,item) for item in continent['countries']]).get('中国') or { 'code': 'CN', 'name': '中国' }
        return country


