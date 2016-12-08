# coding: utf-8
import uuid

from fabric.contrib.files import exists as fab_exists
from fabric.contrib.files import put
from fabric.contrib.console import confirm
from fabric.operations import run, sudo
from fabric.operations import prompt
from fabric.context_managers import cd

from .managed_task import ManagedTask
from .utility import lazy_property


class Ssl(ManagedTask):
    certificates = lazy_property()
    private_key = lazy_property((str, unicode))
    private_key_password = lazy_property((str, unicode))
    remote_path = lazy_property((str, unicode))
    regenerate = lazy_property(bool)
    use_sudo = lazy_property(bool)

    def __init__(self, certificates=None, private_key=None,
                 private_key_password=None,
                 remote_path='/etc/nginx/ssl/site',
                 regenerate=False, use_sudo=True, *args, **kw):
        super(Ssl, self).__init__(*args, **kw)
        self.certificates = certificates
        self.private_key = private_key
        self.private_key_password = private_key_password
        self.remote_path = remote_path
        self.regenerate = regenerate
        self.use_sudo = use_sudo

    def run(self):
        if fab_exists(self.cert_path):
            reg = self.regenerate
            if self.regenerate is None:
                reg = confirm('regenerate ssl files?', default=False)
            if not reg:
                return
        tmp_dir = '/tmp/{}'.format(uuid.uuid4().hex)
        run('mkdir {}'.format(tmp_dir))
        with cd(tmp_dir):
            if self.certificates is None:
                onetime_pass = uuid.uuid4().hex
                run('openssl genrsa -des3 -out server.key '
                    '-passout pass:{} 2048'.format(onetime_pass))
                run('openssl req -passin pass:{} -new -key server.key '
                    '-out server.csr'.format(onetime_pass))
                run('cp server.key server.key.org')
                run('openssl rsa -passin pass:{} -in server.key.org '
                    '-out server.key'.format(onetime_pass))
                run('openssl x509 -req -days 365 -in server.csr '
                    '-signkey server.key -out server.crt')
            else:
                for i in enumerate(self.certificates):
                    put(i, 'crt')
                    run('cat crt >> server.crt')
                put(self.private_key, 'server.org.key')
                p = self.private_key_password
                if self.private_key_password is None:
                    p = prompt('enter private key password')
                if p:
                    run('openssl rsa -passin pass:{} -in '
                        'server.org.key -out server.key'.format(p))
                else:
                    run('cp server.org.key server.key')
            _run = run
            if self.use_sudo:
                _run = sudo
            _run('cp server.crt {}'.format(self.cert_path))
            _run('cp server.key {}'.format(self.key_path))
        run('rm -rf {}'.format(tmp_dir))

    def getCertPath(self):
        return '{}.crt'.format(self.remote_path)

    def getKeyPath(self):
        return '{}.key'.format(self.remote_path)
    cert_path = property(getCertPath)
    key_path = property(getKeyPath)
