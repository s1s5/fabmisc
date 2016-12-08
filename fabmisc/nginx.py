# coding: utf-8

import os
import StringIO
import subprocess

from fabric.operations import put
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
                 use_sudo=True, *args, **kw):
        super(NginxHtpasswd, self).__init__(*args, **kw)
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

        put(remote_path=self.dst_htpasswd,
            local_path=StringIO.StringIO(stdout),
            use_sudo=self.use_sudo)


class NginxLocation(object):
    pattern = lazy_property((str, unicode))
    options = lazy_property()
    htpasswd = lazy_property(NginxHtpasswd)

    def __init__(self, pattern='/', htpasswd=None, options=None):
        super(NginxLocation, self).__init__()
        self.pattern = pattern
        self.htpasswd = htpasswd
        self.options = options


class NginxAlias(NginxLocation):
    alias = lazy_property((str, unicode))

    def __init__(self, path='/var/www', *args, **kw):
        super(NginxAlias, self).__init__(args, kw)
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

    def __init__(self, proxy_host='127.0.0.1', proxy_port=8080,
                 *args, **kw):
        super(NginxProxy, self).__init__(*args, **kw)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        if self.options is None:
            self.options = [
                "proxy_set_header X-Forwarded-Protocol $scheme",
                "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for",
                "proxy_set_header Host $http_host",
                "proxy_redirect off",
                "proxy_buffering on",
            ]


class NginxUpstream(NginxProxy):
    pass


class NginxSite(ManagedTask):
    nginx = lazy_property(Nginx)
    site_name = lazy_property((str, unicode))
    site_conf_filename = lazy_property((str, unicode))
    template_dir = lazy_property((str, unicode))
    kw_dict = lazy_property()
    locations = lazy_property()
    ssl = lazy_property(Ssl)

    def __init__(self, nginx, site_name, site_conf_filename='nginx_site.conf',
                 template_dir=TEMPLATE_DIR, kw_dict={}, locations=(), ssl=None,
                 *args, **kw):
        super(NginxSite, self).__init__(*args, **kw)
        self.nginx = nginx
        self.site_name = site_name
        self.site_conf_filename = site_conf_filename
        self.template_dir = template_dir
        self.kw_dict = kw_dict
        self.locations = locations
        self.ssl = ssl

    def run(self):
        available = '/etc/nginx/sites-available/{}'.format(self.site_name)
        enabled = '/etc/nginx/sites-enabled/{}'.format(self.site_name)
        context = dict(
            locations=self.locations,
            upstreams=[x for x in self.locations
                       if isinstance(x, NginxUpstream)],
            ssl=self.ssl,
        )
        context.update(self.kw_dict)
        upload_template(self.site_conf_filename, available,
                        context=context, template_dir=self.template_dir,
                        use_jinja=True, use_sudo=True, )
        utility.link(available, enabled, use_sudo=True)
        self.nginx.restart()
