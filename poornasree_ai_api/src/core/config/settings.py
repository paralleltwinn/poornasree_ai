"""
Application Settings Configuration
================================

Centralized configuration management for the Poornasree AI API.
"""

import os
from typing import Optional
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "Poornasree AI Chatbot API"
    app_version: str = "3.0.0"
    debug: bool = False
    
    # Database settings
    db_host: str = "RDP-Main-Server"
    db_port: str = "3306"
    db_user: str = "root"
    db_password: str = "123@456"
    db_name: str = "psrAI"
    
    # AI settings
    gemini_api_key: Optional[str] = None
    ai_model: str = "gemini-2.5-flash-lite"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls"]
    
    # Paths
    data_dir: str = "data"
    uploads_dir: str = "data/uploads"
    knowledge_base_dir: str = "data/knowledge_base"
    logs_dir: str = "data/logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
