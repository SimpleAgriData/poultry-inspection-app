from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config.app import AppConfig
from app.core.config.database import DatabaseConfig
from app.core.config.keycloak import KeycloakConfig
from app.core.config.server import ServerConfig
from app.core.config.stallkarte import StallkarteConfig

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    keycloak: KeycloakConfig = Field(default_factory=KeycloakConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    stallkarte: StallkarteConfig = Field(default_factory=StallkarteConfig)


@lru_cache
def get_settings() -> Settings:
    return Settings()
