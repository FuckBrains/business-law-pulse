# -*- coding: utf-8 -*-

import re,uuid
import traceback,threading

from bs4 import BeautifulSoup

import logging
logger = logging.getLogger('thriftpy')



def decode_escape(text):
    MAP = {
        ('&#34',   '&quot')     : '"',
        ('&#38',   '&amp')      : '&',
        ('&#60',   '&lt')       : '<',
        ('&#62',   '&gt')       : '>',
        ('&#160',  '&nbsp')     : ' ',
        ('&#161',  '&iexcl')    : '¡',
        ('&#162',  '&cent')     : '¢',
        ('&#163',  '&pound')    : '£',
        ('&#164',  '&curren')   : '¤',
        ('&#165',  '&yen')      : '¥',
        ('&#166',  '&brvbar')   : '¦',
        ('&#167',  '&sect')     : '§',
        ('&#168',  '&uml')      : '¨',
        ('&#169',  '&copy')     : '©',
        ('&#170',  '&ordf')     : 'ª',
        ('&#171',  '&laquo')    : '«',
        ('&#171',  '&not')      : '¬',
        ('&#174',  '&reg')      : '®',
        ('&#175',  '&macr')     : '¯',
        ('&#176',  '&deg')      : '°',
        ('&#177',  '&plusmn')   : '±',
        ('&#178',  '&sup2')     : '²',
        ('&#179',  '&sup3')     : '³',
        ('&#180',  '&acute')    : '´',
        ('&#181',  '&micro')    : 'µ',
        ('&#182',  '&para')     : '¶',
        ('&#183',  '&middot')   : '·',
        ('&#184',  '&cedil')    : '¸',
        ('&#185',  '&sup1')     : '¹',
        ('&#186',  '&ordm')     : 'º',
        ('&#187',  '&raquo')    : '»',
        ('&#188',  '&frac14')   : '¼',
        ('&#189',  '&frac12')   : '½',
        ('&#190',  '&frac34')   : '¾',
        ('&#191',  '&iquest')   : '¿',
        ('&#192',  '&Agrave')   : 'À',
        ('&#193',  '&Aacute')   : 'Á',
        ('&#194',  '&circ')     : 'Â',
        ('&#195',  '&Atilde')   : 'Ã',
        ('&#196',  '&Auml')     : 'Ä',
        ('&#197',  '&ring')     : 'Å',
        ('&#198',  '&AElig')    : 'Æ',
        ('&#199',  '&Ccedil')   : 'Ç',
        ('&#200',  '&Egrave')   : 'È',
        ('&#201',  '&Eacute')   : 'É',
        ('&#202',  '&Ecirc')    : 'Ê',
        ('&#203',  '&Euml')     : 'Ë',
        ('&#204',  '&Igrave')   : 'Ì',
        ('&#205',  '&Iacute')   : 'Í',
        ('&#206',  '&Icirc')    : 'Î',
        ('&#207',  '&Iuml')     : 'Ï',
        ('&#208',  '&ETH')      : 'Ð',
        ('&#209',  '&Ntilde')   : 'Ñ',
        ('&#210',  '&Ograve')   : 'Ò',
        ('&#211',  '&Oacute')   : 'Ó',
        ('&#212',  '&Ocirc')    : 'Ô',
        ('&#213',  '&Otilde')   : 'Õ',
        ('&#214',  '&Ouml')     : 'Ö',
        ('&#215',  '&times')    : '×',
        ('&#216',  '&Oslash')   : 'Ø',
        ('&#217',  '&Ugrave')   : 'Ù',
        ('&#218',  '&Uacute')   : 'Ú',
        ('&#219',  '&Ucirc')    : 'Û',
        ('&#220',  '&Uuml')     : 'Ü',
        ('&#221',  '&Yacute')   : 'Ý',
        ('&#222',  '&THORN')    : 'Þ',
        ('&#223',  '&szlig')    : 'ß',
        ('&#224',  '&agrave')   : 'à',
        ('&#225',  '&aacute')   : 'á',
        ('&#226',  '&acirc')    : 'â',
        ('&#227',  '&atilde')   : 'ã',
        ('&#228',  '&auml')     : 'ä',
        ('&#229',  '&aring')    : 'å',
        ('&#230',  '&aelig')    : 'æ',
        ('&#231',  '&ccedil')   : 'ç',
        ('&#232',  '&egrave')   : 'è',
        ('&#233',  '&eacute')   : 'é',
        ('&#234',  '&ecirc')    : 'ê',
        ('&#235',  '&euml')     : 'ë',
        ('&#236',  '&igrave')   : 'ì',
        ('&#237',  '&iacute')   : 'í',
        ('&#238',  '&icirc')    : 'î',
        ('&#239',  '&iuml')     : 'ï',
        ('&#240',  '&ieth')     : 'ð',
        ('&#241',  '&ntilde')   : 'ñ',
        ('&#242',  '&ograve')   : 'ò',
        ('&#243',  '&oacute')   : 'ó',
        ('&#244',  '&ocirc')    : 'ô',
        ('&#245',  '&otilde')   : 'õ',
        ('&#246',  '&ouml')     : 'ö',
        ('&#247',  '&divide')   : '÷',
        ('&#248',  '&oslash')   : 'ø',
        ('&#249',  '&ugrave')   : 'ù',
        ('&#250',  '&uacute')   : 'ú',
        ('&#251',  '&ucirc')    : 'û',
        ('&#252',  '&uuml')     : 'ü',
        ('&#253',  '&yacute')   : 'ý',
        ('&#254',  '&thorn')    : 'þ',
        ('&#255',  '&yuml')     : 'ÿ',
    }

    for key in MAP:
        exp = '(%s|%s);?' % key
        text = re.sub(exp, MAP[key], text)


def is_internal_ip(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“. ”转成10进制的 3232235789 即可
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    ip_into_int = lambda x: reduce(lambda x,y:(x<<8)+y,map(int,x.split('.')))

    net_ip = ip_into_int(ip)
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16

    return net_ip >> 24 == net_a or net_ip >>20 == net_b or net_ip >> 16 == net_c


def strip_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()


class AsyncThread(threading.Thread):
    def __init__(self, name='', target=None, args=(), kwargs=None, thread_logger=None):
        part_name = '[' + uuid.uuid1().hex + ']'
        self.target_name = '[running thread] ' + name + part_name
        self.logger = thread_logger if thread_logger else logger
        super(AsyncThread, self).__init__(target=target, name=self.target_name, args=args, kwargs=kwargs)

    def run(self):
        self.logger.info('starting %s' % self.target_name)
        try:
            if self._target:
                res = self._target(*self._args, **self._kwargs)
                self.logger.info('{} result {}'.format(self.target_name, res))
        except Exception as exc:
            trace_log = traceback.format_exc()
            self.logger.error(self.target_name + '%s' % trace_log)
        finally:
            self.logger.info('%s end' % self.target_name)


