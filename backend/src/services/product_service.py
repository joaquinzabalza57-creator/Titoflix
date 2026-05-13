from sqlalchemy.orm import Session                               # Importa la sesión de SQLAlchemy

from src.dtos import (                                           # Importa DTOs de producto
    CalificacionResponseDTO,                                     # DTO respuesta calificación
    ContenidoResponseDTO,                                        # DTO respuesta contenido
    CreateCalificacionDTO,                                       # DTO creación calificación
    CreateContenidoDTO,                                          # DTO creación contenido
    CreateEpisodioDTO,                                           # DTO creación episodio
    CreateTemporadaDTO,                                          # DTO creación temporada
    CreateVistaDTO,                                              # DTO creación vista
    EpisodioResponseDTO,                                         # DTO respuesta episodio
    GeneroResponseDTO,                                           # DTO respuesta género
    TemporadaResponseDTO,                                        # DTO respuesta temporada
    UpdateContenidoDTO,                                          # DTO actualización contenido
    VistaResponseDTO,                                            # DTO respuesta vista
)
from src.mappers import (                                        # Importa mappers de producto
    to_calificacion_response,                                    # Mapper calificación
    to_contenido_response,                                       # Mapper contenido individual
    to_contenido_response_list,                                  # Mapper lista de contenidos
    to_episodio_response,                                        # Mapper episodio
    to_genero_response,                                          # Mapper género
    to_genero_response_list,                                     # Mapper lista de géneros
    to_temporada_response,                                       # Mapper temporada
    to_vista_response,                                           # Mapper vista
    to_vista_response_list,                                      # Mapper lista de vistas
)
from src.repositories import (                                   # Importa repositorios de producto
    CalificacionRepository,                                      # Repo calificaciones
    ContenidoRepository,                                         # Repo contenidos
    EpisodioRepository,                                          # Repo episodios
    GeneroRepository,                                            # Repo géneros
    TemporadaRepository,                                         # Repo temporadas
    VistaRepository,                                             # Repo vistas
)
from src.repositories import PerfilRepository                    # Repo perfiles (usuario)
from src.utils import ConflictError, ForbiddenError, NotFoundError # Excepciones personalizadas


class GeneroService:                                             # Servicio para gestión de Géneros
    def __init__(self, db: Session):                            # Inicializa repositorio
        self.genero_repo = GeneroRepository(db)

    def create(self, nombre: str) -> GeneroResponseDTO:         # Crea un nuevo género
        nombre = nombre.strip()                                 # Limpia espacios en blanco
        if not nombre:                                          # Valida nombre no vacío
            raise ConflictError("El nombre del genero es obligatorio")

        if self.genero_repo.find_by_name(nombre):               # Valida unicidad
            raise ConflictError("Ya existe un genero con ese nombre")

        genero = self.genero_repo.create(nombre)                # Persiste en BD
        return to_genero_response(genero)                       # Retorna respuesta mapeada

    def list_all(self) -> list[GeneroResponseDTO]:              # Lista todos los géneros
        return to_genero_response_list(self.genero_repo.list_all())


