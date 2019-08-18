# -*- coding: utf-8 -*-

from core.utils.command import BaseCommand

from core.utils.setup import setup_redis,setup_mongo
setup_redis()
setup_mongo()

import json,datetime,time
import requests

from service.law.models import LawExchangeHistory



class ExchangeSource(BaseCommand):
    def handle(self, *args, **options):
        url = 'https://www.oanda.com/fx-for-business/historical-rates/api/getSources'
        response = requests.get(url)
        result = json.loads(response.text)
        sources = result['source_list']

        for source in sources:
            print(source)



class ExchangeCurrency(BaseCommand):
    def handle(self, *args, **options):
        currencies = {}

        url = 'https://www.oanda.com/fx-for-business/historical-rates/api/getCurrencies'
        headers = {
            'cookie': 'csrftoken=Oq9bp15VhdHvewolop7ggDF1sohBYzsqRDS04c3xu0Ojl2UuZMqCgZvTc6DdVKcE',
            'x-csrftoken': 'Oq9bp15VhdHvewolop7ggDF1sohBYzsqRDS04c3xu0Ojl2UuZMqCgZvTc6DdVKcE',
            'content-type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url,data={ 'source': 'OANDA' },headers=headers)
        result = json.loads(response.text)
        for item in result['currency_list']:
            if not item.get('label'):
                currencies[item['value']] = { 'name_cn': item['display'] }

        headers = {
            'cookie': 'csrftoken=LtLtAKaQM8zJlHfUQN3PBLQnzUpXpLpbOaCdHDe9QnmRrP5qDBm6Z5JkKzAk5uig',
            'x-csrftoken': 'LtLtAKaQM8zJlHfUQN3PBLQnzUpXpLpbOaCdHDe9QnmRrP5qDBm6Z5JkKzAk5uig',
            'content-type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url,data={ 'source': 'OANDA' },headers=headers)
        result = json.loads(response.text)
        for item in result['currency_list']:
            if not item.get('label'):
                currencies[item['value']].update({ 'name': item['display'] })

        print(currencies)
        """
        LawExchangeCurrency.objects.using('primary').delete()
        codes = list(currencies.keys())
        codes.sort()
        for code in codes:
            value = currencies[code]
            currency = LawExchangeCurrency()
            currency.code = code
            currency.name = value['name']
            currency.name_cn = value['name_cn']
            currency.switch_db('primary').save()
        """



# https://www.oanda.com/fx-for-business/historical-rates
class ExchangePeriod(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('quote', nargs='?', default='CNY')
        parser.add_argument('base', nargs='?', default='USD')
        parser.add_argument('-y', dest='year', nargs='?', default=0, type=int)
        parser.add_argument('-s', dest='start', nargs='?', default='2017-01-01')
        parser.add_argument('-e', dest='end', nargs='?', default='2017-01-01')

    def handle(self, *args, **options):
        if options.get('year'):
            start_date = '%s-01-01' % options['year']
            end_date = '%s-12-31' % options['year']
        else:
            start_date = options['start']
            end_date = options['end']

        url = 'https://www.oanda.com/fx-for-business/historical-rates/api/update/'
        params = dict(
            source='OANDA',
            display='absolute',
            adjustment='0',
            price='bid',
            view='graph',
            period='daily',
            start_date=start_date,
            end_date=end_date,
            quote_currency=options['quote'],
            base_currency_0=options['base'],
        )

        response = requests.get(url,params)
        result = json.loads(response.text)
        widget = result['widget'][0]
        data = widget['data']
        print('Exchange     : %s -> %s' % (options['quote'],options['base']))
        print('Start Date   : %s' % start_date)
        print('End Date     : %s' % end_date)
        data.sort(key=lambda x: x[0])
        for timestamp,rate in data:
            date = datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')
            rate = float(rate)
            print('%s   : %s' % (date,rate))



# https://www.oanda.com/currency/converter/
class ExchangeDate(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('quote', nargs='?', default='MOP')
        parser.add_argument('base', nargs='?', default='USD')
        parser.add_argument('-d', dest='date', nargs='?', default='1998-12-15')

    def handle(self, *args, **options):
        url = 'https://www.oanda.com/lang/cns/currency/converter/update'
        headers = {
            'x-requested-with': 'XMLHttpRequest',
        }
        params = dict(
            action='C',
            end_date=options['date'],
            quote_currency=options['quote'],
            base_currency_0=options['base'],
        )

        response = requests.get(url,params,headers=headers)
        result = json.loads(response.text)
        print('Exchange     : %s -> %s' % (options['quote'],options['base']))
        print('Date         : %s' % options['date'])
        print('Rate         : %s' % result['data']['bid_ask_data']['bid'])




# https://www.oanda.com/currency/converter/
class ExchangeCrawl(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('quote', nargs='?', default='CNY')
        parser.add_argument('base', nargs='?', default='USD')
        parser.add_argument('-s', dest='start_year', nargs='?', default=2017, type=int)
        parser.add_argument('-e', dest='end_year', nargs='?', default=1990, type=int)

    def get_result(self, params):
        url = 'https://www.oanda.com/lang/cns/currency/converter/update'
        headers = {
            'x-requested-with': 'XMLHttpRequest',
        }

        tries = 5
        response = None

        while tries:
            try:
                response = requests.get(url,params,headers=headers)
                break
            except Exception as exc:
                query = '&'.join(['='.join(item) for item in params.items()])
                print('[Failure] %s?%s' % (url,query))
                tries = tries - 1
                time.sleep(3)

        if not response:
            raise Exception('Over Tries')

        result = json.loads(response.text)
        return  result

    def save_history(self, year, logs):
        history = LawExchangeHistory.objects.filter(quote=self.quote,base=self.base,year=year).first()
        if not history:
            history = LawExchangeHistory(quote=self.quote,base=self.base,year=year)
            history.logs = logs

        history.switch_db('primary').save()


    def handle(self, *args, **options):
        #self.quote = options['quote']
        #self.base = options['base']

        #print('Exchange     : %s -> %s' % (self.quote,self.base))
        #start_date = datetime.datetime.strptime('%s-01-01' % (options['start_year']+1), '%Y-%m-%d')
        #end_date = datetime.datetime.strptime('%s-01-01' % options['end_year'], '%Y-%m-%d')

        currencies = [
            #'CNY', # 人民币
            #'HKD', # 港元
            'MOP', # 澳门元
            'TWD', # 台币
            #'USD', # 美元
            'CAD', # 加拿大元
            'EUR', # 欧元
            'GBP', # 英镑
            'CHF', # 瑞士法郎
            'RUB', # 俄罗斯卢布
            'AUD', # 澳大利亚元
            'NZD', # 新西兰元
            'JPY', # 日圆
            'KRW', # 韩元
            'SGD', # 新加坡元
            'INR', # 印度卢比
            'THB', # 泰铢
            'PHP', # 菲律宾比索
            'VND', # 越南盾
            'MYR', # 马来西亚林吉特
            'IDR', # 印尼盾
            'BRL', # 巴西雷亚尔
        ]

        for currency in currencies:
            self.quote = currency
            self.base = 'USD'
            print('Exchange     : %s -> %s' % (self.quote,self.base))

            logs = {}

            year = datetime.datetime.now().year
            while True:
                history = LawExchangeHistory.objects.filter(quote=self.quote,base=self.base,year=year).first()
                if history:
                    year = year - 1
                else:
                    break

            start_date = datetime.datetime.strptime('%s-01-01' % (year+1), '%Y-%m-%d')
            end_date = datetime.datetime.strptime('1990-01-01', '%Y-%m-%d')
            while start_date > end_date:
                start_date = start_date - datetime.timedelta(days=1)
                date_str = start_date.strftime('%Y-%m-%d')

                if start_date.date() >= datetime.datetime.now().date():
                    print('%s   : -' % date_str, flush=True)
                    continue

                params = dict(
                    action='C',
                    end_date=date_str,
                    quote_currency=self.quote,
                    base_currency_0=self.base,
                )

                result = self.get_result(params)
                rate = result['data']['bid_ask_data']['bid']
                print('%s   : %s' % (date_str,rate), flush=True)
                if rate == '-':
                    logs and self.save_history(start_date.year,logs)
                    break

                logs[date_str] = rate

                if start_date.month == 1 and start_date.day == 1:
                    logs and self.save_history(start_date.year,logs)
                    logs = {}





