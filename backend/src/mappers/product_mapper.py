from src.db.models import Calificacion, Contenido, Episodio, Genero, Temporada, Vista
from src.dtos.product_dto import (
    CalificacionResponseDTO,
    ContenidoResponseDTO,
    EpisodioResponseDTO,
    GeneroResponseDTO,
    ProductResponseDTO,
    TemporadaResponseDTO,
    VistaResponseDTO,
)


def to_genero_response(genero: Genero) -> GeneroResponseDTO:
    return GeneroResponseDTO.model_validate(genero)


def to_contenido_response(contenido: Contenido) -> ContenidoResponseDTO:
    return ContenidoResponseDTO.model_validate(contenido)


def to_product_response(product: Contenido) -> ProductResponseDTO:
    return to_contenido_response(product)


def to_temporada_response(temporada: Temporada) -> TemporadaResponseDTO:
    return TemporadaResponseDTO.model_validate(temporada)


def to_episodio_response(episodio: Episodio) -> EpisodioResponseDTO:
    return EpisodioResponseDTO.model_validate(episodio)


def to_vista_response(vista: Vista) -> VistaResponseDTO:
    return VistaResponseDTO.model_validate(vista)


def to_calificacion_response(calificacion: Calificacion) -> CalificacionResponseDTO:
    return CalificacionResponseDTO.model_validate(calificacion)


def to_genero_response_list(generos: list[Genero]) -> list[GeneroResponseDTO]:
    return [to_genero_response(genero) for genero in generos]


def to_contenido_response_list(contenidos: list[Contenido]) -> list[ContenidoResponseDTO]:
    return [to_contenido_response(contenido) for contenido in contenidos]


def to_product_response_list(products: list[Contenido]) -> list[ProductResponseDTO]:
    return [to_product_response(product) for product in products]


def to_temporada_response_list(temporadas: list[Temporada]) -> list[TemporadaResponseDTO]:
    return [to_temporada_response(temporada) for temporada in temporadas]


def to_episodio_response_list(episodios: list[Episodio]) -> list[EpisodioResponseDTO]:
    return [to_episodio_response(episodio) for episodio in episodios]


def to_vista_response_list(vistas: list[Vista]) -> list[VistaResponseDTO]:
    return [to_vista_response(vista) for vista in vistas]


def to_calificacion_response_list(
    calificaciones: list[Calificacion],
) -> list[CalificacionResponseDTO]:
    return [
        to_calificacion_response(calificacion)
        for calificacion in calificaciones
    ]