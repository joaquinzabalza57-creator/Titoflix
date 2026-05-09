from datetime import datetime                   # Manejo de fechas y horas
from typing import Literal                      # Permite definir valores fijos posibles

from pydantic import BaseModel, EmailStr, Field  # Validación de datos para esquemas


PlanType = Literal["basico", "estandar", "premium"]  # Tipos de plan permitidos



class CreateCuentaSchema(BaseModel):
    email: EmailStr                              # Email válido (validado automáticamente)
    password: str = Field(min_length=8, max_length=72)
    plan: PlanType                               # Tipo de plan (basico, estandar, premium)


class UpdateCuentaSchema(BaseModel):
    email: EmailStr | None = None                 # Email opcional (solo si se quiere actualizar)
    password: str | None = Field(default=None, min_length=8, max_length=72)
    plan: PlanType | None = None                  # Plan opcional (basico, estandar, premium)


class CuentaSchema(BaseModel):
    id: int                                      # ID único de la cuenta
    email: EmailStr                              # Email válido de la cuenta
    plan: PlanType                               # Tipo de plan (basico, estandar, premium)
    fecha_alta: datetime | None = None           # Fecha de creación de la cuenta
    
    model_config = {"from_attributes": True}     # Permite crear el schema desde objetos ORM (SQLAlchemy)


class CreatePerfilSchema(BaseModel):
    cuenta_id: int                               # ID de la cuenta a la que pertenece el perfil
    nombre: str = Field(min_length=1, max_length=50)  # Nombre del perfil (entre 1 y 50 caracteres)
    pin: str | None = Field(default=None, min_length=4, max_length=8)  # PIN opcional de exactamente 4 caracteres
    es_infantil: bool = False                    # Indica si el perfil es infantil (por defecto False)
    avatar: str | None = None                    # URL o referencia del avatar (opcional)


class UpdatePerfilSchema(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)  # Nombre opcional (1 a 50 caracteres)
    pin: str | None = Field(default=None, min_length=4, max_length=8)  # PIN opcional de 4 caracteres
    es_infantil: bool | None = None                 # Campo opcional para indicar si es perfil infantil
    avatar: str | None = None                       # Avatar opcional (URL o referencia)


class PerfilSchema(BaseModel):
    id: int                                      # ID único del perfil
    cuenta_id: int                               # ID de la cuenta a la que pertenece
    nombre: str                                  # Nombre del perfil
    pin: str | None = None                       # PIN opcional de la cuenta
    es_infantil: bool                            # Indica si es un perfil infantil
    avatar: str | None = None                    # Avatar opcional (URL o referencia)

    model_config = {"from_attributes": True}     # Permite crear el schema desde objetos ORM (SQLAlchemy)
