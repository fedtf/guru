#!/usr/bin/env bash

sudo /etc/init.d/nginx start;
sudo /etc/init.d/postfix start;

C_FORCE_ROOT=1 DJANGO_SETTINGS_MODULE='Project.production_settings' celery -A Project worker -l info --logfile celery-log.txt 2>&1 &

uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
