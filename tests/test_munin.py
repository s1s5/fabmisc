# coding: utf-8
import os
import imp
import yaml

from fabric.state import env
from fabric.decorators import task

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


ROOT = os.path.dirname(os.path.dirname(__file__))

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))

nginx = fabmisc.Nginx(roles=('manager', 'slave'))
munin = fabmisc.Munin(clients={
    'group': {
        'vmubuntu0': '192.168.11.204',
    }
}, roles=('manager', ))

fabmisc.NginxSite(
    nginx, 'munin',
    locations=(munin, ), roles=('manager', ))

fabmisc.MuninNode(('192.168.11.205', ), roles=('slave', ))


@task
def setup():
    yml_file_content = '''
roledefs:
  manager: [vmubuntu0]
  slave: [vmubuntu1]
'''
    d = yaml.load(yml_file_content)
    env.roledefs = d['roledefs']

# # install nginx, munin, munin-node
# $ fab -f test_munin.py setup tasks.run
