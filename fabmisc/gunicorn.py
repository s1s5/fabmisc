# coding: utf-8
import os

from fabric.api import warn_only
from fabric.operations import sudo
from fabric.contrib.files import exists
from fabric.state import env
from fabric.operations import run
from fabric.context_managers import cd
# from fabric.contrib.files import upload_template

from . import cron
from . import service
from .nginx import NginxProxy
from .virtualenv import Virtualenv
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class Gunicorn(NginxProxy, service.Service):
    work_dir = lazy_property((str, unicode))
    app_name = lazy_property((str, unicode))
    virtualenv = lazy_property(Virtualenv)
    workers = lazy_property(int)
    threads = lazy_property(int)
    timeout = lazy_property(int)
    _reload = lazy_property((str, unicode))
    pidfile = lazy_property((str, unicode))
    umask = lazy_property((str, unicode))
    accesslog = lazy_property((str, unicode))
    errorlog = lazy_property((str, unicode))
    loglevel = lazy_property((str, unicode))

    def __init__(self, app_name, work_dir=None,
                 virtualenv=None, **kw):
        super(Gunicorn, self).__init__(**kw)
        self.app_name = app_name
        self.work_dir = work_dir
        self.virtualenv = virtualenv

        self.workers = kw.get('workers', 4)  # -w
        self.threads = kw.get('threads', 1)  # --threads
        self.timeout = kw.get('timeout', 60)  # -t
        self._reload = '--reload' if kw.get('reload', False) else ''
        self.pidfile = kw.get('pidfile', self.getDefaultPidFile)  # -p
        self.umask = kw.get('umask', '0002')  # -m
        self.accesslog = kw.get('accesslog',
                                self.getDefaultAccessLog)  # --access-logfile
        self.errorlog = kw.get('errorlog',
                               self.getDefaultErrorLog)  # --error-logfile
        self.loglevel = kw.get('loglevel', 'debug')  # --log-level

    def getCommandString(self):
        workers = self.workers
        if workers <= 0:
            workers = 2 * int(run('nproc')) + 1
        options = [
            '--name {}'.format(self.app_name),
            '-b {}:{}'.format(
                self.proxy_host,
                self.proxy_port),
            '-D',
            '-w {}'.format(workers),
            '--threads {}'.format(self.threads),
            '-t {}'.format(self.timeout),
            '{}'.format(self._reload),
            '-p {}'.format(self.pidfile),
            '-m {}'.format(self.umask),
            '--access-logfile {}'.format(self.accesslog),
            '--error-logfile {}'.format(self.errorlog),
            '--log-level {}'.format(self.loglevel),
        ]
        return 'gunicorn {} {}'.format(self.app_name, ' '.join(options))

    def start(self):
        self.stop()

        if self.virtualenv:
            with self.virtualenv.prefix(self.work_dir):
                run(self.getCommandString(), pty=False)
        else:
            with cd(self.work_dir):
                run(self.getCommandString(), pty=False)

    def stop(self):
        if exists(self.pidfile):
            with warn_only():
                run("kill -TERM `cat {}`".format(self.pidfile))

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        sudo('mkdir -p /var/log/gunicorn')
        sudo('chmod 1777 /var/log/gunicorn')

        path = self.virtualenv.getPath(self.work_dir)
        workon = ''
        if self.virtualenv:
            workon = (';source /usr/local/bin/virtualenvwrapper.sh;'
                      ' workon {}; cd {}').format(
                          self.virtualenv.getVEName(), path)
        cron.Cron({
            'gunicorn_{}@{}'.format(self.app_name, path): (
                "@reboot su {} -c 'cd ~; source .bashrc{}; {}'".format(
                    env['user'], workon,
                    self.getCommandString())
            ),
        }, for_root=True).run()

        self.restart()

    def getDefaultPidFile(self):
        return "/tmp/gunicorn_app_{}.pid".format(self.proxy_port)

    def getDefaultAccessLog(self):
        return "/var/log/gunicorn/app_access_{}.log".format(self.proxy_port)

    def getDefaultErrorLog(self):
        return "/var/log/gunicorn/app_error_{}.log".format(self.proxy_port)
