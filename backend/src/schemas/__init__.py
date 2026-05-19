"""Barrel de schemas HTTP usados por routers y documentacion OpenAPI."""

from .auth_schema import (
    AdminLoginSchema,
    AuthAccountSchema,
    LoginSchema,
    PerfilAuthResponseSchema,
    PerfilAuthSchema,
    PinSchema,
    TokenSchema,
)
from .product_schema import (
    CalificacionSchema,
    ContenidoSchema,
    CreateCalificacionSchema,
    CreateContenidoSchema,
    CreateEpisodioSchema,
    CreateTemporadaSchema,
    CreateVistaSchema,
    GeneroSchema,
    MiListaSchema,
    UpdateContenidoSchema,
    UpdateEpisodioSchema,
    UpdateTemporadaSchema,
    VistaSchema,
)
from .user_schema import (
    CreateCuentaSchema,
    CreatePerfilSchema,
    CuentaSchema,
    PerfilSchema,
    UpdateCuentaSchema,
    UpdatePerfilSchema,
)


__all__ = [
    "LoginSchema",
    "AdminLoginSchema",
    "AuthAccountSchema",
    "PinSchema",
    "PerfilAuthSchema",
    "PerfilAuthResponseSchema",
    "TokenSchema",
    "CreateCuentaSchema",
    "UpdateCuentaSchema",
    "CuentaSchema",
    "CreatePerfilSchema",
    "UpdatePerfilSchema",
    "PerfilSchema",
    "GeneroSchema",
    "CreateContenidoSchema",
    "UpdateContenidoSchema",
    "ContenidoSchema",
    "CreateTemporadaSchema",
    "UpdateTemporadaSchema",
    "CreateEpisodioSchema",
    "UpdateEpisodioSchema",
    "CreateVistaSchema",
    "VistaSchema",
    "CreateCalificacionSchema",
    "CalificacionSchema",
    "MiListaSchema",
]
