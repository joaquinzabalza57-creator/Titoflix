from datetime import datetime

from pydantic import BaseModel, Field


class GeneroResponseDTO(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}


class VideoVariantResponseDTO(BaseModel):
    id: int
    quality: str
    video_storage_key: str
    video_mime: str | None = None
    video_size: int | None = None

    model_config = {"from_attributes": True}


class CreateContenidoDTO(BaseModel):
    titulo: str
    tipo: str
    anio: int
    descripcion: str | None = None
    duracion_min: float | None = None
    clasificacion_edad: str
    generos_ids: list[int] = Field(default_factory=list)
    storage_folder_id: str | None = None
    video_storage_key: str | None = None
    video_mime: str | None = None
    video_size: int | None = None


class UpdateContenidoDTO(BaseModel):
    titulo: str | None = None
    tipo: str | None = None
    anio: int | None = None
    descripcion: str | None = None
    duracion_min: float | None = None
    clasificacion_edad: str | None = None
    generos_ids: list[int] | None = None
    video_storage_key: str | None = None
    video_mime: str | None = None
    video_size: int | None = None


class ContenidoResponseDTO(BaseModel):
    id: int
    titulo: str
    tipo: str
    anio: int
    descripcion: str | None = None
    duracion_min: float | None = None
    clasificacion_edad: str
    generos: list[GeneroResponseDTO] = Field(default_factory=list)
    promedio_calificaciones: float | None = None
    storage_folder_id: str | None = None
    video_storage_key: str | None = None
    video_mime: str | None = None
    video_size: int | None = None
    video_variants: list[VideoVariantResponseDTO] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class CreateTemporadaDTO(BaseModel):
    contenido_id: int
    numero: int
    anio: int
    storage_folder_id: str | None = None


class UpdateTemporadaDTO(BaseModel):
    numero: int | None = None
    anio: int | None = None


class TemporadaResponseDTO(BaseModel):
    id: int
    contenido_id: int
    numero: int
    anio: int
    storage_folder_id: str | None = None

    model_config = {"from_attributes": True}


class CreateEpisodioDTO(BaseModel):
    temporada_id: int
    numero: int
    titulo: str
    duracion_min: float | None = None
    storage_folder_id: str | None = None
    video_storage_key: str | None = None
    video_mime: str | None = None
    video_size: int | None = None


class UpdateEpisodioDTO(BaseModel):
    numero: int | None = None
    titulo: str | None = None
    duracion_min: float | None = None


class EpisodioResponseDTO(BaseModel):
    id: int
    temporada_id: int
    numero: int
    titulo: str
    duracion_min: float
    storage_folder_id: str | None = None
    video_storage_key: str | None = None
    video_mime: str | None = None
    video_size: int | None = None
    video_variants: list[VideoVariantResponseDTO] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class CreateVistaDTO(BaseModel):
    perfil_id: int
    episodio_id: int | None = None
    contenido_id: int | None = None
    segundos_vistos: int = 0
    terminado: bool = False


class VistaResponseDTO(BaseModel):
    id: int
    perfil_id: int
    episodio_id: int | None = None
    contenido_id: int | None = None
    fecha: datetime | None = None
    segundos_vistos: int
    terminado: bool

    model_config = {"from_attributes": True}


class CreateCalificacionDTO(BaseModel):
    perfil_id: int
    contenido_id: int
    puntaje: int


class CalificacionResponseDTO(BaseModel):
    id: int
    perfil_id: int
    contenido_id: int
    puntaje: int
    fecha: datetime | None = None

    model_config = {"from_attributes": True}


class MiListaDTO(BaseModel):
    perfil_id: int
    contenido_id: int


CreateProductDTO = CreateContenidoDTO
UpdateProductDTO = UpdateContenidoDTO
ProductResponseDTO = ContenidoResponseDTO
