# coding: utf-8
import random
import subprocess

import docker

from fabric.state import env
# import fabric.contrib.files as files
# from fabric.operations import sudo
# from fabric.api import warn_only

# from . import service
# from .utility import apt_update, apt
from .ssh_rev_tunnel import ReverseTunnel


# class Docker(service.Service):
#     def run(self):
#         apt_update()
#         apt('apt-transport-https ca-certificates')
#         sudo('apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 '
#              '--recv-keys 58118E89F3A912897C070ADBF76221572C52609D')

#         # 14.04 https://apt.dockerproject.org/repo ubuntu-trusty main
#         # 16.04 https://apt.dockerproject.org/repo ubuntu-xenial main
#         files.append('/etc/apt/sources.list.d/docker.list',
#                      'deb https://apt.dockerproject.org/repo '
#                      'ubuntu-xenial main',
#                      use_sudo=True)

#         apt_update()
#         apt('linux-image-extra-$(uname -r) linux-image-extra-virtual')
#         apt_update()
#         apt('docker-engine')
#         self.restart()
#         with warn_only():
#             sudo('groupadd docker')
#         sudo('usermod -aG docker {}'.format(env['user']))


class DockerRegistry(object):
    def __init__(self, project_name, port=55124):
        self.plist = []
        self.project_name = project_name
        self.port = port

    def __enter__(self):
        if self.port <= 0:
            port = random.randint(32768, 65535)
        else:
            port = self.port
        cmd = ['docker', 'run', '-p', '{}:5000'.format(port), '-v',
               '{}_docker_registry:/var/lib/registry'.format(self.project_name),
               'registry:2.3.0']
        self.plist.append(subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        # self.plist.append(subprocess.Popen(cmd))
        # import time
        # time.sleep(10)
        return port

    def __exit__(self, type_, value, traceback):
        from signal import SIGINT
        for p in self.plist:
            p.send_signal(SIGINT)
            p.wait()
        self.plist = []


class DockerTunnel(object):

    def __init__(self, sudo_password, port=-1):
        self.sudo_password = sudo_password
        self.plist = []
        self.port = port

    def __enter__(self):
        if self.plist:
            raise Exception()
        self.plist = []
        if self.port <= 0:
            port = random.randint(32768, 65535)
        else:
            port = self.port

        cmd0 = ["socat", "TCP-LISTEN:{},reuseaddr,fork".format(port),
                "EXEC:'ssh {} socat STDIO TCP:127.0.0.1:{}'".format(env['host_string'], port)]
        cmd1 = (["ssh", "-kTax", env['host_string'], "sudo", ] +
                (["-S", "<<<", self.sudo_password, ] if self.sudo_password else []) +
                ["socat", "TCP-LISTEN:{},fork,reuseaddr".format(port), "UNIX-CONNECT\:/var/run/docker.sock"])
        self.plist.append(subprocess.Popen(cmd0, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        self.plist.append(subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        # import time
        # time.sleep(10)
        return port

    def __exit__(self, type_, value, traceback):
        from signal import SIGINT
        for p in self.plist:
            p.send_signal(SIGINT)
            p.wait()
        self.plist = []


class DockerProxy(object):
    def __init__(self, project_name, registry_port=55124, sudo_password=''):
        self.project_name = project_name
        self.registry_port = registry_port
        self.__local_client = None
        self.__remote_client = None
        self.reg = None

    def __enter__(self):
        if self.reg is not None:
            raise Exception()
        self.reg = DockerRegistry(self.project_name, self.registry_port)
        self.dt = DockerTunnel()
        self.st = ReverseTunnel(self.registry_port, self.registry_port)
        self.reg.__enter__()
        self.dt_port = self.dt.__enter__()
        self.st.__enter__()

        # waiting for service
        import time
        time.sleep(10)
        return self

    def __exit__(self, type_, value, traceback):
        self.reg.__exit__(type_, value, traceback)
        self.dt.__exit__(type_, value, traceback)
        self.st.__exit__(type_, value, traceback)
        self.reg = None
        self.dt = None
        self.st = None
        self.__local_client = None
        self.__remote_client = None

    def getRegistry(self):
        return 'tcp://127.0.0.1:{}'.format(self.registry_port)

    def getSock(self):
        return 'tcp://127.0.0.1:{}'.format(self.dt_port)

    def getLocalClient(self):
        if self.__local_client is None:
            self.__local_client = docker.from_env()
        return self.__local_client

    def getRemoteClient(self):
        if self.__remote_client is None:
            self.__remote_client = docker.from_env(environment=dict(DOCKER_HOST=self.sock))
        return self.__remote_client

    registry = property(getRegistry)
    sock = property(getSock)
    local_client = property(getLocalClient)
    remote_client = property(getRemoteClient)
