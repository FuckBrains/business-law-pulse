# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('thriftpy')

import json,datetime
import uuid,base64,hashlib,hmac

import requests
requests.packages.urllib3.disable_warnings()

from urllib.parse import quote



class AliyunSMS(object):
    def __init__(self, config, proxies):
        self.access_key = config['key_id']
        self.access_secret = config['key_secret']

        self.url = config['url']
        self.action = 'SingleSendSms'
        self.format = 'JSON'
        self.version = '2016-09-27'
        self.signature_method = 'HMAC-SHA1'
        self.signature_version = '1.0'
        self.sign_name = config['signname']
        self.template_code = config['templatecode']

        self.proxies = proxies

    # https://help.aliyun.com/document_detail/44363.html
    def sign(self, payload, method):
        parse = lambda x: quote(x,safe='-_.~')
        canonicalized_query_string = '&'.join(['{}={}'.format(parse(k),parse(v)) for k,v in sorted(payload.items())])
        string_to_sign = method + '&' + parse('/') + '&' + parse(canonicalized_query_string)
        key = self.access_secret + '&'

        sign_hmac = hmac.new(key.encode('utf8'), string_to_sign.encode('utf8'), hashlib.sha1).digest()
        sign_base64 = base64.b64encode(sign_hmac).decode('utf-8')
        signature = parse(sign_base64)

        return signature

    def build_payload(self, recnum, params={}, method='POST'):
        if not isinstance(recnum, list):
            recnum = [recnum]

        payload = {
            'AccessKeyId': self.access_key,
            'Action': self.action,
            'Format': self.format,
            'Version': self.version,
            'SignatureMethod': self.signature_method,
            'SignatureVersion': self.signature_version,
            'SignatureNonce': uuid.uuid1().hex,
            'Timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'SignName': self.sign_name,
            'TemplateCode': self.template_code,
            'ParamString': json.dumps(params),
            'RecNum': ','.join([i for i in recnum]),
        }

        signature = self.sign(payload,method=method)
        payload.update({ 'Signature': signature })
        return payload

    # https://help.aliyun.com/document_detail/44363.html
    def send(self, payload, method='POST'):
        if method not in ('GET','POST'):
            logger.error('[ SMS Error ] Invalid method')
            return None

        result = None

        try:
            query = '&'.join(['{}={}'.format(k,v) for k,v in sorted(payload.items())])

            if method == 'POST':
                headers = { 'Content-Type':'application/x-www-form-urlencoded' }
                response = requests.post(self.url, data=query.encode('utf8'), headers=headers, proxies=self.proxies)
            else:
                url = self.url + '?' + query
                response = requests.get(url, proxies=self.proxies)

            result = response.json()

        except Exception as e:
            logger.error('[ SMS Error ] %s' % e)

        if result and 'Model' not in result:
            logger.error('[ SMS Error ] %s' % result)
            return None

        return result


