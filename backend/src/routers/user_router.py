from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.user_dto import (
    CreateCuentaDTO,
    CreatePerfilDTO,
    CuentaResponseDTO,
    PerfilResponseDTO,
    UpdateCuentaDTO,
    UpdatePerfilDTO,
)
from src.schemas.user_schema import (
    CreateCuentaSchema,
    CreatePerfilSchema,
    UpdateCuentaSchema,
    UpdatePerfilSchema,
)
from src.services.user_service import CuentaService, PerfilService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=CuentaResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(payload: CreateCuentaSchema, db: Session = Depends(get_db)):
    """Crear una nueva cuenta de usuario."""
    dto = CreateCuentaDTO(**payload.model_dump())
    return CuentaService(db).create(dto)


@router.get("/", response_model=list[CuentaResponseDTO])
def list_users(db: Session = Depends(get_db)):
    """Listar todas las cuentas de usuario."""
    return CuentaService(db).list_all()


@router.post("/perfiles", response_model=PerfilResponseDTO, status_code=status.HTTP_201_CREATED)
def create_profile(payload: CreatePerfilSchema, db: Session = Depends(get_db)):
    """Crear un nuevo perfil."""
    dto = CreatePerfilDTO(**payload.model_dump())
    return PerfilService(db).create(dto)


@router.get("/{user_id}/perfiles", response_model=list[PerfilResponseDTO])
def list_profiles_by_user(user_id: int, db: Session = Depends(get_db)):
    """Listar todos los perfiles de una cuenta."""
    return PerfilService(db).list_by_cuenta(user_id)


@router.get("/perfiles/{profile_id}", response_model=PerfilResponseDTO)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Obtener los datos de un perfil por ID."""
    return PerfilService(db).get_by_id(profile_id)


@router.put("/perfiles/{profile_id}", response_model=PerfilResponseDTO)
def update_profile(profile_id: int, payload: UpdatePerfilSchema, db: Session = Depends(get_db)):
    """Actualizar un perfil."""
    dto = UpdatePerfilDTO(**payload.model_dump(exclude_unset=True))
    return PerfilService(db).update(profile_id, dto)


@router.delete("/perfiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Eliminar un perfil."""
    PerfilService(db).delete(profile_id)


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
