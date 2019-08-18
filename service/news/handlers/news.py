# -*- coding: utf-8 -*-

from service.news.conf.const import CATEGORIES
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os,json,re
from urllib.parse import urlparse

import thriftpy
thriftpy.load(os.path.join(IDL_DIR, 'common.thrift'), module_name='common_thrift')
import common_thrift

thriftpy.load(os.path.join(IDL_DIR, 'news.thrift'), module_name='news_thrift')
import news_thrift

from service.news.models import CrawlNewsArticle,EditNewsArticle



class NewsHandler(ThriftHandler):
    def filter(self, request):
        # compatible for app legacy version
        if request.device.channel == 'app' and request.device.version < (1,4,0):
            with thrift_connect(service=news_thrift.CrawlService) as crawl_service:
                payload = Payload(gid=request.gid,data=request.data,device=request.device)
                result = crawl_service.filter(payload)

            articles = result.data['articles']
            total = result.data['total']
            return Result(data=dict(articles=articles,total=total))

        tag = request.data.get('tag','')
        page = request.data.get('page') or { 'size': 20 }

        key = 'news:tag:%s:list' % tag
        start = 0
        end = 0

        size = page['size']
        base = page.get('base')
        if not base:
            start = 0
            end = size-1
        else:
            value = json.dumps({
                'type': base['type'],
                'data': { 'id': base['id'] }
            }, sort_keys=True)
            rank = REDIS['app'].zrank(key,value)
            rank = 0 if rank is None else rank+1

            if page.get('action','N') == 'N':
                if not rank:
                    start = 0
                    end = size-1
                else:
                    start = 0 if rank<size else rank-size
                    end = rank-1
            else:
                total = REDIS['app'].zcard(key)
                if not rank:
                    start = total
                    end = total
                else:
                    start = rank+1
                    end = total if total<=rank+size else rank+size

        values = [json.loads(value) for value in REDIS['app'].zrange(key,start,end)]

        hot_articles = json.loads(REDIS['app'].get('news:hot') or '[]')
        hot_article_ids = [article['id'] for article in hot_articles]

        crawl_article_ids = [value['data']['id'] for value in values if value['type'] == 'news/crawl']
        crawl_articles = CrawlNewsArticle.objects.filter(id__in=crawl_article_ids).filter(id__nin=hot_article_ids)
        crawl_article_bulk = dict([(str(article.id),article.digest()) for article in crawl_articles])

        edit_article_ids = [value['data']['id'] for value in values if value['type'] == 'news/edit']
        edit_articles = EditNewsArticle.objects.filter(id__in=edit_article_ids).filter(id__nin=hot_article_ids)
        edit_article_bulk = dict([(str(article.id),article.digest()) for article in edit_articles])

        articles = []
        for value in values:
            if value['type'] == 'news/crawl':
                if value['data']['id'] in crawl_article_bulk:
                    articles.append({ 'type': value['type'], 'data': crawl_article_bulk[value['data']['id']] })
            elif value['type'] == 'news/edit':
                if value['data']['id'] in edit_article_bulk:
                    articles.append({ 'type': value['type'], 'data': edit_article_bulk[value['data']['id']] })

        return Result(data=dict(articles=articles,total=0))

    def list_hot(self, request):
        articles = self.get_hot_articles()
        _articles = []
        for article in articles:
            if request.device.platform in ('android','ios') and request.device.version < (1,5,0):
                if article['type'] == 'news/crawl':
                    _article = article['data']
                    _article['website'] = { 'name': _article['website'] }
                    _article.update({ 'label': article['label'] })
                    _articles.append(_article)
            else:
                _articles.append(article)

        return Result(data=dict(articles=_articles))

    @check_admin_auth
    def add_hot(self, request):
        article_id = request.data['article']
        type = request.data['type']

        if type == 'news/crawl':
            article = CrawlNewsArticle.objects.filter(id=article_id).first()
            if not article:
                raise BizException('新闻记录不存在')

            if '最新' in article.dtags:
                raise BizException('不能添加重复新闻')

        else:
            article = EditNewsArticle.objects.filter(id=article_id).first()
            if not article:
                raise BizException('新闻记录不存在')

        hot_items = json.loads(REDIS['app'].get('news:hot') or '[]')
        hot_crawl_article_ids = [item['id'] for item in hot_items if item['type']=='news/crawl']
        hot_manual_article_ids = [item['id'] for item in hot_items if item['type']=='news/edit']
        if article_id in hot_crawl_article_ids or article_id in hot_manual_article_ids:
            raise BizException('已添加此新闻')

        hot_items.append({ 'type': type, 'id': article_id, 'label': '推荐' })
        REDIS['app'].set('news:hot',json.dumps(hot_items))

        articles = self.get_hot_articles()
        _articles = []
        for article in articles:
            if request.device.platform in ('android','ios') and request.device.version < (1,5,0):
                if article['type'] == 'news/crawl':
                    _article = article['data']
                    _article.update({ 'label': article['label'] })
                    _articles.append(_article)
            else:
                _articles.append(article)

        with thrift_connect(common_thrift.MqttService) as mqtt_service:
            payload = Payload(gid=request.gid, data=dict(
                topic='news/hot',
                body={
                    'articles': _articles
                },
            ))
            result = mqtt_service.push(payload)
            #AsyncThread(name='mqtt_service.push', target=mqtt_service.push, args=(payload,), thread_logger=self.logger).start()

        return Result(msg='提交成功')

    @check_admin_auth
    def update_hot(self, request):
        articles = request.data['articles']
        REDIS['app'].set('news:hot', json.dumps(articles))
        return Result(msg='提交成功')

    def categorize(self, request):
        tags = []
        for category in CATEGORIES:
            tags += category['tags']

        tag_map = dict([(tag['name'],tag) for tag in tags])
        default_tags = ['中超', '英超', '西甲', '意甲', '德甲', '法甲', '欧冠', '亚冠']
        defaults = [tag_map[item] for item in default_tags]

        return Result(data=dict(categories=CATEGORIES,defaults=defaults))

    def inject_script(self, request):
        url = request.data['url']

        parser = urlparse(url)
        hostname = parser.hostname

        path = ''

        # footballzone.com
        if hostname.endswith('footballzone.com'):
            path = 'footballzone/1.js'

        # hupu.com
        elif hostname.endswith('hupu.com'):
            path = 'hupu/1.js'

        # 163.com
        elif hostname.endswith('163.com'):
            path = '163/1.js'

        # sina.cn
        elif hostname.endswith('sina.cn') or hostname.endswith('sina.com.cn'):
            path = 'sina/1.js'

        # sohu.com
        elif hostname.endswith('sohu.com'):
            path = 'sohu/1.js'

        # zhibo8.cc
        elif hostname.endswith('zhibo8.cc'):
            path = 'zhibo8/1.js'

        script = ''
        if path:
            path = os.path.join(os.path.dirname(__file__), os.path.pardir, 'scripts', path)
            script = open(path,'r').read()

        self.logger.debug(script)

        script = re.sub('\n','',script)
        script = re.sub('\s+',' ',script)
        return Result(data=dict(script=script))

    @thrift_exempt
    def get_hot_articles(self):
        hot_items = json.loads(REDIS['app'].get('news:hot') or '[]')

        hot_crawl_article_ids = [item['id'] for item in hot_items if item['type']=='news/crawl']
        hot_crawl_articles = CrawlNewsArticle.objects.filter(id__in=hot_crawl_article_ids)
        hot_crawl_article_bulk = dict([(str(article.id),article.digest()) for article in hot_crawl_articles])

        hot_manual_article_ids = [item['id'] for item in hot_items if item['type']=='news/edit']
        hot_manual_articles = EditNewsArticle.objects.filter(id__in=hot_manual_article_ids)
        hot_manual_article_bulk = dict([(str(article.id),article.digest()) for article in hot_manual_articles])

        articles = []
        for item in hot_items:
            if item['type'] == 'news/crawl':
                article = hot_crawl_article_bulk[item['id']]
            else:
                article = hot_manual_article_bulk[item['id']]

            articles.append({
                'type': item['type'],
                'label': item['label'],
                'data': article,
            })

        return articles
