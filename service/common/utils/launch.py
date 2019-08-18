# -*- coding: utf-8 -*-

from core.utils import REDIS

import json,datetime



def get_launch():
    launches = json.loads(REDIS['app'].get('push:launch') or '[]')
    if not launches:
        return None
    now_time = datetime.datetime.now().timestamp()*1000
    launches_c = launches[:]
    for l in launches:
        if l['end'] > now_time >= l['start']:
            return {
                'image': l.get('image'),
                'countdown': l.get('countdown'),
                'url': l.get('url'),
                'expire': l.get('end')
            }
        elif now_time >= l['end']:
            launches_c.pop(launches_c.index(l))
            REDIS['app'].set('push:launch', json.dumps(launches_c))
        elif now_time < l['start']:
            return None
    else:
        return None


def rm_launch(key, image_url, prefix=None, launch_key='push:launch'):
    key_comb = key + image_url
    REDIS[prefix].delete(key_comb)

    sorted_launches = get_sort_launches(key=key, prefix=prefix)
    REDIS[prefix].set(launch_key, json.dumps(sorted_launches))


def get_launches(key, prefix=None):
    if prefix:
        launches = [':'.join(key.split(':')[1:]) for key in REDIS[prefix].scan_iter(key+'*')]
        launches_value = [json.loads(REDIS[prefix].get(key)) for key in launches]
    else:
        launches = [':'.join(key.split(':')[1:]) for key in REDIS.scan_iter(key+'*')]
        launches_value = [json.loads(REDIS.get(key)) for key in launches]

    f = lambda x: x['timestamp']
    slaunches = sorted(launches_value, key=f)
    return slaunches


def get_sort_launches(key, prefix=None):
    launches_value = get_launches(key, prefix=prefix)
    launches = [l for l in launches_value if l['end'] > int(datetime.datetime.now().timestamp()*1000)]

    f = lambda x: -x['timestamp']
    slaunches = sorted(launches, key=f)

    launche_ters = set()
    for launch in launches:
        launche_ters.add(launch['start'])
        launche_ters.add(launch['end'])
    launche_ters = sorted(list(launche_ters))

    temp = None
    sorted_launches = list()
    for p in launche_ters:
        pre = temp
        temp = p
        if pre:
            now_time = datetime.datetime.now().timestamp()*1000
            if now_time > p:
                continue
            avg = (pre + p)/2
            for la in slaunches:
                if la['end'] >= avg >= la['start']:
                    break
            else:
                continue
            sorted_launches.append({
                'start': pre,
                'end': p,
                'image': la.get('image'),
                'countdown': la.get('countdown'),
                'url': la.get('url'),
            })

    return sorted_launches


def set_launches(key, value, expire, prefix=None, launch_key='push:launch'):
    key_comb = key + value['image']
    REDIS[prefix].set(key_comb, json.dumps(value), ex=expire)

    sorted_launches = get_sort_launches(key=key, prefix=prefix)
    REDIS[prefix].set(launch_key, json.dumps(sorted_launches))



