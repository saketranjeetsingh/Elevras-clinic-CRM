import os
import secrets
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import jwt
from jose import JWTError
from dotenv import load_dotenv

from passlib.context import CryptContext


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable not set. Create a backend/.env file or set the environment variable."
        " See backend/.env.example for the expected format."
    )

WEAK_SECRET_KEYS = {"your-secret-key-here", "change-me", "changeme", "secret"}
if len(SECRET_KEY.strip()) < 32 or SECRET_KEY.strip().lower() in WEAK_SECRET_KEYS:
    raise RuntimeError(
        "SECRET_KEY is too weak. Use a random string of at least 32 characters"
        " (e.g. `python -c \"import secrets; print(secrets.token_hex(32))\"`)."
        " See backend/.env.example."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire, "type": "access"}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token():
    """Generate a secure random refresh token."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for storage."""
    return pwd_context.hash(token)


def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    """Verify a refresh token against its hash."""
    return pwd_context.verify(plain_token, hashed_token)


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def decode_token_unsafe(token: str):
    """Decode token without verification (for debugging)."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    except JWTError:
        return None