from typing import cast

from sqlalchemy.orm import Session

from src.config.env import settings
from src.dtos import (
    CreateCuentaDTO,
    CreatePerfilDTO,
    CuentaResponseDTO,
    PerfilResponseDTO,
    UpdateCuentaDTO,
    UpdatePerfilDTO,
)
from src.mappers import (
    to_cuenta_response,
    to_cuenta_response_list,
    to_perfil_response,
    to_perfil_response_list,
)
from src.repositories import CuentaRepository, PerfilRepository
from src.services.storage_service import StorageService
from src.utils import ConflictError, NotFoundError, hash_password


# Reglas comerciales simples del plan. Se validan tanto al crear perfiles como
# al degradar el plan de una cuenta existente.
PLAN_LIMITS = {
    "basico": 1,
    "estandar": 2,
    "premium": 5,
}


class CuentaService:
    """Logica de negocio para cuentas: passwords, planes y limpieza de assets."""

    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def create(self, dto: CreateCuentaDTO) -> CuentaResponseDTO:
        """Crea una cuenta con password hasheada y email unico."""
        existing = self.cuenta_repo.find_by_email(dto.email)
        if existing:
            raise ConflictError("Ya existe una cuenta con ese email")

        cuenta = self.cuenta_repo.create(
            email=dto.email,
            password_hash=hash_password(dto.password),
            plan=dto.plan,
            is_admin=dto.is_admin,
        )
        return to_cuenta_response(cuenta)

    def get_by_id(self, cuenta_id: int) -> CuentaResponseDTO:
        """Obtiene una cuenta o traduce ausencia a NotFoundError."""
        cuenta = self.cuenta_repo.find_by_id(cuenta_id)
        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")
        return to_cuenta_response(cuenta)

    def list_all(self) -> list[CuentaResponseDTO]:
        """Lista cuentas para la consola administrativa."""
        return to_cuenta_response_list(self.cuenta_repo.list_all())

    def update(self, cuenta_id: int, dto: UpdateCuentaDTO) -> CuentaResponseDTO:
        """Actualiza datos sensibles validando duplicados y limites del plan."""
        fields = dto.model_dump(exclude_unset=True)

        if "email" in fields:
            existing = self.cuenta_repo.find_by_email(fields["email"])
            if existing and existing.id != cuenta_id:
                raise ConflictError("Ya existe una cuenta con ese email")

        if "password" in fields:
            fields["password_hash"] = hash_password(fields.pop("password"))

        if "plan" in fields:
            perfiles = self.perfil_repo.list_by_cuenta(cuenta_id)
            if len(perfiles) > PLAN_LIMITS[fields["plan"]]:
                raise ConflictError("La cuenta tiene mas perfiles que los permitidos por ese plan")

        cuenta = self.cuenta_repo.update(cuenta_id, **fields)
        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")
        return to_cuenta_response(cuenta)

    def delete(self, cuenta_id: int) -> None:
        """Elimina la cuenta y los assets de todos sus perfiles."""
        cuenta = self.cuenta_repo.find_by_id(cuenta_id)
        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")

        StorageService().delete_prefix(
            f"{settings.S3_ASSETS_PREFIX.strip('/')}/cuentas/{cuenta_id}"
        )
        if not self.cuenta_repo.delete(cuenta_id):
            raise NotFoundError("Cuenta no encontrada")


