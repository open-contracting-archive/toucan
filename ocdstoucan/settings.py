"""
Django settings for ocdstoucan project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

production = os.getenv('DJANGO_ENV') == 'production'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', '0cxa(_o&i+f%3ua3c-%ox-lf_f_-8)%tc2x8zr4^iblbn9yp3d')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not production

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS.extend(os.getenv('ALLOWED_HOSTS').split(','))


# Application definition

INSTALLED_APPS = [
    'default.apps.DefaultConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ocdstoucan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                # 'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'default.context_processors.analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'ocdstoucan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.getenv('OCDS_TOUCAN_MEDIA_ROOT', 'media')

LOCALE_PATHS = [os.getenv('OCDS_TOUCAN_LOCALE_PATH', 'locale')]

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]

# https://docs.djangoproject.com/en/3.2/topics/logging/#django-security
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
       'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
       'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

FATHOM_ANALYTICS_DOMAIN = os.getenv('FATHOM_ANALYTICS_DOMAIN', 'cdn.usefathom.com')
FATHOM_ANALYTICS_ID = os.getenv('FATHOM_ANALYTICS_ID')
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID')

if 'SENTRY_DSN' in os.environ:
    # https://docs.sentry.io/platforms/python/logging/#ignoring-a-logger
    ignore_logger('django.security.DisallowedHost')
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration(), SqlalchemyIntegration()]
    )

OCDS_TOUCAN_MAXNUMFILES = os.getenv('OCDS_TOUCAN_MAXNUMFILES', 20)
OCDS_TOUCAN_MAXFILESIZE = os.getenv('OCDS_TOUCAN_MAXFILESIZE', 10000000)  # in bytes
OCDS_TOUCAN_GOOGLE_API_CREDENTIALS_FILE = os.getenv('OCDS_TOUCAN_CREDENTIALS_DRIVE', 'googleapi_credentials.json')

# https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
if production:
    # Run: env DJANGO_ENV=production SECURE_HSTS_SECONDS=1 ./manage.py check --deploy
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_REFERRER_POLICY = 'same-origin'

    # https://docs.djangoproject.com/en/3.2/ref/middleware/#http-strict-transport-security
    if 'SECURE_HSTS_SECONDS' in os.environ:
        SECURE_HSTS_SECONDS = os.getenv('SECURE_HSTS_SECONDS')
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
