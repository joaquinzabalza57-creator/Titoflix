from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from src.db import Calificacion, Contenido, Episodio, Genero, Temporada, Vista


class GeneroRepository:
<<<<<<< HEAD
                                                                            # Repositorio para manejar operaciones relacionadas con géneros de contenido.
    def __init__(self, db: Session):
        self.db = db                                                        # Guarda la sesión de base de datos para ejecutar consultas.

    def create(self, nombre: str) -> Genero:
        genero = Genero(nombre=nombre)                                      # Crea el objeto Genero en memoria.
        self.db.add(genero)
        self.db.commit()
        self.db.refresh(genero)
        return genero                                                       # Devuelve el género persistido.

    def find_by_id(self, genero_id: int) -> Genero | None:
        return self.db.query(Genero).filter(Genero.id == genero_id).first() # Busca un género por su id.

    def list_all(self) -> list[Genero]:
        return self.db.query(Genero).order_by(Genero.nombre).all()          # Devuelve todos los géneros ordenados por nombre.


class ContenidoRepository:
                                                                            # Repositorio para manejar operaciones relacionadas con contenidos (películas, series, etc.).
=======
    def __init__(self, db: Session):
        self.db = db

    def create(self, nombre: str) -> Genero:
        genero = Genero(nombre=nombre)
        self.db.add(genero)
        self.db.commit()
        self.db.refresh(genero)
        return genero

    def find_by_id(self, genero_id: int) -> Genero | None:
        return self.db.query(Genero).filter(Genero.id == genero_id).first()

    def find_by_name(self, nombre: str) -> Genero | None:
        return self.db.query(Genero).filter(func.lower(Genero.nombre) == nombre.lower()).first()

    def list_all(self) -> list[Genero]:
        return self.db.query(Genero).order_by(Genero.nombre).all()


class ContenidoRepository:
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
    def __init__(self, db: Session):
        self.db = db

    def create(                                                             # Crea un nuevo contenido con los datos recibidos y lo persiste en la base de datos.
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
<<<<<<< HEAD
        )                                                                   # Inicializa el contenido con los campos recibidos.

        if generos_ids:
            contenido.generos = (
                self.db.query(Genero)
                .filter(Genero.id.in_(generos_ids))
                .all()
            )                                                               # Si hay ids de géneros, los carga y asocia al contenido.
=======
        )

        if generos_ids:
            contenido.generos = self.db.query(Genero).filter(Genero.id.in_(generos_ids)).all()
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

        self.db.add(contenido)
        self.db.commit()
        self.db.refresh(contenido)
<<<<<<< HEAD
        return contenido                                                    # Retorna el contenido recién creado.

    def find_by_id(self, contenido_id: int) -> Contenido | None:
        return self.db.query(Contenido).filter(Contenido.id == contenido_id).first() # Busca contenido por id.

    def list_all(self) -> list[Contenido]:
        return self.db.query(Contenido).all()                               # Lista todos los contenidos.
=======
        return contenido

    def find_by_id(self, contenido_id: int) -> Contenido | None:
        return self.db.query(Contenido).filter(Contenido.id == contenido_id).first()

    def list_all(self) -> list[Contenido]:
        return self.db.query(Contenido).all()
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

    def search(
        self,
        texto: str | None = None,
        tipo: str | None = None,
        genero_id: int | None = None,
        genero: str | None = None,
        clasificacion_edad: str | None = None,
        ordenar: str | None = None,
    ) -> list[Contenido]:
<<<<<<< HEAD
        query = self.db.query(Contenido)                                    # Inicia la consulta sobre el modelo Contenido.

        if texto:
            query = query.filter(Contenido.titulo.ilike(f"%{texto}%"))      # Filtra por texto en el título.

        if tipo:
            query = query.filter(Contenido.tipo == tipo)                    # Filtra por tipo de contenido.
