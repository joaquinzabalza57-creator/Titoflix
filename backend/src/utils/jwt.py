from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from src.config.env import settings
from src.utils.errors import UnauthorizedError


ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(
    payload: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    data = payload.copy()
    data.update({"exp": expire})

    return jwt.encode(
        data,
        settings.JWT_SECRET,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise UnauthorizedError("Token inválido o expirado")