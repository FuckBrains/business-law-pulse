# -*- coding: utf-8 -*-

from website.sys.views import page


routes = [
    # login
    { 'method': 'GET', 'path': '/', 'handler': page.index },
    { 'method': 'GET', 'path': '/login', 'handler': page.login },

    # debug
    { 'method': 'GET', 'path': '/debug/{path:.+}', 'handler': page.debug },

    # manage
    { 'method': 'GET', 'path': '/manage/{path:.*}', 'handler': page.manage },
]

