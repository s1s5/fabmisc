# coding: utf-8
import os

from fabric.contrib.files import upload_template
from fabric.operations import run
from fabric.contrib.files import exists

from .virtualenv import Virtualenv
from .service import Service
from .nginx import NginxProxy
from .utility import lazy_property
from .utility import link


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class BuildbotMaster(Service):
    path = lazy_property((str, unicode))
    url = lazy_property((str, unicode))
    port = lazy_property(int)
    url_for_worker = lazy_property((str, unicode))
    port_for_worker = lazy_property(int)
    buildbot_url = lazy_property((str, unicode))
    title = lazy_property((str, unicode))
    title_url = lazy_property((str, unicode))
    virtualenv = lazy_property(Virtualenv)

    basename = property(lambda x: os.path.basename(x.path))
    dirname = property(lambda x: os.path.dirname(x.path))

    def __init__(self, path, url='127.0.0.1', port=8010,
                 url_for_worker=None, port_for_worker=9989,
                 buildbot_url=None,
                 title='master', title_url='',
                 virtualenv=None, **kw):
        super(BuildbotMaster, self).__init__(**kw)
        self.path = path
        self.url = url
        self.port = port
        if url_for_worker is None:
            url_for_worker = self.url
        self.url_for_worker = url_for_worker
        self.port_for_worker = port_for_worker
        if buildbot_url is None:
            buildbot_url = 'http://{}:{}/'.format(self.url, self.port)
        self.buildbot_url = buildbot_url
        self.title = title
        self.title_url = title_url
        if virtualenv is None:
            virtualenv = Virtualenv(self.name, self.dirname,
                                    requirements_filename=None)
        self.virtualenv = virtualenv
        self.workers = []

    def run(self):
        self.virtualenv.run()
        with self.virtualenv.prefix():
            run("pip install buildbot buildbot-www "
                "buildbot-waterfall-view buildbot-console-view ")
            if not exists(os.path.join(self.basename)):
                run('buildbot create-master master')
                run('mv {path}/master.cfg.sample '
                    '{path}/master.cfg'.format(path=self.basename))
        run('mkdir -p {}/config-available'.format(self.path))
        run('mkdir -p {}/config-enabled'.format(self.path))
        upload_template(
            'buildbot_master.cfg', '{}/master.cfg'.format(self.path),
            context=dict(master=self),
            template_dir=TEMPLATE_DIR, use_jinja=True)
        upload_template(
            'buildbot_master_default.py',
            '{}/config-available/default.py'.format(self.path),
            context=dict(master=self),
            template_dir=TEMPLATE_DIR, use_jinja=True)
        link('{}/config-available/default.py'.format(self.path),
             '{}/config-enabled/default.py'.format(self.path))
        self.restart()

    def getLocations(self):
        locations = [
            NginxProxy(pattern='/buildbot/', proxy_port=self.port,
                       rewrite_url=False),
            NginxProxy(pattern='/buildbot/sse', proxy_port=self.port,
                       proxy_path='sse/', rewrite_url=False, options=[
                           'proxy_buffering off',
                       ]),
            NginxProxy(pattern='/buildbot/ws', proxy_port=self.port,
                       proxy_path='ws/', rewrite_url=False, options=[
                           'proxy_http_version 1.1',
                           'proxy_set_header Upgrade $http_upgrade',
                           'proxy_set_header Connection "upgrade"',
                           'proxy_read_timeout 6000s',
                       ]),
        ]
        return locations

    def start(self):
        with self.virtualenv.prefix():
            run("buildbot reconfig {}".format(self.basename))
            run("buildbot start {}".format(self.basename))

    def stop(self):
        with self.virtualenv.prefix():
            run("buildbot stop {}".format(self.basename))

    def restart(self):
        self.stop()
        self.start()


class BuildbotWorker(Service):
    path = lazy_property((str, unicode))
    master = lazy_property(BuildbotMaster)
    worker_name = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    virtualenv = lazy_property(Virtualenv)

    basename = property(lambda x: os.path.basename(x.path))
    dirname = property(lambda x: os.path.dirname(x.path))

    def __init__(self, path, master, worker_name,
                 password, virtualenv=None, **kw):
        super(BuildbotWorker, self).__init__(**kw)
        self.path = path
        self.master = master
        self.worker_name = worker_name
        self.password = password
        if virtualenv is None:
            virtualenv = Virtualenv(self.name + "-" + self.worker_name,
                                    self.dirname,
                                    requirements_filename=None)
        self.virtualenv = virtualenv
        self.master.workers.append(self)

    def run(self):
        self.virtualenv.run()
        with self.virtualenv.prefix():
            run("pip install buildbot-worker")
            run("buildbot-worker create-worker {path} {url}:{port} "
                "{worker_name} {password}".format(
                    path=self.basename, url=self.master.url_for_worker,
                    port=self.master.port_for_worker,
                    worker_name=self.worker_name, password=self.password))
        upload_template(
            'buildbot_worker.tac', '{}/buildbot.tac'.format(self.path),
            context=dict(worker=self),
            template_dir=TEMPLATE_DIR, use_jinja=True)
        self.restart()

    def start(self):
        with self.virtualenv.prefix():
            run('buildbot-worker start {}'.format(self.basename))

    def stop(self):
        with self.virtualenv.prefix():
            run('buildbot-worker stop {}'.format(self.basename))

    def restart(self):
        self.stop()
        self.start()
