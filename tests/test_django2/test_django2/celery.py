# coding: utf-8
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_django2.settings')
app = Celery('test_django2')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS + ['test_django2'])

# from kombu import BrokerConnection
# app2 = Celery('test_django2_v2', broker="amqp://localhost:5672/")
# # app2.config_from_object('django.conf:settings')
# app2.autodiscover_tasks(lambda: settings.INSTALLED_APPS + ['test_django2'])
# # app2.broker_connection = BrokerConnection("amqp://localhost:5672/")
