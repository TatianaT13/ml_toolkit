"""
Enterprise Security Layer - ML Toolkit API
Niveau: Production commerciale
"""

import os
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ─── Logging sécurisé ────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("security")

# ─── Configuration ───────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

if not SECRET_KEY:
    raise RuntimeError("❌ SECRET_KEY not set in environment variables!")

# ─── Password Hashing ────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# ─── Models ──────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list = []

class User(BaseModel):
    username: str
    email: str
    is_active: bool = True
    role: str = "user"  # user, admin, enterprise

# ─── Fake DB (remplacer par vraie DB en production) ──────────
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@mltoolkit.com",
        "hashed_password": pwd_context.hash("change-me-in-production"),
        "role": "admin",
        "is_active": True
    }
}

# ─── API Keys (pour accès programmatique) ────────────────────
API_KEYS_DB = {
    # Format: "key": {"owner": "...", "tier": "free/pro/enterprise", "requests_left": n}
}

# ─── Token Functions ─────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(16)  # JWT ID unique
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(username=username, scopes=payload.get("scopes", []))
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

# ─── Auth Dependencies ───────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    token_data = verify_token(token)
    user = USERS_DB.get(token_data.username)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="Inactive user")
    logger.info(f"✅ Authenticated: {token_data.username}")
    return User(**user)

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        logger.warning(f"⚠️ Unauthorized admin access attempt: {current_user.username}")
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user

async def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not api_key or api_key not in API_KEYS_DB:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    key_data = API_KEYS_DB[api_key]
    if key_data["requests_left"] <= 0:
        raise HTTPException(status_code=429, detail="API quota exceeded")
    # Décrémenter les requêtes
    API_KEYS_DB[api_key]["requests_left"] -= 1
    return key_data

# ─── Input Validation ────────────────────────────────────────
def sanitize_filename(filename: str) -> str:
    """Empêche path traversal attacks"""
    import re
    # Supprimer tout sauf alphanumériques, points, tirets
    clean = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Empêcher ../
    clean = clean.replace('..', '')
    if not clean:
        raise HTTPException(400, "Invalid filename")
    return clean

def validate_csv_file(file_content: bytes, max_size_mb: int = 50) -> bool:
    """Valide qu'un fichier CSV est sûr"""
    # Vérifier la taille
    size_mb = len(file_content) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise HTTPException(413, f"File too large: {size_mb:.1f}MB > {max_size_mb}MB")
    # Vérifier que c'est du texte (pas un binaire malveillant)
    try:
        file_content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be valid UTF-8 CSV")
    return True

# ─── Audit Log ───────────────────────────────────────────────
def audit_log(action: str, user: str, resource: str, ip: str, success: bool):
    """Log toutes les actions importantes"""
    logger.info(
        f"AUDIT | action={action} | user={user} | "
        f"resource={resource} | ip={ip} | success={success}"
    )
