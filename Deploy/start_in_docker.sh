#!/usr/bin/env bash

DJANGO_SETTINGS_MODULE='Project.production_settings' celery -A Project worker --logfile django.log -l info 2>&1 &
sudo /etc/init.d/nginx start;
uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
