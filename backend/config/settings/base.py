"""
NEXUS AI Tutor - Django Settings (Base)
Ultra Pro Max Edition
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'nexus-dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    
    # Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    'django_celery_beat',
    'django_celery_results',
    
    # NEXUS Apps
    'apps.core',
    'apps.users',
    'apps.students',
    'apps.digital_twin',
    'apps.courses',
    'apps.assessments',
    'apps.analytics',
    'apps.content',
    'apps.reports',
    'apps.blockchain',
    'apps.federation',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database - PostgreSQL with pgvector
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'nexus_db'),
        'USER': os.environ.get('POSTGRES_USER', 'nexus_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}

# Neo4j Graph Database (Knowledge Graph)
NEO4J_CONFIG = {
    'URI': os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
    'USER': os.environ.get('NEO4J_USER', 'neo4j'),
    'PASSWORD': os.environ.get('NEO4J_PASSWORD', 'password'),
}

# Redis
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Channels (WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# Vector Database Settings
VECTOR_DB = {
    'BACKEND': 'pgvector',  # or 'pinecone'
    'DIMENSIONS': 1536,
    'PINECONE_API_KEY': os.environ.get('PINECONE_API_KEY', ''),
    'PINECONE_ENVIRONMENT': os.environ.get('PINECONE_ENV', ''),
}

# ML Model Settings
ML_CONFIG = {
    'MODEL_DIR': BASE_DIR.parent / 'ml_models',
    'DEVICE': os.environ.get('ML_DEVICE', 'cuda' if os.environ.get('CUDA_AVAILABLE') else 'cpu'),
    'BATCH_SIZE': int(os.environ.get('ML_BATCH_SIZE', 32)),
    'MAX_SEQ_LENGTH': 512,
    'EMBEDDING_MODEL': 'sentence-transformers/all-MiniLM-L6-v2',
    'LLM_MODEL': os.environ.get('LLM_MODEL', 'meta-llama/Llama-3.1-8B-Instruct'),
}

# Gemini AI Config
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Neuromorphic Computing Settings
NEUROMORPHIC_CONFIG = {
    'SPIKE_THRESHOLD': 1.0,
    'MEMBRANE_LEAK': 0.9,
    'TIME_STEPS': 100,
    'HEBBIAN_LR': 0.01,
}

# Emotion AI Settings  
EMOTION_AI_CONFIG = {
    'FACE_MODEL': 'fer2013',
    'VOICE_MODEL': 'wav2vec2-emotion',
    'COGNITIVE_LOAD_THRESHOLD': 0.7,
}

# Reinforcement Learning Settings
RL_CONFIG = {
    'ALGORITHM': 'PPO',
    'LEARNING_RATE': 3e-4,
    'GAMMA': 0.99,
    'GAE_LAMBDA': 0.95,
    'CLIP_RANGE': 0.2,
    'NUM_ENVS': 8,
}

# Digital Twin Settings
DIGITAL_TWIN_CONFIG = {
    'KNOWLEDGE_GRAPH_DIMS': 256,
    'MEMORY_CAPACITY': 10000,
    'FORGETTING_BASE_RATE': 0.1,
    'TRANSFER_LEARNING_THRESHOLD': 0.3,
}

# Blockchain Settings
BLOCKCHAIN_CONFIG = {
    'NETWORK': os.environ.get('BLOCKCHAIN_NETWORK', 'polygon'),
    'CONTRACT_ADDRESS': os.environ.get('CREDENTIAL_CONTRACT', ''),
    'IPFS_GATEWAY': os.environ.get('IPFS_GATEWAY', 'https://ipfs.io'),
}

# Federated Learning Settings
FEDERATED_CONFIG = {
    'ROUNDS': 10,
    'MIN_CLIENTS': 5,
    'AGGREGATION': 'fedavg',
    'DIFFERENTIAL_PRIVACY_EPSILON': 1.0,
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'nexus': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
