from Project.settings import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    '*'
]

with open('/opt/app/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/opt/app/django.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

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

GITLAB_APPLICATION_ID = '233cfd2c66b28969706973d2278fae23c94645753e36a1d59dca3ff1fb1de92a'
GITLAB_APPLICATION_SECRET = '1dc472cab31ef44d89ad81e8f1d67155240fff6eafd2a2ef95af8d5f25261b9f'
GITLAB_URL = 'http://185.22.60.142:8889'
