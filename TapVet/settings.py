"""
Django settings for TapVet project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'umo(75h#$6!k36efxl5s36dt@8yqx2!acgq&3$w+(b-vp(oa6^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

INTERNAL_APPS = (
    'users',
    'countries',
    'pets',
    'posts',
    'comments',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'django_extensions',
    'rest_framework.authtoken',
    'corsheaders',
    'rest_framework_docs',
)

INSTALLED_APPS = DJANGO_APPS + INTERNAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TapVet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
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

WSGI_APPLICATION = 'TapVet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': os.environ.get('MYSQL_SERVER'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'users.User'

# CORS to allow any connection from any host (or any mobile phone)
CORS_ORIGIN_ALLOW_ALL = True

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')
MEDIA_URL = '/media/'
STATIC_ROOT = os.environ.get('STATIC_ROOT')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

"""
Email BACKEND, this is the default, im leaving here, because soon we need
to change it
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# This will be change to more stable enviroment
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = "[TapVet]"
DEFAULT_FROM_EMAIL = 'blanclink.test@gmail.com'

ADMINS = [
    ('Leopoldo Pimentel', 'leofaster@gmail.com'),
    ('Mayra Canas', 'mayrac@blanclabs.com'),
]

BREADER_MESSAGE_ADMIN_TITLE = "New Breeeder Pending"
VET_MESSAGE_ADMIN_TITLE = "New Vet Pending"
PAID_POST_AMOUNT = '100'

# Stripe data
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# APP LABELS
APP_LABEL = {
    2: 'Breeder',
    3: 'Veterinarian',
    4: 'Student',
    5: 'Technician'
}
