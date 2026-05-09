from sqlalchemy.orm import Session

from src.dtos import (
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
from src.mappers import (
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
from src.repositories import (
    CalificacionRepository,
    ContenidoRepository,
    EpisodioRepository,
    GeneroRepository,
    TemporadaRepository,
    VistaRepository,
)
from src.repositories import PerfilRepository
from src.utils import ConflictError, ForbiddenError, NotFoundError


class GeneroService:
    def __init__(self, db: Session):
        self.genero_repo = GeneroRepository(db)

    def create(self, nombre: str) -> GeneroResponseDTO:
        nombre = nombre.strip()
        if not nombre:
            raise ConflictError("El nombre del genero es obligatorio")

        if self.genero_repo.find_by_name(nombre):
            raise ConflictError("Ya existe un genero con ese nombre")

        genero = self.genero_repo.create(nombre)
        return to_genero_response(genero)

    def list_all(self) -> list[GeneroResponseDTO]:
        return to_genero_response_list(self.genero_repo.list_all())


class ContenidoService:
    def __init__(self, db: Session):
        self.contenido_repo = ContenidoRepository(db)
        self.genero_repo = GeneroRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def create(self, dto: CreateContenidoDTO) -> ContenidoResponseDTO:
        self._validate_content_payload(
            tipo=dto.tipo,
            duracion_min=dto.duracion_min,
            generos_ids=dto.generos_ids,
        )

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
        genero: str | None = None,
        perfil_id: int | None = None,
        ordenar: str | None = None,
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
            genero=genero,
            clasificacion_edad=clasificacion_edad,
            ordenar=ordenar,
        )
        return to_contenido_response_list(contenidos)

    def update(self, contenido_id: int, dto: UpdateContenidoDTO) -> ContenidoResponseDTO:
        contenido_actual = self.contenido_repo.find_by_id(contenido_id)
        if not contenido_actual:
            raise NotFoundError("Contenido no encontrado")

        fields = dto.model_dump(exclude_unset=True)
        self._validate_content_payload(
            tipo=fields.get("tipo", contenido_actual.tipo),
            duracion_min=fields.get("duracion_min", contenido_actual.duracion_min),
            generos_ids=fields.get("generos_ids"),
            require_generos=False,
        )

        contenido = self.contenido_repo.update(contenido_id, **fields)
        if not contenido:
            raise NotFoundError("Contenido no encontrado")

        return to_contenido_response(contenido)

    def delete(self, contenido_id: int) -> None:
        if not self.contenido_repo.delete(contenido_id):
            raise NotFoundError("Contenido no encontrado")

    def top(self, genero: str | None = None) -> list[ContenidoResponseDTO]:
        contenidos = self.contenido_repo.top(limit=10, genero=genero)
        return to_contenido_response_list(contenidos)

    def _validate_content_payload(
        self,
        tipo: str,
        duracion_min: int | None,
        generos_ids: list[int] | None,
        require_generos: bool = True,
    ) -> None:
        if require_generos and not generos_ids:
            raise ConflictError("Cada contenido debe tener al menos un genero")

        if generos_ids is not None:
            if not generos_ids:
                raise ConflictError("Cada contenido debe tener al menos un genero")
            generos = [self.genero_repo.find_by_id(genero_id) for genero_id in generos_ids]
            if any(genero is None for genero in generos):
                raise NotFoundError("Uno o mas generos no existen")

        if tipo == "pelicula" and duracion_min is None:
            raise ConflictError("Una pelicula debe tener duracion")

        if tipo == "serie" and duracion_min is not None:
            raise ConflictError("Una serie no debe tener duracion directa")


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
        if not self.contenido_repo.find_by_id(contenido_id):
            raise NotFoundError("Contenido no encontrado")

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
        if not self.temporada_repo.find_by_id(temporada_id):
            raise NotFoundError("Temporada no encontrada")

        episodios = self.episodio_repo.list_by_temporada(temporada_id)
        return [to_episodio_response(episodio) for episodio in episodios]


class VistaService:
    def __init__(self, db: Session):
        self.perfil_repo = PerfilRepository(db)
        self.contenido_repo = ContenidoRepository(db)
        self.episodio_repo = EpisodioRepository(db)
        self.vista_repo = VistaRepository(db)

    def create(self, dto: CreateVistaDTO) -> VistaResponseDTO:
        if self.vista_repo.find_existing(dto.perfil_id, dto.episodio_id, dto.contenido_id):
            raise ConflictError("La vista ya existe para este perfil y episodio")

        return self._save(dto)

    def update(self, dto: CreateVistaDTO) -> VistaResponseDTO:
        if not self.vista_repo.find_existing(dto.perfil_id, dto.episodio_id, dto.contenido_id):
            raise NotFoundError("Vista no encontrada")

        return self._save(dto)

    def create_or_update(self, dto: CreateVistaDTO) -> VistaResponseDTO:
        return self._save(dto)

    def _save(self, dto: CreateVistaDTO) -> VistaResponseDTO:
        perfil = self.perfil_repo.find_by_id(dto.perfil_id)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        if (dto.episodio_id is None) == (dto.contenido_id is None):
            raise ConflictError("La vista debe ser de un episodio o de una pelicula")

        if dto.episodio_id is not None:
            episodio = self.episodio_repo.find_by_id(dto.episodio_id)
            if not episodio:
                raise NotFoundError("Episodio no encontrado")

            contenido = episodio.temporada.contenido
            duracion_min = episodio.duracion_min
        else:
            contenido = self.contenido_repo.find_by_id(dto.contenido_id)  # type: ignore[arg-type]
            if not contenido:
                raise NotFoundError("Contenido no encontrado")
            if contenido.tipo != "pelicula":
                raise ConflictError("Las series se registran por episodio")
            if contenido.duracion_min is None:
                raise ConflictError("La pelicula debe tener duracion")

            duracion_min = contenido.duracion_min

        if perfil.es_infantil and contenido.clasificacion_edad != "ATP":
            raise ForbiddenError("El perfil infantil no puede ver este contenido")

        duracion_segundos = duracion_min * 60
        if dto.segundos_vistos > duracion_segundos:
            raise ConflictError("Los segundos vistos superan la duracion")

        terminado = dto.terminado or dto.segundos_vistos >= duracion_segundos * 0.9
        vista = self.vista_repo.create_or_update(
            perfil_id=dto.perfil_id,
            episodio_id=dto.episodio_id,
            contenido_id=dto.contenido_id,
            segundos_vistos=dto.segundos_vistos,
            terminado=terminado,
        )
        return to_vista_response(vista)

    def continuar_viendo(self, perfil_id: int) -> list[VistaResponseDTO]:
        if not self.perfil_repo.find_by_id(perfil_id):
            raise NotFoundError("Perfil no encontrado")

        vistas = self.vista_repo.continuar_viendo(perfil_id)[:10]
        return to_vista_response_list(vistas)

    def delete(
        self,
        perfil_id: int,
        episodio_id: int | None = None,
        contenido_id: int | None = None,
    ) -> None:
        if not self.perfil_repo.find_by_id(perfil_id):
            raise NotFoundError("Perfil no encontrado")

        if episodio_id is not None and not self.episodio_repo.find_by_id(episodio_id):
            raise NotFoundError("Episodio no encontrado")

        if contenido_id is not None and not self.contenido_repo.find_by_id(contenido_id):
            raise NotFoundError("Contenido no encontrado")

        if not self.vista_repo.delete(perfil_id, episodio_id, contenido_id):
            raise NotFoundError("Vista no encontrada")


class MiListaService:
    def __init__(self, db: Session):
        self.perfil_repo = PerfilRepository(db)
        self.contenido_repo = ContenidoRepository(db)

    def add(self, perfil_id: int, contenido_id: int) -> list[ContenidoResponseDTO]:
        perfil = self.perfil_repo.find_by_id(perfil_id)
        contenido = self.contenido_repo.find_by_id(contenido_id)

        if not perfil:
            raise NotFoundError("Perfil no encontrado")
        if not contenido:
            raise NotFoundError("Contenido no encontrado")
        if perfil.es_infantil and contenido.clasificacion_edad != "ATP":
            raise ForbiddenError("El perfil infantil no puede agregar este contenido")

        perfil = self.perfil_repo.add_to_mi_lista(perfil_id, contenido_id)
        return to_contenido_response_list(perfil.mi_lista)

    def remove(self, perfil_id: int, contenido_id: int) -> list[ContenidoResponseDTO]:
        perfil = self.perfil_repo.remove_from_mi_lista(perfil_id, contenido_id)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        return to_contenido_response_list(perfil.mi_lista)

    def list(self, perfil_id: int) -> list[ContenidoResponseDTO]:
        perfil = self.perfil_repo.find_by_id(perfil_id)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        contenidos = self.perfil_repo.get_mi_lista(perfil_id)
        if perfil.es_infantil:
            contenidos = [
                contenido for contenido in contenidos
                if contenido.clasificacion_edad == "ATP"
            ]

        return to_contenido_response_list(contenidos)


class CalificacionService:
    def __init__(self, db: Session):
        self.perfil_repo = PerfilRepository(db)
        self.contenido_repo = ContenidoRepository(db)
        self.calificacion_repo = CalificacionRepository(db)
        self.vista_repo = VistaRepository(db)

    def create(self, dto: CreateCalificacionDTO) -> CalificacionResponseDTO:
        if self.calificacion_repo.find_by_perfil_and_contenido(dto.perfil_id, dto.contenido_id):
            raise ConflictError("La calificacion ya existe para este perfil y contenido")

        return self._save(dto)

    def update(self, dto: CreateCalificacionDTO) -> CalificacionResponseDTO:
        if not self.calificacion_repo.find_by_perfil_and_contenido(dto.perfil_id, dto.contenido_id):
            raise NotFoundError("Calificacion no encontrada")

        return self._save(dto)

    def create_or_update(self, dto: CreateCalificacionDTO) -> CalificacionResponseDTO:
        return self._save(dto)

    def _save(self, dto: CreateCalificacionDTO) -> CalificacionResponseDTO:
        perfil = self.perfil_repo.find_by_id(dto.perfil_id)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        contenido = self.contenido_repo.find_by_id(dto.contenido_id)
        if not contenido:
            raise NotFoundError("Contenido no encontrado")

        vistas = self.vista_repo.list_by_perfil(dto.perfil_id)
        empezo_contenido = any(
            (
                vista.contenido_id == dto.contenido_id
                or (
                    vista.episodio is not None
                    and vista.episodio.temporada.contenido_id == dto.contenido_id
                )
            )
            and vista.segundos_vistos > 0
            for vista in vistas
        )
        if not empezo_contenido:
            raise ConflictError("Solo se puede calificar contenido empezado")

        calificacion = self.calificacion_repo.create_or_update(
            perfil_id=dto.perfil_id,
            contenido_id=dto.contenido_id,
            puntaje=dto.puntaje,
        )
        return to_calificacion_response(calificacion)

    def delete(self, perfil_id: int, contenido_id: int) -> None:
        if not self.perfil_repo.find_by_id(perfil_id):
            raise NotFoundError("Perfil no encontrado")

        if not self.contenido_repo.find_by_id(contenido_id):
            raise NotFoundError("Contenido no encontrado")

        if not self.calificacion_repo.delete(perfil_id, contenido_id):
            raise NotFoundError("Calificacion no encontrada")
