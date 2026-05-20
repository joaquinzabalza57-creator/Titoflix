from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.config import settings
from src.dtos import AdminLoginDTO, AuthAccountDTO, LoginDTO, PerfilAuthDTO, PerfilAuthResponseDTO, TokenDTO
from src.repositories import CuentaRepository, PerfilRepository
from src.utils import LockedError, UnauthorizedError, create_access_token, verify_password


MAX_PIN_ATTEMPTS = 3
PIN_LOCK_MINUTES = 15


class AuthService:
    """Orquesta autenticacion de cuentas y seleccion segura de perfiles."""

    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def login(self, dto: LoginDTO) -> TokenDTO:
        """Valida email/password y emite el token que usa el frontend."""
        cuenta = self.cuenta_repo.find_by_email(dto.email)

        if not cuenta or not verify_password(dto.password, cuenta.password_hash):
            raise UnauthorizedError("Credenciales invalidas")

        token = create_access_token(
            {
                "sub": str(cuenta.id),
                "email": cuenta.email,
                "admin": bool(cuenta.is_admin),
            }
        )
        return TokenDTO(
            access_token=token,
            token_type="bearer",
            id=cuenta.id,
            is_admin=bool(cuenta.is_admin),
            email=cuenta.email,
            plan=cuenta.plan,
        )

    def admin_login(self, dto: AdminLoginDTO) -> TokenDTO:
        """Autentica administradores por usuario+password o solo password admin."""
        cuenta = None

        if dto.username:
            cuenta = self.cuenta_repo.find_by_email(dto.username)
            if not cuenta or not cuenta.is_admin:
                raise UnauthorizedError("Credenciales admin invalidas")

            if not verify_password(dto.password, cuenta.password_hash):
                raise UnauthorizedError("Credenciales admin invalidas")
        else:
            admins = self.cuenta_repo.list_admins()
            for admin in admins:
                if verify_password(dto.password, admin.password_hash):
                    cuenta = admin
                    break

            if not cuenta:
                raise UnauthorizedError("Credenciales admin invalidas")

        token = create_access_token(
            {
                "sub": str(cuenta.id),
                "email": cuenta.email,
                "admin": True,
            }
        )
        return TokenDTO(
            access_token=token,
            token_type="bearer",
            id=cuenta.id,
            is_admin=True,
            email=cuenta.email,
            plan=cuenta.plan,
        )

    def get_current_account(self, cuenta_id: int) -> AuthAccountDTO:
        """Recupera la cuenta actual para rehidratar estado en el cliente."""
        cuenta = self.cuenta_repo.find_by_id(cuenta_id)
        if not cuenta:
            raise UnauthorizedError("Cuenta no encontrada")

        return AuthAccountDTO(
            id=cuenta.id,
            email=cuenta.email,
            plan=cuenta.plan,
            is_admin=bool(cuenta.is_admin),
        )

    def auth_perfil(self, cuenta_id: int, perfil_id: int, dto: PerfilAuthDTO) -> PerfilAuthResponseDTO:
        """Valida que el perfil sea de la cuenta y que el PIN coincida si existe."""
        perfil = self.perfil_repo.find_by_id(perfil_id)

        if not perfil or perfil.cuenta_id != cuenta_id:
            raise UnauthorizedError("Perfil no autorizado")

        if perfil.pin:
            now = datetime.utcnow()
            if perfil.pin_locked_until and perfil.pin_locked_until > now:
                raise LockedError(f"Perfil bloqueado hasta {perfil.pin_locked_until.isoformat()}")

            if dto.pin is None or not verify_password(dto.pin, perfil.pin):
                failed_attempts = int(perfil.pin_failed_attempts or 0) + 1
                locked_until = None
                if failed_attempts >= MAX_PIN_ATTEMPTS:
                    locked_until = now + timedelta(minutes=PIN_LOCK_MINUTES)
                    failed_attempts = MAX_PIN_ATTEMPTS
                self.perfil_repo.update(
                    perfil.id,
                    pin_failed_attempts=failed_attempts,
                    pin_locked_until=locked_until,
                )
                if locked_until:
                    raise LockedError(f"Perfil bloqueado hasta {locked_until.isoformat()}")
                raise UnauthorizedError(f"PIN invalido. Intentos restantes: {MAX_PIN_ATTEMPTS - failed_attempts}")

            if perfil.pin_failed_attempts or perfil.pin_locked_until:
                self.perfil_repo.update(
                    perfil.id,
                    pin_failed_attempts=0,
                    pin_locked_until=None,
                )

        return PerfilAuthResponseDTO(
            message="Perfil autorizado",
            perfil_id=perfil.id,
            cuenta_id=perfil.cuenta_id,
        )
