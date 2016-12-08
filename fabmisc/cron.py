# coding: utf-8
import uuid
from fabric.api import warn_only
from fabric.operations import run, sudo
from fabric.contrib.files import append

from . import utility
from .utility import lazy_property
from .managed_task import ManagedTask


class Cron(ManagedTask):
    line_map = lazy_property(dict)
    for_root = lazy_property(bool)

    def __init__(self, line_map, for_root=False, **kw):
        super(Cron, self).__init__(**kw)
        self.line_map = line_map
        self.for_root = for_root

    def run(self):
        r = run
        if self.for_root:
            r = sudo
        u = uuid.uuid4()
        fn = '/tmp/crontab_{}.dump'.format(u)
        with warn_only():
            r('crontab -l > {}'.format(fn))
        for key, value in self.line_map.items():
            utility.delete_lines_with_sed(
                fn, '# {}'.format(key), use_sudo=self.for_root)
            append(fn, '{} # {}'.format(value, key), use_sudo=self.for_root)
        r('crontab < {}'.format(fn))
