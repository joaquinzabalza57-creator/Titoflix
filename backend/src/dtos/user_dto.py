from datetime import datetime

from pydantic import BaseModel


# DTOs de cuenta/perfil usados dentro de servicios y como response_model en routers.
class CreateCuentaDTO(BaseModel):
    email: str
    password: str
    plan: str
    is_admin: bool = False


class UpdateCuentaDTO(BaseModel):
    email: str | None = None
    password: str | None = None
    plan: str | None = None
    is_admin: bool | None = None


class CuentaResponseDTO(BaseModel):
    id: int
    email: str
    plan: str
    is_admin: bool
    fecha_alta: datetime | None = None

    model_config = {"from_attributes": True}


class CreatePerfilDTO(BaseModel):
    cuenta_id: int
    nombre: str
    pin: str | None = None
    es_infantil: bool = False
    avatar: str | None = None


class UpdatePerfilDTO(BaseModel):
    nombre: str | None = None
    pin: str | None = None
    es_infantil: bool | None = None
    avatar: str | None = None


class PerfilResponseDTO(BaseModel):
    id: int
    cuenta_id: int
    nombre: str
    es_infantil: bool
    avatar: str | None = None
    has_pin: bool = False

    model_config = {"from_attributes": True}
