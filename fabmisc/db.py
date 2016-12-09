# coding: utf-8
import uuid

from fabric.operations import run
from fabric.operations import get
from fabric.operations import put
from .utility import lazy_property


class DatabaseMixin(object):
    database = lazy_property((str, unicode))
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))
    hostname = lazy_property((str, unicode))

    def __init__(self, database, user=None,
                 password=None, hostname='127.0.0.1', **kw):
        super(DatabaseMixin, self).__init__(**kw)
        self.database = database
        self.user = user
        self.password = password
        self.hostname = hostname

    def getCommands(self):
        org = {
            'sql': 'sql',
            'backup': 'backup',
            'restore': 'restore',
            'backup_to_local': 'backup_to_local',
            'restore_from_local': 'restore_from_local',
        }
        org.update(super(DatabaseMixin, self).getCommands())
        return org

    def sql(self, command):
        raise NotImplementedError()

    def backup(self, filename):
        raise NotImplementedError()

    def restore(self, filename):
        raise NotImplementedError()

    def backup_to_local(self, filename):
        tmp_filename = '/tmp/{}.backup.xz'.format(uuid.uuid4().hex)
        self.backup(tmp_filename)
        get(remote_path=tmp_filename, local_path=filename)
        run('rm {}'.format(tmp_filename))

    def restore_from_local(self, filename):
        tmp_filename = '/tmp/{}.backup.xz'.format(uuid.uuid4().hex)
        put(remote_path=tmp_filename, local_path=filename)
        self.restore(tmp_filename)
        run('rm {}'.format(tmp_filename))
