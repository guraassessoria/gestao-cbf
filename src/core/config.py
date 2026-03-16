from functools import lru_cache

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

    # Armazenado como string para evitar problemas de parse do pydantic-settings
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def CORS_ORIGINS(self) -> list:
        value = self.CORS_ORIGINS_STR.strip()
        if value.startswith("["):
            import json
            try:
                return json.loads(value)
            except Exception:
                pass
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
