from .auth_schema import LoginSchema, PinSchema, TokenSchema  # Importa schemas relacionados a autenticación
from .product_schema import (                                 # Importa schemas relacionados a contenido/productos
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
    VistaSchema,
)
from .user_schema import (                                    # Importa schemas relacionados a usuarios
    CreateCuentaSchema,
    CreatePerfilSchema,
    CuentaSchema,
    PerfilSchema,
    UpdateCuentaSchema,
    UpdatePerfilSchema,
)

__all__ = [                                                   # Define qué se exporta al hacer "from module import *"
    "LoginSchema", "PinSchema", "TokenSchema",                # Schemas de autenticación
    "CreateCuentaSchema", "UpdateCuentaSchema", "CuentaSchema",  # Schemas de cuenta
    "CreatePerfilSchema", "UpdatePerfilSchema", "PerfilSchema",  # Schemas de perfil
    "GeneroSchema", "CreateContenidoSchema", "UpdateContenidoSchema",  # Schemas de contenido
    "ContenidoSchema", "CreateTemporadaSchema", "CreateEpisodioSchema",  # Más schemas de contenido
    "CreateVistaSchema", "VistaSchema",                      # Schemas de vistas
    "CreateCalificacionSchema", "CalificacionSchema",        # Schemas de calificaciones
    "MiListaSchema",                                        # Schema de lista personalizada
]