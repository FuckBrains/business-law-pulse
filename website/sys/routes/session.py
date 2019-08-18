# -*- coding: utf-8 -*-

from website.sys.views import session


routes = [
    { 'method': 'POST', 'path': '/session/sync', 'handler': session.sync },
    { 'method': 'POST', 'path': '/session/login', 'handler': session.login },
    { 'method': 'POST', 'path': '/session/logout', 'handler': session.logout },
    { 'method': 'POST', 'path': '/session/user/switch', 'handler': session.switch_user },
    { 'method': 'POST', 'path': '/session/user/detach', 'handler': session.detach_user },
]


