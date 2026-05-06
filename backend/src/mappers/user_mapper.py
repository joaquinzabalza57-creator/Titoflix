from src.db.models.user_model import Cuenta, Perfil                # Importa el modelo de Usuario
from src.db.models import Cuenta, Perfil                 # Importa modelos de Cuenta y Perfil
from src.dtos.user_dto import CuentaResponseDTO, PerfilResponseDTO # Importa DTOs de usuario

def to_user_response(user: Cuenta) -> CuentaResponseDTO:     # Convierte Usuario a DTO
    """Convierte un Model SQLAlchemy en un DTO de respuesta (sin campos sensibles)."""
    return CuentaResponseDTO.model_validate(user)          # Valida y transforma al esquema

def to_cuenta_response(cuenta: Cuenta) -> CuentaResponseDTO:    # Convierte Cuenta a DTO
    return CuentaResponseDTO.model_validate(cuenta)             # Valida y transforma al esquema


def to_perfil_response(perfil: Perfil) -> PerfilResponseDTO:    # Convierte Perfil a DTO
    return PerfilResponseDTO.model_validate(perfil)             # Valida y transforma al esquema


def to_cuenta_response_list(cuentas: list[Cuenta]) -> list[CuentaResponseDTO]:    # Convierte lista de Cuentas a DTOs
    return [to_cuenta_response(cuenta) for cuenta in cuentas]                     # Itera y aplica el mapper individual


def to_perfil_response_list(perfiles: list[Perfil]) -> list[PerfilResponseDTO]:   # Convierte lista de Perfiles a DTOs
    return [to_perfil_response(perfil) for perfil in perfiles]
