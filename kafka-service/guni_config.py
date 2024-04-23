pidfile = 'kafka-dispatcher.pid'
worker_tmp_dir = '/dev/shm'

# Websocket gevent worker
# Normal gevent worker
worker_class = 'gevent'
workers = 1
worker_connections = 1000
timeout = 60
keepalive = 5

proc_name = 'kafka-dispatcher'
bind = '0.0.0.0:9002'
# maximum number of pending connections that can be queued by the operating system
backlog = 2048
accesslog = 'access.log'
errorlog = 'error.log'
