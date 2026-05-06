from datetime import datetime

from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    email: str
    password: str
    age: int


class UpdateUserDTO(BaseModel):
    email: str | None = None
    password: str | None = None
    age: int | None = None


class UserResponseDTO(BaseModel):
    id: int
    email: str
    age: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateCuentaDTO(BaseModel):
    email: str
    plan: str
    pin: str | None = None


class UpdateCuentaDTO(BaseModel):
    email: str | None = None
    plan: str | None = None
    pin: str | None = None


class CuentaResponseDTO(BaseModel):
    id: int
    email: str
    plan: str
    pin: str | None = None
    fecha_alta: datetime | None = None

    model_config = {"from_attributes": True}


class CreatePerfilDTO(BaseModel):
    cuenta_id: int
    nombre: str
    es_infantil: bool = False
    avatar: str | None = None


class UpdatePerfilDTO(BaseModel):
    nombre: str | None = None
    es_infantil: bool | None = None
    avatar: str | None = None


class PerfilResponseDTO(BaseModel):
    id: int
    cuenta_id: int
    nombre: str
    es_infantil: bool
    avatar: str | None = None

    model_config = {"from_attributes": True}