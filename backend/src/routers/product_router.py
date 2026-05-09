from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.db import get_db
from src.dtos import (
    CreateCalificacionDTO,
    CreateContenidoDTO,
    CreateEpisodioDTO,
    CreateTemporadaDTO,
    CreateVistaDTO,
    CalificacionResponseDTO,
    ContenidoResponseDTO,
    EpisodioResponseDTO,
    GeneroResponseDTO,
    TemporadaResponseDTO,
    UpdateContenidoDTO,
    VistaResponseDTO,
)
from src.schemas.product_schema import (
    CreateCalificacionSchema,
    CreateContenidoSchema,
    CreateEpisodioSchema,
    CreateTemporadaSchema,
    CreateVistaSchema,
    UpdateContenidoSchema,
)
from src.services.product_service import (
    CalificacionService,
    ContenidoService,
    EpisodioService,
    GeneroService,
    MiListaService,
    TemporadaService,
    VistaService,
)


router = APIRouter(tags=["products"])


@router.post(
    "/generos",
    response_model=GeneroResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_genero(nombre: str, db: Session = Depends(get_db)):
    return GeneroService(db).create(nombre)


@router.get("/generos", response_model=list[GeneroResponseDTO])
def list_generos(db: Session = Depends(get_db)):
    return GeneroService(db).list_all()


@router.post(
    "/contenidos",
    response_model=ContenidoResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_contenido(payload: CreateContenidoSchema, db: Session = Depends(get_db)):
    dto = CreateContenidoDTO(**payload.model_dump())

    return ContenidoService(db).create(dto)


@router.get("/contenidos", response_model=list[ContenidoResponseDTO])
def search_contenidos(
    q: str | None = None,
    tipo: str | None = None,
    genero_id: int | None = None,
    genero: str | None = None,
    perfil_id: int | None = None,
    ordenar: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return ContenidoService(db).search(
        q=q,
        tipo=tipo,
        genero_id=genero_id,
        genero=genero,
        perfil_id=perfil_id,
        ordenar=ordenar,
    )


@router.get("/contenidos/top", response_model=list[ContenidoResponseDTO])
def top_contenidos(genero: str | None = None, db: Session = Depends(get_db)):
    return ContenidoService(db).top(genero=genero)


@router.get("/contenidos/{contenido_id}", response_model=ContenidoResponseDTO)
def get_contenido(contenido_id: int, db: Session = Depends(get_db)):
    return ContenidoService(db).get_by_id(contenido_id)


@router.put("/contenidos/{contenido_id}", response_model=ContenidoResponseDTO)
def update_contenido(
    contenido_id: int,
    payload: UpdateContenidoSchema,
    db: Session = Depends(get_db),
):
    dto = UpdateContenidoDTO(**payload.model_dump(exclude_unset=True))

    return ContenidoService(db).update(contenido_id, dto)


@router.delete("/contenidos/{contenido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contenido(contenido_id: int, db: Session = Depends(get_db)):
    ContenidoService(db).delete(contenido_id)


@router.post(
    "/temporadas",
    response_model=TemporadaResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_temporada(payload: CreateTemporadaSchema, db: Session = Depends(get_db)):
    dto = CreateTemporadaDTO(**payload.model_dump())

    return TemporadaService(db).create(dto)


@router.get("/contenidos/{contenido_id}/temporadas", response_model=list[TemporadaResponseDTO])
def list_temporadas(contenido_id: int, db: Session = Depends(get_db)):
    return TemporadaService(db).list_by_contenido(contenido_id)


@router.post(
    "/episodios",
    response_model=EpisodioResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_episodio(payload: CreateEpisodioSchema, db: Session = Depends(get_db)):
    dto = CreateEpisodioDTO(**payload.model_dump())

    return EpisodioService(db).create(dto)


@router.get("/temporadas/{temporada_id}/episodios", response_model=list[EpisodioResponseDTO])
def list_episodios(temporada_id: int, db: Session = Depends(get_db)):
    return EpisodioService(db).list_by_temporada(temporada_id)


@router.post(
    "/vistas",
    response_model=VistaResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_vista(payload: CreateVistaSchema, db: Session = Depends(get_db)):
    dto = CreateVistaDTO(**payload.model_dump())

    return VistaService(db).create_or_update(dto)


@router.get("/perfiles/{perfil_id}/continuar", response_model=list[VistaResponseDTO])
def continuar_viendo(perfil_id: int, db: Session = Depends(get_db)):
    return VistaService(db).continuar_viendo(perfil_id)


@router.post("/perfiles/{perfil_id}/mi-lista", response_model=list[ContenidoResponseDTO])
def add_to_mi_lista(
    perfil_id: int,
    contenido_id: int,
    db: Session = Depends(get_db),
):
    return MiListaService(db).add(perfil_id, contenido_id)


@router.get("/perfiles/{perfil_id}/mi-lista", response_model=list[ContenidoResponseDTO])
def get_mi_lista(perfil_id: int, db: Session = Depends(get_db)):
    return MiListaService(db).list(perfil_id)


@router.delete("/perfiles/{perfil_id}/mi-lista/{contenido_id}", response_model=list[ContenidoResponseDTO])
def remove_from_mi_lista(
    perfil_id: int,
    contenido_id: int,
    db: Session = Depends(get_db),
):
    return MiListaService(db).remove(perfil_id, contenido_id)


@router.post(
    "/calificaciones",
    response_model=CalificacionResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_calificacion(
    payload: CreateCalificacionSchema,
    db: Session = Depends(get_db),
):
    dto = CreateCalificacionDTO(**payload.model_dump())

    return CalificacionService(db).create_or_update(dto)
