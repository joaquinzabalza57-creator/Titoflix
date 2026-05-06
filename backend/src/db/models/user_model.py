from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.connection import Base


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    plan = Column(String, nullable=False)
    pin = Column(String, nullable=True)
    fecha_alta = Column(DateTime, server_default=func.now())

    perfiles = relationship(
        "Perfil",
        back_populates="cuenta",
        cascade="all, delete-orphan",
    )


class Perfil(Base):
    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    es_infantil = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)

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
