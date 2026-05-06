from .auth_dto import LoginDTO, PinDTO, TokenDTO        # Importa DTOs de autenticación
from .product_dto import (                              # Importa DTOs relacionados a contenido/productos
    CalificacionResponseDTO,
    ContenidoResponseDTO,
    CreateCalificacionDTO,
    CreateContenidoDTO,
    CreateEpisodioDTO,
    CreateProductDTO,
    CreateTemporadaDTO,
    CreateVistaDTO,
    EpisodioResponseDTO,
    GeneroResponseDTO,
    MiListaDTO,
    ProductResponseDTO,
    TemporadaResponseDTO,
    UpdateContenidoDTO,
    UpdateProductDTO,
    VistaResponseDTO,
)
from .user_dto import (                                 # Importa DTOs relacionados a usuarios
    CreateCuentaDTO,
    CreatePerfilDTO,
    CuentaResponseDTO,
    PerfilResponseDTO,
    UpdateCuentaDTO,
    UpdatePerfilDTO,
)

__all__ = [                                             # Define qué se exporta al usar "from module import *"
    "LoginDTO",                                         # DTOs de autenticación
    "PinDTO",
    "TokenDTO",
    "CreateUserDTO", "UpdateUserDTO", "UserResponseDTO",  # DTOs de usuario
    "CreateCuentaDTO", "UpdateCuentaDTO", "CuentaResponseDTO",  # DTOs de cuenta
    "CreatePerfilDTO", "UpdatePerfilDTO", "PerfilResponseDTO",  # DTOs de perfil
    "GeneroResponseDTO",                                # DTO de género
    "CreateContenidoDTO", "UpdateContenidoDTO", "ContenidoResponseDTO",  # DTOs de contenido
    "CreateProductDTO", "UpdateProductDTO", "ProductResponseDTO",  # DTOs generales de producto
    "CreateTemporadaDTO", "TemporadaResponseDTO",       # DTOs de temporada
    "CreateEpisodioDTO", "EpisodioResponseDTO",         # DTOs de episodio
    "CreateVistaDTO", "VistaResponseDTO",               # DTOs de vistas
    "CreateCalificacionDTO", "CalificacionResponseDTO", # DTOs de calificaciones
    "MiListaDTO",                                      # DTO de lista personalizada
]