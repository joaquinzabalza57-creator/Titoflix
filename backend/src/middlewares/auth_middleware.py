from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.user_model import Cuenta, Perfil
from src.repositories.user_repository import CuentaRepository, PerfilRepository
from src.utils.errors import UnauthorizedError
from src.utils.jwt import decode_access_token


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> Cuenta:
    return get_user_from_authorization(authorization, db)


def get_user_from_authorization(authorization: str | None, db: Session) -> Cuenta:
    if not authorization:
        raise UnauthorizedError("Missing or malformed Authorization header")

    token = authorization.strip()
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()

    return get_user_from_token(token, db)


def get_user_from_token(token: str | None, db: Session) -> Cuenta:
    if not token:
        raise UnauthorizedError("Missing or malformed Authorization header")

    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid token payload")

    user = CuentaRepository(db).find_by_id(int(user_id))
    if user is None:
        raise UnauthorizedError("User no longer exists")

    return user


def get_profile_from_authorization(access_token: str | None, db: Session) -> Perfil:
    if not access_token:
        raise UnauthorizedError("Missing profile access token")

    token = access_token.strip()
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()

    payload = decode_access_token(token)
    perfil_id = payload.get("perfil_id")
    cuenta_id = payload.get("sub")

    if perfil_id is None or cuenta_id is None:
        raise UnauthorizedError("Invalid profile token payload")

    perfil = PerfilRepository(db).find_by_id(int(perfil_id))
    if perfil is None or perfil.cuenta_id != int(cuenta_id):
        raise UnauthorizedError("Profile token no longer matches an existing profile")

    return perfil
