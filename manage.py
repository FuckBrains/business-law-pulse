# -*- coding: utf-8 -*-

import os,sys
import re,traceback,subprocess,argparse,importlib,colorama


WEBSITE = {
    'api': 8000,
    'www': 8010,
    'sys': 8020,
}



def run_server(module,app,action):
    if module == 'website':
        config = WEBSITE
        try:
            assert app in config
        except AssertionError as err:
            print(colorama.Fore.WHITE + '\n# undefined website : %s\n' % app + colorama.Fore.RESET)
            return

    from core.utils.setup import setup_init
    setup_init('%s.%s' % (module,app))

    from core.conf import CONST
    gunicorn_config = CONST['gunicorn']

    if module == 'website':
        port = config[app]
    elif module == 'service':
        config = CONST['thrift']
        thrift_module = '%s_thrift' % app

        try:
            assert thrift_module in config
        except AssertionError as err:
            print(colorama.Fore.WHITE + '\n# undefined service : %s\n' % app + colorama.Fore.RESET)
            return

        port = config[thrift_module]['port']

    reload_config = ''
    if action == 'debug' or CONST['env'] != 'prd':
        reload_config = '--reload'

    daemon_config = ''
    logging_config = ''
    if action == 'daemon':
        daemon_config = '--daemon'
        logging_config = '--access-logfile log/%s.%s.gunicorn.log --error-logfile log/%s.%s.gunicorn.log' % (module,app,module,app)

    if module == 'website':
        cmd = 'gunicorn \
                --worker-class aiohttp.worker.GunicornUVLoopWebWorker \
                --workers %s --timeout %s %s %s %s \
                --bind 127.0.0.1:%s \
                %s.%s.main:application'
    else:
        cmd = 'gunicorn_thrift \
                --thrift-protocol-factory thriftpy.protocol:TCyBinaryProtocolFactory \
                --thrift-transport-factory thriftpy.transport:TCyBufferedTransportFactory \
                --worker-class thriftpy_gevent \
                --workers %s --timeout %s %s %s %s \
                --bind 127.0.0.1:%s \
                %s.%s.main:processor'

    cmd = cmd % (gunicorn_config['workers'],gunicorn_config['timeout'],
                reload_config,daemon_config,logging_config,
                port,module,app)
    cmd = re.sub(r'\s+',' ',cmd)

    stop_server(module,app)

    try:
        print(colorama.Fore.WHITE + '\n%s\n' % cmd + colorama.Fore.RESET)
        subprocess.call(cmd, shell=True)
    except Exception as exc:
        sys.exit(0)


def stop_server(module,app):
    if module == 'website':
        grep = '%s.%s.main:application' % (module,app)
    else:
        grep = '%s.%s.main:processor' % (module,app)

    try:
        output = subprocess.getoutput("ps -ef | grep '%s' | grep -v grep | wc -l" % grep)
        if output and int(output.strip()) == 0:
            return

        subprocess.call("ps -ef | grep '%s' | grep -v grep | awk '{ print $2 }' | xargs kill -9" % grep, shell=True)

        # double check
        output = subprocess.getoutput("ps -ef | grep '%s' | grep -v grep | wc -l" % grep)
        if output and int(output.strip()) > 0:
            print(colorama.Fore.WHITE + '\nGunicorn process remains\n' + colorama.Fore.RESET)
            sys.exit(0)

    except Exception as exc:
        sys.exit(0)


def daemon_all(module):
    stop_all(module)

    apps = []
    for app in os.listdir(module):
        if not app.startswith('__') and os.path.isdir(os.path.join(module,app)):
            apps.append(app)

    for app in apps:
        run_server(module,app,'daemon')
        print(colorama.Fore.WHITE + '# %s %s is started' % (module,app) + colorama.Fore.RESET)


def stop_all(module):
    if module == 'website':
        grep = 'main:application'
    else:
        grep = 'main:processor'

    try:
        output = subprocess.getoutput("ps -ef | grep '%s' | grep -v grep | wc -l" % grep)
        if output and int(output.strip()) == 0:
            return

        subprocess.call("ps -ef | grep '%s' | grep -v grep | awk '{ print $2 }' | xargs kill -9" % grep, shell=True)

        # double check
        output = subprocess.getoutput("ps -ef | grep '%s' | grep -v grep | wc -l" % grep)
        if output and int(output.strip()) > 0:
            print(colorama.Fore.WHITE + '\nGunicorn process remains\n' + colorama.Fore.RESET)
            sys.exit(0)

    except Exception as exc:
        sys.exit(0)


