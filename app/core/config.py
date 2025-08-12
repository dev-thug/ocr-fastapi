from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_port: int = 8080
    allowed_origins: List[str] = []
    auth_mode: str = "api-key"  # cognito | api-key
    api_key: str | None = None
    max_file_mb: int = 10
    default_lang: str = "en"
    model_default: str = "pp-ocrv5"
    # Comma-separated list of allowed language codes for PaddleOCR (lowercase)
    # Example: "en,korean,ch,japan,latin,chinese_cht"
    allowed_langs: List[str] = [
        "en", "korean", "ch", "japan", "latin", "chinese_cht",
        "fr", "german", "arabic", "cyrillic", "devanagari"
    ]

    # Image processing
    max_image_px: int | None = 2048

    # Preload models on startup (reduce cold start)
    preload_models: bool = False

    # ChatOCR PoC toggle & token (placeholder)
    chatocr_enabled: bool = False
    chatocr_api_token: str | None = None

    # Cognito
    cognito_issuer: str | None = None
    cognito_audience: str | None = None


settings = Settings()  # type: ignore
