from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.connection import Base


# Tabla puente N:M entre contenidos y generos del catalogo.
contenido_generos = Table(
    "contenido_generos",
    Base.metadata,
    Column("contenido_id", Integer, ForeignKey("contenidos.id"), primary_key=True),
    Column("genero_id", Integer, ForeignKey("generos.id"), primary_key=True),
)


# Tabla puente N:M para "Mi lista" por perfil, con fecha de agregado.
mi_lista = Table(
    "mi_lista",
    Base.metadata,
    Column("perfil_id", Integer, ForeignKey("perfiles.id"), primary_key=True),
    Column("contenido_id", Integer, ForeignKey("contenidos.id"), primary_key=True),
    Column("fecha_agregada", DateTime, server_default=func.now()),
)


class Genero(Base):
    """Categoria editorial usada para filtrar y agrupar contenidos."""

    __tablename__ = "generos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

    contenidos = relationship(
        "Contenido",
        secondary=contenido_generos,
        back_populates="generos",
    )


class Contenido(Base):
    """Pelicula o serie visible en el catalogo principal."""

    __tablename__ = "contenidos"

    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=True)
    duracion_min = Column(Float, nullable=True)
    clasificacion_edad = Column(String, nullable=False)
    # Metadatos de storage: Postgres guarda referencias, MinIO guarda los bytes.
    storage_folder_id = Column(String, nullable=True)
    video_storage_key = Column(String, nullable=True)
    video_mime = Column(String, nullable=True)
    video_size = Column(BigInteger, nullable=True)
    portada_url = Column(String, nullable=True)

    generos = relationship(
        "Genero",
        secondary=contenido_generos,
        back_populates="contenidos",
    )
    temporadas = relationship(
        "Temporada",
        back_populates="contenido",
        cascade="all, delete-orphan",
    )
    vistas = relationship(
        "Vista",
        back_populates="contenido",
        cascade="all, delete-orphan",
    )
    calificaciones = relationship(
        "Calificacion",
        back_populates="contenido",
        cascade="all, delete-orphan",
    )
    en_listas = relationship(
        "Perfil",
        secondary=mi_lista,
        back_populates="mi_lista",
    )
    video_variants = relationship(
        "VideoVariant",
        back_populates="contenido",
        cascade="all, delete-orphan",
    )


class Temporada(Base):
    """Agrupa episodios de una serie."""

    __tablename__ = "temporadas"

    id = Column(Integer, primary_key=True)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    storage_folder_id = Column(String, nullable=True)

    contenido = relationship("Contenido", back_populates="temporadas")
    episodios = relationship(
        "Episodio",
        back_populates="temporada",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("contenido_id", "numero", name="uq_temporada_numero_por_contenido"),
    )


class Episodio(Base):
    """Unidad reproducible de una temporada."""

    __tablename__ = "episodios"

    id = Column(Integer, primary_key=True)
    temporada_id = Column(Integer, ForeignKey("temporadas.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    titulo = Column(String, nullable=False)
    duracion_min = Column(Float, nullable=False)
    storage_folder_id = Column(String, nullable=True)
    video_storage_key = Column(String, nullable=True)
    video_mime = Column(String, nullable=True)
    video_size = Column(BigInteger, nullable=True)
    thumbnail_url = Column(String, nullable=True)

    temporada = relationship("Temporada", back_populates="episodios")
    vistas = relationship("Vista", back_populates="episodio", cascade="all, delete-orphan")
    video_variants = relationship(
        "VideoVariant",
        back_populates="episodio",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("temporada_id", "numero", name="uq_episodio_numero_por_temporada"),
    )


class VideoVariant(Base):
    """Version transcodificada de un video en una calidad concreta."""

    __tablename__ = "video_variants"

    id = Column(Integer, primary_key=True)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=True)
    episodio_id = Column(Integer, ForeignKey("episodios.id"), nullable=True)
    quality = Column(String, nullable=False)
    video_storage_key = Column(String, nullable=False)
    video_mime = Column(String, nullable=True)
    video_size = Column(BigInteger, nullable=True)

    contenido = relationship("Contenido", back_populates="video_variants")
    episodio = relationship("Episodio", back_populates="video_variants")

    __table_args__ = (
        UniqueConstraint("contenido_id", "quality", name="uq_video_variant_contenido_quality"),
        UniqueConstraint("episodio_id", "quality", name="uq_video_variant_episodio_quality"),
        CheckConstraint(
            # Una variante pertenece a una pelicula o a un episodio, nunca a ambos.
            "(contenido_id IS NOT NULL AND episodio_id IS NULL) OR "
            "(contenido_id IS NULL AND episodio_id IS NOT NULL)",
            name="ck_video_variant_un_solo_recurso",
        ),
        CheckConstraint("quality IN ('FHD', 'QHD', '4K')", name="ck_video_variant_quality"),
    )


class Vista(Base):
    """Progreso de reproduccion de un perfil sobre una pelicula o episodio."""

    __tablename__ = "vistas"

    id = Column(Integer, primary_key=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id"), nullable=False)
    episodio_id = Column(Integer, ForeignKey("episodios.id"), nullable=True)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=True)
    fecha = Column(DateTime, server_default=func.now())
    segundos_vistos = Column(Integer, default=0)
    terminado = Column(Boolean, default=False)

    perfil = relationship("Perfil", back_populates="vistas")
    episodio = relationship("Episodio", back_populates="vistas")
    contenido = relationship("Contenido", back_populates="vistas")

    __table_args__ = (
        UniqueConstraint("perfil_id", "episodio_id", name="uq_vista_perfil_episodio"),
        UniqueConstraint("perfil_id", "contenido_id", name="uq_vista_perfil_contenido"),
        CheckConstraint(
            # Una vista registra pelicula directa o episodio, no los dos a la vez.
            "(episodio_id IS NOT NULL AND contenido_id IS NULL) OR "
            "(episodio_id IS NULL AND contenido_id IS NOT NULL)",
            name="ck_vista_un_solo_recurso",
        ),
    )


class Calificacion(Base):
    """Puntaje dado por un perfil a un contenido."""

    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id"), nullable=False)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=False)
    puntaje = Column(Integer, nullable=False)
    fecha = Column(DateTime, server_default=func.now())

    perfil = relationship("Perfil", back_populates="calificaciones")
    contenido = relationship("Contenido", back_populates="calificaciones")

    __table_args__ = (
        UniqueConstraint("perfil_id", "contenido_id", name="uq_calificacion_perfil_contenido"),
    )
