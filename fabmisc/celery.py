# coding: utf-8
from fabric.state import env
from fabric.operations import run as fab_run
from fabric.context_managers import cd
from fabric.operations import sudo

from .rabbitmq import RabbitmqBroker
from .virtualenv import Virtualenv
from .utility import lazy_property
from . import cron
from . import service


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

    def getStartCommandString(self):
        ext = ''
        if self.broker:
            ext += '--broker=amqp://{}:{}@{}:{}/{} '.format(
                self.broker.user, self.broker.password,
                self.broker.hostname, self.broker.port, self.broker.vhost)
        return ('celery multi start {worker} -A {proj} --loglevel=INFO '
                '--pidfile="/tmp/celery_{worker}.pid" '
                '--logfile="/var/log/celery-{worker}.log" {ext}'.format(
                    worker=self.worker_name, proj=self.project_name, ext=ext
                ))

    def start(self):
        ext = ''
        if self.broker:
            ext += '--broker=amqp://{}:{}@{}:{}/{} '.format(
                self.broker.user, self.broker.password,
                self.broker.hostname, self.broker.port, self.broker.vhost)
        self.__run(lambda: fab_run(self.getStartCommandString()))

    def stop(self):
        self.__run(lambda: fab_run(
            'celery multi stopwait {worker} '
            '--pidfile="/tmp/celery_{worker}.pid" '.format(
                worker=self.worker_name
            )))

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        sudo('mkdir -p /var/log/celery')
        sudo('chmod 1777 /var/log/celery')

        path = self.virtualenv.getPath(self.work_dir)
        workon = ''
        if self.virtualenv:
            workon = (';source /usr/local/bin/virtualenvwrapper.sh;'
                      ' workon {}; cd {}').format(
                          self.virtualenv.getVEName(), path)
        key = 'celery_{} {}@{}'.format(
            self.project_name, self.worker_name, path)
        cron.Cron({
            key: (
                "@reboot su {} -c 'cd ~; source .bashrc{}; {}'".format(
                    env['user'], workon,
                    self.getStartCommandString())
            ),
        }, for_root=True).run()

        self.restart()
