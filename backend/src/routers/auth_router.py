from fastapi import APIRouter, Depends, Header                      # Importa utilidades de rutas y dependencias
from sqlalchemy.orm import Session                                  # Importa el tipado para la sesión de BD

from src.db import get_db                                           # Importa la función para obtener la sesión
from src.dtos import LoginDTO, PerfilAuthDTO, TokenDTO              # Importa objetos de transferencia de datos
from src.middlewares import get_user_from_authorization             # Dependencia para validar el JWT de cuenta
from src.schemas import LoginSchema, PerfilAuthSchema, TokenSchema  # Importa esquemas de validación Pydantic
from src.services import AuthService                                # Importa el servicio de autenticación

router = APIRouter(prefix="/auth", tags=["auth"])                   # Define el router con prefijo y etiquetas


@router.post("/login", response_model=TokenSchema)                  # Endpoint para inicio de sesión de cuenta
def login(payload: LoginSchema, db: Session = Depends(get_db)):     # Recibe credenciales y la sesión de BD
    dto = LoginDTO(**payload.model_dump())                          # Convierte el esquema validado en DTO
    token: TokenDTO = AuthService(db).login(dto)                    # Ejecuta la lógica de login en el servicio
    return TokenSchema(**token.model_dump())                        # Retorna el token mapeado al esquema


@router.post("/perfiles/{perfil_id}", response_model=TokenSchema)   # Endpoint para acceso a un perfil específico
def auth_perfil(
    perfil_id: int,                                                 # ID del perfil enviado en la URL
    payload: PerfilAuthSchema,                                      # Esquema que puede contener el PIN
    authorization: str | None = Header(default=None),               # Captura el token del header Authorization
    db: Session = Depends(get_db),                                  # Inyecta la sesión de la base de datos
):
    current_user = get_user_from_authorization(authorization, db)   # Valida que la cuenta esté autenticada
    dto = PerfilAuthDTO(**payload.model_dump())                     # Mapea los datos de entrada a DTO
    token: TokenDTO = AuthService(db).auth_perfil(current_user.id, perfil_id, dto) # Valida acceso al perfil
    return TokenSchema(**token.model_dump())                        # Retorna el nuevo token con perfil_id
