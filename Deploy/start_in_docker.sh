#!/usr/bin/env bash

sudo /etc/init.d/nginx start;

C_FORCE_ROOT=1 DJANGO_SETTINGS_MODULE='Project.production_settings' python3 ./manage.py celery worker -l debug --logfile celery-log.txt 2>&1 &

uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
