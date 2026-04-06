"""
NEXUS AI Tutor - Settings Package
"""

import os
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *

