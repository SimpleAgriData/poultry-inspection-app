from pydantic_settings import BaseSettings, SettingsConfigDict


class StallkarteConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="stallkarte_", extra="ignore")

    template_file: str
    template_file_default_worksheet: str
