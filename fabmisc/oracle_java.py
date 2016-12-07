# coding: utf-8
from fabric.operations import run
from fabric.operations import sudo
from fabric.context_managers import hide

from . import utility
from .managed_task import ManagedTask


class OracleJava(ManagedTask):
    def getJavaHome(self):
        return '/usr/lib/jvm/java-8-oracle'

    def run(self):
        utility.apt('python-software-properties debconf-utils')
        with hide('stdout'):
            sudo('add-apt-repository -y ppa:webupd8team/java')
            sudo('apt-get update')
        run('echo "oracle-java8-installer shared/accepted-oracle-license-v1-1'
            ' select true" | sudo debconf-set-selections')
        utility.apt('oracle-java8-installer')
