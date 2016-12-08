# coding: utf-8
import os
import imp

from fabric.state import env
from fabric.operations import sudo
from fabric.decorators import task
from fabric import api as fab_api

from .managed_task import ManagedTask


class Service(ManagedTask):
    __services = []
    __module = None

    def __init__(self, **kw):
        super(Service, self).__init__(**kw)
        Service.__services.append(self)
        all_services = ','.join([x.name for x in self.__services])
        for key, value in self.__allMethods().items():
            value.__func__.__doc__ = (
                '{} all services ({})'.format(key, all_services))
            setattr(self._getModule(), key, task(name=key)(value))

    def service(self, command, *args, **kw):
        if self.name:
            return sudo('service {} {}'.format(self.name, command))
        raise NotImplementedError()

    def start(self):
        self.service('start')

    def stop(self):
        self.service('stop')

    def restart(self):
        self.service('restart')

    def getCommands(self):
        d = {}
        d['deploy'] = self.run
        d['start'] = self.start
        d['stop'] = self.stop
        d['restart'] = self.restart
        return d

    @classmethod
    def __runAll(self, method_name):
        for i in Service.__services:
            fab_api.execute(i._decorator(getattr(i, method_name)))

    @classmethod
    def __deployAll(self):
        self.__runAll('run')

    @classmethod
    def __startAll(self):
        self.__runAll('start')

    @classmethod
    def __stopAll(self):
        self.__runAll('stop')

    @classmethod
    def __restartAll(self):
        self.__runAll('restart')

    @classmethod
    def __allMethods(self):
        return {
            'deploy': self.__deployAll,
            'start': self.__startAll,
            'stop': self.__stopAll,
            'restart': self.__restartAll,
        }

    def _messagePrefix(self):
        return "service "

    def _getModuleName(self):
        return "services"

    def _getModule(self):
        if Service.__module is None:
            Service.__module = imp.new_module(self._getModuleName())
            top_package = __import__(
                os.path.splitext(os.path.split(env.real_fabfile)[1])[0])
            setattr(top_package, self._getModuleName(), Service.__module)
        return Service.__module
