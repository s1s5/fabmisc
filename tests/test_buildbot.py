# coding: utf-8
import os
import imp

from fabric.state import env

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


ROOT = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, ROOT)

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))

master = fabmisc.BuildbotMaster(
    path='~/buildbot/master', port=13612,
    buildbot_url='http://192.168.11.204/buildbot/')
fabmisc.BuildbotWorker(
    path='~/buildbot/worker', master=master,
    worker_name="example_worker", password="password")

nginx = fabmisc.Nginx()
site = fabmisc.NginxSite(nginx, 'buildbot',
                         locations=master.getLocations())
