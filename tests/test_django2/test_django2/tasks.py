# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from celery import task


@task
def delay_hello():
    print "task started"
    import time
    time.sleep(10)
    print "hello async task"


@task
def delay_hello2():
    print "app2 task started"
    import time
    time.sleep(20)
    print "hello2 async task !!!"
