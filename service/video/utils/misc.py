# -*- coding: utf-8 -*-

from core.conf import CONST

import json,re

import requests
requests.packages.urllib3.disable_warnings()

from bs4 import BeautifulSoup
from urllib.parse import urlparse


def parse_duration(duration_str):
    # xx:xx:xx
    if re.search('(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{2})', duration_str):
        pattern = re.search('(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{2})', duration_str).groupdict()
        duration = int(pattern['hour']) * 60 * 60 + int(pattern['minute']) * 60 + int(pattern['second'])

    # xx:xx
    elif re.search('(?P<minute>\d{1,2}):(?P<second>\d{2})', duration_str):
        pattern = re.search('(?P<minute>\d{1,2}):(?P<second>\d{2})', duration_str).groupdict()
        duration = int(pattern['minute']) * 60 + int(pattern['second'])

    else:
        duration = 0

    return duration


def extract_source(origin):

    PROXIES = {
        'http': 'http://%s:%s' % (
            CONST['proxies']['default']['http']['host'],
            CONST['proxies']['default']['http']['port']
        ),
        'https': 'http://%s:%s' % (
            CONST['proxies']['default']['http']['host'],
            CONST['proxies']['default']['http']['port']
        ),
    }

    HEADERS = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    }

    video = {'origin': origin, 'cover': ''}

    # le.com
    if origin.find('letv.com') != -1 or origin.find('le.com') != -1 or origin.find('lesports.com') != -1:
        if re.search('(related|record|highlights)/(?P<vid>\d+)', urlparse(origin).fragment):
            pattern = re.search('(video|related|record|highlights)/(?P<vid>\d+)', urlparse(origin).fragment).groupdict()
            vid = pattern['vid']
        else:
            response = requests.get(origin, timeout=5, headers=HEADERS, proxies=PROXIES, verify=False)
            soup = BeautifulSoup(response.content, 'lxml')
            node = soup.find(attrs={'id': 'SOHUCS'})
            vid = node.attrs.get('sid', '')
            video['origin'] = response.url

        response = requests.get('http://static.api.sports.letv.com/sms/v1/videos/%s?caller=1001' % vid, timeout=5, proxies=PROXIES, verify=False)
        result = json.loads(response.text)

        video['cover'] = list(result['data']['imageUrl'].items())[0][1]
        video['duration'] = int(result['data']['duration'])
        video['title'] = result['data']['name']
        video['description'] = result['data']['desc']
        # http://minisite.letv.com/tuiguang/index.shtml?vid=23544914&ark=100&autoPlay=none&isAutoPlay=0
        video['url'] = 'http://minisite.letv.com/tuiguang/index.shtml?vid=%s&ark=100' % vid

    # pptv.com
    elif origin.find('pptv.com') != -1:
        response = requests.get(origin, timeout=5, proxies=PROXIES, verify=False)
        soup = BeautifulSoup(response.content, 'lxml')
        scripts = soup.find_all('script')
        webcfg = {}
        for script in scripts:
            content = script.text.strip()
            if content.startswith('var webcfg ='):
                webcfg = json.loads(content.replace('var webcfg =', '').replace(';', ''))
                break

        video['url'] = 'http://player.aplus.pptv.com/corporate/proxy/proxy.html#id=%s&autoplay=1' % webcfg['id']
        video['duration'] = webcfg['duration']
        video['title'] = webcfg['title']
        video['description'] = webcfg['title']

    # youku.com
    elif origin.find('youku.com') != -1:
        response = requests.get(origin, timeout=5, proxies=PROXIES, verify=False)

        soup = BeautifulSoup(response.content, 'lxml')

        video['title'] = soup.find(attrs={'class': 'title'}).text.replace('\n', '').strip()
        video['description'] = soup.find('meta', attrs={'name': 'description'}).attrs['content']

        iframe = soup.find(id='link4').attrs['value']
        html = BeautifulSoup(iframe, 'lxml')
        video['url'] = html.find('iframe').attrs['src']

        url = 'http://play-ali.youku.com/play/get.json?ct=12&vid=%s' % video['url'].split('/')[-1]
        response = requests.get(url, timeout=5, proxies=PROXIES, verify=False)
        result = json.loads(response.text)
        video['image'] = result.get('data', {}).get('video', {}).get('logo', '')

    # qq.com
    elif origin.find('qq.com') != -1:
        response = requests.get(origin, timeout=5, proxies=PROXIES, verify=False)
        soup = BeautifulSoup(response.content, 'lxml')

        video['title'] = soup.find('meta', attrs={'itemprop': 'name'}).attrs['content']
        video['description'] = soup.find('meta', attrs={'itemprop': 'description'}).attrs['content']
        video['duration'] = int(soup.find('meta', attrs={'itemprop': 'duration'}).attrs['content'])
        video['image'] = soup.find('meta', attrs={'itemprop': 'image'}).attrs['content']

        parser = urlparse(origin)
        path = parser.path.split('/')[-1]
        vid = path.split('.')[0]
        video['url'] = 'http://v.qq.com/iframe/player.html?vid=%s&tiny=0&auto=0' % vid

    # iqiyi.com
    # elif origin.find('iqiyi.com') != -1:
    #    response = requests.get(origin, timeout=5, proxies=PROXIES, verify=False)
    #    soup = BeautifulSoup(response.content, 'lxml')
    #    div = soup.find(id='flashbox')
    #    vid = div.attrs['data-player-videoid']
    #    tvid = div.attrs['data-player-tvid']
    #    video['url'] = 'http://open.iqiyi.com/developer/player_js/coopPlayerIndex.html?vid=%s&tvId=%s' % (vid, tvid)

    # 新浪、搜狐、网易、土豆
    else:
        pass

    if video.get('url', ''):
        return video

    return None
