import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "H4WK5INT"
    version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql://h4wk5int:h4wk5int@localhost:5432/h4wk5int"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    jwt_secret: str = "your-jwt-secret-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Tor Configuration
    tor_proxy: str = "socks5://127.0.0.1:9050"
    use_tor: bool = True
    
    # Report Storage
    reports_path: str = "./reports/generated"
    
    # OSINT API Keys (Optional)
    shodan_api_key: Optional[str] = None
    virustotal_api_key: Optional[str] = None
    hunter_io_api_key: Optional[str] = None
    
    # Social Media API Keys (Optional)
    twitter_bearer_token: Optional[str] = None
    facebook_access_token: Optional[str] = None
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()