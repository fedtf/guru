#!/usr/bin/env bash

sudo /etc/init.d/nginx start;
uwsgi --socket /tmp/uwsgi.sock --module Project.wsgi --chmod-socket=777 --processes=10
