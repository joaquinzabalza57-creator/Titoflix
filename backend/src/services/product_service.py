from sqlalchemy.orm import Session                               # Importa la sesión de SQLAlchemy

from src.dtos.product_dto import (                               # Importa DTOs de Producto
    CalificacionResponseDTO,                                     # DTO para respuesta de Calificación
    ContenidoResponseDTO,                                        # DTO para respuesta de Contenido
    CreateCalificacionDTO,                                       # DTO para creación de Calificación
    CreateContenidoDTO,                                          # DTO para creación de Contenido
    CreateEpisodioDTO,                                           # DTO para creación de Episodio
    CreateTemporadaDTO,                                          # DTO para creación de Temporada
    CreateVistaDTO,                                              # DTO para creación de Vista
    EpisodioResponseDTO,                                         # DTO para respuesta de Episodio
    GeneroResponseDTO,                                           # DTO para respuesta de Género
    TemporadaResponseDTO,                                        # DTO para respuesta de Temporada
    UpdateContenidoDTO,                                          # DTO para actualización de Contenido
    VistaResponseDTO,                                            # DTO para respuesta de Vista
)
from src.mappers.product_mapper import (                      # Importa mappers de productos
    to_calificacion_response,                                 # Mapper de Calificación a DTO
    to_contenido_response,                                    # Mapper de Contenido a DTO
    to_contenido_response_list,                               # Mapper de lista de Contenidos a DTOs
    to_episodio_response,                                     # Mapper de Episodio a DTO
    to_genero_response,                                       # Mapper de Género a DTO
    to_genero_response_list,                                  # Mapper de lista de Géneros a DTOs
    to_temporada_response,                                    # Mapper de Temporada a DTO
    to_vista_response,                                        # Mapper de Vista a DTO
    to_vista_response_list,                                   # Mapper de lista de Vistas a DTOs
)
from src.repositories.product_repository import (             # Importa repositorios de producto
    CalificacionRepository,                                   # Repositorio de Calificaciones
    ContenidoRepository,                                      # Repositorio de Contenidos
    EpisodioRepository,                                       # Repositorio de Episodios
    GeneroRepository,                                         # Repositorio de Géneros
    TemporadaRepository,                                      # Repositorio de Temporadas
    VistaRepository,                                          # Repositorio de Vistas
)
from src.repositories.user_repository import PerfilRepository # Repositorio de Perfiles
from src.utils.errors import ConflictError, ForbiddenError, NotFoundError # Excepciones personalizadas


class GeneroService:                                            # Servicio para lógica de negocio de Géneros
    def __init__(self, db: Session):                            # Inicializa el servicio con sesión de BD
        self.genero_repo = GeneroRepository(db)                 # Instancia el repositorio de Géneros

    def create(self, nombre: str) -> GeneroResponseDTO:         # Crea un nuevo género
        genero = self.genero_repo.create(nombre)                # Persiste el género en la base de datos
        return to_genero_response(genero)                       # Retorna la respuesta mapeada

    def list_all(self) -> list[GeneroResponseDTO]:              # Obtiene listado de todos los géneros
        generos = self.genero_repo.list_all()                   # Consulta todos los registros
        return to_genero_response_list(generos)                 # Retorna la lista de respuestas mapeadas


