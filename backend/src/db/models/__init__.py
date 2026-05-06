from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Table, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.connection import Base

# ============================================================================
# ENTIDADES PRINCIPALES
# ============================================================================

class Cuenta(Base):
    __tablename__ = "cuentas"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    plan = Column(String, nullable=False)  # basico, estandar, premium
    pin = Column(String, nullable=True)  # PIN de 4 dígitos
    fecha_alta = Column(DateTime, server_default=func.now())
    
    # Relaciones
    perfiles = relationship("Perfil", back_populates="cuenta", cascade="all, delete-orphan")


class Perfil(Base):
    __tablename__ = "perfiles"
    
    id = Column(Integer, primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    es_infantil = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    
    # Relaciones
    cuenta = relationship("Cuenta", back_populates="perfiles")
    vistas = relationship("Vista", back_populates="perfil", cascade="all, delete-orphan")
    calificaciones = relationship("Calificacion", back_populates="perfil", cascade="all, delete-orphan")
    mi_lista = relationship("Contenido", secondary="mi_lista", back_populates="en_listas")


class Genero(Base):
    __tablename__ = "generos"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    
    # Relaciones
    contenidos = relationship("Contenido", secondary="contenido_generos", back_populates="generos")


class Contenido(Base):
    __tablename__ = "contenidos"
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # pelicula, serie
    anio = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=True)
    duracion_min = Column(Integer, nullable=True)  # para películas
    clasificacion_edad = Column(String, nullable=False)  # ATP, +13, +16, +18
    
    # Relaciones
    generos = relationship("Genero", secondary="contenido_generos", back_populates="contenidos")
    temporadas = relationship("Temporada", back_populates="contenido", cascade="all, delete-orphan")
    calificaciones = relationship("Calificacion", back_populates="contenido", cascade="all, delete-orphan")
    en_listas = relationship("Perfil", secondary="mi_lista", back_populates="mi_lista")


class Temporada(Base):
    __tablename__ = "temporadas"
    
    id = Column(Integer, primary_key=True)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    
    # Relaciones
    contenido = relationship("Contenido", back_populates="temporadas")
    episodios = relationship("Episodio", back_populates="temporada", cascade="all, delete-orphan")


class Episodio(Base):
    __tablename__ = "episodios"
    
    id = Column(Integer, primary_key=True)
    temporada_id = Column(Integer, ForeignKey("temporadas.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    titulo = Column(String, nullable=False)
    duracion_min = Column(Integer, nullable=False)
    
    # Relaciones
    temporada = relationship("Temporada", back_populates="episodios")
    vistas = relationship("Vista", back_populates="episodio", cascade="all, delete-orphan")


class Vista(Base):
    __tablename__ = "vistas"
    
    id = Column(Integer, primary_key=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id"), nullable=False)
    episodio_id = Column(Integer, ForeignKey("episodios.id"), nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    segundos_vistos = Column(Integer, default=0)
    terminado = Column(Boolean, default=False)
    
    # Relaciones
    perfil = relationship("Perfil", back_populates="vistas")
    episodio = relationship("Episodio", back_populates="vistas")


class Calificacion(Base):
    __tablename__ = "calificaciones"
    
    id = Column(Integer, primary_key=True)
    perfil_id = Column(Integer, ForeignKey("perfiles.id"), nullable=False)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=False)
    puntaje = Column(Integer, nullable=False)  # 1-5
    fecha = Column(DateTime, server_default=func.now())
    
    # Relaciones
    perfil = relationship("Perfil", back_populates="calificaciones")
    contenido = relationship("Contenido", back_populates="calificaciones")


# ============================================================================
# RELACIONES N a M
# ============================================================================

contenido_generos = Table(
    "contenido_generos",
    Base.metadata,
    Column("contenido_id", Integer, ForeignKey("contenidos.id"), primary_key=True),
    Column("genero_id", Integer, ForeignKey("generos.id"), primary_key=True),
)

mi_lista = Table(
    "mi_lista",
    Base.metadata,
    Column("perfil_id", Integer, ForeignKey("perfiles.id"), primary_key=True),
    Column("contenido_id", Integer, ForeignKey("contenidos.id"), primary_key=True),
    Column("fecha_agregada", DateTime, server_default=func.now()),
)


# ============================================================================
# EXPORTS (para que sea fácil importar desde cualquier lado)
# ============================================================================

__all__ = [
    "Cuenta",
    "Perfil",
    "Genero",
    "Contenido",
    "Temporada",
    "Episodio",
    "Vista",
    "Calificacion",
    "contenido_generos",
    "mi_lista",
]