"""
Configuration settings for Flask Movie Recommendation App
Supports development, testing, and production environments
"""

import os
from datetime import timedelta


class Config:
    """Base configuration shared across all environments"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTForms CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Pagination
    ITEMS_PER_PAGE = 12
    
    # TMDB API Configuration
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
    
    # Admin settings
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///movie_recommendation_dev.db'
    SESSION_COOKIE_SECURE = False  # Allow http in development


class TestingConfig(Config):
    """Testing environment configuration"""
    
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///movie_recommendation.db'


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration object based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    # Enforce SECRET_KEY for production
    if env == 'production' and not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    return config_by_name.get(env, DevelopmentConfig)
