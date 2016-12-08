# coding: utf-8
from fabric.state import env
from fabric.decorators import task
import yaml

import fabmisc

env.forward_agent = True
env.use_ssh_config = True

lazy = fabmisc.lazy

fabmisc.Packages(
    lazy(env, 'apt', []),
    lazy(env, 'pip', []))
nginx = fabmisc.Nginx()
fabmisc.Git('work/fabmisc', 'git@github.com:s1s5/fabmisc.git')
env['virtualenv'] = fabmisc.Virtualenv(
    "test_django", "work/fabmisc/tests/test_django")
gunicorn = fabmisc.Gunicorn(
    'test_django.wsgi:application',
    virtualenv=lazy(env, 'virtualenv'))
fabmisc.NginxSite(nginx, 'test_django',
                  locations=(gunicorn, ))


@task
def conf(yml_file='conf.yml'):
    d = yaml.load(open(yml_file))
    fabmisc.expand_config(env, d)
