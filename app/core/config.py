"""
Application Configuration Settings

This module contains the Pydantic settings class for managing application configuration.
It handles environment variables, default values, and configuration validation.
"""

import os
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application metadata
    PROJECT_NAME: str = "OCR FastAPI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS and allowed hosts
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./ocr_app.db"
    
    # PaddleOCR 3.1 settings
    PADDLE_OCR_USE_GPU: bool = False
    PADDLE_OCR_USE_MP: bool = True
    PADDLE_OCR_TOTAL_PROC_NUM: int = 1
    PADDLE_OCR_ENABLE_MKLDNN: bool = True
    PADDLE_OCR_CPU_MATH_LIB_NUM_THREADS: int = 10
    PADDLE_OCR_USE_TENSORRT: bool = False
    PADDLE_OCR_USE_FP16: bool = False
    PADDLE_OCR_DET_DB_THRESH: float = 0.3
    PADDLE_OCR_DET_DB_BOX_THRESH: float = 0.6
    PADDLE_OCR_DET_DB_UN_CLIP_RATIO: float = 1.6
    PADDLE_OCR_MAX_BATCH_SIZE: int = 10
    PADDLE_OCR_USE_ZERO_COPY_RUN: bool = False
    PADDLE_OCR_USE_PDF2DOCX_API: bool = False
    PADDLE_OCR_USE_SPACE_CHAR: bool = True
    PADDLE_OCR_DROP_SCORE: float = 0.5
    PADDLE_OCR_REC_CHAR_DICT_PATH: Optional[str] = None
    PADDLE_OCR_DET_LIMIT_SIDE_NUM: int = 960
    PADDLE_OCR_DET_LIMIT_TYPE: str = "max"
    PADDLE_OCR_REC_BATCH_NUM: int = 6
    PADDLE_OCR_REC_MODEL_DIR: Optional[str] = None
    PADDLE_OCR_DET_MODEL_DIR: Optional[str] = None
    PADDLE_OCR_CLS_MODEL_DIR: Optional[str] = None
    PADDLE_OCR_USE_ANGLE_CLS: bool = True
    PADDLE_OCR_CLS_THRESH: float = 0.9
    PADDLE_OCR_USE_GREEDY_DECODER: bool = False
    PADDLE_OCR_VERSION: str = "PP-OCRv5"
    
    # Supported languages for PaddleOCR 3.1
    SUPPORTED_LANGUAGES: List[str] = ["ch", "en", "french", "german", "korean", "japan"]
    DEFAULT_LANGUAGE: str = "korean"  # Default to Korean for Korean document processing
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Development settings
    DEBUG: bool = True
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse ALLOWED_HOSTS from string to list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("SUPPORTED_LANGUAGES", pre=True)
    def parse_supported_languages(cls, v):
        """Parse SUPPORTED_LANGUAGES from string to list."""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        """Parse ALLOWED_EXTENSIONS from string to list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True
        validate_default = False


# Create settings instance
settings = Settings() 