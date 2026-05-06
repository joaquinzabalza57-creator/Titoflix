from sqlalchemy.orm import Session                               # Importa la sesión de SQLAlchemy

from src.dtos.auth_dto import LoginDTO, TokenDTO                 # Importa esquemas para Login y Token
from src.repositories.user_repository import CuentaRepository    # Importa el repositorio de Usuarios
from src.utils.errors import UnauthorizedError                   # Importa manejo de errores personalizados
from src.utils.hash import verify_password                       # Importa utilidad de verificación de contraseñas
from src.utils.jwt import create_access_token                    # Importa utilidad para generación de tokens


class AuthService:                                            # Servicio para manejar la autenticación
    def __init__(self, db: Session):                          # Inicializa el servicio con sesión de BD
        self.cuenta_repo = CuentaRepository(db)                 # Instancia el repositorio de Usuarios

    def login(self, dto: LoginDTO) -> TokenDTO:               # Autentica usuario y genera token
        cuenta = self.cuenta_repo.find_by_email(dto.email)        # Busca usuario en la BD por email

        if not cuenta or not verify_password(dto.password, cuenta.password_hash): # Valida credenciales
            raise UnauthorizedError("Credenciales invalidas") # Lanza error si fallan

        token = create_access_token({"sub": str(cuenta.id), "email": cuenta.email}) # Genera JWT de acceso

        return TokenDTO(access_token=token, token_type="bearer") # Retorna DTO con el token