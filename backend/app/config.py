"""Application configuration settings for Intelligent Task Management System."""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./tasks.db"
    
    # Application Settings
    debug: bool = True
    app_name: str = "Intelligent Task Management System"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

