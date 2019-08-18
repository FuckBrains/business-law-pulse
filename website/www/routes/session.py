# -*- coding: utf-8 -*-

from website.www.views import session


routes = [
    { 'method': 'POST', 'path': '/session/sync', 'handler': session.sync },
    { 'method': 'POST', 'path': '/session/login', 'handler': session.login },
    { 'method': 'POST', 'path': '/session/logout', 'handler': session.logout },
]


