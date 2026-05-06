from sqlalchemy.orm import Session

from src.dtos.user_dto import (
    CreateCuentaDTO,
    CreatePerfilDTO,
    CuentaResponseDTO,
    PerfilResponseDTO,
    UpdateCuentaDTO,
    UpdatePerfilDTO,
)
from src.mappers.user_mapper import (
    to_cuenta_response,
    to_cuenta_response_list,
    to_perfil_response,
    to_perfil_response_list,
)
from src.repositories.user_repository import CuentaRepository, PerfilRepository
from src.utils.errors import ConflictError, NotFoundError


PLAN_LIMITS = {
    "basico": 1,
    "estandar": 2,
    "premium": 5,
}


class CuentaService:
    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)

    def create(self, dto: CreateCuentaDTO) -> CuentaResponseDTO:
        existing = self.cuenta_repo.find_by_email(dto.email)

        if existing:
            raise ConflictError("Ya existe una cuenta con ese email")

        cuenta = self.cuenta_repo.create(
            email=dto.email,
            plan=dto.plan,
            pin=dto.pin,
        )

        return to_cuenta_response(cuenta)

    def get_by_id(self, cuenta_id: int) -> CuentaResponseDTO:
        cuenta = self.cuenta_repo.find_by_id(cuenta_id)

        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")

        return to_cuenta_response(cuenta)

    def list_all(self) -> list[CuentaResponseDTO]:
        cuentas = self.cuenta_repo.list_all()
        return to_cuenta_response_list(cuentas)

    def update(self, cuenta_id: int, dto: UpdateCuentaDTO) -> CuentaResponseDTO:
        fields = dto.model_dump(exclude_unset=True)

        cuenta = self.cuenta_repo.update(cuenta_id, **fields)

        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")

        return to_cuenta_response(cuenta)

    def delete(self, cuenta_id: int) -> None:
        deleted = self.cuenta_repo.delete(cuenta_id)

        if not deleted:
            raise NotFoundError("Cuenta no encontrada")


class PerfilService:
    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def create(self, dto: CreatePerfilDTO) -> PerfilResponseDTO:
        cuenta = self.cuenta_repo.find_by_id(dto.cuenta_id)

        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")

        perfiles = self.perfil_repo.list_by_cuenta(dto.cuenta_id)
        max_perfiles = PLAN_LIMITS[cuenta.plan]

        if len(perfiles) >= max_perfiles:
            raise ConflictError("El plan no permite crear más perfiles")

        repeated_name = any(perfil.nombre == dto.nombre for perfil in perfiles)

        if repeated_name:
            raise ConflictError("Ya existe un perfil con ese nombre en la cuenta")

        perfil = self.perfil_repo.create(
            cuenta_id=dto.cuenta_id,
            nombre=dto.nombre,
            es_infantil=dto.es_infantil,
            avatar=dto.avatar,
        )

        return to_perfil_response(perfil)

    def get_by_id(self, perfil_id: int) -> PerfilResponseDTO:
        perfil = self.perfil_repo.find_by_id(perfil_id)

        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        return to_perfil_response(perfil)

    def list_by_cuenta(self, cuenta_id: int) -> list[PerfilResponseDTO]:
        cuenta = self.cuenta_repo.find_by_id(cuenta_id)

        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")

        perfiles = self.perfil_repo.list_by_cuenta(cuenta_id)
        return to_perfil_response_list(perfiles)

    def update(self, perfil_id: int, dto: UpdatePerfilDTO) -> PerfilResponseDTO:
        fields = dto.model_dump(exclude_unset=True)

        perfil = self.perfil_repo.update(perfil_id, **fields)

        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        return to_perfil_response(perfil)

    def delete(self, perfil_id: int) -> None:
        deleted = self.perfil_repo.delete(perfil_id)

        if not deleted:
            raise NotFoundError("Perfil no encontrado")