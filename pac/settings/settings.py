"""
Django settings for pac project.

Generated by 'django-admin startproject' using Django 2.1.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import pdb
import logging
logging.getLogger().setLevel(logging.INFO)

import django
from decouple import config
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient

from pac.rrf.utils import str2bool

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# from pac.blobs.utils import BlobFileUploadHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*+%a(n%k&u361f=o@h6q&bnbn*4)!5l^9v(@lxk1f_*m-4u!w7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEVELOP = True

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

ALLOWED_HOSTS = ['*']

HOSTED_ENVIRONMENT = config('HOSTED_ENVIRONMENT', False)

# AZURE KEYVAULT
AZURE_TENANT_ID = config('AZURE_TENANT_ID')
AZURE_CLIENT_ID = config('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = config('AZURE_CLIENT_SECRET')
credential = ClientSecretCredential(tenant_id=AZURE_TENANT_ID,
                                    client_id=AZURE_CLIENT_ID, client_secret=AZURE_CLIENT_SECRET)
AZURE_VAULT_URL = config('AZURE_VAULT_URL')
secret_client = SecretClient(vault_url=AZURE_VAULT_URL, credential=credential)

# Rateware API Credentials
RATEWARE_USERNAME = secret_client.get_secret("RATEWARE-USERNAME").value
RATEWARE_PASSWORD = secret_client.get_secret("RATEWARE-PASSWORD").value
RATEWARE_LICENSE_KEY = secret_client.get_secret("RATEWARE-LICENSE-KEY").value

# Service Bus Config
SERVICE_BUS_CONNECTION_STRING = secret_client.get_secret("SERVICE-BUS-CONNECTION-STRING").value
SERVICE_BUS_QUEUE_PRICING_ENGINE = secret_client.get_secret("SERVICE-BUS-QUEUE-PRICING-ENGINE").value

# SMTP2GO Email Provider
SMTP2GO_BASE_URL = secret_client.get_secret("SMTP2GO-BASE-URL").value
SMTP2GO_API_KEY = secret_client.get_secret("SMTP2GO-API-KEY").value
SMTP2GO_FROM_EMAIL = secret_client.get_secret("SMTP2GO-FROM-EMAIL").value

# Database Configuration
DB_NAME = secret_client.get_secret("DB-NAME").value
DB_HOST = secret_client.get_secret("DB-HOST").value
DB_PORT = secret_client.get_secret("DB-PORT").value
DB_USER = secret_client.get_secret("DB-USER").value
DB_PASSWORD = secret_client.get_secret("DB-PASSWORD").value

# Connection to Pricing ENGINE
PRICING_ENGINE_URL = secret_client.get_secret("PricingEngineURL").value

# Temporary hardcoded values
LINE_HAUL_CAPACITY_FACTOR = float(secret_client.get_secret("LINE-HAUL-CAPACITY-FACTOR").value)
WEIGHT_BREAK_MAX_UPPER_BOUND_INCREMENT = int(secret_client.get_secret("WEIGHT-BREAK-MAX-UPPER-BOUND-INCREMENT").value)
SPEED_SHEET_PROFIT_MARGIN_MULTIPLIER = float(secret_client.get_secret("SPEED-SHEET-PROFIT-MARGIN-MULTIPLIER").value)

# Margin Variables
PROFIT_FACTOR = float(secret_client.get_secret("PROFIT-FACTOR").value)
INTERLINE_SERVICE_PICKUP_MARGIN = float(secret_client.get_secret("INTERLINE-SERVICE-PICKUP-MARGIN").value)
INTERLINE_SERVICE_DELIVERY_MARGIN = float(secret_client.get_secret("INTERLINE-SERVICE-DELIVERY-MARGIN").value)
INTERLINE_PICKUP_MINIMUM = int(secret_client.get_secret("INTERLINE-PICKUP-MINIMUM").value)
INTERLINE_DELIVERY_MINIMUM = int(secret_client.get_secret("INTERLINE-DELIVERY-MINIMUM").value)
INTERLINE_AT_PICKUP = int(secret_client.get_secret("INTERLINE-AT-PICKUP").value)
INTERLINE_AT_DELIVERY = int(secret_client.get_secret("INTERLINE-AT-DELIVERY").value)

# Other Variables
ENGINE_RATE = int(secret_client.get_secret("ENGINE-RATE").value)
GATEWAY_TERMINAL_TEMP = secret_client.get_secret("GATEWAY-TERMINAL-TEMP").value
REVENUE = int(secret_client.get_secret("REVENUE").value)
BULK_SAVE_BATCH_SIZE = int(secret_client.get_secret("BULK-SAVE-BATCH-SIZE").value)

# Service level base point restrictions
BASE_RESTRICTION_SERVICE_LEVEL_CODES = ['CS', 'DL', 'FB', 'SO', 'TL', 'CB', 'RS']
for sl in BASE_RESTRICTION_SERVICE_LEVEL_CODES:
    globals()['SERVICE_LEVEL_BASE_POINT_RESTRICTION_FOR_' + sl] = secret_client.get_secret(
        'SERVICE-LEVEL-BASE-POINT-RESTRICTION-FOR-' + sl).value

RATEWARE_HEADER = {"AuthenticationToken": {"username": RATEWARE_USERNAME,
                                           "password": RATEWARE_PASSWORD, "licenseKey": RATEWARE_LICENSE_KEY}}

RUNSERVER_PLUS_PRINT_SQL_TRUNCATE = None
SHELL_PLUS_PRINT_SQL_TRUNCATE = None

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'rest_framework_api_key',
    'rest_framework_swagger',
    'corsheaders',
    'django_filters',
    'core',
    'pac',
    'pac.pre_costing',
    'pac.rrf',
    'azure'

]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'pac.urls'

CORS_ORIGIN_ALLOW_ALL = True  # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
CORS_ORIGIN_WHITELIST = [  # TODO keep this for future configuration
    'http://localhost:30662',
]  # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://localhost:3030',
]

JINJA_TEMPLATE_DIR=os.path.join(BASE_DIR,'rrf', 'templates', 'jinja')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [JINJA_TEMPLATE_DIR],
    },
]

WSGI_APPLICATION = 'pac.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
}

DATABASE_CONNECTION_POOLING = False

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

# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/f

STATIC_URL = '/static/'

CPU_COUNT = os.cpu_count() or 1

AUTH_ENABLED = config('AUTH_ENABLED', default=True)
if AUTH_ENABLED and str(AUTH_ENABLED).lower() == 'true':
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'core.authentication.AzureActiveDirectoryAuthentication',
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ],

        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
            # 'core.permissions.IsAuthorized',
            #'rest_framework_api_key.permissions.HasAPIKey',
        ],
        'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
    }


AUTHENTICATION_BACKENDS = [
    'core.authentication.BackendAuthentication',
    'django.contrib.auth.backends.ModelBackend'
]

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    # For using django admin panel for authentication
    'SECURITY_DEFINITIONS': {
        'AzureActiveDirectoryAuthentication': {
            'type': 'apiKey',
            'name': 'X-CSRFToken',
            'in': 'header',
        }
    }
}

AUTH_USER_MODEL = 'core.User'

# List of upload handler classes to be applied in order.
# FILE_UPLOAD_HANDLERS = [
#     'pac.blobs.utils.BlobFileUploadHandler'
# ]

FILE_UPLOAD_HANDLERS = [

    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]
# "django.core.files.uploadhandler.MemoryFileUploadHandler",
DEFAULT_FILE_STORAGE = 'pac.blobs.azure_storage.AzureStorage'
STATIC_LOCATION = '8334f9db-e4c1-43d7-8f4c-87f63abdb1f5'
AZURE_SSL = True
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER")
AZURE_CONTAINER_URL = os.getenv("AZURE_CONTAINER_URL")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AP_SCHEDULER_ENABLE = str2bool(os.getenv("AP_SCHEDULER_ENABLE", default=False))
AP_SCHEDULER_INTERVAL_VALIDATE = 10
AP_SCHEDULER_INTERVAL_STATUS_WATCHER = 30