class ContenidoService:                                         # Servicio para lógica de negocio de Contenidos
    def __init__(self, db: Session):                            # Inicializa repositorios requeridos
        self.contenido_repo = ContenidoRepository(db)           # Repositorio de Contenidos
        self.genero_repo = GeneroRepository(db)                 # Repositorio de Géneros
        self.perfil_repo = PerfilRepository(db)                 # Repositorio de Perfiles

    def create(self, dto: CreateContenidoDTO) -> ContenidoResponseDTO: # Crea un nuevo contenido
        if not dto.generos_ids:                                 # Valida asignación de géneros
            raise ConflictError("Cada contenido debe tener al menos un género")

        if dto.tipo == "pelicula" and dto.duracion_min is None: # Validación para películas
            raise ConflictError("Una película debe tener duración")

        if dto.tipo == "serie" and dto.duracion_min is not None: # Validación para series
            raise ConflictError("Una serie no debe tener duración directa")

        contenido = self.contenido_repo.create(                 # Persiste el contenido con sus relaciones
            titulo=dto.titulo,
            tipo=dto.tipo,
            anio=dto.anio,
            descripcion=dto.descripcion,
            duracion_min=dto.duracion_min,
            clasificacion_edad=dto.clasificacion_edad,
            generos_ids=dto.generos_ids,
        )

        return to_contenido_response(contenido)                 # Retorna respuesta mapeada

    def get_by_id(self, contenido_id: int) -> ContenidoResponseDTO: # Busca contenido por ID
        contenido = self.contenido_repo.find_by_id(contenido_id) # Consulta repositorio

        if not contenido:                                       # Valida existencia
            raise NotFoundError("Contenido no encontrado")

        return to_contenido_response(contenido)                 # Retorna respuesta mapeada

    def search(                                                 # Busca contenidos con filtros opcionales
        self,
        q: str | None = None,
        tipo: str | None = None,
        genero_id: int | None = None,
        perfil_id: int | None = None,
    ) -> list[ContenidoResponseDTO]:
        clasificacion_edad = None                               # Inicializa filtro de edad

        if perfil_id is not None:                               # Aplica filtro si se proporciona perfil
            perfil = self.perfil_repo.find_by_id(perfil_id)     # Busca perfil

            if not perfil:                                      # Valida existencia
                raise NotFoundError("Perfil no encontrado")

            if perfil.es_infantil:                              # Aplica restricción para perfil infantil
                clasificacion_edad = "ATP"

        contenidos = self.contenido_repo.search(                # Ejecuta búsqueda filtrada
            texto=q,
            tipo=tipo,
            genero_id=genero_id,
            clasificacion_edad=clasificacion_edad,
        )

        return to_contenido_response_list(contenidos)           # Retorna lista mapeada

    def update(self, contenido_id: int, dto: UpdateContenidoDTO) -> ContenidoResponseDTO: # Actualiza datos
        fields = dto.model_dump(exclude_unset=True)             # Filtra solo campos proporcionados

        contenido = self.contenido_repo.update(contenido_id, **fields) # Aplica cambios

        if not contenido:                                       # Valida existencia
            raise NotFoundError("Contenido no encontrado")

        return to_contenido_response(contenido)                 # Retorna contenido actualizado

    def delete(self, contenido_id: int) -> None:                # Elimina un contenido
        deleted = self.contenido_repo.delete(contenido_id)      # Ejecuta borrado

        if not deleted:                                         # Valida si existía
            raise NotFoundError("Contenido no encontrado")

    def top(self) -> list[ContenidoResponseDTO]:                # Obtiene top 10 contenidos populares
        contenidos = self.contenido_repo.top(limit=10)          # Consulta repositorio
        return to_contenido_response_list(contenidos)           # Retorna lista mapeada

class TemporadaService:                                         # Servicio para lógica de negocio de Temporadas
    def __init__(self, db: Session):                            # Inicializa repositorios requeridos
        self.contenido_repo = ContenidoRepository(db)           # Repositorio de Contenidos
        self.temporada_repo = TemporadaRepository(db)           # Repositorio de Temporadas

    def create(self, dto: CreateTemporadaDTO) -> TemporadaResponseDTO: # Crea una nueva temporada
        contenido = self.contenido_repo.find_by_id(dto.contenido_id) # Busca el contenido asociado

        if not contenido:                                       # Valida existencia del contenido
            raise NotFoundError("Contenido no encontrado")

        if contenido.tipo != "serie":                           # Asegura que sea una serie
            raise ConflictError("Solo las series pueden tener temporadas")

        temporada = self.temporada_repo.create(                 # Persiste la nueva temporada
            contenido_id=dto.contenido_id,
            numero=dto.numero,
            anio=dto.anio,
        )

        return to_temporada_response(temporada)                 # Retorna la respuesta mapeada

    def list_by_contenido(self, contenido_id: int) -> list[TemporadaResponseDTO]: # Lista temporadas por serie
        temporadas = self.temporada_repo.list_by_contenido(contenido_id) # Obtiene temporadas del repo
        return [to_temporada_response(temporada) for temporada in temporadas] # Mapea cada una a DTO


