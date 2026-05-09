from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from src.db import get_db
from src.dtos import LoginDTO, PerfilAuthDTO, TokenDTO
from src.middlewares import get_user_from_authorization
from src.schemas import LoginSchema, PerfilAuthSchema, TokenSchema
from src.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenSchema)
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    dto = LoginDTO(**payload.model_dump())
    token: TokenDTO = AuthService(db).login(dto)
    return TokenSchema(**token.model_dump())


@router.post("/perfiles/{perfil_id}", response_model=TokenSchema)
def auth_perfil(
    perfil_id: int,
    payload: PerfilAuthSchema,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    current_user = get_user_from_authorization(authorization, db)
    dto = PerfilAuthDTO(**payload.model_dump())
    token: TokenDTO = AuthService(db).auth_perfil(current_user.id, perfil_id, dto)
    return TokenSchema(**token.model_dump())
