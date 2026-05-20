from src.db import Cuenta, Perfil
from src.dtos import CuentaResponseDTO, PerfilResponseDTO


def to_cuenta_response(cuenta: Cuenta) -> CuentaResponseDTO:
    """Convierte Cuenta ORM a DTO sin exponer password_hash."""
    return CuentaResponseDTO.model_validate(cuenta)


def to_perfil_response(perfil: Perfil) -> PerfilResponseDTO:
    """Convierte Perfil ORM a DTO y expone solo si tiene PIN, no el PIN hasheado."""
    dto = PerfilResponseDTO.model_validate(perfil)
    dto.has_pin = bool(perfil.pin)
    return dto


def to_cuenta_response_list(cuentas: list[Cuenta]) -> list[CuentaResponseDTO]:
    """Convierte una lista de cuentas a DTOs."""
    return [to_cuenta_response(cuenta) for cuenta in cuentas]


def to_perfil_response_list(perfiles: list[Perfil]) -> list[PerfilResponseDTO]:
    """Convierte una lista de perfiles a DTOs."""
    return [to_perfil_response(perfil) for perfil in perfiles]
