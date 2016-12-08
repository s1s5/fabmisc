# coding: utf-8
import os
import imp
import yaml

from fabric.state import env

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


ROOT = os.path.dirname(os.path.dirname(__file__))

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))

yml_file_content = '''
roles:
  server: [vmubuntu]
  postfix: [vmubuntu]
  rabbitmq: [vmubuntu]

remote_port: 32596
deploy_base_dir: fabmisc
deploy_project_name: fabmisc

fabmisc:
  debug: True
  root: /var/www/html
'''
d = yaml.load(yml_file_content)

fabmisc.expand_config(env, d)
for key in env:
    if not key.startswith('fabmisc'):
        continue
    print key, '=>', env[key]
