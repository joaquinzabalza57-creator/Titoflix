from pydantic import BaseModel


# DTOs de autenticacion: separan requests validadas de tokens/respuestas internas.
class LoginDTO(BaseModel):
    email: str
    password: str


class AdminLoginDTO(BaseModel):
    username: str | None = None
    password: str


class TokenDTO(BaseModel):
    """Respuesta que el frontend guarda para llamadas posteriores."""

    access_token: str
    token_type: str = "bearer"
    id: int | None = None
    is_admin: bool = False
    email: str | None = None
    plan: str | None = None


class AuthAccountDTO(BaseModel):
    id: int
    email: str
    plan: str
    is_admin: bool


class PinDTO(BaseModel):
    pin: str


class PerfilAuthDTO(BaseModel):
    pin: str | None = None


class PerfilAuthResponseDTO(BaseModel):
    message: str
    perfil_id: int
    cuenta_id: int
    bloqueado_hasta: str | None = None