def run_shell(module,app):
    from core.utils.setup import setup_init,setup_redis,setup_mongo
    setup_init('%s.%s' % (module,app))
    setup_redis()
    setup_mongo()

    from IPython import start_ipython
    start_ipython(argv=[])


def run_test(module,app,testcase='list'):
    from core.utils.setup import setup_init,setup_redis,setup_mongo
    setup_init('%s.%s' % (module,app))
    setup_redis()
    setup_mongo()

    import unittest
    runner = unittest.TextTestRunner()

    try:
        package = importlib.import_module('%s.%s.tests' % (module,app))
    except ModuleNotFoundError as e:
        print(traceback.format_exc())
        sys.exit(0)

    found = False
    for attr_name in dir(package):
        attr_object = getattr(package, attr_name)
        if isinstance(attr_object,type) and issubclass(attr_object,unittest.TestCase):
            if testcase == 'list':
                print(attr_name)
            elif testcase == 'all' or testcase == attr_name:
                found = True

    if testcase == 'list' or testcase == 'all':
        return

    if found:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(attr_object)
        runner.run(suite)
    else:
        print(colorama.Fore.WHITE + '\n%s not found\n' % testcase + colorama.Fore.RESET)


def run_command(module,app,command='list',argv=[]):
    from core.utils.setup import setup_init
    setup_init('%s.%s' % (module,app))

    from core.utils.command import BaseCommand

    try:
        package = importlib.import_module('%s.%s.commands' % (module,app))
    except ModuleNotFoundError as e:
        print(traceback.format_exc())
        sys.exit(0)

    found = False
    command_instance = None
    for attr_name in dir(package):
        attr_object = getattr(package, attr_name)
        if isinstance(attr_object,type) and issubclass(attr_object,BaseCommand):
            if command == 'list':
                print(attr_name)
            elif command == attr_name:
                command_instance = attr_object()
                found = True
                break

    if command == 'list':
        return

    if found:
        command_instance.execute(argv)
    else:
        print(colorama.Fore.WHITE + '\n%s not found\n' % command + colorama.Fore.RESET)


def show_help():
    description = """
python3 manage.py [website | service] [app] [action] [arguments]

[website - app]
all         : all websites
api         : website for api
www         : website for www
sys         : website for sys

[service - app]
all         : all services
common      : common service in thrift
admin       : admin service in thrift
user        : user service in thrift

[action]
debug       : run as debug process
daemon      : run as daemon process
stop        : stop gunicorn process
shell       : run ipython shell
test        : run testcase [ list | all | TestCase ]
command     : run command [ list | Command ]
"""
    print(colorama.Fore.WHITE + description + colorama.Fore.RESET)


####################################################################################################


if __name__ == '__main__':
    pwd = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, pwd)
    os.chdir(pwd)

    if not os.path.exists('log') or not os.path.exists('media'):
        print('Folders for log and media are required')
        sys.exit(0)

    parser = argparse.ArgumentParser()

    # positional arguments
    parser.add_argument('module', nargs='?', choices=['website','service'])
    parser.add_argument('app', nargs='?', )
    parser.add_argument('action', nargs='?', choices=['debug','daemon','stop','shell','test','command'])
    parser.add_argument('parameter', nargs='?', default='list')

    options = parser.parse_args(sys.argv[1:5])

    try:
        if options.action == 'debug':
            run_server(options.module,options.app,'debug')
        elif options.action == 'daemon':
            if options.app == 'all':
                daemon_all(options.module)
            else:
                run_server(options.module,options.app,'daemon')
        elif options.action == 'stop':
            if options.app == 'all':
                stop_all(options.module)
            else:
                stop_server(options.module,options.app)
        elif options.action == 'shell':
            run_shell(options.module,options.app)
        elif options.action == 'test':
            run_test(options.module,options.app,options.parameter)
        elif options.action == 'command':
            run_command(options.module,options.app,options.parameter,sys.argv[5:])
        else:
            show_help()

    except Exception as exc:
        print(traceback.format_exc())
        show_help()



