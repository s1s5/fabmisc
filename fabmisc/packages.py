# coding: utf-8

from fabric.context_managers import hide
from fabric.operations import sudo
from fabric.api import shell_env

from .managed_task import ManagedTask
from .utility import lazy_property


class Packages(ManagedTask):
    apt_packages = lazy_property()
    pip_packages = lazy_property()
    lang = lazy_property((str, unicode))
    timezone = lazy_property((str, unicode))

    def __init__(self, apt_packages, pip_packages,
                 lang='ja_JP.UTF-8', timezone='Asia/Tokyo', **kw):
        super(Packages, self).__init__(**kw)
        self.apt_packages = apt_packages
        self.pip_packages = pip_packages
        self.lang = lang
        self.timezone = timezone

    def run(self):
        with hide('stdout'):
            sudo('apt-get update')
            for package in self.apt_packages + [
                    'python-pip', 'locales', 'language-pack-ja']:
                sudo('apt-get install {} -y'.format(package), pty=False)

            for package in self.pip_packages + [
                    'setuptools', 'virtualenvwrapper']:
                sudo('pip install {}'.format(package), pty=False)

            with shell_env(LANG=self.lang):
                sudo('dpkg-reconfigure -f noninteractive locales')
            sudo('update-locale LANG={}'.format(self.lang))
            sudo('timedatectl set-timezone {}'.format(self.timezone))
            # sudo('hostnamectl set-hostname new-hostname')
