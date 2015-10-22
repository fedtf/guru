"""
Django settings for Project project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^(#$0ksk8_e)e1d4b&-pg-h&#gp3ann14$913=z-)xun6fzghn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'bootstrap3',
    'HuskyJamGuru',
    'rest_framework',
    'debug_toolbar',
    'kombu.transport.django',
    'djcelery',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'Project.middlewares.RequireLoginMiddleware'
)

ROOT_URLCONF = 'Project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['%s/templates' % BASE_DIR, ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'HuskyJamGuru.context_processors.version_description'
            ],
        },
    },
]

WSGI_APPLICATION = 'Project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'django://'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)

STATIC_URL = '/static/'

GITLAB_URL = 'http://185.22.60.142:8889'
GITLAB_APPLICATION_ID = '9bc472164fc76c3dda596f01205cba2bb63a47d4e57d59fd5dd01762b3042721'
GITLAB_APPLICATION_SECRET = 'b3d2981b461dded4655810765b2e898ced9fd55a277348a1502607960da5c1f2'

SITE_ID = 1

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

LOGIN_REQUIRED_URLS = (
    r'(.*)$',
)

LOGIN_REQUIRED_URLS_EXCEPTIONS = (
    r'/login(.*)$',
    r'/admin(.*)$',
    r'/gitlab_auth_callback(.*)$',
)
