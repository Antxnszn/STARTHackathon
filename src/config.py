"""
GreenPass Backend - Configuration Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Database
    database_url: str = "postgresql://greenpass:hackathon_password@localhost:5432/greenpass_db"
    
    # External API Keys
    climatiq_api_key: str = ""
    gfw_api_key: str = ""
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # External API URLs
    gfw_api_url: str = "https://data-api.globalforestwatch.org"
    openmeteo_api_url: str = "https://archive-api.open-meteo.com/v1/archive"
    climatiq_api_url: str = "https://api.climatiq.io/data/v1"
    
    # EUDR Settings
    eudr_cutoff_date: str = "2020-12-31"  # No deforestation after this date


settings = Settings()
