from pathlib import Path
import os

# ????????????????????????????????????????? consider adding Django's Logging Setting

# environment variables:
# SECRET_KEY
# RDS_DB_NAME
# RDS_USERNAME
# RDS_PASSWORD
# RDS_HOSTNAME
# RDS_PORT

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-%e%yh-0s_!&aq=-^@&pqld#bd1r4jmct5e0@jhg$ck@5wdj-5$'
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['v9m2jp3tgz.eu-west-1.awsapprunner.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'base.apps.BaseConfig',

    'rest_framework',
    'corsheaders'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'memebackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        BASE_DIR / 'templates' # BASE_DIR takes us back to the main directory of this project
        ],
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

WSGI_APPLICATION = 'memebackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres', # os.environ.get('RDS_DB_NAME'),
        'USER': 'postgres', # os.environ.get('RDS_USERNAME'),
        'PASSWORD': 'kkOOK61610216', # os.environ.get('RDS_PASSWORD'),
        'HOST': 'database-2.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com', # os.environ.get('RDS_HOSTNAME'),
        'PORT': 5432 # os.environ.get('RDS_PORT'),
    }
}

# Static and Media Files: ??????????????????????????????????????????????????????????????? do i need it? like s
# AWS_STORAGE_BUCKET_NAME = 'your_s3_bucket_name'
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_DEFAULT_ACL = 'public-read'
# STATIC_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# MEDIA_URL = 'https://%s/media/' % AWS_S3_CUSTOM_DOMAIN
# Ensure you've added boto3 and django-storages to your requirements.txt for S3 integration.

# Security Settings: ?????????????????????????????????????????????????????????????????????? is it correct
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'



# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/' 

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = ['https://main.d1j24jpipbs08c.amplifyapp.com/'] # specify allowed urls
CORS_ALLOWED_ORIGINS = [
    'https://main.d1j24jpipbs08c.amplifyapp.com/',
    'http://localhost:3000',  
    'http://127.0.0.1:3000', 
    'http://localhost:3001',  
    'http://127.0.0.1:3001',  
]

# CORS_ALLOWED_ORIGIN_REGEXES = [] # specify allowed urls with regex