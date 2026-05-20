"""Barrel de repositorios para imports cortos desde servicios."""

from .product_repository import (
    CalificacionRepository,
    ContenidoRepository,
    EpisodioRepository,
    GeneroRepository,
    TemporadaRepository,
    VideoVariantRepository,
    VistaRepository,
)
from .user_repository import CuentaRepository, PerfilRepository


__all__ = [
    "CuentaRepository",
    "PerfilRepository",
    "GeneroRepository",
    "ContenidoRepository",
    "TemporadaRepository",
    "VideoVariantRepository",
    "EpisodioRepository",
    "VistaRepository",
    "CalificacionRepository",
]
