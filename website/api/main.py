# -*- coding: utf-8 -*-

import os,sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
sys.path.insert(0, root)

from core.utils.setup import setup_init
setup_init(__package__)


#######################################################################################################################


def setup_middlewares(app):
    from core.utils.http import basic_middleware_factory
    app.middlewares.append(basic_middleware_factory)

    # from utils.http import session_middleware_factory
    # app.middlewares.append(session_middleware_factory)

    from core.utils.http import logging_middleware_factory
    app.middlewares.append(logging_middleware_factory)

    from core.utils.http import cors_middleware_factory
    app.middlewares.append(cors_middleware_factory)

    from core.utils.http import override_http_status
    app.middlewares.append(override_http_status(app))


def setup_routes(app):
    import importlib
    package = importlib.import_module('website.api.routes')

    routes = []
    for name in dir(package):
        if name.startswith('_'):
            continue

        module = getattr(package, name)
        if module.__class__.__name__ == 'module':
            routes.extend(module.routes)

    for route in routes:
        method = route.get('method', '*')
        path = route.get('path', '')
        handler = route.get('handler', None)
        name = route.get('name', None)
        expect_handler = route.get('handler', None)
        app.router.add_route(method=method, path=path, handler=handler, name=name, expect_handler=expect_handler)


#######################################################################################################################


from core.utils.http import create_app
application = create_app(loop=None,
                middlewares=setup_middlewares,
                routes=setup_routes)