=======
        query = self.db.query(Contenido)

        if texto:
            query = query.filter(Contenido.titulo.ilike(f"%{texto}%"))

        if tipo:
            query = query.filter(Contenido.tipo == tipo)
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

        if clasificacion_edad:
            query = query.filter(Contenido.clasificacion_edad == clasificacion_edad)

        if genero_id:
            query = query.join(Contenido.generos).filter(Genero.id == genero_id)
        elif genero:
            query = query.join(Contenido.generos).filter(Genero.nombre.ilike(genero))

<<<<<<< HEAD
        return query.all()                                                  # Ejecuta la consulta y devuelve los resultados.
=======
        if ordenar == "anio_desc":
            query = query.order_by(Contenido.anio.desc(), Contenido.titulo.asc())
        else:
            query = query.order_by(Contenido.titulo.asc())
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

        return query.all()

    def top(self, limit: int = 10, genero: str | None = None) -> list[Contenido]:
        vista_contenido = aliased(Vista)
        vista_episodio = aliased(Vista)
        total_vistas = (
            func.count(func.distinct(vista_contenido.id))
            + func.count(func.distinct(vista_episodio.id))
        )

        query = (
            self.db.query(Contenido)
            .outerjoin(vista_contenido, vista_contenido.contenido_id == Contenido.id)
            .outerjoin(Temporada, Temporada.contenido_id == Contenido.id)
            .outerjoin(Episodio, Episodio.temporada_id == Temporada.id)
            .outerjoin(vista_episodio, vista_episodio.episodio_id == Episodio.id)
            .filter(
                (vista_contenido.terminado.is_(True))
                | (vista_episodio.terminado.is_(True))
            )
        )

        if genero:
            query = query.join(Contenido.generos).filter(Genero.nombre.ilike(genero))

        return (
            query.group_by(Contenido.id)
            .order_by(total_vistas.desc(), Contenido.titulo.asc())
            .limit(limit)
            .all()
<<<<<<< HEAD
        )                                                                   # Devuelve los contenidos con mejor promedio de calificación.

    def update(self, contenido_id: int, **fields) -> Contenido | None:
        generos_ids = fields.pop("generos_ids", None)                       # Extrae los géneros si se enviaron.
=======
        )

    def update(self, contenido_id: int, **fields) -> Contenido | None:
        generos_ids = fields.pop("generos_ids", None)
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
        contenido = self.find_by_id(contenido_id)
        if not contenido:
<<<<<<< HEAD
            return None                                                     # Si no existe el contenido, retorna None.

        for key, value in fields.items():
            setattr(contenido, key, value)                                  # Actualiza dinámicamente los campos recibidos.

        if generos_ids is not None:
            contenido.generos = (
                self.db.query(Genero)
                .filter(Genero.id.in_(generos_ids))
                .all()
            )                                                               # Reemplaza los géneros si se especificaron.

        self.db.commit()
        self.db.refresh(contenido)
        return contenido                                                    # Retorna el contenido actualizado.

    def delete(self, contenido_id: int) -> bool:
        contenido = self.find_by_id(contenido_id)                           # Busca el contenido a eliminar.
        if not contenido:
            return False                                                    # Retorna False si no existe el contenido.

        self.db.delete(contenido)
        self.db.commit()
        return True                                                         # Elimina y confirma la operación.


class TemporadaRepository:
                                                                            # Repositorio para manejar operaciones relacionadas con temporadas.
=======
            return None

        for key, value in fields.items():
            setattr(contenido, key, value)

        if generos_ids is not None:
            contenido.generos = self.db.query(Genero).filter(Genero.id.in_(generos_ids)).all()

        self.db.commit()
        self.db.refresh(contenido)
        return contenido

    def delete(self, contenido_id: int) -> bool:
        contenido = self.find_by_id(contenido_id)
        if not contenido:
            return False

        self.db.delete(contenido)
        self.db.commit()
        return True


class TemporadaRepository:
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
    def __init__(self, db: Session):
        self.db = db

    def create(self, contenido_id: int, numero: int, anio: int) -> Temporada:
        temporada = Temporada(contenido_id=contenido_id, numero=numero, anio=anio)
        self.db.add(temporada)
        self.db.commit()
        self.db.refresh(temporada)
