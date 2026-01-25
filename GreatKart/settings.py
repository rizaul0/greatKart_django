"""
Django settings for GreatKart project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------
# BASE & ENV
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# -------------------------------
# SECURITY
# -------------------------------
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = False   # set False on Render later

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
]

# -------------------------------
# APPLICATIONS
# -------------------------------
INSTALLED_APPS = [
    # 🔥 MUST BE FIRST
    'cloudinary',
    'cloudinary_storage',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'views',
    'category',
    'accounts',
    'store',
    'cart',
    'orders',
    'owneradmin',
    'coupons',
]

SITE_ID = 1

# -------------------------------
# STORAGE (IMPORTANT)
# -------------------------------
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------
# URLS & TEMPLATES
# -------------------------------
ROOT_URLCONF = 'GreatKart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'GreatKart' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'views.context_processors.get_categories',
                'views.context_processors.cart_count',
                'views.context_processors.get_brands',
            ],
        },
    },
]

WSGI_APPLICATION = 'GreatKart.wsgi.application'

AUTH_USER_MODEL = 'accounts.Account'

# -------------------------------
# DATABASE (PostgreSQL)
# -------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# -------------------------------
# PASSWORD VALIDATION
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------
# INTERNATIONALIZATION
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -------------------------------
# STATIC FILES
# -------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'GreatKart' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# -------------------------------
# EMAIL
# -------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"GreatKart <{EMAIL_HOST_USER}>"

# -------------------------------
# PAYU
# -------------------------------
PAYU_MERCHANT_KEY = os.getenv('PAYU_MERCHANT_KEY')
PAYU_MERCHANT_SALT = os.getenv('PAYU_MERCHANT_SALT')
PAYU_URL = os.getenv('PAYMENT_URL')
PAYU_ENV = os.getenv('PAYU_ENV')
