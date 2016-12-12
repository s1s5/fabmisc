# coding: utf-8
import os
import imp

from fabric.state import env

env.forward_agent = True
env.use_ssh_config = True


ROOT = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, ROOT)

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))

public_git = fabmisc.Git(
    "/tmp/sample",
    "ssh://dev.sizebook.jp:32125/sawai/sample.git",
    name="pub_git")

private_git = fabmisc.Git(
    "/tmp/sample2",
    "ssh://dev.sizebook.jp:32125/sawai/sample2.git",
    name="priv_git")
