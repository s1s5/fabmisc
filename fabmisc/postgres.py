# coding: utf-8
import os

from fabric.state import env
from fabric.operations import run
from fabric.operations import sudo
from fabric.contrib.console import confirm
from fabric.context_managers import hide
from fabric.contrib.files import upload_template
from fabric.api import cd
from fabtools import postgres as funcs
from fabric.api import warn_only

from . import service
from .managed_task import ManagedTask
from .utility import lazy_property
from .db import DatabaseMixin


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

    def __init__(self, version_string, **kw):
        super(Postgres, self).__init__(**kw)
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


class PostgresDatabase(DatabaseMixin, ManagedTask):
    def run(self):
        user = env['user']
        if self.user:
            user = self.user

        if not funcs.user_exists(user):
            funcs.create_user(user, self.password)

        if not funcs.database_exists(self.database):
            funcs.create_database(
                self.database, user, locale='ja_JP.utf8')

    def sql(self, command):
        run('PGPASSWORD={} psql -d {} -U {} -h {} -c "{}"'.format(
            self.password,
            self.database,
            self.user,
            self.hostname,
            command))

    def backup(self, filename):
        run('PGPASSWORD={} pg_dump -d {} -U {} -h {} | bzip2 -9 -c > {}'.format(
            self.password, self.database, self.user, self.hostname, filename))

    def restore(self, filename):
        if not confirm('Are you sure to delete database?', default=False):
            return
        with warn_only():
            sudo('sudo -u postgres dropdb {}'.format(self.database))
        funcs.create_database(
            self.database, self.user, locale='ja_JP.utf8')
        sudo('bzip2 -d -c {} | sudo -u postgres psql -d {}'.format(
            filename, self.database))
