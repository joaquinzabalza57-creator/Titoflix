from sqlalchemy.orm import Session

from src.dtos.product_dto import (
    CalificacionResponseDTO,
    ContenidoResponseDTO,
    CreateCalificacionDTO,
    CreateContenidoDTO,
    CreateEpisodioDTO,
    CreateTemporadaDTO,
    CreateVistaDTO,
    EpisodioResponseDTO,
    GeneroResponseDTO,
    TemporadaResponseDTO,
    UpdateContenidoDTO,
    VistaResponseDTO,
)
from src.mappers.product_mapper import (
    to_calificacion_response,
    to_contenido_response,
    to_contenido_response_list,
    to_episodio_response,
    to_genero_response,
    to_genero_response_list,
    to_temporada_response,
    to_vista_response,
    to_vista_response_list,
)
from src.repositories.product_repository import (
    CalificacionRepository,
    ContenidoRepository,
    EpisodioRepository,
    GeneroRepository,
    TemporadaRepository,
    VistaRepository,
)
from src.repositories.user_repository import PerfilRepository
from src.utils.errors import ConflictError, ForbiddenError, NotFoundError


class GeneroService:
    def __init__(self, db: Session):
        self.genero_repo = GeneroRepository(db)

    def create(self, nombre: str) -> GeneroResponseDTO:
        genero = self.genero_repo.create(nombre)
        return to_genero_response(genero)

    def list_all(self) -> list[GeneroResponseDTO]:
        generos = self.genero_repo.list_all()
        return to_genero_response_list(generos)


class ContenidoService:
    def __init__(self, db: Session):
        self.contenido_repo = ContenidoRepository(db)
        self.genero_repo = GeneroRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def create(self, dto: CreateContenidoDTO) -> ContenidoResponseDTO:
        if not dto.generos_ids:
            raise ConflictError("Cada contenido debe tener al menos un género")

        if dto.tipo == "pelicula" and dto.duracion_min is None:
            raise ConflictError("Una película debe tener duración")

        if dto.tipo == "serie" and dto.duracion_min is not None:
            raise ConflictError("Una serie no debe tener duración directa")

        contenido = self.contenido_repo.create(
            titulo=dto.titulo,
            tipo=dto.tipo,
            anio=dto.anio,
            descripcion=dto.descripcion,
            duracion_min=dto.duracion_min,
            clasificacion_edad=dto.clasificacion_edad,
            generos_ids=dto.generos_ids,
        )

        return to_contenido_response(contenido)

    def get_by_id(self, contenido_id: int) -> ContenidoResponseDTO:
        contenido = self.contenido_repo.find_by_id(contenido_id)

        if not contenido:
            raise NotFoundError("Contenido no encontrado")

        return to_contenido_response(contenido)

    def search(
        self,
        q: str | None = None,
        tipo: str | None = None,
        genero_id: int | None = None,
        perfil_id: int | None = None,
    ) -> list[ContenidoResponseDTO]:
        clasificacion_edad = None

        if perfil_id is not None:
            perfil = self.perfil_repo.find_by_id(perfil_id)

            if not perfil:
                raise NotFoundError("Perfil no encontrado")

            if perfil.es_infantil:
                clasificacion_edad = "ATP"

        contenidos = self.contenido_repo.search(
            texto=q,
            tipo=tipo,
            genero_id=genero_id,
            clasificacion_edad=clasificacion_edad,
        )

        return to_contenido_response_list(contenidos)

    def update(self, contenido_id: int, dto: UpdateContenidoDTO) -> ContenidoResponseDTO:
        fields = dto.model_dump(exclude_unset=True)

        contenido = self.contenido_repo.update(contenido_id, **fields)

        if not contenido:
            raise NotFoundError("Contenido no encontrado")

        return to_contenido_response(contenido)

    def delete(self, contenido_id: int) -> None:
        deleted = self.contenido_repo.delete(contenido_id)

        if not deleted:
            raise NotFoundError("Contenido no encontrado")

    def top(self) -> list[ContenidoResponseDTO]:
        contenidos = self.contenido_repo.top(limit=10)
        return to_contenido_response_list(contenidos)


class TemporadaService:
    def __init__(self, db: Session):
        self.contenido_repo = ContenidoRepository(db)
        self.temporada_repo = TemporadaRepository(db)

    def create(self, dto: CreateTemporadaDTO) -> TemporadaResponseDTO:
        contenido = self.contenido_repo.find_by_id(dto.contenido_id)

        if not contenido:
            raise NotFoundError("Contenido no encontrado")

        if contenido.tipo != "serie":
            raise ConflictError("Solo las series pueden tener temporadas")

        temporada = self.temporada_repo.create(
            contenido_id=dto.contenido_id,
            numero=dto.numero,
            anio=dto.anio,
        )

        return to_temporada_response(temporada)

    def list_by_contenido(self, contenido_id: int) -> list[TemporadaResponseDTO]:
        temporadas = self.temporada_repo.list_by_contenido(contenido_id)
        return [to_temporada_response(temporada) for temporada in temporadas]


class EpisodioService:
    def __init__(self, db: Session):
        self.temporada_repo = TemporadaRepository(db)
        self.episodio_repo = EpisodioRepository(db)

    def create(self, dto: CreateEpisodioDTO) -> EpisodioResponseDTO:
        temporada = self.temporada_repo.find_by_id(dto.temporada_id)

        if not temporada:
            raise NotFoundError("Temporada no encontrada")

        episodio = self.episodio_repo.create(
            temporada_id=dto.temporada_id,
            numero=dto.numero,
            titulo=dto.titulo,
            duracion_min=dto.duracion_min,
        )

        return to_episodio_response(episodio)

    def list_by_temporada(self, temporada_id: int) -> list[EpisodioResponseDTO]:
        episodios = self.episodio_repo.list_by_temporada(temporada_id)
        return [to_episodio_response(episodio) for episodio in episodios]