# -*- coding: utf-8 -*-

from website.www.views import page


routes = [
    # index
    { 'method': 'GET', 'path': '/', 'handler': page.index },

    # api
    { 'method': 'GET', 'path': '/debug/{path:.+}', 'handler': page.debug },

    # law
    { 'method': 'GET', 'path': '/law/{path:.+}', 'handler': page.law },

    # generate
    { 'method': 'GET', 'path': '/generate', 'handler': page.generate },
    { 'method': 'POST', 'path': '/generate/pdf', 'handler': page.generate_pdf },
]

