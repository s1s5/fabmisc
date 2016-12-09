# coding: utf-8
import os
import time
from datetime import datetime

from fabric.contrib.files import upload_template
from fabric.operations import run
from fabric.operations import sudo
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.contrib.files import put

from .nginx import NginxProxy
from .tomcat import Tomcat
from .managed_task import ManagedTask
from .utility import lazy_property
from .postgres import PostgresTable
from .db import TableMixin


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class GitBucket(NginxProxy, ManagedTask):
    gitbucket_home = lazy_property((str, unicode))
    version = lazy_property((str, unicode))
    tomcat = lazy_property(Tomcat)
    plugins = lazy_property()
    db_table = lazy_property(TableMixin)

    def __init__(self, version, tomcat,
                 plugins=dict(), db_table=None, **kw):
        if 'pattern' not in kw:
            kw['pattern'] = '/gitbucket'
        if 'rewrite_url' not in kw:
            kw['rewrite_url'] = False
        # if 'proxy_path' not in kw:
        #     kw['proxy_path'] = '/gitbucket/$1'
        kw['proxy_port'] = lambda: self.tomcat.proxy_port
        super(GitBucket, self).__init__(**kw)
        self.gitbucket_home = '/usr/share/{}/.gitbucket'.format(
            tomcat.name)
        self.version = version
        self.tomcat = tomcat
        self.plugins = plugins
        self.db_table = db_table

    def _backup(self):
        i = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sudo('{home}/backup.sh {home} {home}/backup-{uuid} '
             'http://localhost:{port}/gitbucket/database/backup'.format(
                 home=self.gitbucket_home, uuid=i, port=self.tomcat.port
             ))
        with cd(self.gitbucket_home):
            sudo('tar -cf - backup-{uuid} | '
                 'xz -9 -c - > {home}/backup-{uuid}.tar.xz'.format(
                     home=self.gitbucket_home, uuid=i
                 ))
        sudo('rm -rf {home}/backup-{uuid}'.format(
            home=self.gitbucket_home, uuid=i,))

    def _move2postgres(self):
        def psql(command):
            run('PGPASSWORD={} psql -d {} -U {} -h {} -c "{}"'.format(
                self.db_table.password,
                self.db_table.table,
                self.db_table.user,
                self.db_table.hostname,
                command))
        psql("SELECT setval('label_label_id_seq', "
             "(select max(label_id) + 1 from label));")
        psql("SELECT setval('activity_activity_id_seq', "
             "(select max(activity_id) + 1 from activity));")
        psql("SELECT setval('access_token_access_token_id_seq', "
             "(select max(access_token_id) + 1 from access_token));")
        psql("SELECT setval('commit_comment_comment_id_seq', "
             "(select max(comment_id) + 1 from commit_comment));")
        psql("SELECT setval('commit_status_commit_status_id_seq', "
             "(select max(commit_status_id) + 1 from commit_status));")
        psql("SELECT setval('milestone_milestone_id_seq', "
             "(select max(milestone_id) + 1 from milestone));")
        psql("SELECT setval('issue_comment_comment_id_seq', "
             "(select max(comment_id) + 1 from issue_comment));")
        psql("SELECT setval('ssh_key_ssh_key_id_seq', "
             "(select max(ssh_key_id) + 1 from ssh_key));")

    def run(self):
        run('mkdir -p {}'.format('Downloads'))
        with cd('~/Downloads'):
            if not exists('gitbucket_{}.war'.format(self.version)):
                run('wget https://github.com/gitbucket/gitbucket/'
                    'releases/download/{}/gitbucket.war -O '
                    'gitbucket_{}.war'.format(
                        self.version, self.version))
        sudo('cp ~/Downloads/gitbucket_{version}.war /var/lib/{tomcat}/'
             'webapps/gitbucket.war'.format(
                 version=self.version, tomcat=self.tomcat.name))
        self.tomcat.restart()  # create ${GITBUCKET_HOME}/.gitbucket

        for i in range(10):
            if exists(self.gitbucket_home):
                break
            time.sleep(1)  # gitbucket_home not created...

        put(os.path.join(TEMPLATE_DIR, 'gitbucket_backup.sh'),
            '{}/backup.sh'.format(self.gitbucket_home), use_sudo=True)
        sudo('chmod +x {}/backup.sh'.format(self.gitbucket_home))

        if self.db_table:
            d = dict(
                table=self.db_table.table,
                user=self.db_table.user,
                password=self.db_table.password,
                hostname=self.db_table.hostname,
            )
            if isinstance(self.db_table, PostgresTable):
                d['db_type'] = 'postgresql'
            else:
                raise Exception("Unknown database type")
            upload_template(
                'gitbucket_database.conf',
                '{}/database.conf'.format(self.gitbucket_home),
                context=d,
                template_dir=TEMPLATE_DIR, use_jinja=True, use_sudo=True)

        for key, url in self.plugins.items():
            sudo('mkdir -p {}/plugins'.format(self.gitbucket_home))
            sudo('chown -R {tomcat}:{tomcat} {home}/plugins'.format(
                home=self.gitbucket_home, tomcat=self.tomcat.name))
            with cd('~/Downloads'):
                if not exists('{}.jar'.format(key)):
                    run('wget {} -O {}.jar'.format(url, key))
                sudo('cp {key}.jar {home}/plugins/{key}.jar'.format(
                    key=key, home=self.gitbucket_home))
                sudo('chown {tomcat}:{tomcat} {home}/plugins/{key}.jar'.format(
                    key=key, home=self.gitbucket_home,
                    tomcat=self.tomcat.name))
        self.tomcat.restart()

    def getCommands(self):
        d = super(GitBucket, self).getCommands()
        d['backup'] = '_backup'
        d['move2postgres'] = '_move2postgres'
        return d
