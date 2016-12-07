# coding: utf-8
import uuid

from fabric.state import env
from fabric.operations import run, sudo
from fabric.context_managers import hide
from fabric.context_managers import shell_env
from fabric.contrib.files import exists


def _run_or_sudo(use_sudo):
    if use_sudo:
        return sudo
    return run


def apt(package):
    with hide('stdout'), shell_env(DEBIAN_FRONTEND='noninteractive'):
        sudo('apt-get install {} -y'.format(package), pty=False)


def chmod(path, mode, use_sudo=False):
    if mode:
        _run_or_sudo(use_sudo)('chmod {} {}'.format(mode, path))


def touch(path, mode=None, use_sudo=False):
    _run_or_sudo(use_sudo)("touch {}".format(path))
    chmod(path, mode, use_sudo)


def mkdir(path, use_sudo=False, mode=None):
    _run_or_sudo(use_sudo)("mkdir -p {}".format(path))
    chmod(path, mode, use_sudo)


def link(src, dst, use_sudo=False):
    if exists(dst):
        _run_or_sudo(use_sudo)("rm {}".format(dst))
    _run_or_sudo(use_sudo)("ln -s {} {}".format(src, dst))


def rm(path, use_sudo=False):
    if exists(path):
        _run_or_sudo(use_sudo)("rm {}".format(path))


def delete_lines_with_sed(path, sed_pattern, use_sudo=False):
    _run_or_sudo(use_sudo)("sed -i '/{}/d' {}".format(sed_pattern, path))


class DummyAccessor(object):
    def __init__(self, value, klass):
        self.value = value
        self.klass = klass

    def __call__(self):
        if self.value is None:
            return self.value
        if self.klass and (not isinstance(self.value, self.klass)):
            raise TypeError()
        return self.value


class _RaiseError(object):
    pass


class LazyAccessor(object):
    def __init__(self, dictionary, key,
                 default_value=_RaiseError, klass=None):
        self.dictionary = dictionary
        self.key = key
        self.default_value = default_value
        self.klass = klass

    def __call__(self):
        if self.key not in self.dictionary:
            if self.default_value is _RaiseError:
                raise KeyError()
            else:
                value = self.default_value
        else:
            value = self.dictionary[self.key]
        if self.klass and (not isinstance(value, self.klass)):
            raise TypeError()
        return value


def lazy(dictionary, key, default_value=_RaiseError):
    return LazyAccessor(dictionary, key, default_value)


def recv_lazy(value, klass=None):
    if isinstance(value, LazyAccessor):
        return LazyAccessor(value.dictionary, value.key,
                            value.default_value, klass)
    else:
        return DummyAccessor(value, klass)


def lazy_property(klass=None):
    prop_name = uuid.uuid4()

    def getter(self):
        p = '_uuid_' + prop_name
        a = getattr(self, p)
        return a()

    def setter(self, value):
        setattr(self, '_uuid_' + prop_name, recv_lazy(value, klass))

    return property(getter, setter)
