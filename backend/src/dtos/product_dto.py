from datetime import datetime              # Manejo de fechas y horas (aunque no se usa directamente aquí)

from pydantic import BaseModel, Field      # Base para definir DTOs


class GeneroResponseDTO(BaseModel):
    id: int                                # ID único del género
    nombre: str                            # Nombre del género

    model_config = {"from_attributes": True}  # Permite crear el DTO desde objetos ORM (SQLAlchemy)


class CreateContenidoDTO(BaseModel):
    titulo: str                              # Título del contenido
    tipo: str                                # Tipo de contenido (pelicula o serie)
    anio: int                                # Año de lanzamiento
    descripcion: str | None = None           # Descripción opcional
    duracion_min: int | None = None          # Duración en minutos (opcional)
    clasificacion_edad: str                  # Clasificación por edad
    generos_ids: list[int] = Field(default_factory=list)  # Lista de IDs de generos asociados


class UpdateContenidoDTO(BaseModel):
    titulo: str | None = None                # Título opcional (para actualización)
    tipo: str | None = None                 # Tipo opcional
    anio: int | None = None                 # Año opcional
    descripcion: str | None = None          # Descripción opcional
    duracion_min: int | None = None         # Duración opcional
    clasificacion_edad: str | None = None   # Clasificación opcional
    generos_ids: list[int] | None = None    # Lista opcional de IDs de géneros


class ContenidoResponseDTO(BaseModel):
    id: int                                      # ID único del contenido
    titulo: str                                  # Título del contenido
    tipo: str                                    # Tipo de contenido (pelicula, serie)
    anio: int                                    # Año de lanzamiento
    descripcion: str | None = None               # Descripción breve (opcional)
    duracion_min: int | None = None              # Duración en minutos (opcional)
    clasificacion_edad: str                      # Clasificación por edad (ATP, +13, etc.)
    generos: list[GeneroResponseDTO] = Field(default_factory=list)  # Lista de generos asociados
    promedio_calificaciones: float | None = None

    model_config = {"from_attributes": True}     # Permite convertir desde el objeto ORM


class CreateTemporadaDTO(BaseModel):
    contenido_id: int                            # ID de la serie asociada
    numero: int                                  # Número de la temporada
    anio: int                                    # Año de estreno de la temporada


class TemporadaResponseDTO(BaseModel):
    id: int                                      # ID único de la temporada
    contenido_id: int                            # ID del contenido (serie) al que pertenece
    numero: int                                  # Número de la temporada
    anio: int                                    # Año de estreno de la temporada

    model_config = {"from_attributes": True}     # Configuración para lectura desde ORM


class CreateEpisodioDTO(BaseModel):
    temporada_id: int                            # ID de la temporada a la que pertenece
    numero: int                                  # Número del episodio
    titulo: str                                  # Título del episodio
    duracion_min: int                            # Duración en minutos


class EpisodioResponseDTO(BaseModel):
    id: int                                      # ID único del episodio
    temporada_id: int                            # ID de la temporada asociada
    numero: int                                  # Número del episodio
    titulo: str                                  # Título del episodio
    duracion_min: int                            # Duración en minutos

    model_config = {"from_attributes": True}     # Configuración para lectura desde ORM


class CreateVistaDTO(BaseModel):
    perfil_id: int                               # ID del perfil que ve el episodio
    episodio_id: int                             # ID del episodio que se está viendo
    segundos_vistos: int = 0                     # Tiempo reproducido en segundos
    terminado: bool = False                      # Estado: True si completó el episodio


class VistaResponseDTO(BaseModel):
    id: int                                      # ID único de la vista
    perfil_id: int                               # ID del perfil que realizó la vista
    episodio_id: int                             # ID del episodio visto
    fecha: datetime | None = None                # Fecha y hora de la visualización
    segundos_vistos: int                         # Cantidad de segundos reproducidos
    terminado: bool                              # Indica si el episodio se vio completo

    model_config = {"from_attributes": True}     # Configuración para lectura desde ORM


class CreateCalificacionDTO(BaseModel):
    perfil_id: int                               # ID del perfil que califica
    contenido_id: int                            # ID del contenido calificado
    puntaje: int                                 # Puntuación otorgada (escala de 1 a 5)


class CalificacionResponseDTO(BaseModel):
    id: int                                      # ID único de la calificación
    perfil_id: int                               # ID del perfil que califica
    contenido_id: int                            # ID del contenido calificado
    puntaje: int                                 # Puntaje otorgado
    fecha: datetime | None = None                # Fecha de la calificación

    model_config = {"from_attributes": True}     # Configuración para lectura desde ORM


class MiListaDTO(BaseModel):
    perfil_id: int                               # ID del perfil dueño de la lista
    contenido_id: int                            # ID del contenido en la lista


# Alias de clases para estandarizar nombres de DTOs
CreateProductDTO = CreateContenidoDTO
UpdateProductDTO = UpdateContenidoDTO
ProductResponseDTO = ContenidoResponseDTO 
