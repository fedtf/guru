from Project.settings import *
import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE_NAME'),
        'USER': 'root',
        'PASSWORD': os.environ.get('MYSQL_CHARSET_ENV_MYSQL_ROOT_PASSWORD'),
        'HOST': os.environ.get('MYSQL_CHARSET_PORT_3306_TCP_ADDR'),
        'PORT': '',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

DEBUG = True
