"""
Utilities package for the Flask application
"""

from .logger import setup_logging
from .validation import (
    ValidationError,
    validate_username,
    validate_email,
    validate_password,
    validate_rating,
    validate_search_query,
    validate_movie_title,
    validate_movie_year
)

__all__ = [
    'setup_logging',
    'ValidationError',
    'validate_username',
    'validate_email',
    'validate_password',
    'validate_rating',
    'validate_search_query',
    'validate_movie_title',
    'validate_movie_year'
]
