#!/bin/bash
# -*- mode: shell-script -*-
PROGNAME=`basename $0`
BASEDIR=`dirname $0`
PIDFILE=$BASEDIR/$PROGNAME.pid

start() {
    if [ -e $PIDFILE ]; then
        stop
    fi
    echo "Starting server..."
    cd $BASEDIR
    gunicorn {{ gunicorn.app_name }} -c gunicorn_conf.py -p $PIDFILE -D --access-logfile /tmp/gunicorn_access.log --error-logfile /tmp/gunicorn_error.log --log-level debug
}

stop() {
    echo "Stopping server..."
    if [ -e $PIDFILE ]; then
        kill -TERM `cat $PIDFILE`
        rm -f $PIDFILE
    fi
}

usage() {
    echo "usage: $PROGNAME start|stop|restart"
}

if [ $# -lt 1 ];  then
    usage
    exit 255
fi

case $1 in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
esac