class ContenidoService:                                          # Servicio para gestión de Películas/Series
    def __init__(self, db: Session):                            # Inicializa repositorios
        self.contenido_repo = ContenidoRepository(db)
        self.genero_repo = GeneroRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def create(self, dto: CreateContenidoDTO) -> ContenidoResponseDTO: # Crea contenido
        self._validate_content_payload(                         # Valida lógica de negocio
            tipo=dto.tipo,
            duracion_min=dto.duracion_min,
            generos_ids=dto.generos_ids,
        )

        contenido = self.contenido_repo.create(                 # Persiste contenido
            titulo=dto.titulo,
            tipo=dto.tipo,
            anio=dto.anio,
            descripcion=dto.descripcion,
            duracion_min=dto.duracion_min,
            clasificacion_edad=dto.clasificacion_edad,
            generos_ids=dto.generos_ids,
        )
        return to_contenido_response(contenido)                 # Retorna respuesta mapeada

    def get_by_id(self, contenido_id: int) -> ContenidoResponseDTO: # Busca por ID
        contenido = self.contenido_repo.find_by_id(contenido_id)
        if not contenido:                                       # Valida existencia
            raise NotFoundError("Contenido no encontrado")
        return to_contenido_response(contenido)

    def search(self, q=None, tipo=None, genero_id=None, genero=None, perfil_id=None, ordenar=None): # Buscador
        clasificacion_edad = None                               # Init filtro edad
        if perfil_id is not None:                               # Si hay perfil, aplica control parental
            perfil = self.perfil_repo.find_by_id(perfil_id)
            if not perfil: raise NotFoundError("Perfil no encontrado")
            if perfil.es_infantil: clasificacion_edad = "ATP"

        contenidos = self.contenido_repo.search(                # Ejecuta búsqueda filtrada
            texto=q, tipo=tipo, genero_id=genero_id,
            genero=genero, clasificacion_edad=clasificacion_edad, ordenar=ordenar,
        )
        return to_contenido_response_list(contenidos)           # Retorna lista mapeada

    def update(self, contenido_id: int, dto: UpdateContenidoDTO) -> ContenidoResponseDTO: # Actualiza contenido
        contenido_actual = self.contenido_repo.find_by_id(contenido_id)
        if not contenido_actual: raise NotFoundError("Contenido no encontrado")

        fields = dto.model_dump(exclude_unset=True)             # Solo campos enviados
        self._validate_content_payload(                         # Valida cambios vs tipo de contenido
            tipo=fields.get("tipo", contenido_actual.tipo),
            duracion_min=fields.get("duracion_min", contenido_actual.duracion_min),
            generos_ids=fields.get("generos_ids"),
            require_generos=False,
        )

        contenido = self.contenido_repo.update(contenido_id, **fields)
        return to_contenido_response(contenido)

    def delete(self, contenido_id: int) -> None:                # Elimina contenido
        if not self.contenido_repo.delete(contenido_id):
            raise NotFoundError("Contenido no encontrado")

    def top(self, genero: str | None = None) -> list[ContenidoResponseDTO]: # Top 10 popularidad
        contenidos = self.contenido_repo.top(limit=10, genero=genero)
        return to_contenido_response_list(contenidos)

    def _validate_content_payload(self, tipo, duracion_min, generos_ids, require_generos=True): # Validaciones internas
        if require_generos and not generos_ids:
            raise ConflictError("Cada contenido debe tener al menos un genero")
        if generos_ids:                                         # Valida que los géneros existan en BD
            generos = [self.genero_repo.find_by_id(gid) for gid in generos_ids]
            if any(g is None for g in generos): raise NotFoundError("Uno o mas generos no existen")
        if tipo == "pelicula" and duracion_min is None:         # Película requiere tiempo
            raise ConflictError("Una pelicula debe tener duracion")
        if tipo == "serie" and duracion_min is not None:        # Serie no tiene tiempo global
            raise ConflictError("Una serie no debe tener duracion directa")


class TemporadaService:                                          # Servicio para Temporadas de Series
    def __init__(self, db: Session):
        self.contenido_repo = ContenidoRepository(db)
        self.temporada_repo = TemporadaRepository(db)

    def create(self, dto: CreateTemporadaDTO) -> TemporadaResponseDTO: # Crea temporada
        contenido = self.contenido_repo.find_by_id(dto.contenido_id)
        if not contenido: raise NotFoundError("Contenido no encontrado")
        if contenido.tipo != "serie":                           # Valida que el padre sea serie
            raise ConflictError("Solo las series pueden tener temporadas")

        temporada = self.temporada_repo.create(                 # Persiste temporada
            contenido_id=dto.contenido_id, numero=dto.numero, anio=dto.anio
        )
        return to_temporada_response(temporada)

    def list_by_contenido(self, contenido_id: int) -> list[TemporadaResponseDTO]: # Lista por serie
        if not self.contenido_repo.find_by_id(contenido_id):
            raise NotFoundError("Contenido no encontrado")
        return [to_temporada_response(t) for t in self.temporada_repo.list_by_contenido(contenido_id)]


class EpisodioService:                                           # Servicio para Episodios
    def __init__(self, db: Session):
        self.temporada_repo = TemporadaRepository(db)
        self.episodio_repo = EpisodioRepository(db)

    def create(self, dto: CreateEpisodioDTO) -> EpisodioResponseDTO: # Crea episodio
        temporada = self.temporada_repo.find_by_id(dto.temporada_id)
        if not temporada: raise NotFoundError("Temporada no encontrada")

        episodio = self.episodio_repo.create(                   # Persiste episodio
            temporada_id=dto.temporada_id, numero=dto.numero,
            titulo=dto.titulo, duracion_min=dto.duracion_min
        )
        return to_episodio_response(episodio)

    def list_by_temporada(self, temporada_id: int) -> list[EpisodioResponseDTO]: # Lista por temporada
        if not self.temporada_repo.find_by_id(temporada_id):
            raise NotFoundError("Temporada no encontrada")
        return [to_episodio_response(e) for e in self.episodio_repo.list_by_temporada(temporada_id)]