<<<<<<< HEAD
        return temporada                                                    # Devuelve la temporada persistida.
=======
        return temporada
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

    def find_by_id(self, temporada_id: int) -> Temporada | None:
        return self.db.query(Temporada).filter(Temporada.id == temporada_id).first()

    def list_by_contenido(self, contenido_id: int) -> list[Temporada]:
        return (
            self.db.query(Temporada)
            .filter(Temporada.contenido_id == contenido_id)
            .order_by(Temporada.numero)
            .all()
<<<<<<< HEAD
        )                                                                   # Lista temporadas de un contenido ordenadas por número.


class EpisodioRepository:
                                                                            # Repositorio para manejar operaciones relacionadas con episodios.
=======
        )


class EpisodioRepository:
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
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
<<<<<<< HEAD
        )                                                                   # Crea el objeto Episodio con los datos recibidos.
        self.db.add(episodio)
        self.db.commit()
        self.db.refresh(episodio)
        return episodio                                                     # Retorna el episodio creado.
=======
        )
        self.db.add(episodio)
        self.db.commit()
        self.db.refresh(episodio)
        return episodio
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

    def find_by_id(self, episodio_id: int) -> Episodio | None:
        return self.db.query(Episodio).filter(Episodio.id == episodio_id).first()

    def list_by_temporada(self, temporada_id: int) -> list[Episodio]:
        return (
            self.db.query(Episodio)
            .filter(Episodio.temporada_id == temporada_id)
            .order_by(Episodio.numero)
            .all()
<<<<<<< HEAD
        )                                                                   # Lista episodios de una temporada ordenados por número.


class VistaRepository:
                                                                            # Repositorio para manejar vistas de perfiles sobre episodios.
=======
        )


class VistaRepository:
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
    def __init__(self, db: Session):
        self.db = db

    def find_by_perfil_and_episodio(self, perfil_id: int, episodio_id: int) -> Vista | None:
        return (
            self.db.query(Vista)
            .filter(Vista.perfil_id == perfil_id, Vista.episodio_id == episodio_id)
            .first()
        )

    def find_by_perfil_and_contenido(self, perfil_id: int, contenido_id: int) -> Vista | None:
        return (
            self.db.query(Vista)
            .filter(Vista.perfil_id == perfil_id, Vista.contenido_id == contenido_id)
            .first()
        )

    def find_existing(
        self,
        perfil_id: int,
        episodio_id: int | None = None,
        contenido_id: int | None = None,
    ) -> Vista | None:
        if episodio_id is not None:
            return self.find_by_perfil_and_episodio(perfil_id, episodio_id)

        if contenido_id is not None:
            return self.find_by_perfil_and_contenido(perfil_id, contenido_id)

        return None

    def create_or_update(
        self,
        perfil_id: int,
        segundos_vistos: int,
        terminado: bool,
        episodio_id: int | None = None,
        contenido_id: int | None = None,
    ) -> Vista:
<<<<<<< HEAD
        vista = (
            self.db.query(Vista)
            .filter(
                Vista.perfil_id == perfil_id,
                Vista.episodio_id == episodio_id,
            )
            .first()
        )                                                                     # Busca si ya existe un registro de vista para ese perfil y episodio.

        if not vista:
            vista = Vista(perfil_id=perfil_id, episodio_id=episodio_id)       # Crea la vista si no existía.
            self.db.add(vista)

        vista.segundos_vistos = segundos_vistos                               # Actualiza el avance en segundos.
        vista.terminado = terminado                                           # Marca si el episodio quedó terminado.

        self.db.commit()
        self.db.refresh(vista)
        return vista                                                          # Retorna la vista creada o actualizada.
