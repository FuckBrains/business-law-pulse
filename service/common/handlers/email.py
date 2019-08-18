# -*- coding: utf-8 -*-

from core.conf import CONST
from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result
from core.utils.thrift import thrift_exempt

import os,smtplib,socket

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template



class EmailHandler(ThriftHandler):
    def __init__(self):
        super(EmailHandler, self).__init__()

        self.scenes = {
            'register': '用户注册',
            'retrieve': '找回密码',
            'bind': '绑定邮箱',
            'login': '帐号登录',
        }

    def send_validation(self,request):
        email = request.data['email']
        validation = request.data['validation']
        scene = request.data['scene']
        user = request.data['user']

        if scene not in self.scenes:
            raise BizException('无法识别的场景码')

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'templates/%s.html' % scene))
        html = open(path,'r').read()
        template = Template(html)

        if scene == 'retrieve':
            title = '找回密码 - 足球地带'
            content = template.render(CONST=CONST,email=email,validation=validation)
        elif scene == 'bind':
            title = '绑定邮箱 - 足球地带'
            content = template.render(CONST=CONST,email=email,validation=validation,user=user)

        self.deliver('service',[email],title,content)
        return Result(msg='发送成功', data=dict(intervl=0))

    @thrift_exempt
    def deliver(self,sender,recipients,subject,content,attachments=[]):
        config = CONST['email'][sender]

        msg = MIMEMultipart()
        msg['subject'] = subject
        msg['from'] = config['display']
        msg['to'] = ';'.join(recipients)
        msg.attach(MIMEText(content,'html'))

        try:
            smtp = smtplib.SMTP_SSL(config['smtp'],timeout=10)
            #smtp.set_debuglevel(1)
            #smtp.ehlo(config['smtp'])
            smtp.login(config['username'], config['password'])
            smtp.sendmail(config['username'], recipients, msg.as_string())
            smtp.quit()

        except socket.timeout as exc:
            raise BizException('邮件发送超时')

        except Exception as exc:
            raise exc


