# coding: utf-8
import os
import imp

from fabric.state import env
from fabric.api import execute
from fabric.operations import run
from fabric.decorators import task, roles

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


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
        d['backup'] = '_backup'
        return d

    def run(self):
        run('echo ---- task0 {}; ifconfig | grep 192.168'.format(self.message))


class Test1(Test0):
    def run(self):
        run('echo ---- task1 {}; ifconfig | grep 192.168'.format(self.message))

a = Test0("A", roles=('a', ))
b = Test0("B", roles=('b', ))
ab = Test1("AB", roles=('a', 'b'))


@task
def conf():
    '''set environment variables'''
    env['roledefs'] = {
        'a': ['vmubuntu1', 'vmubuntu0'],
        'b': ['vmubuntu0']
    }


@task
def deploy():
    execute('conf')
    execute('services.deploy')


@task
@roles('b',)
def hello_b():
    run('echo hello B!')

fabmisc.task_group('a_only', [a, ab])
fabmisc.task_group('b_only', [b, ab])
# fabmisc.task_group('b_only', [b, ab, hello_b]) <= not work....
