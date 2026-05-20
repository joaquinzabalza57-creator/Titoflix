"""Barrel de modelos ORM y tablas puente."""

from src.db.models.user_model import Cuenta, Perfil
from src.db.models.product_model import (
    Calificacion,
    Contenido,
    Episodio,
    Genero,
    Temporada,
    VideoVariant,
    Vista,
    contenido_generos,
    mi_lista,
)


__all__ = [
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
