# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result
from core.utils.thrift import thrift_exempt
from core.utils.decorators import check_admin_auth

import json

from service.news.models import CrawlNewsArticle,CrawlSpiderStats



class CrawlHandler(ThriftHandler):
    def filter(self,request):
        duplicate = request.data.get('duplicate',1)
        tag = request.data.get('tag','')
        page = request.data.get('page') or { 'size': 20 }

        articles = CrawlNewsArticle.objects.filter(status__ne=0)

        if duplicate:
            articles = articles.filter(dtags__ne=tag)

        if tag:
            articles = articles.filter(tags=tag)

        base_id = page.get('base',{}).get('id')
        base = CrawlNewsArticle.objects.filter(id=base_id or '0'*24).first()

        if not base:
            total = articles.count()
            articles = articles.order_by('-published')[:page['size']]
        else:
            if page.get('action','N') == 'N':
                articles = articles.filter(published__gt=base.published)
                total = articles.count()
                articles = articles.order_by('-published')[max(0,articles.count()-page['size']):]
            else:
                articles = articles.filter(published__lt=base.published)
                total = articles.count()
                articles = articles.order_by('-published')[:page['size']]

        hot_articles = json.loads(REDIS['app'].get('news:hot') or '[]')
        hot_article_ids = [article['id'] for article in hot_articles]

        _articles = []
        for article in articles:
            if request.device.channel == 'app' and str(article.id) in hot_article_ids:
                continue

            _articles.append(article.digest())

        return Result(data=dict(articles=_articles,total=total))

    @check_admin_auth
    def remove(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = CrawlNewsArticle.objects.filter(id=article_id or '0'*24).first()
        if not article:
            raise BizException('新闻记录不存在')

        article.status = 0
        article.switch_db('crawl-primary').save()

        self.update_news_article_list(article, remove=True)
        return Result(msg='删除成功')

    def get_detail(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = CrawlNewsArticle.objects.filter(id=article_id or '0'*24).first()

        _article = article.detail() if article else None
        return Result(data=dict(article=_article))

    def get_multiple(self,request):
        article_ids = []
        for item in request.data['articles']:
            article_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(article_ids) > 100:
            raise BizException('记录数量超过上限')

        articles = CrawlNewsArticle.objects.filter(id__in=article_ids)

        _articles = [article.digest() for article in articles]
        return Result(data=dict(articles=_articles))

    @check_admin_auth
    def reset_duplicate(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = CrawlNewsArticle.objects.filter(id=article_id or '0'*24).first()
        if not article:
            raise BizException('新闻记录不存在')

        article.dtags = []
        article.dinfo = {}
        article.switch_db('crawl-primary').save()

        self.update_news_article_list(article)
        return Result(msg='重置成功')

    @check_admin_auth
    def get_stats(self,request):
        tag = request.data.get('tag',None)

        stats = CrawlSpiderStats.objects.all()
        if tag:
            stats = stats.filter(tag=tag)

        _stats = [item.json() for item in stats]
        return Result(data=dict(stats=_stats))

    @thrift_exempt
    def update_news_article_list(article, remove=False):
        for tag in article.tags:
            key = 'news:tag:%s:list' % tag
            value = json.dumps({
                'type': 'crawl',
                'data': { 'id': str(article.id) },
            }, sort_keys=True)

            if not remove:
                score = -int(article.published.timestamp()*1000)
                REDIS['app'].zadd(key, value, score)
            else:
                REDIS['app'].zrem(key, value)


