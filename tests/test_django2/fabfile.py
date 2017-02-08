# coding: utf-8
from fabric.state import env
from fabric.decorators import task
import yaml

import fabmisc

env.forward_agent = True
env.use_ssh_config = True
env.disable_known_hosts = True

lazy = fabmisc.lazy

packages = fabmisc.Packages(
    lazy(env, 'apt', []),
    lazy(env, 'pip', []))
nginx = fabmisc.Nginx()
git = fabmisc.Git('work/fabmisc', 'git@github.com:s1s5/fabmisc.git')
virtualenv = fabmisc.Virtualenv(
    "test_django2", "work/fabmisc/tests/test_django2")
rabbitmq = fabmisc.Rabbitmq()
broker0 = fabmisc.RabbitmqBroker(
    user="broker0", password="broker0_password",
    vhost="broker0")
broker1 = fabmisc.RabbitmqBroker(
    user="broker1", password="broker1_password",
    vhost="broker1")
celery0 = fabmisc.Celery('test_django2', 'test_django2_worker0',
                         virtualenv=virtualenv)
celery1 = fabmisc.Celery('test_django2', 'test_django2_worker1',
                         broker=broker1, virtualenv=virtualenv)
gunicorn = fabmisc.Gunicorn(
    'test_django2.wsgi:application',
    virtualenv=virtualenv,
    pattern='/test_django2',
    proxy_port=8199)
nginx_site = fabmisc.NginxSite(nginx, 'test_django2',
                               locations=(gunicorn, ))


@task
def say_hello():
    from fabric.operations import run
    run('echo hello world')


@task
def conf(yml_file='conf.yml'):
    d = yaml.load(open(yml_file))
    fabmisc.expand_config(env, d)


fabmisc.task_group('deploy', (
    packages,
    nginx,
    git,
    virtualenv,
    rabbitmq,
    say_hello,
    broker0,
    broker1,
    celery0,
    celery1,
    gunicorn,
    nginx_site))

fabmisc.task_group('update', (
    say_hello,
    git,
    virtualenv,
))
