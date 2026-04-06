"""
NEXUS AI Tutor - Development Settings
"""

from .base import *

DEBUG = True

# Development-specific database (PostgreSQL from Docker)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nexus_db',
        'USER': 'nexus_user',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Additional development apps
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']

# CORS - Allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable password validation in development
AUTH_PASSWORD_VALIDATORS = []

# Use in-memory channel layer for development
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Celery - eager mode for synchronous execution in development
CELERY_TASK_ALWAYS_EAGER = True
