# coding: utf-8
from fabric.operations import run as fab_run
from fabric.context_managers import cd
from fabric.operations import sudo
from . import service
from .rabbitmq import RabbitmqBroker
from .virtualenv import Virtualenv
from .utility import lazy_property


class Celery(service.Service):
    project_name = lazy_property((str, unicode))
    work_dir = lazy_property((str, unicode))
    worker_name = lazy_property((str, unicode))
    broker = lazy_property(RabbitmqBroker)
    virtualenv = lazy_property(Virtualenv)

    def __init__(self, project_name, worker_name, work_dir=None,
                 broker=None, virtualenv=None, **kw):
        super(Celery, self).__init__(**kw)
        self.project_name = project_name
        self.work_dir = work_dir
        self.worker_name = worker_name
        self.broker = broker
        self.virtualenv = virtualenv

    def __run(self, func):
        if self.virtualenv:
            with self.virtualenv.prefix(self.work_dir):
                func()
        else:
            with cd(self.work_dir):
                func()

    def start(self):
        ext = ''
        if self.broker:
            ext += '--broker=amqp://{}:{}@{}:{}/{} '.format(
                self.broker.user, self.broker.password,
                self.hostname, self.port, self.vhost)
        self.__run(lambda: fab_run(
            'celery multi start {} -A {} '
            '--pidfile="/var/run/celery/%n.pid" '
            '--logfile="/var/log/celery/%n.log" {}'.format(
                self.worker_name, self.project_name, ext
            )))

    def stop(self):
        self.__run(lambda: fab_run(
            'celery multi stopwait {} '
            '--pidfile="/var/run/celery/%n.pid" '.format(
                self.worker_name
            )))

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        sudo('mkdir -p /var/run/celery')
        sudo('chmod 1777 /var/run/celery')
        sudo('mkdir -p /var/log/celery')
        sudo('chmod 1777 /var/log/celery')
