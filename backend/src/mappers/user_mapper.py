from src.db.models.user_model import User
from src.db.models import Cuenta, Perfil
from src.dtos.user_dto import CuentaResponseDTO, PerfilResponseDTO, UserResponseDTO


def to_user_response(user: User) -> UserResponseDTO:
    """Convierte un Model SQLAlchemy en un DTO de respuesta (sin campos sensibles)."""
    return UserResponseDTO.model_validate(user)


def to_cuenta_response(cuenta: Cuenta) -> CuentaResponseDTO:
    return CuentaResponseDTO.model_validate(cuenta)


def to_perfil_response(perfil: Perfil) -> PerfilResponseDTO:
    return PerfilResponseDTO.model_validate(perfil)


def to_cuenta_response_list(cuentas: list[Cuenta]) -> list[CuentaResponseDTO]:
    return [to_cuenta_response(cuenta) for cuenta in cuentas]


def to_perfil_response_list(perfiles: list[Perfil]) -> list[PerfilResponseDTO]:
    return [to_perfil_response(perfil) for perfil in perfiles]
