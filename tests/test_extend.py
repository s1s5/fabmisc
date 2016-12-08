# coding: utf-8
import os
import imp

from fabric.state import env
from fabric.api import execute
from fabric.operations import run
from fabric.decorators import task


ROOT = os.path.dirname(os.path.dirname(__file__))

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))


class Test0(fabmisc.service.Service):
    def __init__(self, message, *args, **kw):
        super(Test0, self).__init__(*args, **kw)
        self.message = message

    def _backup(self):
        run('echo backup {}'.format(self.message))

    def getCommands(self):
        d = super(Test0, self).getCommands()
        d['backup'] = self._backup
        return d

    def run(self):
        run('echo task0 {}; hostname'.format(self.message))


class Test1(fabmisc.service.Service):
    def run(self):
        run('echo task1; hostname')

Test0("A", roles=('a', ))
Test0("B", roles=('b', ))
Test1("AB", roles=('a', 'b'))


@task
def deploy():
    '''set environment variables'''
    env['hosts'] = ['vmubuntu0']
    env['roledefs'] = {
        'a': ['vmubuntu1', 'vmubuntu0'],
        'b': []
    }
    execute('services.deploy')
