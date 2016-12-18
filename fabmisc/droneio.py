# coding: utf-8
from fabric.contrib.files import exists
from fabric.context_managers import cd
from fabric.operations import run as fab_run
from fabric.operations import sudo

from . import service


class Droneio(service.Service):
    def run(self):
        download_dir = '~/Downloads'
        fab_run('mkdir -p {}'.format(download_dir))

        with cd(download_dir):
            if not exists('{}/drone.deb'.format(download_dir)):
                fab_run('wget http://downloads.drone.io/master/drone.deb')
            not_installed = False
            try:
                sudo('dpkg-query -l drone')
            except:
                not_installed = True

            if not_installed:
                sudo('dpkg -i drone.deb')
            sudo('sudo docker run '
                 '--volume /var/lib/drone:/var/lib/drone '
                 '--volume /var/run/docker.sock:/var/run/docker.sock '
                 '--env-file /etc/drone/drone.toml '
                 '--restart=always '
                 '--publish=8888:8000 '
                 '--detach=true '
                 '--name=drone '
                 'drone/drone:0.4')
