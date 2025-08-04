from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VVZ Crawler Service"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./vvz_crawler.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Crawler settings
    CRAWLER_INTERVAL_MINUTES: int = 60  # Run every hour
    VVZ_API_BASE_URL: str = "https://vvz.nipez.cz/api"
    
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
