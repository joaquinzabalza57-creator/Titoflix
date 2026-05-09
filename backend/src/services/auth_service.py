from sqlalchemy.orm import Session

from src.dtos import LoginDTO, PerfilAuthDTO, TokenDTO
from src.repositories import CuentaRepository, PerfilRepository
from src.utils import UnauthorizedError, verify_password, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.cuenta_repo = CuentaRepository(db)
        self.perfil_repo = PerfilRepository(db)

    def login(self, dto: LoginDTO) -> TokenDTO:
        cuenta = self.cuenta_repo.find_by_email(dto.email)

        if not cuenta or not verify_password(dto.password, cuenta.password_hash): # type: ignore
            raise UnauthorizedError("Credenciales invalidas")

        token = create_access_token({"sub": str(cuenta.id), "email": cuenta.email})

        return TokenDTO(access_token=token, token_type="bearer")

    def auth_perfil(self, cuenta_id: int, perfil_id: int, dto: PerfilAuthDTO) -> TokenDTO:
        perfil = self.perfil_repo.find_by_id(perfil_id)

        if not perfil or perfil.cuenta_id != cuenta_id: # type: ignore
            raise UnauthorizedError("Perfil no autorizado")

        if perfil.pin and (dto.pin is None or not verify_password(dto.pin, perfil.pin)): # type: ignore
            raise UnauthorizedError("PIN invalido")

        token = create_access_token({"sub": str(cuenta_id), "perfil_id": str(perfil.id)})

        return TokenDTO(access_token=token, token_type="bearer")
