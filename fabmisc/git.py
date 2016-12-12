# coding: utf-8
# import os

from fabric.contrib.files import exists
from fabric.operations import run
from fabric.context_managers import cd

from .managed_task import ManagedTask
from .utility import apt, lazy_property


class Git(ManagedTask):
    deploy_dir = lazy_property((str, unicode))
    repo_url = lazy_property((str, unicode))
    branch = lazy_property((str, unicode))

    def __init__(self, deploy_dir, repo_url, branch="master",
                 **kw):
        super(Git, self).__init__(**kw)
        self.deploy_dir = deploy_dir
        self.repo_url = repo_url
        self.branch = branch

    def run(self):
        apt('git-core')
        # user = self.git_user_name
        # if user is None:
        #     user = os.environ['USER']
        # email = self.git_user_email
        # if email is None:
        #     email = os.environ.get('EMAIL', '{}@localhost'.format(user))
        # run('git config --global user.name "{}"'.format(user))
        # run('git config --global user.email "{}"'.format(email))
        if not exists(self.deploy_dir):
            run("git clone %s %s" %
                (self.repo_url, self.deploy_dir), pty=False)
            with cd(self.deploy_dir):
                run("git submodule init", pty=False)
        with cd(self.deploy_dir):
            run("git checkout %s" % self.branch)
            run("git remote set-url origin %s" % self.repo_url)
            run("git pull", pty=False)
            run("git submodule update", pty=False)
