# -*- coding: utf-8; mode: python -*-
import multiprocessing

# bind = 'unix:/tmp/gunicorn_memo.sock'
bind = "127.0.0.1:{{ gunicorn.proxy_port }}"

backlog = 2048
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 0
timeout = 30
keepalive = 2

spew = False

preload_app = True
daemon = True
debug = False

# /var/run/gunicornを作成しておく
# pidfile = '/tmp/gunicorn.pid'
# user = '{{ ansible_user_id }}'
# group = '{{ ansible_user_id }}'
umask = 0002
# tmp_upload_dir = None

# /var/log/gunicornを作成しておく
logfile = 'gunicorn.log'
loglevel = 'info'
logconfig = None

proc_name = '{{ gunicorn.app_name }}'
