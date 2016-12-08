# coding: utf-8
import os

from fabric.state import env
from fabric.operations import run
from fabric.context_managers import cd
from fabric.contrib.files import upload_template

from . import cron
from . import service
from .nginx import NginxProxy
from .virtualenv import Virtualenv
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class Gunicorn(service.Service, NginxProxy):
    work_dir = lazy_property((str, unicode))
    app_name = lazy_property((str, unicode))
    shell_filename = lazy_property((str, unicode))
    conf_filename = lazy_property((str, unicode))
    virtualenv = lazy_property(Virtualenv)

    def __init__(self, app_name, work_dir=None,
                 shell_filename='gunicorn.sh',
                 conf_filename='gunicorn_conf.py',
                 virtualenv=None, **kw):
        pattern = app_name
        if 'pattern' in kw:
            pattern = kw.pop('pattern')
        super(Gunicorn, self).__init__(pattern=pattern, **kw)
        self.app_name = app_name
        self.work_dir = work_dir
        self.shell_filename = shell_filename
        self.conf_filename = conf_filename
        self.virtualenv = virtualenv

    def service(self, command, *args, **kw):
        if self.virtualenv:
            with self.virtualenv.prefix(self.work_dir):
                run('./{} {}'.format(self.shell_filename, command), pty=False)
        else:
            with cd(self.work_dir):
                run('./{} {}'.format(self.shell_filename, command), pty=False)

    def run(self):
        path = self.virtualenv.getPath(self.work_dir)
        upload_template('gunicorn_conf.py',
                        os.path.join(path, self.conf_filename),
                        context=self.__dict__, template_dir=TEMPLATE_DIR,
                        use_jinja=True)
        upload_template('gunicorn.sh',
                        os.path.join(path, self.shell_filename),
                        context=self.__dict__, template_dir=TEMPLATE_DIR,
                        use_jinja=True, mode='0755')
        workon = ''
        if self.virtualenv:
            workon = '; workon {}; cd {}'.format(
                self.virtualenv.getVEName(), path)
        c = cron.Cron({
            'gunicorn_{}@{}'.format(self.app_name, path): (
                "@reboot su {} -c 'cd ~; source .bashrc{}; ./{} start'".format(
                    env['user'], workon,
                    self.shell_filename)
            ),
        }, for_root=True)
        c.run()
        self.restart()
