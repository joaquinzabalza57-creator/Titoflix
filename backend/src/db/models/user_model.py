from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.connection import Base


class Cuenta(Base):
    """Cuenta de login: guarda credenciales, plan y permisos administrativos."""

    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Nunca se guarda la password en texto plano.
    plan = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    fecha_alta = Column(DateTime, server_default=func.now())

    perfiles = relationship(
        "Perfil",
        back_populates="cuenta",
        cascade="all, delete-orphan",
    )


class Perfil(Base):
    """Perfil de visualizacion dentro de una cuenta, con PIN y avatar opcionales."""

    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    pin = Column(String, nullable=True)  # Si existe, tambien se guarda hasheado.
    es_infantil = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)  # Object key o URL de imagen.

    cuenta = relationship("Cuenta", back_populates="perfiles")
    vistas = relationship("Vista", back_populates="perfil", cascade="all, delete-orphan")
    calificaciones = relationship(
        "Calificacion",
        back_populates="perfil",
        cascade="all, delete-orphan",
    )
    mi_lista = relationship(
        "Contenido",
        secondary="mi_lista",
        back_populates="en_listas",
    )

    __table_args__ = (
        UniqueConstraint("cuenta_id", "nombre", name="uq_perfil_nombre_por_cuenta"),
    )
