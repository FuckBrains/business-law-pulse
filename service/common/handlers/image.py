# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils import REDIS
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result,IDL_DIR
from core.utils.thrift import thrift_exempt

import os,json,datetime,time
import re,random,uuid,tempfile,io,subprocess

import thriftpy
thriftpy.load(os.path.join(IDL_DIR,'common.thrift'), module_name='common_thrift')
import common_thrift

import requests
requests.packages.urllib3.disable_warnings()

from urllib.parse import urlparse

from PIL import Image
#from PIL import ImageFile
#ImageFile.LOAD_TRUNCATED_IMAGES = True



class ImageHandler(ThriftHandler):
    storage = None

    content_types = {
        ('image/jpeg','JPEG'),
        ('image/png','PNG'),
        ('image/bmp','BMP'),
        ('image/gif','GIF'),
        ('image/webp','WEBP'),
    }

    def __init__(self):
        super(ImageHandler, self).__init__()
        from core.utils.storage import instantiate_storage
        self.storage = instantiate_storage()

    def store(self,request):
        scene = request.data['scene']
        path = request.data['path']
        name = request.data.get('name','')

        content = self.storage.open(path)
        image = self.save(content,name,scene)
        self.storage.delete(path)

        REDIS['cache'].set('image:%s:store' % image['id'], json.dumps(image), ex=60*60*12)  # 12 hours
        return Result(data={ 'image': image })

    def download(self,request):
        scene = request.data['scene']
        url = request.data['url']

        if not url:
            return Result(data={ 'image': None })

        try:
            proxies = None if CONST['env'] == 'local' else self.random_proxy()
            response = requests.get(url, proxies=proxies, verify=False, timeout=10)
            if response.status_code != 200:
                raise Exception('HTTP code : %s' % response.status_code)
        except:
            return Result(data={ 'image': None })

        content_type = response.headers.get('content-type','')
        if content_type not in dict(self.content_types):
            return Result(data={ 'image': None })

        name = urlparse(url).path.split('/')[-1]
        if not re.search('.+\.(?P<format>((?i)(jpg|jpeg|png|bmp|gif|webp)))$',name):
            name = uuid.uuid1().hex + '.' + content_type.split('/')[1]

        content = tempfile.NamedTemporaryFile()
        for chunk in response.iter_content(chunk_size=1024*512):
            content.write(chunk)

        image = self.save(content,name,scene)
        content.close()

        REDIS['cache'].set('image:%s:store' % image['id'], json.dumps(image), ex=60*60*12)  # 12 hours
        return Result(data={ 'image': image })

    def extract(self,request):
        image_id = request.data['image'] if isinstance(request.data['image'],str) else request.data['image']['id']
        image = json.loads(REDIS['cache'].get('image:%s:store' % image_id) or 'null')
        return Result(data={ 'image': image })

    def construct(self,request):
        scene = request.data['scene']
        path = request.data['path']

        _, ext = os.path.splitext(path)
        ext = ext[1:].upper()

        image = {
            'id': '',
            'name': '',
            'type': 'JPEG' if ext == 'JPG' else ext,
            'scene': scene,
            'url': self.storage.url(path),
            'size': 0,
            'width': 0,
            'height': 0,
            'created': int(datetime.datetime.now().timestamp()*1000),
            'thumbnails': [],
        }

        for dimension in common_thrift.SCENE[scene]:
            image['thumbnails'].append({ 'url': self.storage.url(path), 'width': 0, 'height': 0 })

        return Result(data={ 'image': image })

    def remove(self,request):
        image = request.data['image']

        path = self.get_path_from_url(image['url'])
        self.storage.delete(path)
        for thumbnail in image['thumbnails']:
            path = self.get_path_from_url(thumbnail['url'])
            self.storage.delete(path)

        return Result(msg='删除成功')

    @thrift_exempt
    def get_path_from_url(self,url):
        prefix = '%s://%s/media/' % ('https' if CONST['ssl'] else 'http', CONST['domain']['www'])
        path = url[len(prefix):] if url.startswith(prefix) else ''
        return path

    @thrift_exempt
    def save(self,content,name,scene):
        im = Image.open(content)

        try:
            output = io.BytesIO()
            im.save(output, im.format, quality=100)
        except:
            # PIL can not process highly compressed image
            raise BizException('无法识别图片格式')

        #if im.format == 'WEBP':
        #    embed.type = 'PNG'

        #    output = io.BytesIO()
        #    im.save(output, 'PNG', quality=100)

        #    output.seek(0)
        #    im = Image.open(output)

        if im.format not in ('JPEG','PNG','BMP','GIF'):
            raise BizException('无法识别图片类型')

        origin_path = uuid.uuid1().hex + '.' + im.format.lower()
        origin_path = os.path.join(scene,datetime.datetime.now().strftime('%Y/%m%d/%H%M'), origin_path)

        path = self.storage.save(content,origin_path,name)

        (width, height) = im.size

        image = {
            'id': uuid.uuid1().hex,
            'name': name,
            'type': im.format,
            'scene': scene,
            'url': self.storage.url(path),
            'width': width,
            'height': height,
            'thumbnails': [],
        }

        for dimension in common_thrift.SCENE[scene]:
            if dimension[0]>im.size[0] or dimension[1]>im.size[1]:
                (width, height) = im.size
            else:
                ratio = max(dimension[0]/im.size[0], dimension[1]/im.size[1])
                width = int(im.size[0]*ratio)
                height = int(im.size[1]*ratio)

            if im.format == 'GIF':
                output = tempfile.NamedTemporaryFile()

                # http://www.lcdf.org/gifsicle/man.html
                # gifsicle --no-warnings --resize 150x100 -o output.gif target.gif
                cmd = 'gifsicle --no-warnings --resize %sx%s -o %s %s' % (width,height,output.name,content.name)
                process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdoutdata, stderrdata) = process.communicate()
                error = stderrdata.decode('utf8').replace('\n','')
                if error:
                    output.close()
                    content.close()
                    raise BizException(error)

            # JPEG / PNG / BMP
            else:
                #output = tempfile.NamedTemporaryFile()
                output = io.BytesIO()

                #imc = im.copy()
                #imc.thumbnail(dimension, Image.ANTIALIAS)
                imc = im.resize((width, height), Image.ANTIALIAS)
                imc.save(output, im.format, quality=100)

                """
                if im.format == 'JPEG':
                    cmd = 'jpegoptim %s' % output.name
                elif im.format == 'PNG':
                    cmd = 'optipng %s' % output.name

                if im.format != 'BMP':
                    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (stdoutdata, stderrdata) = process.communicate()
                    error = stderrdata.decode('utf8').replace('\n','')
                    if error and error.lower().find('error') != -1:
                        output.close()
                        content.close()
                        raise BizException(error)
                """

            output.seek(0)
            path = self.storage.save(output,origin_path,name)
            output.close()

            image['thumbnails'].append({
                'url': self.storage.url(path),
                'width': width,
                'height': height,
            })

        content.close()
        return image

    @thrift_exempt
    def random_proxy(self):
        random.seed(time.time())
        proxies = CONST['squid']
        proxy = proxies[random.randint(0,len(proxies)-1)]

        return {
            'http': 'http://%s:%s' % (proxy['host'],proxy['port']),
            'https': 'https://%s:%s' % (proxy['host'],proxy['port']),
        }



