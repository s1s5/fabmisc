# coding: utf-8
import os

from fabric.state import env
from fabric.operations import sudo
from fabric.context_managers import hide
from fabric.contrib.files import upload_template
from fabric.api import cd
from fabtools import postgres as funcs

from . import service
from .managed_task import ManagedTask
from .utility import lazy_property
from .db import TableMixin


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


def _run_as_pg(command):
    """
    Run command as 'postgres' user
    """
    with cd('/var/lib/postgresql'):
        return sudo('sudo -u postgres %s' % command)

funcs._run_as_pg = _run_as_pg


# $ psql -h 127.0.0.1 -p 5432 -d <database>
# > \l  # <= table 一覧
class Postgres(service.Service):
    version_string = lazy_property((str, unicode))

    def __init__(self, version_string, *args, **kw):
        super(Postgres, self).__init__(*args, **kw)
        self.version_string = version_string

    def service(self, command, *args, **kw):
        return sudo('service postgresql {}'.format(command))

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


class PostgresTable(TableMixin, ManagedTask):
    def run(self):
        user = env['user']
        if self.user:
            user = self.user

        if not funcs.user_exists(user):
            funcs.create_user(user, self.password)

        if not funcs.database_exists(self.table):
            funcs.create_database(
                self.table, user, locale='ja_JP.utf8')
