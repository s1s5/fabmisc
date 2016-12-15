# coding: utf-8
import uuid

from fabric.operations import run
from fabric.operations import get
from fabric.operations import put


class BackupableMixin(object):
    def backup(self, filename):
        raise NotImplementedError()

    def restore(self, filename):
        raise NotImplementedError()

    def backup_to_local(self, filename):
        tmp_filename = '/tmp/{}.backup.tmp'.format(uuid.uuid4().hex)
        self.backup(tmp_filename)
        get(remote_path=tmp_filename, local_path=filename)
        run('rm {}'.format(tmp_filename))

    def restore_from_local(self, filename):
        tmp_filename = '/tmp/{}.backup.tmp'.format(uuid.uuid4().hex)
        put(remote_path=tmp_filename, local_path=filename)
        self.restore(tmp_filename)
        run('rm {}'.format(tmp_filename))
