from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="server_", extra="ignore")

    cors_allow_origins: list[str] = ["*"]
