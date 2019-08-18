# -*- coding: utf-8 -*-

from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os,json,datetime

import thriftpy
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

from service.news.models import EditNewsArticle



class EditHandler(ThriftHandler):

    @thrift_exempt
    @property
    def default_cover(self):
        if hasattr(self,'_default_cover'):
            return self._default_cover

        module,app = self.__class__.__module__.split('.')[:2]
        name = self.__class__.__name__
        gid = '%s.%s.%s' % (module,app,name)
        with thrift_connect(service=common_thrift.ImageService) as image_service:
            payload = Payload(gid=gid,data=dict(scene='news/cover',path='images/default/video_cover.png'))
            result = image_service.construct(payload)
            self._default_cover = result.data['image']

        return self._default_cover

    def filter(self,request):
        keyword = request.data.get('keyword', '').strip()
        page = request.data.get('page') or { 'size': 20 }

        articles = EditNewsArticle.objects.filter(status__ne=0)

        if keyword:
            articles = articles.filter(title__icontains=keyword)

        if page.get('no'):
            total = articles.count()
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            articles = articles.order_by('-published')[start:end]
        else:
            base_id = page.get('base',{}).get('id')
            base = EditNewsArticle.objects.filter(id=base_id or '0'*24).first()

            if not base:
                total = articles.count()
                articles = articles.order_by('-published')[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    articles = articles.filter(published__gt=base.published)
                    total = articles.count()
                    articles = articles.order_by('-published')[max(0,total-page['size']):]
                else:
                    articles = articles.filter(published__lt=base.published)
                    total = articles.count()
                    articles = articles.order_by('-published')[:page['size']]

        _articles = [article.digest() for article in articles]
        return Result(data=dict(articles=_articles,total=total))

    @check_admin_auth
    def create(self,request):
        article = EditNewsArticle()

        cover = request.data.get('cover','')
        if cover:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=cover))
                result = image_service.extract(payload)
                cover = result.data['image']

        article.cover = cover or self.default_cover

        title = request.data.get('title','').strip()
        if not title:
            raise BizException('新闻标题不能为空')

        article.title = title

        content = request.data.get('content','')
        article.content = content

        summary = request.data.get('summary','').strip()
        article.summary = summary

        tags = request.data.get('tags',[])
        article.tags = list(set([tag.strip() for tag in tags]))

        published = request.data.get('published',0)
        article.published = datetime.datetime.fromtimestamp(published/1000.0)

        article.switch_db('edit-primary').save()

        self.update_news_article_list(article)
        return Result(msg='提交成功')

    @check_admin_auth
    def update(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = EditNewsArticle.objects.filter(id=article_id or '0'*24).first()
        if not article:
            raise BizException('新闻记录不存在')

        cover = request.data.get('cover',None)
        if cover:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=cover))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    EditNewsArticle.cover = image

        title = request.data.get('title',None)
        if title is not None and title.strip():
            article.title = title.strip()

        content = request.data.get('content',None)
        if content is not None:
            article.content = content

        summary = request.data.get('summary',None)
        if summary is not None and summary.strip():
            article.summary = summary.strip()

        tags = request.data.get('tags',None)
        if tags is not None:
            article.tags = list(set([tag.strip() for tag in tags]))

        published = request.data.get('published',None)
        if published:
            article.published = datetime.datetime.fromtimestamp(published/1000.0)

        article.switch_db('edit-primary').save()

        self.update_news_article_list(article)
        return Result(msg='提交成功')

    @check_admin_auth
    def remove(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = EditNewsArticle.objects.filter(id=article_id or '0'*24).first()
        if not article:
            raise BizException('新闻记录不存在')

        article.status = 0
        article.switch_db('edit-primary').save()

        self.update_news_article_list(article, remove=True)
        return Result(msg='提交成功')

    def get_detail(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = EditNewsArticle.objects.filter(id=article_id or '0'*24).first()

        _article = article.detail() if article else None
        return Result(data=dict(article=_article))

    def get_multiple(self,request):
        article_ids = []
        for item in request.data['articles']:
            article_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(article_ids) > 100:
            raise BizException('记录数量超过上限')

        articles = EditNewsArticle.objects.filter(id__in=article_ids)

        _articles = [article.digest() for article in articles]
        return Result(data=dict(articles=_articles))

    def view(self,request):
        article_id = request.data['article']['id'] if isinstance(request.data['article'],dict) else request.data['article']
        article = EditNewsArticle.objects.filter(id=article_id or '0'*24).first()
        if not article:
            raise BizException('新闻记录不存在')

        article.view = article.view + 9
        article.switch_db('edit-primary').save()
        return Result(msg='更新成功')

    @thrift_exempt
    def update_news_article_list(self, article, remove=False):
        for tag in article.tags:
            key = 'news:tag:%s:list' % tag
            value = json.dumps({
                'type': 'news',
                'data': { 'id': str(article.id) },
            }, sort_keys=True)

            if not remove:
                score = -int(article.published.timestamp()*1000)
                REDIS['app'].zadd(key, score, value)
            else:
                REDIS['app'].zrem(key, value)
