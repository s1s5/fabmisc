# coding: utf-8

import os
import StringIO
import subprocess

from fabric.operations import run, sudo, put
from fabric.contrib.files import upload_template

from . import service
from .ssl import Ssl
from .managed_task import ManagedTask
import utility
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class Nginx(service.Service):

    def run(self):
        apt_packages = [
            "nginx",
            "nginx-extras",
            "apache2-utils",
        ]
        for package in apt_packages:
            utility.apt(package)
        utility.mkdir('/etc/nginx/sites-available', use_sudo=True)
        utility.mkdir('/etc/nginx/sites-enabled', use_sudo=True)

        upload_template('nginx.conf',
                        '/etc/nginx/nginx.conf',
                        context={}, template_dir=TEMPLATE_DIR,
                        use_jinja=True, use_sudo=True)
        utility.rm('/etc/nginx/sites-enabled/default', use_sudo=True)
        self.restart()


class NginxHtpasswd(ManagedTask):
    path = lazy_property((str, unicode))
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    use_sudo = lazy_property(bool)

    def __init__(self, path, user, password,
                 use_sudo=True, **kw):
        super(NginxHtpasswd, self).__init__(**kw)
        self.path = path
        self.user = user
        self.password = password
        self.use_sudo = use_sudo

    def run(self):
        p = subprocess.Popen(
            'htpasswd -n -b {} {}'.format(self.user, self.password),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        if p.returncode:
            raise Exception(stdout + "\n" + stderr)
        _run = run
        if self.use_sudo:
            _run = sudo
        _run('mkdir -p {}'.format(os.path.dirname(self.path)))
        put(remote_path=self.path,
            local_path=StringIO.StringIO(stdout),
            use_sudo=self.use_sudo)


class NginxLocation(object):
    pattern = lazy_property((str, unicode))
    options = lazy_property()
    htpasswd = lazy_property(NginxHtpasswd)

    def __init__(self, pattern='/', htpasswd=None, options=None, **kw):
        super(NginxLocation, self).__init__(**kw)
        self.pattern = pattern
        self.htpasswd = htpasswd
        self.options = options


class NginxAlias(NginxLocation):
    alias = lazy_property((str, unicode))

    def __init__(self, path='/var/www', **kw):
        super(NginxAlias, self).__init__(**kw)
        self.alias = path
        if self.options is None:
            self.options = [
                "expires 1y",
                "access_log off",
                'add_header Cache-Control "public"',
                ("gzip_types text/css text/javascript "
                 "application/javascript application/json"),
                "gzip on",
            ]


class NginxProxy(NginxLocation):
    proxy_host = lazy_property((str, unicode))
    proxy_port = lazy_property(int)
    proxy_path = lazy_property((str, unicode))

    def __init__(self, proxy_host='127.0.0.1', proxy_port=8080,
                 proxy_path='', rewrite_url=True, **kw):
        super(NginxProxy, self).__init__(**kw)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_path = proxy_path

        if self.options is None:
            self.options = self.getDefaultOptions()

        if rewrite_url and self.pattern != '/':
            self.options.append(
                'rewrite {}(.*) $1 break'.format(self.pattern))

    def getDefaultOptions(self):
        return [
            "proxy_set_header X-Forwarded-Protocol $scheme",
            "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for",
            "proxy_set_header Host $http_host",
            "proxy_redirect off",
            "proxy_buffering on",
        ]


class NginxSite(ManagedTask):
    nginx = lazy_property(Nginx)
    site_name = lazy_property((str, unicode))
    site_conf_filename = lazy_property((str, unicode))
    template_dir = lazy_property((str, unicode))
    kw_dict = lazy_property()
    locations = lazy_property()
    ssl = lazy_property(Ssl)
    server_name = lazy_property((str, unicode))

    def __init__(self, nginx, site_name, site_conf_filename='nginx_site.conf',
                 template_dir=TEMPLATE_DIR, kw_dict={}, locations=(), ssl=None,
                 server_name='', **kw):
        super(NginxSite, self).__init__(**kw)
        self.nginx = nginx
        self.site_name = site_name
        self.site_conf_filename = site_conf_filename
        self.template_dir = template_dir
        self.kw_dict = kw_dict
        self.locations = locations
        self.ssl = ssl
        self.server_name = server_name

    def run(self):
        available = '/etc/nginx/sites-available/{}'.format(self.site_name)
        enabled = '/etc/nginx/sites-enabled/{}'.format(self.site_name)
        context = dict(
            locations=self.locations,
            ssl=self.ssl,
            server_name=self.server_name,
        )
        context.update(self.kw_dict)
        upload_template(self.site_conf_filename, available,
                        context=context, template_dir=self.template_dir,
                        use_jinja=True, use_sudo=True, )
        utility.link(available, enabled, use_sudo=True)
        self.nginx.restart()
