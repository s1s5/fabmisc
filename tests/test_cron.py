# coding: utf-8
import os
import imp

from fabric.state import env

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


ROOT = os.path.dirname(os.path.dirname(__file__))

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))

line_map = {
    "some unique key never changed": "56 * * * * echo `date` >> /tmp/log",
}

fabmisc.Cron(line_map)
