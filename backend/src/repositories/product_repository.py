from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import Calificacion, Contenido, Episodio, Genero, Temporada, Vista


class GeneroRepository:
    # Repositorio para manejar operaciones relacionadas con géneros de contenido.
    def __init__(self, db: Session):
        self.db = db  # Guarda la sesión de base de datos para ejecutar consultas.

    def create(self, nombre: str) -> Genero:
        genero = Genero(nombre=nombre)  # Crea el objeto Genero en memoria.
        self.db.add(genero)
        self.db.commit()
        self.db.refresh(genero)
        return genero  # Devuelve el género persistido.

    def find_by_id(self, genero_id: int) -> Genero | None:
        return self.db.query(Genero).filter(Genero.id == genero_id).first()  # Busca un género por su id.

    def list_all(self) -> list[Genero]:
        return self.db.query(Genero).order_by(Genero.nombre).all()  # Devuelve todos los géneros ordenados por nombre.


class ContenidoRepository:
    # Repositorio para manejar operaciones relacionadas con contenidos (películas, series, etc.).
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        titulo: str,
        tipo: str,
        anio: int,
        clasificacion_edad: str,
        descripcion: str | None = None,
        duracion_min: int | None = None,
        generos_ids: list[int] | None = None,
    ) -> Contenido:
        contenido = Contenido(
            titulo=titulo,
            tipo=tipo,
            anio=anio,
            descripcion=descripcion,
            duracion_min=duracion_min,
            clasificacion_edad=clasificacion_edad,
        )  # Inicializa el contenido con los campos recibidos.

        if generos_ids:
            contenido.generos = (
                self.db.query(Genero)
                .filter(Genero.id.in_(generos_ids))
                .all()
            )  # Si hay ids de géneros, los carga y asocia al contenido.

        self.db.add(contenido)
        self.db.commit()
        self.db.refresh(contenido)
        return contenido  # Retorna el contenido recién creado.

    def find_by_id(self, contenido_id: int) -> Contenido | None:
        return self.db.query(Contenido).filter(Contenido.id == contenido_id).first()  # Busca contenido por id.

    def list_all(self) -> list[Contenido]:
        return self.db.query(Contenido).all()  # Lista todos los contenidos.

    def search(
        self,
        texto: str | None = None,
        tipo: str | None = None,
        genero_id: int | None = None,
        clasificacion_edad: str | None = None,
    ) -> list[Contenido]:
        query = self.db.query(Contenido)  # Inicia la consulta sobre el modelo Contenido.

        if texto:
            query = query.filter(Contenido.titulo.ilike(f"%{texto}%"))  # Filtra por texto en el título.

        if tipo:
            query = query.filter(Contenido.tipo == tipo)  # Filtra por tipo de contenido.

        if clasificacion_edad:
            query = query.filter(Contenido.clasificacion_edad == clasificacion_edad)  # Filtra por clasificación de edad.

        if genero_id:
            query = query.join(Contenido.generos).filter(Genero.id == genero_id)  # Filtra por género.

        return query.all()  # Ejecuta la consulta y devuelve los resultados.

    def top(self, limit: int = 10) -> list[Contenido]:
        return (
            self.db.query(Contenido)
            .join(Calificacion)
            .group_by(Contenido.id)
            .order_by(func.avg(Calificacion.puntaje).desc())
            .limit(limit)
            .all()
        )  # Devuelve los contenidos con mejor promedio de calificación.

    def update(self, contenido_id: int, **fields) -> Contenido | None:
        generos_ids = fields.pop("generos_ids", None)  # Extrae los géneros si se enviaron.
        contenido = self.find_by_id(contenido_id)

        if not contenido:
            return None  # Si no existe el contenido, retorna None.

        for key, value in fields.items():
            setattr(contenido, key, value)  # Actualiza dinámicamente los campos recibidos.

        if generos_ids is not None:
            contenido.generos = (
                self.db.query(Genero)
                .filter(Genero.id.in_(generos_ids))
                .all()
            )  # Reemplaza los géneros si se especificaron.

        self.db.commit()
        self.db.refresh(contenido)
        return contenido  # Retorna el contenido actualizado.

    def delete(self, contenido_id: int) -> bool:
        contenido = self.find_by_id(contenido_id)  # Busca el contenido a eliminar.
        if not contenido:
            return False  # Retorna False si no existe el contenido.

        self.db.delete(contenido)
        self.db.commit()
        return True  # Elimina y confirma la operación.