=======
        vista = self.find_existing(
            perfil_id=perfil_id,
            episodio_id=episodio_id,
            contenido_id=contenido_id,
        )

        if not vista:
            vista = Vista(
                perfil_id=perfil_id,
                episodio_id=episodio_id,
                contenido_id=contenido_id,
            )
            self.db.add(vista)

        vista.segundos_vistos = segundos_vistos
        vista.terminado = terminado

        self.db.commit()
        self.db.refresh(vista)
        return vista
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

    def list_by_perfil(self, perfil_id: int) -> list[Vista]:
        return (
            self.db.query(Vista)
            .filter(Vista.perfil_id == perfil_id)
            .order_by(Vista.fecha.desc())
            .all()
<<<<<<< HEAD
        )                                                                   # Lista todas las vistas de un perfil por fecha descendente.
=======
        )

    def delete(
        self,
        perfil_id: int,
        episodio_id: int | None = None,
        contenido_id: int | None = None,
    ) -> bool:
        vista = self.find_existing(
            perfil_id=perfil_id,
            episodio_id=episodio_id,
            contenido_id=contenido_id,
        )
        if not vista:
            return False

        self.db.delete(vista)
        self.db.commit()
        return True
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb

    def continuar_viendo(self, perfil_id: int) -> list[Vista]:
        return (
            self.db.query(Vista)
            .filter(
                Vista.perfil_id == perfil_id,
                Vista.terminado.is_(False),
                Vista.segundos_vistos > 0,
            )
            .order_by(Vista.fecha.desc())
            .all()
<<<<<<< HEAD
        )                                                                   # Devuelve los episodios en progreso para continuar viendo.


class CalificacionRepository:
                                                                            # Repositorio para manejar calificaciones de contenidos.
=======
        )


class CalificacionRepository:
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
    def __init__(self, db: Session):
        self.db = db

    def find_by_perfil_and_contenido(self, perfil_id: int, contenido_id: int) -> Calificacion | None:
        return (
            self.db.query(Calificacion)
            .filter(
                Calificacion.perfil_id == perfil_id,
                Calificacion.contenido_id == contenido_id,
            )
            .first()
        )

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
<<<<<<< HEAD
        )                                                                   # Busca si ya existe una calificación para ese perfil y contenido.

        if not calificacion:
            calificacion = Calificacion(
                perfil_id=perfil_id,
                contenido_id=contenido_id,
            )                                                               # Crea la calificación si no existía.
            self.db.add(calificacion)

        calificacion.puntaje = puntaje                                      # Asigna el puntaje recibido.

        self.db.commit()
        self.db.refresh(calificacion)
        return calificacion                                                 # Retorna la calificación creada o actualizada.

    def list_by_contenido(self, contenido_id: int) -> list[Calificacion]:
        return (
            self.db.query(Calificacion)
            .filter(Calificacion.contenido_id == contenido_id)
            .all()
        )                                                                   # Lista todas las calificaciones de un contenido.

    def list_by_perfil(self, perfil_id: int) -> list[Calificacion]:
        return (
            self.db.query(Calificacion)
            .filter(Calificacion.perfil_id == perfil_id)
            .all()
        )                                                                   # Lista todas las calificaciones hechas por un perfil.
=======
        )

        if not calificacion:
            calificacion = Calificacion(perfil_id=perfil_id, contenido_id=contenido_id)
            self.db.add(calificacion)

        calificacion.puntaje = puntaje

        self.db.commit()
        self.db.refresh(calificacion)
        return calificacion

    def list_by_contenido(self, contenido_id: int) -> list[Calificacion]:
        return self.db.query(Calificacion).filter(Calificacion.contenido_id == contenido_id).all()

    def list_by_perfil(self, perfil_id: int) -> list[Calificacion]:
        return self.db.query(Calificacion).filter(Calificacion.perfil_id == perfil_id).all()

    def delete(self, perfil_id: int, contenido_id: int) -> bool:
        calificacion = self.find_by_perfil_and_contenido(perfil_id, contenido_id)
        if not calificacion:
            return False

        self.db.delete(calificacion)
        self.db.commit()
        return True
>>>>>>> eada49f2c5a6a48b317fd04c6fbe8493836f04eb
