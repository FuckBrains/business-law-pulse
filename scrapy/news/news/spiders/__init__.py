# -*- coding: utf-8 -*-

# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.


from scrapy.spiders import Spider


class NewsSpider(Spider):
    name = ''
    action = { }
    config = { }

    websites = {
        'anjielaw': '安杰律师事务所',
        'dachenglaw': '大成律师事务所',
        'deheng': '德衡律师事务所',
        'glo': '环球律师事务所',
        'gslaw': '广盛律师事务所',
        'grandall': '国浩律师事务所',
        'grandwaylaw': '国枫律师事务所',
        'haiwen': '海问律师事务所',
        'hylandslaw': '浩天信和律师事务所',
        'jiayuan': '嘉源律师事务所',
        'unitalenlaw': '集佳律师事务所',
        'allbrightlaw': '锦天城律师事务所',
        'celg': '京衡律师事务所',
        'jingtian': '竞天公诚律师事务所',
        'solton': '索通律师事务所',
        'tahota': '泰和泰律师事务所',
        'tiantailaw': '天驰君泰律师事务所',
        'concord': '天达共和律师事务所',
        'vtlaw': '万商天勤律师事务所',
        'coeffort': '协力律师事务所',
        'shujin': '广东信达律师事务所',
        'zhonglun': '中伦律师事务所',
        'zhonglunwende': '中伦文德律师事务所',
        'zhongyinlawyer': '中银律师事务所',
        'huashang': '华商律师事务所',
        'yslawfirm': '上海元始律师事务所',
        'zhongmaolawyers': '中茂律师事务所',
        'gaopenglaw': '高朋律师事务所',
        'guantao': '观韬律师事务所',
        'hiwayslaw': '海华永泰律师事务所',
    }

    def __init__(self, *args, **kwargs):
        self.start_urls = self.config.keys()

        modules = self.__class__.__module__.split('.')
        code = modules[2]

        if code in self.websites:
            self.website = self.websites[code]
        else:
            raise Exception('Unknown website')

        super(Spider,self).__init__(*args, **kwargs)


    def parse(self, response):
        entry = self.action['entry']
        fetch = self.action['fetch']
        return entry(response, fetch)




