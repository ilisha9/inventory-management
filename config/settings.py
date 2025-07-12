"""
Configuration settings for ADIENT Inventory Management System
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///adient_inventory.db'
    DATABASE_POOL_SIZE = int(os.environ.get('DATABASE_POOL_SIZE', 10))
    DATABASE_MAX_OVERFLOW = int(os.environ.get('DATABASE_MAX_OVERFLOW', 20))
    
    # Inventory management settings
    INVENTORY_CHECK_INTERVAL = int(os.environ.get('INVENTORY_CHECK_INTERVAL', 300))  # 5 minutes
    LOW_STOCK_THRESHOLD_PERCENTAGE = float(os.environ.get('LOW_STOCK_THRESHOLD', 0.2))  # 20%
    REORDER_POINT_SAFETY_FACTOR = float(os.environ.get('REORDER_SAFETY_FACTOR', 1.5))
    
    # Production monitoring settings
    PRODUCTION_MONITORING_INTERVAL = int(os.environ.get('PROD_MONITORING_INTERVAL', 60))  # 1 minute
    PRODUCTION_ALERT_THRESHOLD = float(os.environ.get('PROD_ALERT_THRESHOLD', 0.8))  # 80% efficiency
    
    # Optimization settings
    OPTIMIZATION_INTERVAL = int(os.environ.get('OPTIMIZATION_INTERVAL', 3600))  # 1 hour
    MAX_OPTIMIZATION_TIME = int(os.environ.get('MAX_OPTIMIZATION_TIME', 300))  # 5 minutes
    
    # Alert settings
    ALERT_EMAIL_ENABLED = os.environ.get('ALERT_EMAIL_ENABLED', 'False').lower() == 'true'
    ALERT_EMAIL_RECIPIENTS = os.environ.get('ALERT_EMAIL_RECIPIENTS', '').split(',')
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'localhost')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/adient_inventory.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # API settings
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 30))
    
    # Manufacturing specific settings
    PRODUCTION_LINE_COUNT = int(os.environ.get('PRODUCTION_LINE_COUNT', 4))
    SHIFT_DURATION_HOURS = int(os.environ.get('SHIFT_DURATION_HOURS', 8))
    SHIFTS_PER_DAY = int(os.environ.get('SHIFTS_PER_DAY', 3))
    
    # Data retention settings
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 365))
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 90))
    
    # Performance settings
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutes
    MAX_CONCURRENT_REQUESTS = int(os.environ.get('MAX_CONCURRENT_REQUESTS', 100))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///dev_adient_inventory.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@localhost/adient_inventory'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}