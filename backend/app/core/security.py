from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from .config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(subject: str, refresh: bool = False) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(
        days=14 if refresh else 0,
        minutes=0 if refresh else settings.access_token_expire_minutes,
    )
    return jwt.encode(
        {
            "sub": subject,
            "type": "refresh" if refresh else "access",
            "iat": now,
            "exp": expires,
        },
        settings.jwt_refresh_secret if refresh else settings.jwt_secret,
        algorithm="HS256",
    )


def decode_token(token: str, refresh: bool = False) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_refresh_secret if refresh else settings.jwt_secret,
        algorithms=["HS256"],
    )
