# -*- coding: utf-8 -*-

from scrapy.conf import settings

import os,sys,json,datetime,time
import random,re,io,calendar,requests
from PIL import Image

from pyvirtualdisplay import Display
from selenium import webdriver

from news.models import EmbeddedImage,EmbeddedThumbnail



class BrowserGenerator:
    driver = None
    device = None
    display = None
    browser = None

    def __init__(self,driver,device):
        self.driver = driver
        self.device = device

    def __enter__(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        if self.driver == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('--user-agent='+USER_AGENTS[self.driver][self.device])

            self.browser = webdriver.Chrome(chrome_options=options)

        elif self.driver == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.set_preference('intl.accept_languages', 'zh-CN')
            profile.set_preference('general.useragent.override', USER_AGENTS[self.driver][self.device])
            #profile.set_preference('network.proxy.type', 1);
            #profile.set_preference('network.proxy.http', yourProxy);
            #profile.set_preference('network.proxy.http_port', yourPort);
            #profile.set_preference('network.proxy.no_proxies_on', '');

            self.browser = webdriver.Firefox(firefox_profile=profile)

        #self.browser.set_page_load_timeout(10)

        return self.browser
 
    def __exit__(self, type, value, trace):
        if self.browser:
            self.browser.quit()

        if self.display:
            self.display.stop()



def open_browser(driver,device):
    return BrowserGenerator(driver,device)




def get_useragent_headers(device):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Connection': 'keep-alive',
    }

    headers.update({ 
        'User-Agent': settings['USER_AGENTS'][settings['BROWSER_DRIVER']][device]
    })

    return headers



def is_future_time(target_time):
    return True if target_time > datetime.datetime.now() + datetime.timedelta(days=1) else False



def parse_publish_time(time_str):

    # x分钟前
    if re.search('(?P<minute>\d+)分钟前',time_str):
        pattern = re.search('(?P<minute>[0-9]+)分钟前',time_str).groupdict()
        published = datetime.datetime.now()-datetime.timedelta(minutes=int(pattern['minute']))

    # x小时前
    elif re.search('(?P<hour>\d+)小时前',time_str):
        pattern = re.search('(?P<hour>\d+)小时前',time_str).groupdict()
        published = datetime.datetime.now()-datetime.timedelta(hours=int(pattern['hour']))

    # x天前
    elif re.search('(?P<day>\d+)天前',time_str):
        pattern = re.search('(?P<day>\d+)天前',time_str).groupdict()
        published = datetime.datetime.now()-datetime.timedelta(days=int(pattern['day']))

    # x月前
    elif re.search('(?P<month>\d+)月前',time_str):
        pattern = re.search('(?P<month>\d+)月前',time_str).groupdict()
        published = datetime.datetime.now()-datetime.timedelta(days=int(pattern['month']) * 30)

    # x年前
    elif re.search('(?P<year>\d+)年前',time_str):
        pattern = re.search('(?P<year>\d+)年前',time_str).groupdict()
        published = datetime.datetime.now()-datetime.timedelta(days=int(pattern['year']) * 365)

    # xxxx-xx-xx xx:xx | xxxx/xx/xx xx:xx | xxxx.xx.xx xx:xx | xxxx年xx月xx日 xx:xx
    elif re.search('(?P<year>\d{4})(年|-|\/|\.)(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})',time_str):
        pattern = re.search('(?P<year>\d{4})(年|-|\/|\.)(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})',time_str).groupdict()
        time_str = '%s-%s-%s %s:%s' % (pattern['year'],pattern['month'],pattern['day'],pattern['hour'],pattern['minute'])
        published = datetime.datetime.strptime(time_str,'%Y-%m-%d %H:%M')

    # xx-xx xx:xx | xx/xx xx:xx | xx.xx xx:xx | xx月xx日 xx:xx
    elif re.search('(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})',time_str):
        pattern = re.search('(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})',time_str).groupdict()
        time_str = '%s-%s-%s %s:%s' % (datetime.datetime.now().year,pattern['month'],pattern['day'],pattern['hour'],pattern['minute'])
        published = datetime.datetime.strptime(time_str,'%Y-%m-%d %H:%M')

    # xxxx-xx-xx | xxxx/xx/xx | xxxx.xx.xx | xxxx年xx月xx日
    elif re.search('(?P<year>\d{4})(年|-|\/|\.)(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?',time_str):
        pattern = re.search('(?P<year>\d{4})(年|-|\/|\.)(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?',time_str).groupdict()
        time_str = '%s-%s-%s' % (pattern['year'],pattern['month'],pattern['day'])
        published = datetime.datetime.strptime(time_str,'%Y-%m-%d')

    # xx-xx | xx/xx | xx.xx | xx月xx日
    elif re.search('(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?',time_str):
        pattern = re.search('(?P<month>\d{1,2})(月|-|\/|\.)(?P<day>\d{1,2})(日)?',time_str).groupdict()
        time_str = '%s-%s-%s' % (datetime.datetime.now().year,pattern['month'],pattern['day'])
        published = datetime.datetime.strptime(time_str,'%Y-%m-%d')

    # xx:xx
    elif re.search('(?P<hour>\d{1,2}):(?P<minute>\d{2})',time_str):
        pattern = re.search('(?P<hour>\d{1,2}):(?P<minute>\d{2})',time_str).groupdict()
        time_str = '%s %s:%s' % (datetime.datetime.now().strftime('%Y-%m-%d'),pattern['hour'],pattern['minute'])
        published = datetime.datetime.strptime(time_str,'%Y-%m-%d %H:%M')

    else:
        published = None

    if published and is_future_time(published):
        if calendar.isleap(datetime.datetime.now().year):
            published = published - datetime.timedelta(days=366)
        else:
            published = published - datetime.timedelta(days=365)

    return published 
        
        