class VistaService:                                              # Servicio para Progreso de Visualización
    def __init__(self, db: Session):
        self.perfil_repo = PerfilRepository(db)
        self.episodio_repo = EpisodioRepository(db)
        self.vista_repo = VistaRepository(db)

    def create_or_update(self, dto: CreateVistaDTO) -> VistaResponseDTO: # Registra progreso
        perfil = self.perfil_repo.find_by_id(dto.perfil_id)
        episodio = self.episodio_repo.find_by_id(dto.episodio_id)
        if not perfil: raise NotFoundError("Perfil no encontrado")
        if not episodio: raise NotFoundError("Episodio no encontrado")

        if perfil.es_infantil and episodio.temporada.contenido.clasificacion_edad != "ATP": # Control parental
            raise ForbiddenError("El perfil infantil no puede ver este contenido")

        duracion_seg = episodio.duracion_min * 60               # Valida tiempo máximo
        if dto.segundos_vistos > duracion_seg:
            raise ConflictError("Los segundos vistos superan la duracion")

        terminado = dto.terminado or dto.segundos_vistos >= duracion_seg * 0.9 # Marca terminado al 90%
        vista = self.vista_repo.create_or_update(               # Persiste en BD
            perfil_id=dto.perfil_id, episodio_id=dto.episodio_id,
            segundos_vistos=dto.segundos_vistos, terminado=terminado
        )
        return to_vista_response(vista)

    def continuar_viendo(self, perfil_id: int) -> list[VistaResponseDTO]: # Obtiene recientes
        if not self.perfil_repo.find_by_id(perfil_id): raise NotFoundError("Perfil no encontrado")
        return to_vista_response_list(self.vista_repo.continuar_viendo(perfil_id)[:10])


class MiListaService:                                            # Servicio para Favoritos/Mi Lista
    def __init__(self, db: Session):
        self.perfil_repo = PerfilRepository(db)
        self.contenido_repo = ContenidoRepository(db)

    def add(self, perfil_id: int, contenido_id: int) -> list[ContenidoResponseDTO]: # Agrega a lista
        perfil = self.perfil_repo.find_by_id(perfil_id)
        contenido = self.contenido_repo.find_by_id(contenido_id)
        if not perfil: raise NotFoundError("Perfil no encontrado")
        if not contenido: raise NotFoundError("Contenido no encontrado")
        if perfil.es_infantil and contenido.clasificacion_edad != "ATP": # Control parental
            raise ForbiddenError("El perfil infantil no puede agregar este contenido")

        perfil = self.perfil_repo.add_to_mi_lista(perfil_id, contenido_id)
        return to_contenido_response_list(perfil.mi_lista)

    def remove(self, perfil_id: int, contenido_id: int) -> list[ContenidoResponseDTO]: # Quita de lista
        perfil = self.perfil_repo.remove_from_mi_lista(perfil_id, contenido_id)
        if not perfil: raise NotFoundError("Perfil no encontrado")
        return to_contenido_response_list(perfil.mi_lista)

    def list(self, perfil_id: int) -> list[ContenidoResponseDTO]: # Lista favoritos
        perfil = self.perfil_repo.find_by_id(perfil_id)
        if not perfil: raise NotFoundError("Perfil no encontrado")
        contenidos = self.perfil_repo.get_mi_lista(perfil_id)
        if perfil.es_infantil:                                  # Filtra si es perfil niño
            contenidos = [c for c in contenidos if c.clasificacion_edad == "ATP"]
        return to_contenido_response_list(contenidos)


class CalificacionService:                                       # Servicio para Calificaciones
    def __init__(self, db: Session):
        self.perfil_repo = PerfilRepository(db)
        self.contenido_repo = ContenidoRepository(db)
        self.calificacion_repo = CalificacionRepository(db)
        self.vista_repo = VistaRepository(db)

    def create_or_update(self, dto: CreateCalificacionDTO) -> CalificacionResponseDTO: # Califica contenido
        if not self.perfil_repo.find_by_id(dto.perfil_id): raise NotFoundError("Perfil no encontrado")
        if not self.contenido_repo.find_by_id(dto.contenido_id): raise NotFoundError("Contenido no encontrado")

        vistas = self.vista_repo.list_by_perfil(dto.perfil_id)  # Valida que haya empezado a verlo
        empezo = any(v.episodio.temporada.contenido_id == dto.contenido_id and v.segundos_vistos > 0 for v in vistas)
        if not empezo: raise ConflictError("Solo se puede calificar contenido empezado")

        calif = self.calificacion_repo.create_or_update(        # Persiste calif (1-5 estrellas)
            perfil_id=dto.perfil_id, contenido_id=dto.contenido_id, puntaje=dto.puntaje
        )
        return to_calificacion_response(calif)
