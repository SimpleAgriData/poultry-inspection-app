from pydantic_settings import BaseSettings, SettingsConfigDict


class KeycloakConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="keycloak_", extra="ignore")

    url: str
    realm: str
    client_id: str
