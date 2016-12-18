# coding: utf-8
from fabric.state import env
import fabric.contrib.files as files
from fabric.operations import sudo
from fabric.api import warn_only

from . import service
from .utility import apt_update, apt


class Docker(service.Service):
    def run(self):
        apt_update()
        apt('apt-transport-https ca-certificates')
        sudo('apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 '
             '--recv-keys 58118E89F3A912897C070ADBF76221572C52609D')

        # 14.04 https://apt.dockerproject.org/repo ubuntu-trusty main
        # 16.04 https://apt.dockerproject.org/repo ubuntu-xenial main
        files.append('/etc/apt/sources.list.d/docker.list',
                     'deb https://apt.dockerproject.org/repo '
                     'ubuntu-xenial main',
                     use_sudo=True)

        apt_update()
        apt('linux-image-extra-$(uname -r) linux-image-extra-virtual')
        apt_update()
        apt('docker-engine')
        self.restart()
        with warn_only():
            sudo('groupadd docker')
        sudo('usermod -aG docker {}'.format(env['user']))
