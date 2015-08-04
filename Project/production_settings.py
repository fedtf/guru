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
