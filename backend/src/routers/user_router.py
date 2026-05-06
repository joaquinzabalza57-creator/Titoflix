from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.user_dto import CreateCuentaDTO, UpdateCuentaDTO, CuentaResponseDTO
from src.schemas.user_schema import CreateUserSchema, UpdateCuentaSchema
from src.services.user_service import CuentaService, PerfilService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=CuentaResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(payload: CreateUserSchema, db: Session = Depends(get_db)):
    """Crear una nueva cuenta de usuario."""
    dto = CreateCuentaDTO(**payload.model_dump())
    return CuentaService(db).create(dto)


@router.get("/", response_model=list[CuentaResponseDTO])
def list_users(db: Session = Depends(get_db)):
    """Listar todas las cuentas de usuario."""
    return CuentaService(db).list_all()


@router.get("/{user_id}", response_model=CuentaResponseDTO)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obtener los datos de una cuenta específica por ID."""
    return CuentaService(db).get_by_id(user_id)


@router.put("/{user_id}", response_model=CuentaResponseDTO)
def update_user(user_id: int, payload: UpdateCuentaSchema, db: Session = Depends(get_db)):
    """Actualizar una cuenta de usuario."""
    dto = UpdateCuentaDTO(**payload.model_dump(exclude_unset=True))
    return CuentaService(db).update(user_id, dto)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Eliminar una cuenta de usuario."""
    CuentaService(db).delete(user_id)