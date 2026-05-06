from datetime import datetime                   # Manejo de fechas y horas
from typing import Literal                      # Permite definir valores fijos posibles

from pydantic import BaseModel, Field           # Base para schemas y validaciones


TipoContenido = Literal["pelicula", "serie"]    # Tipos de contenido permitidos
ClasificacionEdad = Literal["ATP", "+13", "+16", "+18"]  # Clasificaciones de edad permitidas

class GeneroSchema(BaseModel):
    id: int                                      # ID único del género
    nombre: str                                  # Nombre del género

    model_config = {"from_attributes": True}     # Permite crear el schema desde objetos ORM (SQLAlchemy)


class CreateContenidoSchema(BaseModel):
    titulo: str = Field(min_length=1)            # Título obligatorio (mínimo 1 caracter)
    tipo: TipoContenido                         # Tipo de contenido (pelicula o serie)
    anio: int = Field(ge=1900)                  # Año de lanzamiento (≥ 1900)
    descripcion: str | None = None              # Descripción opcional
    duracion_min: int | None = Field(default=None, gt=0)  # Duración en minutos (opcional, > 0)
    clasificacion_edad: ClasificacionEdad       # Clasificación por edad (ATP, +13, +16, +18)
    generos_ids: list[int] = []                 # Lista de IDs de géneros asociados

class UpdateContenidoSchema(BaseModel):
    titulo: str | None = Field(default=None, min_length=1)  # Título opcional (mínimo 1 caracter)
    tipo: TipoContenido | None = None                       # Tipo opcional (pelicula o serie)
    anio: int | None = Field(default=None, ge=1900)         # Año opcional (≥ 1900)
    descripcion: str | None = None                          # Descripción opcional
    duracion_min: int | None = Field(default=None, gt=0)    # Duración opcional (> 0)
    clasificacion_edad: ClasificacionEdad | None = None     # Clasificación opcional
    generos_ids: list[int] | None = None                    # Lista opcional de IDs de géneros


class ContenidoSchema(BaseModel):
    id: int                                      # ID único del contenido
    titulo: str                                  # Título del contenido
    tipo: TipoContenido                          # Tipo (pelicula o serie)
    anio: int                                    # Año de lanzamiento
    descripcion: str | None = None               # Descripción opcional
    duracion_min: int | None = None              # Duración en minutos (opcional)
    clasificacion_edad: ClasificacionEdad        # Clasificación por edad (ATP, +13, +16, +18)

    model_config = {"from_attributes": True}     # Permite crear el schema desde objetos ORM (SQLAlchemy)


class CreateTemporadaSchema(BaseModel):
    contenido_id: int                     # ID del contenido (serie) al que pertenece la temporada
    numero: int = Field(ge=1)             # Número de la temporada (≥ 1)
    anio: int = Field(ge=1900)            # Año de lanzamiento (≥ 1900)


class CreateEpisodioSchema(BaseModel):
    temporada_id: int                     # ID de la temporada a la que pertenece el episodio
    numero: int = Field(ge=1)             # Número del episodio dentro de la temporada (≥ 1)
    titulo: str = Field(min_length=1)     # Título del episodio (mínimo 1 caracter)
    duracion_min: int = Field(gt=0)       # Duración en minutos (> 0)


class CreateVistaSchema(BaseModel):
    perfil_id: int                           # ID del perfil que realiza la visualización
    episodio_id: int                         # ID del episodio visto
    segundos_vistos: int = Field(default=0, ge=0)  # Segundos reproducidos (≥ 0, por defecto 0)
    terminado: bool = False                  # Indica si el episodio fue visto completo (por defecto False)


class CreateCalificacionSchema(BaseModel):
    perfil_id: int                           # ID del perfil que realiza la calificación
    contenido_id: int                        # ID del contenido calificado
    puntaje: int = Field(ge=1, le=5)         # Puntuación entre 1 y 5


class MiListaSchema(BaseModel):
    perfil_id: int                         # ID del perfil que agrega el contenido a su lista
    contenido_id: int                      # ID del contenido agregado a la lista


class VistaSchema(CreateVistaSchema):
    id: int                                # ID único de la vista
    fecha: datetime | None = None          # Fecha de la visualización (puede venir de la BD)

    model_config = {"from_attributes": True}  # Permite crear el schema desde objetos ORM (SQLAlchemy)


class CalificacionSchema(CreateCalificacionSchema):
    id: int                                # ID único de la calificación
    fecha: datetime | None = None          # Fecha en que se realizó la calificación

    model_config = {"from_attributes": True}  # Permite crear el schema desde objetos ORM (SQLAlchemy)