class EpisodioService:                                          # Servicio para lógica de negocio de Episodios
    def __init__(self, db: Session):                            # Inicializa repositorios requeridos
        self.temporada_repo = TemporadaRepository(db)           # Repositorio de Temporadas
        self.episodio_repo = EpisodioRepository(db)             # Repositorio de Episodios

    def create(self, dto: CreateEpisodioDTO) -> EpisodioResponseDTO: # Crea un nuevo episodio
        temporada = self.temporada_repo.find_by_id(dto.temporada_id) # Busca la temporada asociada

        if not temporada:                                       # Valida existencia de la temporada
            raise NotFoundError("Temporada no encontrada")

        episodio = self.episodio_repo.create(                   # Persiste el nuevo episodio
            temporada_id=dto.temporada_id,
            numero=dto.numero,
            titulo=dto.titulo,
            duracion_min=dto.duracion_min,
        )

        return to_episodio_response(episodio)                   # Retorna la respuesta mapeada

    def list_by_temporada(self, temporada_id: int) -> list[EpisodioResponseDTO]: # Lista episodios por temporada
        episodios = self.episodio_repo.list_by_temporada(temporada_id) # Obtiene episodios del repo
        return [to_episodio_response(episodio) for episodio in episodios] # Mapea cada uno a DTO

class VistaService:                                             # Servicio para lógica de negocio de Vistas
    def __init__(self, db: Session):                            # Inicializa repositorios requeridos
        self.perfil_repo = PerfilRepository(db)                 # Repositorio de Perfiles
        self.episodio_repo = EpisodioRepository(db)             # Repositorio de Episodios
        self.vista_repo = VistaRepository(db)                   # Repositorio de Vistas

    def create_or_update(self, dto: CreateVistaDTO) -> VistaResponseDTO: # Registra o actualiza el progreso
        perfil = self.perfil_repo.find_by_id(dto.perfil_id)     # Busca el perfil solicitante

        if not perfil:                                          # Valida que el perfil exista
            raise NotFoundError("Perfil no encontrado")

        episodio = self.episodio_repo.find_by_id(dto.episodio_id) # Busca el episodio asociado

        if not episodio:                                        # Valida que el episodio exista
            raise NotFoundError("Episodio no encontrado")

        contenido = episodio.temporada.contenido                # Obtiene contenido padre para validación

        if perfil.es_infantil and contenido.clasificacion_edad != "ATP": # Control parental
            raise ForbiddenError("El perfil infantil no puede ver este contenido")

        duracion_segundos = episodio.duracion_min * 60          # Convierte duración a segundos

        if dto.segundos_vistos > duracion_segundos:             # Valida consistencia de tiempo
            raise ConflictError("Los segundos vistos superan la duración")

        terminado = dto.terminado or dto.segundos_vistos >= duracion_segundos * 0.9 # Calcula si está finalizado

        vista = self.vista_repo.create_or_update(               # Persiste el avance en BD
            perfil_id=dto.perfil_id,
            episodio_id=dto.episodio_id,
            segundos_vistos=dto.segundos_vistos,
            terminado=terminado,
        )

        return to_vista_response(vista)                         # Retorna respuesta mapeada

    def continuar_viendo(self, perfil_id: int) -> list[VistaResponseDTO]: # Obtiene lista 'continuar viendo'
        perfil = self.perfil_repo.find_by_id(perfil_id)         # Verifica existencia del perfil

        if not perfil:                                          # Lanza error si no existe
            raise NotFoundError("Perfil no encontrado")

        vistas = self.vista_repo.continuar_viendo(perfil_id)[:10] # Obtiene las 10 vistas más recientes
        return to_vista_response_list(vistas)                   # Retorna lista de respuestas mapeadas


