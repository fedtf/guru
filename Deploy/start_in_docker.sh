#!/usr/bin/env bash

sudo /etc/init.d/nginx start;

DJANGO_SETTINGS_MODULE='Project.production_settings' celery -A Project worker -l info 2>&1 &

uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
