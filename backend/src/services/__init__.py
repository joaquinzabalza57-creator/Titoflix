"""Barrel de servicios de negocio usados por routers."""

from src.services.auth_service import AuthService
from src.services.product_service import (
    CalificacionService,
    ContenidoService,
    EpisodioService,
    GeneroService,
    MiListaService,
    ReporteService,
    TemporadaService,
    VistaService,
)
from src.services.user_service import CuentaService, PerfilService


__all__ = [
    "AuthService",
    "CuentaService",
    "PerfilService",
    "GeneroService",
    "ContenidoService",
    "TemporadaService",
    "EpisodioService",
    "VistaService",
    "MiListaService",
    "ReporteService",
    "CalificacionService",
]
