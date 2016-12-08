# coding: utf-8
import os
from datetime import datetime


from fabric.operations import run
from fabric.operations import sudo
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.contrib.files import put

from .nginx import Nginx, NginxSite
from .tomcat import Tomcat
from .managed_task import ManagedTask
from .utility import lazy_property


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class GitBucket(ManagedTask):
    gitbucket_home = lazy_property((str, unicode))
    version = lazy_property((str, unicode))
    tomcat = lazy_property(Tomcat)
    nginx = lazy_property(Nginx)
    plugins = lazy_property()

    def __init__(self, version, tomcat,
                 nginx=None, plugins=dict(), *args, **kw):
        super(GitBucket, self).__init__(*args, **kw)
        self.gitbucket_home = '/usr/share/{}/.gitbucket'.format(
            tomcat.name)
        self.version = version
        self.tomcat = tomcat
        self.nginx = nginx
        self.plugins = plugins

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

        import time
        time.sleep(5)  # gitbucket_home not created...

        put(os.path.join(TEMPLATE_DIR, 'gitbucket_backup.sh'),
            '{}/backup.sh'.format(self.gitbucket_home), use_sudo=True)
        sudo('chmod +x {}/backup.sh'.format(self.gitbucket_home))

        if self.nginx:
            NginxSite(
                'gitbucket', 'nginx_proxy_site.conf',
                TEMPLATE_DIR, dict(URL_ROOT='gitbucket',
                                   PROXY_PORT=self.tomcat.port)).run()
            self.nginx.restart()

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
        d['backup'] = self._backup
        return d
