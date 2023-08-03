pidfile = 'data-wizard.pid'
worker_tmp_dir = '/dev/shm'
# worker_class = 'gthread'
# 'threads' is not used with 'gevent' worker class
# threads = 2
worker_class = 'gevent'
workers = 1
worker_connections = 1000
timeout = 30
keepalive = 2

proc_name = 'data-wizard'
bind = '0.0.0.0:9001'
backlog = 2048
accesslog = '-'
errorlog = '-'