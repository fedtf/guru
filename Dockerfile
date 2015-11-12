FROM ubuntu:14.04

RUN apt-get update && \
	apt-get install -y libxml2-dev libxslt1-dev python3-dev python3-setuptools python3.4 build-essential python3-pip nginx libpq-dev mysql-client libmysqlclient-dev

COPY requirements-develop.txt /opt/app/requirements-develop.txt
COPY requirements.txt /opt/app/requirements.txt
RUN pip3 install -r /opt/app/requirements.txt

COPY . /opt/app

VOLUME ["/opt/app/media"]

WORKDIR /opt/app

RUN openssl rand -base64 32 > secret_key.txt;

RUN python3 /opt/app/manage.py collectstatic --settings=Project.production_settings --noinput

RUN rm /etc/nginx/sites-enabled/default;
RUN ln -s /opt/app/Deploy/nginx.conf /etc/nginx/sites-enabled/;

EXPOSE 80