class PerfilService:
    """Logica de perfiles: limites por plan, PIN, avatar y control infantil."""

    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def create(self, dto: CreatePerfilDTO) -> PerfilResponseDTO:
        """Crea un perfil y guarda avatar base64 si el frontend lo envia."""
        cuenta = self.cuenta_repo.find_by_id(dto.cuenta_id)
        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")

        perfiles = self.perfil_repo.list_by_cuenta(dto.cuenta_id)
        max_perfiles = PLAN_LIMITS[cast(str, cuenta.plan)]
        if len(perfiles) >= max_perfiles:
            raise ConflictError("El plan no permite crear mas perfiles")

        repeated_name = any(perfil.nombre == dto.nombre for perfil in perfiles)
        if repeated_name:
            raise ConflictError("Ya existe un perfil con ese nombre en la cuenta")
        if dto.es_infantil and dto.pin:
            raise ConflictError("Los perfiles infantiles no pueden tener PIN")

        perfil = self.perfil_repo.create(
            cuenta_id=dto.cuenta_id,
            nombre=dto.nombre,
            pin=hash_password(dto.pin) if dto.pin else None,
            es_infantil=dto.es_infantil,
            avatar=None,
        )

        if dto.avatar:
            try:
                avatar = self._store_avatar(dto.avatar, dto.cuenta_id, perfil.id, dto.nombre)
                perfil = self.perfil_repo.update(perfil.id, avatar=avatar) or perfil
            except Exception:
                # Si falla el upload de avatar, se deshace el perfil para no dejar datos a medias.
                self.perfil_repo.delete(perfil.id)
                raise

        return to_perfil_response(perfil)

    def get_by_id(self, perfil_id: int) -> PerfilResponseDTO:
        """Obtiene un perfil por ID."""
        perfil = self.perfil_repo.find_by_id(perfil_id)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")
        return to_perfil_response(perfil)

    def list_by_cuenta(self, cuenta_id: int) -> list[PerfilResponseDTO]:
        """Lista perfiles de una cuenta existente."""
        cuenta = self.cuenta_repo.find_by_id(cuenta_id)
        if not cuenta:
            raise NotFoundError("Cuenta no encontrada")
        return to_perfil_response_list(self.perfil_repo.list_by_cuenta(cuenta_id))

    def update(self, perfil_id: int, dto: UpdatePerfilDTO) -> PerfilResponseDTO:
        """Actualiza perfil y reemplaza avatar almacenado cuando llega uno nuevo."""
        fields = dto.model_dump(exclude_unset=True)

        perfil_actual = self.perfil_repo.find_by_id(perfil_id)
        if not perfil_actual:
            raise NotFoundError("Perfil no encontrado")

        if "nombre" in fields:
            perfiles = self.perfil_repo.list_by_cuenta(perfil_actual.cuenta_id)
            repeated_name = any(
                perfil.id != perfil_id and perfil.nombre == fields["nombre"]
                for perfil in perfiles
            )
            if repeated_name:
                raise ConflictError("Ya existe un perfil con ese nombre en la cuenta")

        if fields.get("es_infantil") is True:
            fields["pin"] = None
            fields["pin_failed_attempts"] = 0
            fields["pin_locked_until"] = None
        elif perfil_actual.es_infantil and fields.get("pin"):
            raise ConflictError("Los perfiles infantiles no pueden tener PIN")

        if "pin" in fields:
            fields["pin"] = hash_password(fields["pin"]) if fields["pin"] else None
            fields["pin_failed_attempts"] = 0
            fields["pin_locked_until"] = None

        if "avatar" in fields:
            avatar = fields["avatar"]
            if avatar and self._is_data_url(avatar):
                fields["avatar"] = self._store_avatar(
                    avatar,
                    perfil_actual.cuenta_id,
                    perfil_actual.id,
                    fields.get("nombre") or perfil_actual.nombre,
                )
                self._delete_stored_avatar(perfil_actual.avatar)
            elif avatar is None:
                self._delete_stored_avatar(perfil_actual.avatar)

        perfil = self.perfil_repo.update(perfil_id, **fields)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")
        return to_perfil_response(perfil)

    def delete(self, perfil_id: int) -> None:
        """Elimina un perfil y los assets cargados para ese perfil."""
        perfil = self.perfil_repo.find_by_id(perfil_id)
        if not perfil:
            raise NotFoundError("Perfil no encontrado")

        StorageService().delete_prefix(
            f"{settings.S3_ASSETS_PREFIX.strip('/')}/cuentas/{perfil.cuenta_id}/perfiles/{perfil_id}"
        )
        if not self.perfil_repo.delete(perfil_id):
            raise NotFoundError("Perfil no encontrado")

    def _store_avatar(self, avatar: str, cuenta_id: int, perfil_id: int, profile_name: str) -> str:
        """Acepta URLs existentes o data URLs nuevas enviadas desde el frontend."""
        if not self._is_data_url(avatar):
            return avatar

        upload = StorageService().upload_asset_data_url(
            avatar,
            cuenta_id=cuenta_id,
            perfil_id=perfil_id,
            filename=f"{profile_name}-avatar",
        )
        return upload.object_key

    def _delete_stored_avatar(self, avatar: str | None) -> None:
        """Borra solo avatares administrados por nuestro bucket de assets."""
        if avatar and avatar.startswith(f"{settings.S3_ASSETS_PREFIX.strip('/')}/"):
            StorageService().delete_object(avatar)

    def _is_data_url(self, value: str) -> bool:
        """Detecta imagenes embebidas del canvas/file picker del frontend."""
        return value.startswith("data:")
