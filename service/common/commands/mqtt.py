# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.command import BaseCommand

import json,datetime
import uuid

from paho.mqtt import client as paho
from paho.mqtt import publish



class PublishMessage(BaseCommand):
    def publish_single(self):
        config = CONST['mqtt']['admin']
        auth = { 'username': config['username'], 'password': config['password'] }

        for i in range(0,10):
            payload = json.dumps({
                'mid': uuid.uuid1().hex,
                'data': { 'games': [] },
                'timestamp': int(datetime.datetime.now().timestamp()*1000),
            })

            print(payload, flush=True)
            client_id = 'python-' + uuid.uuid1().hex
            publish.single('fifa/game/live', payload=payload, qos=0, retain=False,
                        hostname=config['host'], port=config['port'], auth=auth,
                        client_id=client_id)

    def handle(self, *args, **options):
        self.publish_single()



class StartClient(BaseCommand):
    def get_callbacks(self):
        def on_log(client, userdata, level, buf):
            #print('level = %s' % level, flush=True)
            #print('buf = %s' % buf, flush=True)
            pass

        def on_publish(client, userdata, mid):
            print('PUBLISH      > mid = %s' % mid, flush=True)

        def on_message(client, userdata, message):
            QoS = {
                0: 'At most once',
                1: 'At least once',
                2: 'Exactly once',
            }

            print('\nvvvvvvvvvv MESSAGE vvvvvvvvvv\n', flush=True)
            print('mid          : %s' % message.mid, flush=True)
            print('state        : %s' % message.state, flush=True)
            print('qos          : %s ( %s )' % (message.qos, QoS[message.qos]), flush=True)
            print('duplicate    : %s' % 'N' if message.dup==0 else 'Y', flush=True)
            print('retained     : %s' % 'N' if message.retain==0 else 'Y', flush=True)
            print('timestamp    : %s' % datetime.datetime.fromtimestamp(message.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'), flush=True)
            print('topic        : %s' % message.topic, flush=True)
            print('payload      : %s' % message.payload.decode('utf8'), flush=True)
            print('\n^^^^^^^^^^ MESSAGE ^^^^^^^^^^\n', flush=True)

        def on_subscribe(client, userdata, mid, granted_qos):
            print('SUBSCRIBE    > mid = %s, granted_qos = %s' % (mid,granted_qos), flush=True)

            #publish = dict(topic='topic/python', payload='this is a python client', qos=0, retain=False)
            #for i in range(0,5):
            #    (rc, mid) = client.publish(**publish)
            #    print('# rc = %s, mid = %s' % (rc,mid), flush=True)

        def on_unsubscribe(client, userdata, mid):
            print('UNSUBSCRIBE  > mid = %s' % mid, flush=True)

        def on_connect(client, userdata, flags, rc):
            print('CONNECT      > %s ( rc = %s )' % (paho.connack_string(rc),rc), flush=True)
            subscribe = [dict(topic='fifa/game/chatroom/message', qos=0)]
            client.subscribe([(item['topic'],item['qos']) for item in subscribe])

        def on_disconnect(client, userdata, rc):
            print('DISCONNECT   > %s ( rc = %s )' % (paho.connack_string(rc),rc), flush=True)

        return dict(
            on_log=on_log,on_publish=on_publish,on_message=on_message,
            on_subscribe=on_subscribe,on_unsubscribe=on_unsubscribe,
            on_connect=on_connect,on_disconnect=on_disconnect,
        )

    def handle(self, *args, **options):
        client_id = 'python-' + uuid.uuid1().hex
        client = paho.Client(client_id=client_id,clean_session=True)

        callbacks = self.get_callbacks()
        client.on_log = callbacks['on_log']
        client.on_connect = callbacks['on_connect']
        client.on_disconnect = callbacks['on_disconnect']
        client.on_subscribe = callbacks['on_subscribe']
        client.on_unsubscribe = callbacks['on_unsubscribe']
        client.on_publish = callbacks['on_publish']
        client.on_message = callbacks['on_message']

        will = dict(topic='topic/halt', payload='python disconnected', qos=0, retain=False)
        client.will_set(**will)

        config = dict(
            host='mqtt.footballzone.dev',
            port=1883,
            username='footballzone/app',
            password='app',
        )

        client.username_pw_set(config['username'],config['password'])
        rc = client.connect(host=config['host'], port=config['port'], keepalive=60)
        client.loop_forever()



