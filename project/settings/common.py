import os
from pathlib import Path

import environ
import redis

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, 'assets/dev.env'))

IS_DEBUG = int(env('DEBUG', default='1'))

STATIC_ROOT = env('APP_STATIC_VOLUME_LOCATION', default='/var/services/panc/static')
VAULT_PUBLIC_ROOT = env('APP_VAULT_PUBLIC', default='/var/services/panc/vault')
VAULT_PRIVATE_ROOT = env('APP_VAULT_PRIVATE', default='/var/services/panc/vault')

PRIVATE_KEY = open(VAULT_PRIVATE_ROOT + '/id_rsa').read()
PUBLIC_KEY = open(VAULT_PUBLIC_ROOT + '/id_rsa.pub').read()

ACCESS_TOKEN_EXP_SECONDS = 1 * 60 * 60
REFRESH_TOKEN_EXP_SECONDS = 1 * 60 * 60

REDIS_HOST = env('REDIS_HOST', default='localhost')
REDIS_PORT = env('REDIS_PORT', default=6379)
REDIS_INSTANCE = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)

SECRET_KEY = env('SECRET_KEY', default='DUMMY_KEY')

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379')

API_KEY = env('API_KEY', default='')
API_KEY_CRYPTOCOMPARE = env('API_KEY_CRYPTOCOMPARE', default='')
CONVERT_API_CURRENCY_V1 = 'https://min-api.cryptocompare.com/data/price'
CONVERT_API_CURRENCY_V2 = 'https://api.api-ninjas.com/v1/cryptoprice'

INFURA_API = 'https://mainnet.infura.io/v3/'
INFURA_API_KEY = env('INFURA_API_KEY', default='')

DEBUG = True if IS_DEBUG == 1 else False

ALLOWED_HOSTS = ['http://panc', 'localhost', '127.0.0.1', '0.0.0.0']

MEDIA_BASE_URL = '/media'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_beat',
    'user.apps.UserConfig',
    'wallet.apps.WalletConfig',
    'config.apps.ConfigConfig',
    'lottery.apps.LotteryConfig',
    # third_apps
    # 'django.contrib.staticfiles',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'project/templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default=''),
        'USER': env('DB_USER', default=''),
        'HOST': env('DB_HOST', default=''),
        'PORT': env('DB_PORT', default=''),
        'PASSWORD': env('DB_PASSWORD', default=''),
    },
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # OTHER SETTINGS
}
