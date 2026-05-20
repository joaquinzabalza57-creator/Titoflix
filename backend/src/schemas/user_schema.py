from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


PlanType = Literal["basico", "estandar", "premium"]


# Schemas HTTP para cuentas y perfiles. FastAPI los usa para validar requests
# antes de que la logica de negocio cree DTOs.
class CreateCuentaSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    plan: PlanType
    is_admin: bool = False


class UpdateCuentaSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)
    plan: PlanType | None = None
    is_admin: bool | None = None


class CuentaSchema(BaseModel):
    id: int
    email: EmailStr
    plan: PlanType
    is_admin: bool
    fecha_alta: datetime | None = None

    model_config = {"from_attributes": True}


class CreatePerfilSchema(BaseModel):
    cuenta_id: int | None = None
    nombre: str = Field(min_length=1, max_length=50)
    pin: str | None = Field(default=None, pattern=r"^\d{4}$")
    es_infantil: bool = False
    avatar: str | None = None


class UpdatePerfilSchema(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    pin: str | None = Field(default=None, pattern=r"^\d{4}$")
    es_infantil: bool | None = None
    avatar: str | None = None


class PerfilSchema(BaseModel):
    id: int
    cuenta_id: int
    nombre: str
    es_infantil: bool
    avatar: str | None = None
    has_pin: bool = False

    model_config = {"from_attributes": True}
