"""
Configuration file for Arcaload Flask application
Handles all environment variables and app configuration
"""

import os
from datetime import timedelta
from pathlib import Path

# Get the base directory
basedir = Path(__file__).parent.absolute()

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{basedir}/instance/arcaload.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_PERMANENT = True
    
    # Security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration for Render/deployment"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # DATABASE_URL should be set as environment variable on Render


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Config mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Get active config
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
active_config = config_by_name.get(FLASK_ENV, DevelopmentConfig)