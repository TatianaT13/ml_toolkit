"""
Keycloak Authentication - Version simplifiée
"""
import os
import httpx
import logging
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from pydantic import BaseModel

logger = logging.getLogger("keycloak")

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8180")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "ml-toolkit")
KEYCLOAK_CERTS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"

bearer_scheme = HTTPBearer(auto_error=False)

class KeycloakUser(BaseModel):
    id: str
    username: str
    email: str = ""
    roles: List[str] = []
    mfa_enabled: bool = False

def verify_token(token: str) -> dict:
    try:
        jwks = httpx.get(KEYCLOAK_CERTS_URL, timeout=10).json()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
                "verify_exp": True,
                "verify_iss": False,
                "verify_at_hash": False,
            }
        )
        return payload
    except Exception as e:
        logger.warning(f"Token error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> KeycloakUser:
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = verify_token(credentials.credentials)
    
    roles = []
    roles.extend(payload.get("realm_access", {}).get("roles", []))
    
    user = KeycloakUser(
        id=payload.get("sub", ""),
        username=payload.get("preferred_username", "unknown"),
        email=payload.get("email", ""),
        roles=roles,
        mfa_enabled="otp" in payload.get("amr", [])
    )
    
    logger.info(f"✅ Authenticated: {user.username}")
    return user
