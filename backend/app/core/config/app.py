from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_", extra="ignore")

    name: str = "SiAD - Stallkarte API"
    version: str = "unknown"
    git_version: str = "unknown"
    description: str = "SiAD - Stallkarte Backend"
