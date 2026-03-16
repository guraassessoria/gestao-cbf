from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    APP_NAME: str = "Balancete MVP API"
    APP_ENV: str = "development"
    APP_BASE_URL: str = "http://127.0.0.1:8000"

    DATABASE_URL: str
    DIRECT_DATABASE_URL: str | None = None

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    DEFAULT_ADMIN_EMAIL: str = "admin@empresa.com"
    DEFAULT_ADMIN_NAME: str = "Administrador"
    DEFAULT_ADMIN_PASSWORD: str = "TroqueEssaSenha123!"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, value):
        if isinstance(value, str):
            value = value.strip()
            # Se vier como JSON array ex: ["url1","url2"]
            if value.startswith("["):
                import json
                try:
                    return json.loads(value)
                except Exception:
                    pass
            # Se vier como lista separada por virgula ex: url1,url2
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
