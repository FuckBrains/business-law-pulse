# -*- coding: utf-8 -*-

from core.conf import CONST

from aiohttp import web
from aiohttp_session import get_session
from aiohttp_jinja2 import render_template

import logging
logger = logging.getLogger('aiohttp.server')


MAIN = CONST['static']['url'] + 'pages/sys/%s?_v=' + CONST['static']['cache']


async def index(request):
    return web.HTTPFound('/login')


async def login(request):
    context = { 'main': MAIN % 'pc/login/main.js' }
    return render_template('pc/login.html', request, context)


async def debug(request):
    if request.device.is_mobile:
        context = { 'main': MAIN % 'm/debug/main.js' }
        return render_template('m/debug.html', request, context)

    context = { 'main': MAIN % 'pc/debug/main.js' }
    return render_template('pc/debug.html', request, context)


async def manage(request):
    session = await get_session(request)
    admin = session.get('admin',{})
    if not admin:
        return web.HTTPFound('/')

    context = { 'main': MAIN % 'pc/dashboard/main.js' }
    return render_template('pc/manage.html', request, context)


