"""test_django2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from django.http.response import HttpResponse


def return_hello(*args, **kw):
    from test_django2 import tasks
    tasks.delay_hello.delay()

    from kombu import BrokerConnection
    tasks.delay_hello2.apply_async(
        (), connection=BrokerConnection(
            "amqp://broker1:broker1_password@localhost:5672/broker1"))
    return HttpResponse("hello world")

urlpatterns = [
    url(r'^hello/', return_hello),
    url(r'^admin/', admin.site.urls),
]