def parse_video_duration(duration_str):
    # xx:xx:xx
    if re.search('(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{2})',duration_str):
        pattern = re.search('(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{2})',duration_str).groupdict()
        duration = int(pattern['hour'])*60*60 + int(pattern['minute'])*60 + int(pattern['second'])

    # xx:xx
    elif re.search('(?P<minute>\d{1,2}):(?P<second>\d{2})',duration_str):
        pattern = re.search('(?P<minute>\d{1,2}):(?P<second>\d{2})',duration_str).groupdict()
        duration = int(pattern['minute'])*60 + int(pattern['second'])

    else:
        duration = 0

    return duration
        
        

def get_random_proxies():
    if not settings['SQUID_PROXIES']:
        return {}

    random.seed(time.time())
    proxy = settings['SQUID_PROXIES'][random.randint(0,len(settings['SQUID_PROXIES'])-1)]

    return {
        'http': 'http://%s:%s' % (proxy['host'],proxy['port']),
        'https': 'https://%s:%s' % (proxy['host'],proxy['port']),
    }



def redirect_url(origin,headers={},times=1,timeout=3):
    url = origin
    for i in range(0,times):
        if not settings['USE_PROXY']:
            response = requests.get(url,headers=headers,timeout=3,verify=False)
        else:
            response = requests.get(url,headers=headers,timeout=3,proxies=get_random_proxies(),verify=False)

        url = response.url

    return url



def download_image(url):
    # supplement domain for '//'
    if url.startswith('//'):
        url = 'http:%s' % url

    # filter 'data:image'
    if url.startswith('data:image'):
        url = ''

    # csrf for bbsstaticoss.hoopchina.com.cn
    if url.startswith('https://bbsstaticoss.hoopchina.com.cn/'):
        url = 'http://img04.store.sogou.com/net/a/46/link?appid=46&url=' + url

    if not url:
        return None

    if not settings['USE_PROXY']:
        response = requests.get(url,verify=False)
    else:
        response = requests.get(url,proxies=get_random_proxies(),verify=False)

    if response.status_code == 404:
        return None

    url = response.url

    # filter image in case of holder image
    if len(response.content) < 1024:
        return None

    im = Image.open(io.BytesIO(response.content))
    width,height = im.size

    # filter image in case of iconic or logo
    if width < 75 or height < 75:
        return None

    # filter image in case of portrait image
    if width/height < 0.75:
        return None

    image = EmbeddedImage(id=uuid.uuid1().hex)
    image.scene = 'info/news/cover'
    image.path = url
    image.width = width
    image.height = height
    image.size = len(response.content)
    image.thumbnails = [EmbeddedThumbnail(width=width,height=height,path=image.path) for i in range(0,2)]
    image.created = datetime.datetime.now()

    return image




