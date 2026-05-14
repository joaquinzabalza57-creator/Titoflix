from sqlalchemy.orm import Session

from src.config import settings
from src.dtos import AdminLoginDTO, LoginDTO, PerfilAuthDTO, PerfilAuthResponseDTO, TokenDTO
from src.repositories import CuentaRepository, PerfilRepository
from src.utils import UnauthorizedError, create_access_token, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def login(self, dto: LoginDTO) -> TokenDTO:
        cuenta = self.cuenta_repo.find_by_email(dto.email)

        if not cuenta or not verify_password(dto.password, cuenta.password_hash):
            raise UnauthorizedError("Credenciales invalidas")

        token = create_access_token({"sub": str(cuenta.id), "email": cuenta.email})
        return TokenDTO(access_token=token, token_type="bearer")

    def admin_login(self, dto: AdminLoginDTO) -> TokenDTO:
        if dto.username != settings.ADMIN_USERNAME:
            raise UnauthorizedError("Credenciales admin invalidas")

        cuenta = self.cuenta_repo.find_by_email(settings.ADMIN_USERNAME)
        if not cuenta or not cuenta.is_admin or not verify_password(dto.password, cuenta.password_hash):
            raise UnauthorizedError("Credenciales admin invalidas")

        token = create_access_token(
            {
                "sub": str(cuenta.id),
                "email": cuenta.email,
                "admin": True,
            }
        )
        return TokenDTO(access_token=token, token_type="bearer")

    def auth_perfil(
        self,
        cuenta_id: int,
        perfil_id: int,
        dto: PerfilAuthDTO,
    ) -> PerfilAuthResponseDTO:
        perfil = self.perfil_repo.find_by_id(perfil_id)

        if not perfil or perfil.cuenta_id != cuenta_id:
            raise UnauthorizedError("Perfil no autorizado")

        if perfil.pin and (dto.pin is None or not verify_password(dto.pin, perfil.pin)):
            raise UnauthorizedError("PIN invalido")

        return PerfilAuthResponseDTO(
            message="Perfil autorizado",
            perfil_id=perfil.id,
            cuenta_id=cuenta_id,
        )
