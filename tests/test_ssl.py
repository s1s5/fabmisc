# coding: utf-8
import os
import imp

from fabric.state import env
from fabric.api import execute
from fabric.decorators import task

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


ROOT = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, ROOT)

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))

_l = fabmisc.lazy

nginx = fabmisc.Nginx()
ssl = fabmisc.Ssl(
    certificates=_l(env, 'certificates', None),
    private_key=_l(env, 'private_key', None))
location = fabmisc.NginxAlias(path='/var/www/html')
fabmisc.NginxSite(nginx, 'static_files',
                  locations=(location, ), ssl=ssl)


def putSampleHtml():
    from fabric.contrib.files import put
    import StringIO
    put(local_path=StringIO.StringIO("hello world"),
        remote_path='/var/www/html/hello.html', use_sudo=True)


@task
def deploy_self_certificated():
    execute('tasks.run')
    putSampleHtml()
