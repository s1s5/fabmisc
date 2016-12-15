# coding: utf-8
from buildbot.plugins import *

c['change_source'].append(changes.GitPoller(
    'git://github.com/buildbot/pyflakes.git',
    workdir='gitpoller-workdir', branch='master',
    pollinterval=300))
c['schedulers'].append(schedulers.SingleBranchScheduler(
    name="all",
    change_filter=util.ChangeFilter(branch='master'),
    treeStableTimer=None,
    builderNames=["runtests"]))
c['schedulers'].append(schedulers.ForceScheduler(
    name="force",
    builderNames=["runtests"]))
factory = util.BuildFactory()
factory.addStep(steps.Git(
    repourl='git://github.com/buildbot/pyflakes.git', mode='incremental'))
factory.addStep(steps.ShellCommand(command=["trial", "pyflakes"]))
c['builders'].append(
    util.BuilderConfig(name="runtests",
                       workernames=[
                           {% for worker in master.workers %}"{{ worker.worker_name }}",
                           {% endfor %}
                       ],
                       factory=factory))
