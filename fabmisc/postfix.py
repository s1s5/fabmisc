# coding: utf-8
import StringIO

from fabric.operations import sudo, put
# from fabric.contrib.files import exists
from fabric.contrib.files import append

from . import service
from . import utility
from .utility import lazy_property


# キューの確認
# $ postqueue -p
# キューをすべて削除
# $ postsuper -d ALL deferred
# rootにメール送信
# echo test | mail root
# mail -s title hoge@foo.bar < desc
# /var/log/maillog
class Postfix(service.Service):
    relayhost = lazy_property((str, unicode))
    port = lazy_property(int)
    user = lazy_property((str, unicode))
    password = lazy_property((str, unicode))

    def __init__(self, relayhost, port, user, password, *args, **kw):
        super(Postfix, self).__init__(*args, **kw)
        self.relayhost = relayhost
        self.port = port
        self.user = user
        self.password = password

    def run(self):
        apt_packages = [
            'postfix',
            'sasl2-bin',
            'mailutils',
        ]

        for package in apt_packages:
            utility.apt(package)

        m = {
            'relayhost': '[{}]:{}'.format(self.relayhost, self.port),
            'smtp_use_tls': 'yes',
            'smtp_sasl_auth_enable': 'yes',
            'smtp_sasl_password_maps': 'hash:/etc/postfix/sasl_passwd',
            'smtp_sasl_tls_security_options': 'noanonymous',
            'smtp_sasl_mechanism_filter': 'plain',
            'smtp_tls_CApath': '/etc/pki/tls/certs/ca-bundle.crt',
            'smtp_sasl_security_options': 'noanonymous',
            'inet_interfaces': 'loopback-only',
            'smtpd_client_connection_rate_limit': '50',
            # http://www.unix-power.net/linux/centos_postfix.html
            'anvil_rate_time_unit': '900s',
            'smtpd_soft_error_limit': '10',
            'smtpd_hard_error_limit': '30',
            'smtpd_error_sleep_time': '60s',
            'smtpd_client_message_rate_limit': '100',
            'smtpd_client_recipient_rate_limit': '200',
        }
        sasl_passwd = '[{}]:{} {}:{}'.format(
            self.relayhost, self.port, self.user, self.password)

        main_cf = '/etc/postfix/main.cf'
        for key, value in m.items():
            utility.delete_lines_with_sed(
                main_cf, '{}'.format(key), use_sudo=True)
            append(main_cf, '{} = {}'.format(key, value), use_sudo=True)
        sasl_passwd_path = '/etc/postfix/sasl_passwd'
        put(remote_path=sasl_passwd_path,
            local_path=StringIO.StringIO(sasl_passwd),
            mode='0600', use_sudo=True)
        sudo('chown root:root {}'.format(sasl_passwd_path))
        sudo('postmap /etc/postfix/sasl_passwd')
        sudo('chown root:root /etc/postfix/sasl_passwd.db')
        sudo('chmod 600 /etc/postfix/sasl_passwd.db')
        self.restart()
        # if not exists('/etc/postfix/main.cf'):
        #     sudo('cp /usr/lib/postfix/main.cf /etc/postfix/main.cf')
