from fastapi import Depends

from app.core.config import (
    DatabaseConfig,
    KeycloakConfig,
    ServerConfig,
    Settings,
    StallkarteConfig,
    get_settings,
)


def stallkarte_config(settings: Settings = Depends(get_settings)) -> StallkarteConfig:
    return settings.stallkarte


def server_config(settings: Settings = Depends(get_settings)) -> ServerConfig:
    return settings.server


def keycloak_config(settings: Settings = Depends(get_settings)) -> KeycloakConfig:
    return settings.keycloak


def database_config(settings: Settings = Depends(get_settings)) -> DatabaseConfig:
    return settings.db
