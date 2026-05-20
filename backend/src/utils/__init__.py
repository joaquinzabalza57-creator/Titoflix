from src.utils.errors import (                                   # Importa excepciones personalizadas
    AppError,                                                    # Error base de la aplicación
    BadRequestError,                                             # Error para peticiones incorrectas (400)
    ConflictError,                                               # Error para conflictos de recursos (409)
    ForbiddenError,                                              # Error para accesos prohibidos (403)
    NotFoundError,                                               # Error para recursos no encontrados (404)
    UnauthorizedError,                                           # Error para falta de autenticación (401)
    ValidationError,                                             # Error para fallos de validación (422)
)
from src.utils.hash import hash_password, verify_password        # Utilidades para manejo de contraseñas
from src.utils.jwt import create_access_token, decode_access_token # Utilidades para tokens JWT


__all__ = [
    "AppError",                                                  # Exporta error base
    "BadRequestError",                                           # Exporta error de petición incorrecta
    "UnauthorizedError",                                         # Exporta error de no autorizado
    "ForbiddenError",                                            # Exporta error de prohibido
    "NotFoundError",                                             # Exporta error de no encontrado
    "ConflictError",                                             # Exporta error de conflicto
    "ValidationError",                                           # Exporta error de validación
    "hash_password",                                             # Exporta utilidad de hasheo
    "verify_password",                                           # Exporta utilidad de verificación
    "create_access_token",                                       # Exporta creador de tokens
    "decode_access_token",                                       # Exporta decodificador de tokens
]