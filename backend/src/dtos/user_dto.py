from datetime import datetime
from pydantic import BaseModel


class CreateCuentaDTO(BaseModel):
    email: str                                   # Email del usuario (obligatorio)
    password: str
    plan: str                                    # Tipo de plan (ej: basico, estandar, premium)
    pin: str | None = None                       # PIN opcional de 4 dígitos


class UpdateCuentaDTO(BaseModel):
    email: str | None = None                     # Email opcional para actualizar
    password: str | None = None                  # Contraseña opcional para actualizar
    plan: str | None = None                      # Plan opcional para actualizar
    pin: str | None = None                       # PIN opcional para actualizar

class CuentaResponseDTO(BaseModel):
    id: int                                      # ID único de la cuenta
    email: str                                   # Email asociado a la cuenta
    plan: str                                    # Tipo de plan suscrito
    pin: str | None = None                       # PIN opcional de seguridad
    fecha_alta: datetime | None = None           # Fecha de registro de la cuenta

    model_config = {"from_attributes": True}     # Configuración para lectura desde ORM


class CreatePerfilDTO(BaseModel):
    cuenta_id: int                               # ID de la cuenta al que pertenece el perfil
    nombre: str                                  # Nombre del perfil
    es_infantil: bool = False                    # Flag para indicar si es perfil infantil
    avatar: str | None = None                    # URL o identificador del avatar


class UpdatePerfilDTO(BaseModel):
    nombre: str | None = None                    # Nombre opcional para actualizar
    es_infantil: bool | None = None              # Estado opcional de perfil infantil
    avatar: str | None = None                    # Avatar opcional para actualizar


class PerfilResponseDTO(BaseModel):
    id: int                                      # ID único del perfil
    cuenta_id: int                               # ID de la cuenta a la que pertenece
    nombre: str                                  # Nombre del perfil
    es_infantil: bool                            # Indica si es un perfil infantil
    avatar: str | None = None                    # URL o referencia del avatar

    model_config = {"from_attributes": True}     # Configuración para lectura desde ORM