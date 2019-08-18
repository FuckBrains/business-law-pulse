# -*- coding: utf-8 -*-

import os,sys,time
import getpass,argparse,subprocess,paramiko,socket

# https://pypi.python.org/pypi/colorama
import colorama

# http://blog.chinaunix.net/uid-27714502-id-4110758.html
# \33[nA    光标上移n行
# \33[nB    光标下移n行
# \33[nC    光标右移n行
# \33[nD    光标左移n行
# \33[y;xH  设置光标位置
# \33[2J    清屏
# \33[K     清除从光标到行尾的内容
# \33[s     保存光标位置
# \33[u     恢复光标位置
# \33[?25l  隐藏光标
# \33[?25h  显示光标


CONFIG = {
    'username': 'michael',
    'password': '',

    'proxy': { 'host': 'vpn.liangyongxiong.cn', 'username': 'michael' },
    'path': '/opt/workspace/businesslawpulse',

    'static': { 'dev': 'vpn.liangyongxiong.cn', 'prd': 'debug.main.blp' },

    'website': {
        'api': { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'] },
        'www': { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'] },
        'sys': { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'] },
    },

    'service': {
        'common': { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'], 'task': [] },
        'admin':  { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'], 'task': [] },
        'user':   { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'], 'task': [] },
        'news':   { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'], 'task': [] },
        'video':  { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'], 'task': [] },
        'law':    { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'], 'debug': ['debug.main.blp'], 'task': [] },
    },

    'scrapy': {
        'news':   { 'dev': ['vpn.liangyongxiong.cn'], 'prd': ['1.main.blp'] },
    },

    'mongo': { 'host': 'localhost', 'port': 30000, 'username': 'blp', 'password': 'blp', 'db': 'blp_default', 'collections': ['doc_module'] },
}


def local(cmd):
    print(colorama.Fore.WHITE + '[LOCAL]$ ' + colorama.Fore.RESET + cmd)

    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()

    if stderrdata:
        print(colorama.Fore.RED + stderrdata.decode('utf8').strip() + colorama.Fore.RESET)
        sys.exit()

    if stdoutdata:
        print(stdoutdata.decode('utf8').strip())

    return stdoutdata.decode('utf8')


def remote(cmd, session):
    session.send(cmd)
    session.send('\n')

    buff = ''
    while not buff.endswith('$ '):
        buff = session.recv(65535).decode('utf8')
        print(buff, end='', flush=True)

    time.sleep(1)


def connect(host, username, password=None):
    print(colorama.Fore.WHITE + '\n[ Connecting to %s ]' % host + colorama.Fore.RESET)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    try:
        sock = None
        if host.endswith('blp'):
            command = 'ssh %s@%s nc %s 22' % (CONFIG['proxy']['username'],CONFIG['proxy']['host'],host)
            sock = paramiko.ProxyCommand(command)

        ssh.connect(host, port=22, username=username, password=password, sock=sock, timeout=30)

    except paramiko.ssh_exception.AuthenticationException as e:
        print(colorama.Fore.RED + str(e) + colorama.Fore.RESET)
        sys.exit()

    except paramiko.ssh_exception.SSHException as e:
        print(colorama.Fore.RED + str(e) + colorama.Fore.RESET)
        sys.exit()

    except socket.timeout as e:
        print(colorama.Fore.RED + str(e) + colorama.Fore.RESET)
        sys.exit()

    except Exception as e:
        print(colorama.Fore.RED + str(e) + colorama.Fore.RESET)
        sys.exit()

    return ssh


def get_session(ssh):
    session = ssh.get_transport().open_session()
    session.settimeout(30)
    session.get_pty(width=320)
    session.invoke_shell()

    time.sleep(3)
    welcome = session.recv(65535).decode('utf8')
    prompt = welcome.split('\n')[-1]
    print(prompt, end='')

    return session


def sftp(localpath, remotepath, ssh):
    (directory, filename) = os.path.split(localpath)

    def _callback(current_size, total_size):
        percentage = int(current_size*100.0/total_size)
        content = '%s : %s / %s => %s%%' % (filename, current_size, total_size, percentage)
        output = colorama.Fore.WHITE + content + colorama.Fore.RESET

        if current_size == total_size:
            print(output)
        else:
            print(end='\r')  # clear line
            print(output, end='\r')

    fp = open(localpath, 'rb')
    fp.seek(0, os.SEEK_END)
    file_size = fp.tell()
    fp.seek(0, os.SEEK_SET)

    client = paramiko.SFTPClient.from_transport(ssh.get_transport())
    print('\33[?25l', end='\r')  # hide cursor
    client.putfo(fp, remotepath, file_size, _callback)
    print('\33[?25h', end='\r')  # show cursor


def deploy_website(env, package):
    #####################################
    # archive local codes
    #####################################
    local("rm -rf tmp && mkdir tmp")
    local("cp -r website core manage.py tmp")
    local("find tmp/website -type d | grep -v 'website/%s' | awk 'NR>1' | xargs rm -rf" % package)

    if env == 'dev':
        local("cd tmp/core/conf && rm -f const_prd.py && mv -f const_dev.py const.py")
        local("cd tmp/website/%s/conf && rm -f const_prd.py && mv -f const_dev.py const.py" % package)
    elif env == 'prd':
        local("cd tmp/core/conf && rm -f const_dev.py && mv -f const_prd.py const.py")
        local("cd tmp/website/%s/conf && rm -f const_dev.py && mv -f const_prd.py const.py" % package)

    local("find tmp %s | xargs rm -rf" % ' -o '.join(['-name "%s"' % item for item in ['__pycache__', '*.swp', '*.log', '*.out']]))
    local("cd tmp && tar jcf website.tar.bz2 * && ls -lh website.tar.bz2")

    #####################################
    # connect remote host
    #####################################
    config = CONFIG['website'][package]
    hosts = config[env]
    for index in range(0,len(hosts)):
        ssh = connect(hosts[index], CONFIG['username'], CONFIG['password'])
        sftp('./tmp/website.tar.bz2', '/tmp/website.tar.bz2', ssh)
        session = get_session(ssh)

        # remote("date +'%Y-%m-%d %H:%M:%S'", session)

        scripts = [
            "cd %s" % CONFIG['path'],
            "rm -rf tmp && mkdir tmp && tar jxfm /tmp/website.tar.bz2 -C tmp && rm -f /tmp/website.tar.bz2",
            "sed -i \"s/'node': '0'/'node': '%s'/g\" tmp/website/%s/conf/const.py" % (index,package),
            "mkdir -p website && rm -rf website/%s && mv tmp/website/%s website" % (package,package),
            "rm -rf core manage.py && mv tmp/core tmp/manage.py . && rm -rf tmp",
            "chmod -R 770 core website && find . -type f | xargs chmod 660",
        ]

        for script in scripts:
            remote(script, session)

        remote("python3 manage.py website %s daemon" % package, session)

        print(end='\n')  # clear line
        ssh.close()

    print(colorama.Fore.YELLOW + '\r########## DEPLOY WEBSITE DONE ##########\n' + colorama.Fore.RESET)


def deploy_service(env, package):
    #####################################
    # archive local codes
    #####################################
    local("rm -rf tmp && mkdir tmp")
    local("cp -r service core manage.py tmp")
    local("find tmp/service -type d | grep -v 'service/%s' | awk 'NR>1' | xargs rm -rf" % package)

    if env == 'dev':
        local("cd tmp/core/conf && rm -f const_prd.py && mv -f const_dev.py const.py")
        local("cd tmp/service/%s/conf && rm -f const_prd.py && mv -f const_dev.py const.py" % package)
    elif env == 'prd':
        local("cd tmp/core/conf && rm -f const_dev.py && mv -f const_prd.py const.py")
        local("cd tmp/service/%s/conf && rm -f const_dev.py && mv -f const_prd.py const.py" % package)

    local("find tmp %s | xargs rm -rf" % ' -o '.join(['-name "%s"' % item for item in ['__pycache__', '*.swp', '*.log', '*.out']]))
    local("cd tmp && tar jcf service.tar.bz2 * && ls -lh service.tar.bz2")

    #####################################
    # connect remote host
    #####################################
    config = CONFIG['service'][package]
    hosts = config[env]
    for index in range(0,len(hosts)):
        ssh = connect(hosts[index], CONFIG['username'], CONFIG['password'])
        sftp('./tmp/service.tar.bz2', '/tmp/service.tar.bz2', ssh)
        session = get_session(ssh)

        # remote("date +'%Y-%m-%d %H:%M:%S'", session)

        scripts = [
            "cd %s" % CONFIG['path'],
            "rm -rf tmp && mkdir tmp && tar jxfm /tmp/service.tar.bz2 -C tmp && rm -f /tmp/service.tar.bz2",
            "sed -i \"s/'node': 0/'node': %s/g\" tmp/service/%s/conf/const.py" % (index,package),
            "mkdir -p service && rm -rf service/%s && mv tmp/service/%s service" % (package,package),
            "rm -rf core manage.py && mv tmp/core tmp/manage.py . && rm -rf tmp",
            "chmod -R 770 core service && find . -type f | xargs chmod 660",
        ]

        for script in scripts:
            remote(script, session)

        remote("python3 manage.py service %s daemon" % package, session)

        print(end='\n')  # clear line
        ssh.close()

    print(colorama.Fore.YELLOW + '\r########## DEPLOY SERVICE DONE ##########\n' + colorama.Fore.RESET)


def deploy_static(env, package):
    #####################################
    # archive local files
    #####################################
    local("rm -rf tmp && mkdir tmp")
    local("cp -r static/%s tmp" % package)
    local("find tmp %s | xargs rm -rf" % ' -o '.join(['-name "%s"' % item for item in ['__pycache__', '*.swp', '*.log', '*.out']]))
    local("cd tmp && tar jcf static.tar.bz2 * && ls -lh static.tar.bz2")

    #####################################
    # connect remote host
    #####################################
    ssh = connect(CONFIG['static'][env], CONFIG['username'], CONFIG['password'])
    sftp('./tmp/static.tar.bz2', '/tmp/static.tar.bz2', ssh)
    session = get_session(ssh)

    scripts = [
        "cd %s" % CONFIG['path'],
        "rm -rf static/%s && tar jxfm /tmp/static.tar.bz2 -C static && rm -f /tmp/static.tar.bz2" % package,
        "chmod -R 775 static/* && find static/* -type f | xargs chmod 664",
    ]

    for script in scripts:
        remote(script, session)

    if env == 'prd' and package != 'vendor':
        pass

    print(end='\n')  # clear line
    ssh.close()

    print(colorama.Fore.YELLOW + '\r########## DEPLOY STATIC DONE ##########\n' + colorama.Fore.RESET)



def deploy_scrapy(env, package):
    #####################################
    # archive local codes
    #####################################
    local("rm -rf tmp && mkdir tmp")
    local("cp -r scrapy tmp")
    local("find tmp/scrapy -type d | grep -v 'scrapy/%s' | awk 'NR>1' | xargs rm -rf" % package)

    if env == 'dev':
        local("cd tmp/scrapy/%s/%s/conf && rm -f const_prd.py && mv -f const_dev.py const.py" % (package,package))
    elif env == 'prd':
        local("cd tmp/scrapy/%s/%s/conf && rm -f const_dev.py && mv -f const_prd.py const.py" % (package,package))

    local("find tmp %s | xargs rm -rf" % ' -o '.join(['-name "%s"' % item for item in ['__pycache__', '*.swp', '*.log', '*.out']]))
    local("cd tmp && tar jcf scrapy.tar.bz2 * && ls -lh scrapy.tar.bz2")

    #####################################
    # connect remote host
    #####################################
    hosts = CONFIG['scrapy'][package][env]
    for index in range(0,len(hosts)):
        ssh = connect(hosts[index], CONFIG['username'], CONFIG['password'])
        sftp('./tmp/scrapy.tar.bz2', '/tmp/scrapy.tar.bz2', ssh)
        session = get_session(ssh)

        # remote("date +'%Y-%m-%d %H:%M:%S'", session)

        scripts = [
            "cd %s" % CONFIG['path'],
            "rm -rf tmp && mkdir tmp && tar jxfm /tmp/scrapy.tar.bz2 -C tmp && rm -f /tmp/scrapy.tar.bz2",
            "mkdir -p scrapy && rm -rf scrapy/%s && mv tmp/scrapy/%s scrapy" % (package,package),
            "rm -rf tmp && chmod -R 770 scrapy && find . -type f | xargs chmod 660",
        ]

        for script in scripts:
            remote(script, session)

        print(end='\n')  # clear line
        ssh.close()

    print(colorama.Fore.YELLOW + '\r########## DEPLOY SCRAPY DONE ##########\n' + colorama.Fore.RESET)



def show_help():
    description = """
python3 deploy [env] [module] [package]

[env]
dev         : develop environment
prd         : product environment
debug       : debug environment
task        : task environment

[module]
website     : website module
service     : service module
static      : static module
"""
    print(colorama.Fore.WHITE + description + colorama.Fore.RESET)


if __name__ == '__main__':
    pwd = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, pwd)
    os.chdir(pwd)

    parser = argparse.ArgumentParser()

    # positional arguments
    parser.add_argument('env', nargs='?', choices=['dev','prd','debug','task'])
    parser.add_argument('module', nargs='?', choices=['website','service','static','scrapy'])
    parser.add_argument('package', nargs='?', default='')

    options = parser.parse_args()

    os.system('find . -name "._*" | xargs rm -rf')
    os.system('find . -name ".DS_Store" | xargs rm -rf')
    os.system('find . -name "*" -type f | xargs chmod 644')

    if options.env != 'dev':
        try:
            CONFIG['password'] = getpass.getpass(colorama.Fore.WHITE + '\nPASSWORD : ' + colorama.Fore.RESET)
            print(colorama.Fore.WHITE + '\n------------------------------\n' + colorama.Fore.RESET)
        except KeyboardInterrupt as exc:
            print('KeyboardInterrupt')
            sys.exit(0)

    if options.module == 'website':
        if options.package not in os.listdir('website'):
            print('Website %s not found' % options.package)
            sys.exit(0)

        deploy_website(options.env, options.package)

    elif options.module == 'service':
        if options.package not in os.listdir('service'):
            print('Service %s not found' % options.package)
            sys.exit(0)

        deploy_service(options.env, options.package)

    elif options.module == 'static':
        if options.package not in os.listdir('static'):
            print('Static %s not found' % options.package)
            sys.exit(0)

        deploy_static(options.env, options.package)

    elif options.module == 'scrapy':
        if options.package not in os.listdir('scrapy'):
            print('Scrapy %s not found' % options.package)
            sys.exit(0)

        deploy_scrapy(options.env, options.package)

    os.system('rm -rf tmp')
