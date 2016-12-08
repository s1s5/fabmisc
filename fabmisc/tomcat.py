# coding: utf-8
from fabric.operations import sudo
from fabric.contrib.files import append
from fabric.contrib.files import sed

from . import service
from . import utility
from .utility import lazy_property


class Tomcat(service.Service):
    version_string = lazy_property((str, unicode))
    java_home = lazy_property((str, unicode))
    port = lazy_property(int)

    def __init__(self, version_string, java_home, port=8080, *args, **kw):
        if 'name' not in kw:
            kw['name'] = 'tomcat{}'.format(version_string)
        super(Tomcat, self).__init__(*args, **kw)
        self.version_string = version_string
        self.java_home = java_home
        self.port = port

    def run(self):
        utility.apt('tomcat{}'.format(self.version_string))
        conf_file = '/etc/default/tomcat{}'.format(self.version_string)
        utility.delete_lines_with_sed(
            conf_file, '{}'.format('JAVA_HOME='), use_sudo=True)
        append(conf_file, '{}={}'.format(
            'JAVA_HOME', self.java_home), use_sudo=True)
        sudo('chown -R tomcat{version}:tomcat{version} '
             '/usr/share/tomcat{version}'.format(version=self.version_string))
        sed('/etc/tomcat{version}/server.xml'.format(
            version=self.version_string),
            '<Connector port="[0-9]*" ',
            '<Connector port="{port}" '.format(version=self.version_string,
                                               port=self.port), use_sudo=True)
        self.restart()