class TemporadaRepository:
    # Repositorio para manejar operaciones relacionadas con temporadas.
    def __init__(self, db: Session):
        self.db = db

    def create(self, contenido_id: int, numero: int, anio: int) -> Temporada:
        temporada = Temporada(contenido_id=contenido_id, numero=numero, anio=anio)  # Crea el objeto Temporada.
        self.db.add(temporada)
        self.db.commit()
        self.db.refresh(temporada)
        return temporada  # Devuelve la temporada persistida.

    def find_by_id(self, temporada_id: int) -> Temporada | None:
        return self.db.query(Temporada).filter(Temporada.id == temporada_id).first()  # Busca temporada por id.

    def list_by_contenido(self, contenido_id: int) -> list[Temporada]:
        return (
            self.db.query(Temporada)
            .filter(Temporada.contenido_id == contenido_id)
            .order_by(Temporada.numero)
            .all()
        )  # Lista temporadas de un contenido ordenadas por número.


class EpisodioRepository:
    # Repositorio para manejar operaciones relacionadas con episodios.
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        temporada_id: int,
        numero: int,
        titulo: str,
        duracion_min: int,
    ) -> Episodio:
        episodio = Episodio(
            temporada_id=temporada_id,
            numero=numero,
            titulo=titulo,
            duracion_min=duracion_min,
        )  # Crea el objeto Episodio con los datos recibidos.
        self.db.add(episodio)
        self.db.commit()
        self.db.refresh(episodio)
        return episodio  # Retorna el episodio creado.

    def find_by_id(self, episodio_id: int) -> Episodio | None:
        return self.db.query(Episodio).filter(Episodio.id == episodio_id).first()  # Busca episodio por id.

    def list_by_temporada(self, temporada_id: int) -> list[Episodio]:
        return (
            self.db.query(Episodio)
            .filter(Episodio.temporada_id == temporada_id)
            .order_by(Episodio.numero)
            .all()
        )  # Lista episodios de una temporada ordenados por número.


class VistaRepository:
    # Repositorio para manejar vistas de perfiles sobre episodios.
    def __init__(self, db: Session):
        self.db = db

    def create_or_update(
        self,
        perfil_id: int,
        episodio_id: int,
        segundos_vistos: int,
        terminado: bool,
    ) -> Vista:
        vista = (
            self.db.query(Vista)
            .filter(
                Vista.perfil_id == perfil_id,
                Vista.episodio_id == episodio_id,
            )
            .first()
        )  # Busca si ya existe un registro de vista para ese perfil y episodio.

        if not vista:
            vista = Vista(perfil_id=perfil_id, episodio_id=episodio_id)  # Crea la vista si no existía.
            self.db.add(vista)

        vista.segundos_vistos = segundos_vistos  # Actualiza el avance en segundos.
        vista.terminado = terminado  # Marca si el episodio quedó terminado.

        self.db.commit()
        self.db.refresh(vista)
        return vista  # Retorna la vista creada o actualizada.

    def list_by_perfil(self, perfil_id: int) -> list[Vista]:
        return (
            self.db.query(Vista)
            .filter(Vista.perfil_id == perfil_id)
            .order_by(Vista.fecha.desc())
            .all()
        )  # Lista todas las vistas de un perfil por fecha descendente.

    def continuar_viendo(self, perfil_id: int) -> list[Vista]:
        return (
            self.db.query(Vista)
            .filter(
                Vista.perfil_id == perfil_id,
                Vista.terminado == False,
                Vista.segundos_vistos > 0,
            )
            .order_by(Vista.fecha.desc())
            .all()
        )  # Devuelve los episodios en progreso para continuar viendo.


class CalificacionRepository:
    # Repositorio para manejar calificaciones de contenidos.
    def __init__(self, db: Session):
        self.db = db

    def create_or_update(
        self,
        perfil_id: int,
        contenido_id: int,
        puntaje: int,
    ) -> Calificacion:
        calificacion = (
            self.db.query(Calificacion)
            .filter(
                Calificacion.perfil_id == perfil_id,
                Calificacion.contenido_id == contenido_id,
            )
            .first()
        )  # Busca si ya existe una calificación para ese perfil y contenido.

        if not calificacion:
            calificacion = Calificacion(
                perfil_id=perfil_id,
                contenido_id=contenido_id,
            )  # Crea la calificación si no existía.
            self.db.add(calificacion)

        calificacion.puntaje = puntaje  # Asigna el puntaje recibido.

        self.db.commit()
        self.db.refresh(calificacion)
        return calificacion  # Retorna la calificación creada o actualizada.

    def list_by_contenido(self, contenido_id: int) -> list[Calificacion]:
        return (
            self.db.query(Calificacion)
            .filter(Calificacion.contenido_id == contenido_id)
            .all()
        )  # Lista todas las calificaciones de un contenido.

    def list_by_perfil(self, perfil_id: int) -> list[Calificacion]:
        return (
            self.db.query(Calificacion)
            .filter(Calificacion.perfil_id == perfil_id)
            .all()
        )  # Lista todas las calificaciones hechas por un perfil.
