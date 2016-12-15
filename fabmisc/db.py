# coding: utf-8
from .backupable import BackupableMixin
from .utility import lazy_property


class DatabaseMixin(BackupableMixin):
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
