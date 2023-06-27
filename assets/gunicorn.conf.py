wsgi_app = 'project.wsgi:application'
loglevel = 'info'
workers = 2
bind = '0.0.0.0:8000'

accesslog = '-'
errorlog = '-'

capture_output = True
