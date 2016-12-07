# coding: utf-8
import os
import imp

from fabric.tasks import Task
from fabric.state import env
from fabric.decorators import task
from fabric import api as fab_api


class ManagedTask(Task):
    __tasks = []
    __module = None

    def __init__(self, hosts=(), roles=(), runs_once=False, *args, **kw):
        super(ManagedTask, self).__init__(*args, **kw)
        self.__decorator = lambda x: x
        if roles:
            self.__decorator = lambda x: fab_api.roles(roles)(x)
        if hosts:
            self.__decorator = lambda x: fab_api.hosts(hosts)(x)
        if runs_once:
            self.__decorator = lambda x: fab_api.runs_once()(x)
        self.__createTasks()

    def getName(self):
        if self.name is not None and self.name != 'undefined':
            return self.name
        return self.__class__.__name__.lower()

    def _getModuleName(self):
        return "tasks"

    def _getModule(self):
        if ManagedTask.__module is None:
            ManagedTask.__module = imp.new_module(self._getModuleName())
            top_package = __import__(
                os.path.splitext(os.path.split(env.real_fabfile)[1])[0])
            setattr(top_package, self._getModuleName(), ManagedTask.__module)
        return ManagedTask.__module

    def getCommands(self):
        return dict(
            run=self.run,
        )

    def _messagePrefix(self):
        return "task "

    def __createTasks(self):
        name = self.getName()
        if not hasattr(self._getModule(), name):
            module = imp.new_module('{}.{}'.format(
                self._getModuleName(), name))
            setattr(self._getModule(), name, module)
        else:
            module = getattr(self._getModule(), name)

        for fname, f in self.getCommands().items():
            message = '{}{} {}'.format(
                self._messagePrefix(), name, fname)
            if hasattr(module, fname):
                pf = getattr(module, fname)

                def chain(a, b):
                    def _f():
                        fab_api.execute(a)
                        fab_api.execute(self.__decorator(b))
                    _f.__doc__ = message
                    return _f
                f = chain(pf, f)
            else:
                f.__func__.__doc__ = message
                f = self.__decorator(f)
            setattr(module, fname, task(name=fname)(f))
