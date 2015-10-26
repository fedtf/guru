#!/usr/bin/env bash

python manage.py celery worker --logfile celery-log.txt --settings Project.production_settings &
sudo /etc/init.d/nginx start;
uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
