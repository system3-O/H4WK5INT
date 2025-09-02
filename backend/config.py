import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://h4wk5int:h4wk5int@localhost:5432/h4wk5int')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Tor Configuration
    TOR_PROXY = os.getenv('TOR_PROXY', 'socks5://127.0.0.1:9050')
    USE_TOR = os.getenv('USE_TOR', 'true').lower() == 'true'
    TOR_TIMEOUT = int(os.getenv('TOR_TIMEOUT', '30'))
    
    # File Storage
    REPORTS_PATH = os.getenv('REPORTS_PATH', './reports/generated')
    UPLOAD_PATH = os.getenv('UPLOAD_PATH', './uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_DEFAULT = '100 per hour'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # External APIs
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', '')
    
    # Selenium Configuration
    SELENIUM_DRIVER_PATH = os.getenv('SELENIUM_DRIVER_PATH', '/usr/bin/chromedriver')
    SELENIUM_HEADLESS = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'h4wk5int.log')
    
    @staticmethod
    def init_app(app):
        # Create directories if they don't exist
        os.makedirs(Config.REPORTS_PATH, exist_ok=True)
        os.makedirs(Config.UPLOAD_PATH, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}