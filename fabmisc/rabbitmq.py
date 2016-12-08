# coding: utf-8

from fabric.operations import sudo
from fabric.context_managers import hide
from fabric.api import warn_only

from . import service
from .managed_task import ManagedTask
from .utility import lazy_property


class Rabbitmq(service.Service):

    def __init__(self, **kw):
        super(Rabbitmq, self).__init__(**kw)

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
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    vhost = lazy_property((str, unicode))
    hostname = lazy_property((str, unicode))
    port = lazy_property(int)

    def __init__(self, user, password, vhost,
                 hostname='127.0.0.1', port=5672, **kw):
        super(RabbitmqBroker, self).__init__(**kw)
        self.user = user
        self.password = password
        self.vhost = vhost
        self.hostname = hostname
        self.port = port

    def run(self):
        with warn_only():
            sudo('rabbitmqctl add_user {} {}'.format(self.user, self.password))
            sudo('rabbitmqctl add_vhost {}'.format(self.vhost))
            sudo('rabbitmqctl set_permissions -p '
                 '{} {} ".*" ".*" ".*"'.format(self.vhost, self.user))