class MiListaService:                                         # Servicio para gestionar la lista de favoritos
    def __init__(self, db: Session):                          # Inicializa repositorios requeridos
        self.perfil_repo = PerfilRepository(db)               # Repositorio de Perfiles
        self.contenido_repo = ContenidoRepository(db)         # Repositorio de Contenidos

    def add(self, perfil_id: int, contenido_id: int) -> list[ContenidoResponseDTO]: # Agrega contenido a lista
        perfil = self.perfil_repo.find_by_id(perfil_id)       # Busca perfil
        contenido = self.contenido_repo.find_by_id(contenido_id) # Busca contenido

        if not perfil:                                        # Valida existencia de perfil
            raise NotFoundError("Perfil no encontrado")

        if not contenido:                                     # Valida existencia de contenido
            raise NotFoundError("Contenido no encontrado")

        if perfil.es_infantil and contenido.clasificacion_edad != "ATP": # Control parental
            raise ForbiddenError("El perfil infantil no puede agregar este contenido")

        perfil = self.perfil_repo.add_to_mi_lista(perfil_id, contenido_id) # Persiste relación en BD
        return to_contenido_response_list(perfil.mi_lista)    # Retorna la lista actualizada

    def remove(self, perfil_id: int, contenido_id: int) -> list[ContenidoResponseDTO]: # Elimina contenido de lista
        perfil = self.perfil_repo.remove_from_mi_lista(perfil_id, contenido_id) # Remueve relación de BD

        if not perfil:                                        # Valida si existe el perfil
            raise NotFoundError("Perfil no encontrado")

        return to_contenido_response_list(perfil.mi_lista)    # Retorna la lista actualizada

    def list(self, perfil_id: int) -> list[ContenidoResponseDTO]: # Lista contenidos de "Mi lista"
        perfil = self.perfil_repo.find_by_id(perfil_id)       # Busca perfil

        if not perfil:                                        # Valida existencia
            raise NotFoundError("Perfil no encontrado")

        contenidos = self.perfil_repo.get_mi_lista(perfil_id) # Consulta contenidos asociados

        if perfil.es_infantil:                                # Aplica filtro para perfiles infantiles
            contenidos = [
                contenido for contenido in contenidos
                if contenido.clasificacion_edad == "ATP"
            ]

        return to_contenido_response_list(contenidos)         # Retorna lista filtrada


class CalificacionService:                                      # Servicio para lógica de negocio de Calificaciones
    def __init__(self, db: Session):                            # Inicializa repositorios requeridos
        self.perfil_repo = PerfilRepository(db)                 # Repositorio de Perfiles
        self.contenido_repo = ContenidoRepository(db)           # Repositorio de Contenidos
        self.calificacion_repo = CalificacionRepository(db)     # Repositorio de Calificaciones
        self.vista_repo = VistaRepository(db)                   # Repositorio de Vistas

    def create_or_update(self, dto: CreateCalificacionDTO) -> CalificacionResponseDTO: # Crea o actualiza calificación
        perfil = self.perfil_repo.find_by_id(dto.perfil_id)     # Busca el perfil solicitante

        if not perfil:                                          # Valida que el perfil exista
            raise NotFoundError("Perfil no encontrado")

        contenido = self.contenido_repo.find_by_id(dto.contenido_id) # Busca el contenido a calificar

        if not contenido:                                       # Valida que el contenido exista
            raise NotFoundError("Contenido no encontrado")

        vistas = self.vista_repo.list_by_perfil(dto.perfil_id)  # Obtiene historial de vistas del perfil
        empezo_contenido = any(                                 # Verifica si el contenido fue iniciado
            vista.episodio.temporada.contenido_id == dto.contenido_id
            and vista.segundos_vistos > 0
            for vista in vistas
        )

        if not empezo_contenido:                                # Restricción: solo calificar lo ya visto
            raise ConflictError("Solo se puede calificar contenido empezado")

        calificacion = self.calificacion_repo.create_or_update( # Persiste o actualiza la calificación
            perfil_id=dto.perfil_id,
            contenido_id=dto.contenido_id,
            puntaje=dto.puntaje,
        )

        return to_calificacion_response(calificacion)           # Retorna respuesta mapeada
