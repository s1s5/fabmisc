# coding: utf-8

import os
import StringIO
import subprocess

from fabric.operations import put
from fabric.contrib.files import upload_template

from . import service
from .managed_task import ManagedTask

import utility
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class Nginx(service.Service):
    service_name = 'nginx'

    def run(self):
        apt_packages = [
            "nginx",
            "apache2-utils",
        ]
        for package in apt_packages:
            utility.apt(package)
        utility.mkdir('/etc/nginx/sites-available', use_sudo=True)
        utility.mkdir('/etc/nginx/sites-enabled', use_sudo=True)

        upload_template('nginx.conf.j2',
                        '/etc/nginx/nginx.conf',
                        context={}, template_dir=TEMPLATE_DIR,
                        use_jinja=True, use_sudo=True)
        utility.rm('/etc/nginx/sites-enabled/default', use_sudo=True)
        self.restart()


class NginxSite(ManagedTask):
    site_name = lazy_property((str, unicode))
    site_conf_filename = lazy_property((str, unicode))
    template_dir = lazy_property((str, unicode))
    kw_dict = lazy_property()

    def __init__(self, site_name, site_conf_filename,
                 template_dir, kw_dict, *args, **kw):
        super(NginxSite, self).__init__(*args, **kw)
        self.site_name = site_name
        self.site_conf_filename = site_conf_filename
        self.template_dir = template_dir
        self.kw_dict = kw_dict

    def run(self):
        available = '/etc/nginx/sites-available/{}'.format(self.site_name)
        enabled = '/etc/nginx/sites-enabled/{}'.format(self.site_name)
        upload_template(self.site_conf_filename, available,
                        context=self.kw_dict, template_dir=self.template_dir,
                        use_jinja=True, use_sudo=True, )
        utility.link(available, enabled, use_sudo=True)


class NginxHtpasswd(ManagedTask):
    dst_htpasswd = lazy_property((str, unicode))
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    use_sudo = lazy_property(bool)

    def __init__(self, dst_htpasswd, user, password, use_sudo, *args, **kw):
        super(NginxHtpasswd, self).__init__(*args, **kw)
        self.dst_htpasswd = dst_htpasswd
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
