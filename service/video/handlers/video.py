# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Payload,Result,IDL_DIR
from core.utils.thrift import thrift_connect,thrift_exempt
from core.utils.decorators import check_admin_auth

import os,datetime,time,re,random
from urllib.parse import urlparse
from mongoengine import Q

import thriftpy
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

from service.video.utils.tag import CATEGORIES
from service.video.models import Video


class VideoHandler(ThriftHandler):

    @thrift_exempt
    @property
    def default_cover(self):
        if hasattr(self,'_default_cover'):
            return self._default_cover

        module,app = self.__class__.__module__.split('.')[:2]
        name = self.__class__.__name__
        gid = '%s.%s.%s' % (module,app,name)
        with thrift_connect(service=common_thrift.ImageService) as image_service:
            payload = Payload(gid=gid,data=dict(scene='video/cover',path='images/default/video_cover.png'))
            result = image_service.construct(payload)
            self._default_cover = result.data['image']

        return self._default_cover

    def categorize(self,request):
        return Result(data=dict(categories=CATEGORIES))

    def filter(self,request):
        tag = request.data.get('tag','')
        keyword = request.data.get('keyword','').strip()
        page = request.data.get('page') or { 'size': 20 }

        videos = Video.objects.filter(status__ne=0)

        if tag:
            videos = videos.filter(tags=tag)

        if keyword:
            videos = videos.filter(title__icontains=keyword)

        _videos = []

        if tag == '视频':
            total = videos.count()
            for i in range(0,min(total,20)):
                video = videos[random.randint(0,total-1)]
                _video = video.digest()
                if _video not in _videos:
                    _videos.append(_video)

            return Result(data=dict(videos=_videos,total=total))

        if page.get('no'):
            total = videos.count()
            start,end = (page['no']-1)*page['size'], page['no']*page['size']
            videos = videos.order_by('-created','title')[start:end]
        else:
            base_id = page.get('base',{}).get('id')
            base = Video.objects.filter(id=base_id or '0'*24).first()

            if not base:
                total = videos.count()
                videos = videos.order_by('-created','title')[:page['size']]
            else:
                if page.get('action','N') == 'N':
                    videos = videos.filter(created__gt=base.created)
                    total = videos.count()
                    videos = videos.order_by('-created','title')[max(0,total-page['size']):]
                else:
                    videos = videos.filter(created__lt=base.created)
                    total = videos.count()
                    videos = videos.order_by('-created','title')[:page['size']]

        _videos = [video.digest() for video in videos]
        return Result(data=dict(videos=_videos,total=total))

    @check_admin_auth
    def create(self,request):
        video = Video()

        title = request.data.get('title','').strip()
        if not title:
            raise BizException('新闻标题不能为空')

        video.title = title.strip()

        cover = request.data.get('cover','')
        if cover:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=cover))
                result = image_service.extract(payload)
                image = result.data['image']
                video.cover = image or self.default_cover

        description = request.data.get('description','').strip()
        video.description = description

        duration = int(request.data.get('duration',0))
        video.duration = duration

        reference = request.data.get('reference','').strip()
        video.reference = reference

        url = request.data.get('url','').strip()
        video.url = url

        random.seed(time.time())
        video.view = random.randint(100,500)

        tags = request.data.get('tags',[])
        tags = list(set([tag.strip() for tag in tags]))
        video.tags = [tag for tag in filter(lambda x: x not in ('视频','集锦','录播'), tags)]

        type = int(request.data.get('type',0))
        if type == 0:
            video.tags.append('视频')
            video.mode = 1
        elif type == 1:
            video.tags.append('集锦')
            video.mode = 2
        elif type == 2:
            video.tags.append('录播')
            video.mode = 2

        video.switch_db('primary').save()
        return Result(msg='添加成功',data=video.digest())

    @check_admin_auth
    def update(self,request):
        video_id = request.data['video']['id'] if isinstance(request.data['video'],dict) else request.data['video']
        video = Video.objects.filter(id=video_id or '0'*24).first()
        if not video:
            raise BizException('视频记录不存在')

        cover = request.data.get('cover',None)
        if cover:
            with thrift_connect(service=common_thrift.ImageService) as image_service:
                payload = Payload(gid=request.gid,data=dict(image=cover))
                result = image_service.extract(payload)
                image = result.data['image']
                if image:
                    video.cover = image

        title = request.data.get('title',None)
        if title is not None:
            video.title = title.strip()

        description = request.data.get('description',None)
        if description is not None:
            video.description = description.strip()

        schedule = request.data.get('schedule',None)
        if schedule is not None:
            video.schedule = schedule.strip()

        reference = request.data.get('reference',None)
        if reference is not None:
            video.reference = reference.strip()

        url = request.data.get('url',None)
        if url is not None:
            video.url = url.strip()

        duration = request.data.get('duration',None)
        if duration is not None:
            video.duration = int(duration)

        type = request.data.get('type',None)
        tags = request.data.get('tags',None)
        if type is not None and tags is not None:
            type = int(type)
            tags = list(set([tag.strip() for tag in tags]))
            video.tags = [tag for tag in filter(lambda x: x not in ('视频','集锦','录播'), tags)]

            if type == 0:
                video.tags.append('视频')
                video.mode = 1
            elif type == 1:
                video.tags.append('集锦')
                video.mode = 2
            elif type == 2:
                video.tags.append('录播')
                video.mode = 2

        video.switch_db('primary').save()
        return Result(msg='修改成功')

    @check_admin_auth
    def remove(self,request):
        video_id = request.data['video']['id'] if isinstance(request.data['video'],dict) else request.data['video']
        video = Video.objects.filter(id=video_id or '0'*24).first()
        if not video:
            raise BizException('视频记录不存在')

        video.status = 0
        video.switch_db('primary').save()
        return Result(msg='删除成功')

    def thumbup(self,request):
        video_id = request.data['video']['id'] if isinstance(request.data['video'],dict) else request.data['video']
        video = Video.objects.filter(id=video_id or '0'*24).first()
        if not video:
            raise BizException('视频记录不存在')

        video.thumbup += 9
        video.switch_db('default-primary').save()
        return Result(msg='点赞成功')

    def bind_program(self,request):
        program = request.data['program']
        video_ids = request.data['videos']
        videos = Video.objects.filter(id__in=video_ids)
        videos.using('primary').update(created=datetime.datetime.fromtimestamp(program['start']/1000))
        return Result(msg='绑定成功')

    def get_detail(self,request):
        video_id = request.data['video']['id'] if isinstance(request.data['video'],dict) else request.data['video']
        video = Video.objects.filter(id=video_id or '0'*24).first()

        _video = video.detail() if video else None
        return Result(data=dict(video=_video))

    def view(self,request):
        video_id = request.data['video']['id'] if isinstance(request.data['video'],dict) else request.data['video']
        video = Video.objects.filter(id=video_id or '0'*24).first()
        if not video:
            raise BizException('视频记录不存在')

        video.view = video.view + 9
        video.switch_db('primary').save()
        return Result(msg='更新成功')

    def get_multiple(self,request):
        video_ids = []
        for item in request.data['videos']:
            video_ids.append(item['id'] if isinstance(item,dict) else item)

        if len(video_ids) > 100:
            raise BizException('记录数量超过上限')

        videos = Video.objects.filter(id__in=video_ids)

        _videos = [video.digest() for video in videos]
        return Result(data=dict(videos=_videos))

    def adjust_created(self,request):
        video_ids = request.data['videos']
        created = request.data['created']

        Video.objects.using('primary').filter(id__in=video_ids).update(created=created)
        return Result(msg='更新成功')

    def list_relavant(self,request):
        video_id = request.data['video']['id'] if isinstance(request.data['video'],dict) else request.data['video']
        video = Video.objects.filter(id=video_id or '0'*24).first()
        if not video:
            raise BizException('视频记录不存在')

        videos = Video.objects.filter(status__ne=0)

        tags = video.tags

        if '视频' in tags:
            tags.remove('视频')
            videos = videos.filter(tags='视频')

        if '集锦' in tags:
            tags.remove('集锦')
            videos = videos.filter(tags='集锦')

        if '录播' in tags:
            tags.remove('录播')
            videos = videos.filter(tags='录播')

        query = Q()
        for tag in tags:
            query = query | Q(tags=tag)

        videos = videos.filter(query)

        _videos = []
        total = videos.count()
        for i in range(0,min(total,10)):
            video = videos[random.randint(0,total-1)]
            _video = video.digest()
            if _video not in _videos:
                _videos.append(_video)

        _videos.sort(key=lambda x: -x['created'])
        return Result(data=dict(videos=_videos))

    def inject_script(self,request):
        url = request.data['url']
        mode = request.data.get('mode',0)

        parser = urlparse(url)
        hostname = parser.hostname

        path = ''

        # ballbar.cc
        if url and mode == 1 and parser.hostname.endswith('ballbar.cc'):
            path = 'ballbar/1.js'

        # 5chajian.com
        elif mode == 1 and hostname.endswith('5chajian.com'):
            path = '5chajian/1.js'

        # jrszhibo.com & tmiaoo.com
        elif mode == 1 and (hostname.endswith('tmiaoo.com') or hostname.endswith('jrszhibo.com')):
            path = 'jrszhibo/1.js'

        # tiantiantv.tv
        elif hostname.endswith('tiantian.tv'):
            if mode == 1:
                path = 'tiantiantv/1.js'
            else:
                path = 'tiantiantv/2.js'

        # pptv.com
        elif hostname.endswith('pptv.com'):
            if mode == 1:
                path = 'pptv/1.js'
            else:
                path = 'pptv/2.js'

        # le.com
        elif mode == 1 and (hostname.endswith('le.com') or hostname.endswith('letv.com')):
            path = 'le/1.js'

        # qq.com
        elif mode == 1 and hostname.endswith('qq.com'):
            path = 'qq/1.js'

        # youku.com
        elif mode == 1 and hostname.endswith('youku.com'):
            path = 'youku/1.js'

        # sina.com
        elif mode == 1 and (hostname.endswith('sina.com') or hostname.endswith('sina.com.cn')):
            path = 'sina/1.js'

        script = ''
        if path:
            path = os.path.join(os.path.dirname(__file__), os.path.pardir, 'scripts', path)
            script = open(path, 'r').read()

        self.logger.debug(script)

        script = re.sub('\n','',script)
        script = re.sub('\s+',' ',script)
        return Result(data=dict(script=script))

    def extract_webpage(self,request):
        url = request.data['url']

        from service.video.utils.misc import extract_source
        video = extract_source(url)
        if not video:
            raise BizException('无法提取视频')

        return Result(data=dict(video=video))



