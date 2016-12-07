# coding: utf-8
import os

from fabric.operations import run
from fabric.api import warn_only
from fabric.context_managers import cd, prefix
from fabric.contrib.files import exists

from .managed_task import ManagedTask
from .utility import lazy_property


class Virtualenv(ManagedTask):
    _name = lazy_property((str, unicode))
    _path = lazy_property((str, unicode))
    _workon_home = lazy_property((str, unicode))
    _requirements_filename = lazy_property((str, unicode))

    class Wrapper(object):
        def __init__(self, name, workon_home, path):
            self.path = path
            self.name = name
            self.workon_home = workon_home

        def __enter__(self):
            self.p = [
                cd(self.path),
                prefix('WORKON_HOME={}'.format(self.workon_home)),
                prefix('source /usr/local/bin/virtualenvwrapper.sh'),
                prefix('workon {}'.format(self.name)),
            ]

            map(lambda x: x.__enter__(), self.p)

        def __exit__(self, *args, **kw):
            map(lambda x: x.__exit__(*args, **kw), self.p)

    def __init__(self, name, path,
                 workon_home='~/.virtualenvs',
                 requirements_filename='requirements.txt', *args, **kw):
        super(Virtualenv, self).__init__(*args, **kw)
        self._name = name
        self._path = path
        self._workon_home = workon_home
        self._requirements_filename = requirements_filename

    def run(self):
        found = False
        with warn_only():
            if run("test -d ~/.virtualenvs/{}".format(self._name)).failed:
                pass
            else:
                found = True

        if not exists(self._path):
            run("mkdir {}".format(self._path))

        if not found:
            with cd(self._path), \
                prefix('WORKON_HOME={}'.format(self._workon_home)), \
                prefix('source /usr/local/bin/virtualenvwrapper.sh'):

                run('mkvirtualenv --no-site-packages {}'.format(self._name))
                # with prefix('workon {}'.format(self._name)):
                #     run('setvirtualenvproject')

        with cd(self._path), \
            prefix('WORKON_HOME={}'.format(self._workon_home)), \
            prefix('source /usr/local/bin/virtualenvwrapper.sh'), \
            prefix('workon {}'.format(self._name)):

            run('pip install -U -r {}'.format(self._requirements_filename),
                pty=False)

    def getVEName(self):
        return self._name

    def getExecutable(self, executable_name):
        return '~/.virtualenvs/{}/bin/{}'.format(self._name, executable_name)

    def getPath(self, path=None):
        np = self._path
        if path:
            if os.path.isabs(path):
                np = path
            else:
                np = os.path.join(np, path)
        return np

    def prefix(self, path=None):
        return self.Wrapper(self._name, self._workon_home, self.getPath(path))
