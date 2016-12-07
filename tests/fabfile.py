# coding: utf-8
import sys
import os
import imp

from fabric.state import env
from fabric.api import execute
from fabric.tasks import Task
from fabric.operations import run
from fabric.decorators import task

env.forward_agent = True
env.use_ssh_config = True


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, ROOT)

fabtools = imp.load_module(
    "fabtools", *imp.find_module(
        "fabtools", [ROOT]))

nginx = fabtools.Nginx()
plugins = {
    'gitbucket-h2-backup-plugin':
    'https://github.com/gitbucket-plugins/gitbucket-h2-backup-plugin/'
    'releases/download/1.3.0/gitbucket-h2-backup.jar',
    'gitbucket-gist-plugin':
    'https://github.com/gitbucket/gitbucket-gist-plugin/'
    'releases/download/4.3.0/gitbucket-gist-plugin_2.11-4.3.0.jar',
    'gitbucket-pages-plugin': 'https://github.com/yaroot/'
    'gitbucket-pages-plugin/releases/download/v0.8/pages-plugin_2.11-0.8.jar',
    'gitbucket-network-plugin': 'https://github.com/mrkm4ntr/'
    'gitbucket-network-plugin/releases/download/1.1/'
    'gitbucket-network-plugin_2.11-1.1.jar',
}

java = fabtools.OracleJava()
tomcat = fabtools.Tomcat('8', java.getJavaHome())
gitbucket = fabtools.GitBucket(
    '4.7.1', tomcat, nginx=nginx, plugins=plugins)
# backup = task(gitbucket.command_backup)

# # fabtools.service.create_services(globals())


@task
def deploy():
    nginx.run()
    java.run()
    tomcat.run()
    gitbucket.run()

# class Test0(fabtools.service.ServiceMixin, Task):
#     def __init__(self, message, *args, **kw):
#         super(Test0, self).__init__(*args, **kw)
#         self.message = message

#     def run(self):
#         run('echo task0 {}; hostname'.format(self.message))


# class Test1(fabtools.service.ServiceMixin, Task):
#     def run(self):
#         run('echo task1; hostname')

# Test0("test", hosts=('vmubuntu0', ))
# Test1(hosts=('vmubuntu1', ))


# Test0("A", roles=('a', ))
# Test0("B", roles=('b', ))


# @task
# def set():
#     '''set environment variables'''
#     env['hosts'] = []
#     env['roledefs'] = {
#         'a': ['vmubuntu1'],
#         'b': []
#     }
#     execute('services.deploy')

fabtools.Munin(clients={
    'group': {
        'vmubuntu0': '192.168.11.204',
    }
}, hosts=('vmubuntu1', ))

fabtools.MuninNode(('192.168.11.205', ), hosts=('vmubuntu0', ))
