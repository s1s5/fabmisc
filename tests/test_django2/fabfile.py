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
    "test_django2", "work/fabmisc/tests/test_django2")
fabmisc.Rabbitmq()
broker0 = fabmisc.RabbitmqBroker(
    user="broker0", password="broker0_password",
    vhost="broker0")
broker1 = fabmisc.RabbitmqBroker(
    user="broker1", password="broker1_password",
    vhost="broker1")
fabmisc.Celery('test_django2', 'test_django2_worker0',
               virtualenv=lazy(env, 'virtualenv'))
fabmisc.Celery('test_django2', 'test_django2_worker1',
               broker=broker1, virtualenv=lazy(env, 'virtualenv'))
gunicorn = fabmisc.Gunicorn(
    'test_django2.wsgi:application',
    virtualenv=lazy(env, 'virtualenv'),
    pattern='/test_django2',
    proxy_port=8199)
fabmisc.NginxSite(nginx, 'test_django2',
                  locations=(gunicorn, ))


@task
def conf(yml_file='conf.yml'):
    d = yaml.load(open(yml_file))
    fabmisc.expand_config(env, d)
