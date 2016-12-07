# coding: utf-8

from fabric.operations import sudo
from fabric.context_managers import hide
from fabric.api import warn_only

from . import service
from .managed_task import ManagedTask
from .utility import lazy_property


class Rabbitmq(service.Service):
    service_name = 'rabbitmq-server'

    def __init__(self, *args, **kw):
        super(Rabbitmq, self).__init__(*args, **kw)

    def run(self):
        apt_packages = [
            "rabbitmq-server",
        ]
        with hide('stdout'):
            sudo("echo 'deb http://www.rabbitmq.com/debian/ testing main' |"
                 "sudo tee /etc/apt/sources.list.d/rabbitmq.list")
            sudo("wget -O- https://www.rabbitmq.com/"
                 "rabbitmq-release-signing-key.asc |"
                 "sudo apt-key add -")
            sudo("sudo apt-get update")
            for package in apt_packages:
                sudo('apt-get install {} -y'.format(package), pty=False)
        self.restart()


class RabbitmqBroker(ManagedTask):
    url = lazy_property((str, unicode))
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    vhost = lazy_property((str, unicode))

    def __init__(self, url, user, password, vhost):
        self.url = url
        self.user = user
        self.password = password
        self.vhost = vhost

    def run(self):
        with warn_only():
            sudo('rabbitmqctl add_user {} {}'.format(self.user, self.password))
            sudo('rabbitmqctl add_vhost {}'.format(self.vhost))
            sudo('rabbitmqctl set_permissions -p '
                 '{} {} ".*" ".*" ".*"'.format(self.vhost, self.user))