from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Table, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.connection import Base

# ============================================================================
# ENTIDADES PRINCIPALES
# ============================================================================

class Cuenta(Base):
    __tablename__ = "cuentas"                                   # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)                      # ID único de la cuenta (clave primaria)
    email = Column(String, unique=True, nullable=False)         # Email del usuario (único y obligatorio)
    plan = Column(String, nullable=False)                       # Tipo de plan (basico, estandar, premium)
    pin = Column(String, nullable=True)                         # PIN opcional de 4 dígitos
    fecha_alta = Column(DateTime, server_default=func.now())    # Fecha de creación automática
    
    perfiles = relationship("Perfil", back_populates="cuenta", cascade="all, delete-orphan")
    # Relación con la tabla Perfil
    # Vincula con el atributo "cuenta" en Perfil
    # Elimina perfiles si se borra la cuenta

class Perfil(Base):
    __tablename__ = "perfiles"                         # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único del perfil (clave primaria)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)  # Foreign Key que vincula con la tabla cuentas
    nombre = Column(String, nullable=False)            # Nombre del perfil
    es_infantil = Column(Boolean, default=False)       # Indica si es un perfil infantil
    avatar = Column(String, nullable=True)             # URL o referencia del avatar (opcional -> nullable)
    
    # Relaciones
    cuenta = relationship("Cuenta", back_populates="perfiles")  # Relación con Cuenta (muchos perfiles → una cuenta)
    vistas = relationship("Vista", back_populates="perfil", cascade="all, delete-orphan")  # Historial de vistas del perfil
    calificaciones = relationship("Calificacion", back_populates="perfil", cascade="all, delete-orphan")  
    # Ratings dados por el perfil
    mi_lista = relationship("Contenido", secondary="mi_lista", back_populates="en_listas")  # Lista personalizada de contenidos


class Genero(Base):
    __tablename__ = "generos"                          # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único del género (clave primaria)
    nombre = Column(String, unique=True, nullable=False)  # Nombre del género (único y obligatorio)
    
    # Relaciones
    contenidos = relationship("Contenido", secondary="contenido_generos", back_populates="generos")  
    # Relación muchos a muchos con Contenido mediante tabla intermedia


class Contenido(Base):
    __tablename__ = "contenidos"                       # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único del contenido (clave primaria)
    titulo = Column(String, nullable=False)            # Título del contenido
    tipo = Column(String, nullable=False)              # Tipo de contenido (pelicula, serie)
    anio = Column(Integer, nullable=False)             # Año de lanzamiento
    descripcion = Column(String, nullable=True)        # Descripción del contenido (opcional)
    duracion_min = Column(Integer, nullable=True)      # Duración en minutos (solo para películas)
    clasificacion_edad = Column(String, nullable=False)  # Clasificación por edad (ATP, +13, +16, +18)
    
    # Relaciones
    generos = relationship("Genero", secondary="contenido_generos", back_populates="contenidos")  
    # Relación muchos a muchos con Género
    temporadas = relationship("Temporada", back_populates="contenido", cascade="all, delete-orphan")  
    # Temporadas asociadas (solo series)
    calificaciones = relationship("Calificacion", back_populates="contenido", cascade="all, delete-orphan")  
    # Calificaciones recibidas
    en_listas = relationship("Perfil", secondary="mi_lista", back_populates="mi_lista")  
    # Perfiles que agregaron este contenido a su lista


class Temporada(Base):
    __tablename__ = "temporadas"                       # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único de la temporada (clave primaria)
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=False)  # Foreign Key que vincula con Contenido
    numero = Column(Integer, nullable=False)           # Número de la temporada (ej: 1, 2, 3...)
    anio = Column(Integer, nullable=False)             # Año de lanzamiento de la temporada
    
    # Relaciones
    contenido = relationship("Contenido", back_populates="temporadas")  
    # Relación con Contenido (muchas temporadas → un contenido)
    episodios = relationship("Episodio", back_populates="temporada", cascade="all, delete-orphan")  
    # Episodios asociados a la temporada


class Episodio(Base):
    __tablename__ = "episodios"                        # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único del episodio (clave primaria)
    temporada_id = Column(Integer, ForeignKey("temporadas.id"), nullable=False)  # Foreign Key que vincula con Temporada
    numero = Column(Integer, nullable=False)           # Número del episodio dentro de la temporada
    titulo = Column(String, nullable=False)            # Título del episodio
    duracion_min = Column(Integer, nullable=False)     # Duración del episodio en minutos
    
    # Relaciones
    temporada = relationship("Temporada", back_populates="episodios")  
    # Relación con Temporada (muchos episodios → una temporada)
    vistas = relationship("Vista", back_populates="episodio", cascade="all, delete-orphan")  
    # Registros de visualización del episodio


class Vista(Base):
    __tablename__ = "vistas"                           # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único de la vista (clave primaria)
    perfil_id = Column(Integer, ForeignKey("perfiles.id"), nullable=False)  # Foreign Key que vincula con Perfil
    episodio_id = Column(Integer, ForeignKey("episodios.id"), nullable=False)  # Foreign Key que vincula con Episodio
    fecha = Column(DateTime, server_default=func.now())  # Fecha y hora de la visualización (automática)
    segundos_vistos = Column(Integer, default=0)       # Cantidad de segundos reproducidos
    terminado = Column(Boolean, default=False)         # Indica si el episodio fue visto completamente
    
    # Relaciones
    perfil = relationship("Perfil", back_populates="vistas")  
    # Relación con Perfil (muchas vistas → un perfil)
    episodio = relationship("Episodio", back_populates="vistas")  
    # Relación con Episodio (muchas vistas → un episodio)


class Calificacion(Base):
    __tablename__ = "calificaciones"                   # Nombre de la tabla en la base de datos
    
    id = Column(Integer, primary_key=True)             # ID único de la calificación (clave primaria)
    perfil_id = Column(Integer, ForeignKey("perfiles.id"), nullable=False)  # Foreign Key que vincula con Perfil
    contenido_id = Column(Integer, ForeignKey("contenidos.id"), nullable=False)  # Foreign Key que vincula con Contenido
    puntaje = Column(Integer, nullable=False)          # Puntuación otorgada (escala de 1 a 5)
    fecha = Column(DateTime, server_default=func.now())  # Fecha en que se realizó la calificación
    
    # Relaciones
    perfil = relationship("Perfil", back_populates="calificaciones")  
    # Relación con Perfil (muchas calificaciones → un perfil)
    contenido = relationship("Contenido", back_populates="calificaciones")  
    # Relación con Contenido (muchas calificaciones → un contenido)


# ============================================================================
# RELACIONES N a M
# ============================================================================

contenido_generos = Table(
    "contenido_generos",                               # Nombre de la tabla intermedia
    Base.metadata,                                     # Metadata de SQLAlchemy
    Column("contenido_id", Integer, ForeignKey("contenidos.id"), primary_key=True),  # FK a Contenido (parte de PK compuesta)
    Column("genero_id", Integer, ForeignKey("generos.id"), primary_key=True),        # FK a Género (parte de PK compuesta)
)

mi_lista = Table(
    "mi_lista",                                        # Nombre de la tabla intermedia
    Base.metadata,                                     # Metadata de SQLAlchemy
    Column("perfil_id", Integer, ForeignKey("perfiles.id"), primary_key=True),       # FK a Perfil (parte de PK compuesta)
    Column("contenido_id", Integer, ForeignKey("contenidos.id"), primary_key=True),  # FK a Contenido (parte de PK compuesta)
    Column("fecha_agregada", DateTime, server_default=func.now()),  # Fecha en que se agregó a la lista
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