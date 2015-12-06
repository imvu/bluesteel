"""
Django testing settings for rowpow project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TESTING = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rgs$vr920yd6i&+p2f!-xx+=+pios(bqn&j&59b%&213%7q1co'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.logic.gitrepo',
    'app.logic.gitfeeder',
    'app.logic.bluesteelworker',
    'app.logic.bluesteel',
    'app.logic.benchmark',
    'app.logic.httpcommon',
    'app.logic.commandrepo',
    'app.logic.fontawesome',
    'app.logic.logger',
    'app.presenter',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages'
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

ROOT_URLCONF = 'bluesteel.urls'

WSGI_APPLICATION = 'bluesteel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'rowpowdb', # Or path to database file if using sqlite3.
#         # The following settings are not used with sqlite3:
#         'USER': 'rowpowuser',
#         'PASSWORD': 'sandcastle',
#         'HOST': 'localhost',    # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#         'PORT': '', # Set to empty string for default.
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = ''
STATIC_URL = '/static/'

# MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'tmp', 'test-media'))
# MEDIA_URL = '/tmp/test-media/'

TMP_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'tmp', 'test'))

EMAIL_USE_TLS = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 25
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend' # development backend
EMAIL_FILE_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'tmp', 'mail'))
DEFAULT_FROM_EMAIL = 'bluesteel@bluesteel.com'

