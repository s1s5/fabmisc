# coding: utf-8
import os

from fabric.state import env
from fabric.operations import sudo
from fabric.context_managers import hide
from fabric.contrib.files import upload_template
from fabtools import postgres as funcs

from . import service
from .managed_task import ManagedTask
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


# $ psql -h 127.0.0.1 -p 5432 -d <database>
# > \l  # <= table 一覧
class Postgres(service.Service):
    version_string = lazy_property((str, unicode))

    def __init__(self, version_string, *args, **kw):
        super(Postgres, self).__init__(*args, **kw)
        self.version_string = version_string

    def run(self):
        apt_packages = [
            "postgresql-{}".format(self.version_string),
            "postgresql-client-{}".format(self.version_string),
            "postgresql-server-dev-{}".format(self.version_string),
        ]
        with hide('stdout'):
            for package in apt_packages:
                sudo('apt-get install {} -y'.format(package), pty=False)

        dst = '/etc/postgresql/{}/main/pg_hba.conf'.format(self.version_string)
        upload_template('postgres_pg_hba.conf', dst,
                        context={}, template_dir=TEMPLATE_DIR,
                        use_jinja=True, use_sudo=True)
        self.restart()


class PostgresTable(ManagedTask):
    db_table = lazy_property((str, unicode))
    db_user = lazy_property((str, unicode))
    db_pass = lazy_property((str, unicode))

    def __init__(self, db_table, db_user=None, db_pass=None):
        self.db_table = db_table
        self.db_user = db_user
        self.db_pass = db_pass

    def run(self):
        user = env['user']
        if self.db_user:
            user = self.db_user
        d = {}
        d.update(self.__dict__)
        d['db_user'] = user

        if not funcs.user_exists(user):
            funcs.create_user(user, self.db_pass)

        if not funcs.database_exists(self.db_table):
            funcs.create_database(
                self.db_table, user, locale='ja_JP.utf8')
