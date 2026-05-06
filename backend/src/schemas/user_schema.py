from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


PlanType = Literal["basico", "estandar", "premium"]


class CreateUserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    age: int = Field(ge=18)


class UpdateUserSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    age: int | None = Field(default=None, ge=18)


class CreateCuentaSchema(BaseModel):
    email: EmailStr
    plan: PlanType
    pin: str | None = Field(default=None, min_length=4, max_length=4)


class UpdateCuentaSchema(BaseModel):
    email: EmailStr | None = None
    plan: PlanType | None = None
    pin: str | None = Field(default=None, min_length=4, max_length=4)


class CuentaSchema(BaseModel):
    id: int
    email: EmailStr
    plan: PlanType
    pin: str | None = None
    fecha_alta: datetime | None = None

    model_config = {"from_attributes": True}


class CreatePerfilSchema(BaseModel):
    cuenta_id: int
    nombre: str = Field(min_length=1, max_length=50)
    es_infantil: bool = False
    avatar: str | None = None


class UpdatePerfilSchema(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    es_infantil: bool | None = None
    avatar: str | None = None


class PerfilSchema(BaseModel):
    id: int
    cuenta_id: int
    nombre: str
    es_infantil: bool
    avatar: str | None = None

    model_config = {"from_attributes": True}