import logging
from typing import Any

import keycloak.exceptions
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from keycloak import KeycloakOpenID

from app.core.config import KeycloakConfig
from app.core.dependencies import settings
from app.domain import User

logger = logging.getLogger(__name__)


def get_keycloak_openid(
    kc_settings: KeycloakConfig = Depends(settings.keycloak_config),
) -> KeycloakOpenID:
    return KeycloakOpenID(
        server_url=kc_settings.url,
        realm_name=kc_settings.realm,
        client_id=kc_settings.client_id,
    )


def map_user(user_info: dict[str, Any]) -> User:
    if (
        "given_name" not in user_info
        or "family_name" not in user_info
        or "preferred_username" not in user_info
        or "sub" not in user_info
    ):
        logger.error(f"Invalid user info received: {user_info}")
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    return User(
        id=user_info["sub"],
        firstname=user_info["given_name"],
        lastname=user_info["family_name"],
        username=user_info["preferred_username"],
    )


bearer_scheme = HTTPBearer()


def authenticate(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    keycloak_openid: KeycloakOpenID = Depends(get_keycloak_openid),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401, detail="missing authentication credentials"
        )

    try:
        user_info = keycloak_openid.userinfo(credentials.credentials)
        if type(user_info) is not dict:
            logger.error(f"Invalid user info type received: {type(user_info)}")
            raise HTTPException(
                status_code=401, detail="invalid authentication credentials"
            )
        return map_user(user_info)
    except keycloak.exceptions.KeycloakAuthenticationError:
        raise HTTPException(
            status_code=401, detail="invalid authentication credentials"
        )
    except Exception:
        logger.exception("Error during authentication")
        raise HTTPException(status_code=500, detail="authentication service error")
