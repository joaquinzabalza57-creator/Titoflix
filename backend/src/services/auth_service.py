from sqlalchemy.orm import Session

from src.dtos.auth_dto import LoginDTO, TokenDTO
from src.repositories.user_repository import UserRepository
from src.utils.errors import UnauthorizedError
from src.utils.hash import verify_password
from src.utils.jwt import create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, dto: LoginDTO) -> TokenDTO:
        user = self.user_repo.find_by_email(dto.email)

        if not user or not verify_password(dto.password, user.password_hash):
            raise UnauthorizedError("Credenciales invalidas")

        token = create_access_token({"sub": str(user.id), "email": user.email})

        return TokenDTO(access_token=token, token_type="bearer")