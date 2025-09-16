# config/__init__.py
"""
Configuration package initialization
"""

# settings.py
DATA_DIR = "data"
TABLEAU_DIR = "tableau"
LOGS_DIR = "logs"

DATA_PROCESSING = {}
LOGGING_CONFIG = {}
FILE_NAMING = {}
TABLEAU_EXPORT = {}

from .api_keys import TWITTER_API_CONFIG, RATE_LIMITS
from .topics_config import TOPICS_CONFIG, COLLECTION_SETTINGS
from .settings import (
    DATA_DIR, TABLEAU_DIR, LOGS_DIR, 
    DATA_PROCESSING, LOGGING_CONFIG, 
    FILE_NAMING, TABLEAU_EXPORT
)

__all__ = [
    'TWITTER_API_CONFIG', 'RATE_LIMITS',
    'TOPICS_CONFIG', 'COLLECTION_SETTINGS',
    'DATA_DIR', 'TABLEAU_DIR', 'LOGS_DIR',
    'DATA_PROCESSING', 'LOGGING_CONFIG',
    'FILE_NAMING', 'TABLEAU_EXPORT'
]

