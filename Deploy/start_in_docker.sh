#!/usr/bin/env bash

DJANGO_SETTINGS_MODULE='Project.production_settings' python manage.py celery worker --logfile django.log -l info 2>&1 &
sudo /etc/init.d/nginx start;
uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
