# -*- python -*-
import os

from buildbot_worker.bot import Worker
from twisted.application import service

basedir = os.path.abspath(os.path.dirname(__file__))
rotateLength = 10000000
maxRotatedFiles = 10

# if this is a relocatable tac file, get the directory containing the TAC
if basedir == '.':
    import os.path
    basedir = os.path.abspath(os.path.dirname(__file__))

# note: this line is matched against to check that this is a worker
# directory; do not edit it.
application = service.Application('buildbot-worker')

try:
    from twisted.python.logfile import LogFile
    from twisted.python.log import ILogObserver, FileLogObserver
    logfile = LogFile.fromFullPath(
        os.path.join(basedir, "twistd.log"), rotateLength=rotateLength,
        maxRotatedFiles=maxRotatedFiles)
    application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
except ImportError:
    # probably not yet twisted 8.2.0 and beyond, can't set log yet
    pass

buildmaster_host = '{{ worker.master.url_for_worker }}'
port = {{ worker.master.port_for_worker }}
workername = '{{ worker.worker_name }}'
passwd = '{{ worker.password }}'
keepalive = 600
umask = None
maxdelay = 300
numcpus = None
allow_shutdown = None

s = Worker(buildmaster_host, port, workername, passwd, basedir,
           keepalive, umask=umask, maxdelay=maxdelay,
           numcpus=numcpus, allow_shutdown=allow_shutdown)
s.setServiceParent(application)
