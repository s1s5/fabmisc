# coding: utf-8
import os
from fabric.operations import sudo
from fabric.contrib.files import append
from fabric.contrib.files import upload_template

from .nginx import NginxAlias
from . import service
from . import utility
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class Munin(NginxAlias, service.Service):
    clients = lazy_property(dict)
    dbdir = lazy_property((str, unicode))
    htmldir = lazy_property((str, unicode))
    logdir = lazy_property((str, unicode))
    rundir = lazy_property((str, unicode))

    def __init__(self, clients,
                 dbdir='/var/lib/munin',
                 htmldir='/var/www/munin',
                 logdir='/var/log/munin',
                 rundir='/var/run/munin', **kw):
        '''clients = {
            "group": {
                "hostname": "ip_address",
                ...
            },
            ...
        }'''
        pattern = '/munin'
        if 'pattern' in kw:
            pattern = kw.pop('pattern')
        super(Munin, self).__init__(
            pattern=pattern,
            path=lambda: self.htmldir,
            **kw)
        self.clients = clients
        self.dbdir = dbdir
        self.htmldir = htmldir
        self.logdir = logdir
        self.rundir = rundir

    def run(self):
        utility.apt('munin')
        for key in ["dbdir", "htmldir", "logdir", "rundir"]:
            d = getattr(self, key)
            sudo('mkdir -p {}'.format(d))
            sudo('chown -R munin:munin {}'.format(d))

        filename = '/etc/munin/munin.conf'
        upload_template('munin.conf', filename,
                        context=dict(
                            dbdir=self.dbdir,
                            htmldir=self.htmldir,
                            logdir=self.logdir,
                            rundir=self.rundir,
                            clients=self.clients
                        ), template_dir=TEMPLATE_DIR,
                        use_jinja=True, use_sudo=True)

        # TODO(sawai) : change cron settings
        self.restart()

    def service(self, command, *args, **kw):
        return sudo('/etc/init.d/munin {}'.format(command))

    def getCommands(self):
        d = super(Munin, self).getCommands()
        d['create'] = self.create
        return d

    def create(self):
        sudo('su - munin --shell=/usr/bin/munin-cron')


class MuninNode(service.Service):
    name = 'munin-node'
    server_ips = lazy_property()
    port = lazy_property(int)
    plugins = lazy_property()

    def __init__(self, server_ips, port=4949, plugins=None, **kw):
        super(MuninNode, self).__init__(**kw)
        self.server_ips = server_ips
        self.port = port
        self.plugins = plugins

    def run(self):
        filename = '/etc/munin/munin-node.conf'
        utility.apt('munin-node')
        suffix = '\t# {}'.format('w65JJ8jG')  # singleton magic number
        utility.delete_lines_with_sed(filename, suffix, use_sudo=True)
        for i in self.server_ips:
            append(filename, 'allow ^{}${}'.format(
                self.escape(i), suffix), use_sudo=True)
        # utility.apt('nginx-extras')
        self.restart()

    def escape(self, value):
        return value.replace('.', '\\.')

    def service(self, command, *args, **kw):
        return sudo('/etc/init.d/munin-node {}'.format(command))
