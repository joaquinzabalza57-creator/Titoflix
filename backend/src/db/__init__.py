"""Exports de base de datos para simplificar imports del resto del backend."""

from .connection import Base, SessionLocal, create_tables, drop_tables, engine, get_db, reset_database
from .models import (
    Calificacion,
    Contenido,
    Cuenta,
    Episodio,
    Genero,
    Perfil,
    Temporada,
    VideoVariant,
    Vista,
    contenido_generos,
    mi_lista,
)


__all__ = [
    "Base",
    "get_db",
    "engine",
    "SessionLocal",
    "create_tables",
    "drop_tables",
    "reset_database",
    "Cuenta",
    "Perfil",
    "Genero",
    "Contenido",
    "Temporada",
    "Episodio",
    "VideoVariant",
    "Vista",
    "Calificacion",
    "contenido_generos",
    "mi_lista",
]
