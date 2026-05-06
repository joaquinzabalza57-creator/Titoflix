from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.product_dto import (
    CreateCalificacionDTO,
    CreateContenidoDTO,
    CreateEpisodioDTO,
    CreateTemporadaDTO,
    CreateVistaDTO,
    UpdateContenidoDTO,
)
from src.schemas.product_schema import (
    CalificacionSchema,
    ContenidoSchema,
    CreateCalificacionSchema,
    CreateContenidoSchema,
    CreateEpisodioSchema,
    CreateTemporadaSchema,
    CreateVistaSchema,
    GeneroSchema,
    UpdateContenidoSchema,
    VistaSchema,
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
    response_model=GeneroSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_genero(nombre: str, db: Session = Depends(get_db)):
    return GeneroService(db).create(nombre)


@router.get("/generos", response_model=list[GeneroSchema])
def list_generos(db: Session = Depends(get_db)):
    return GeneroService(db).list_all()


@router.post(
    "/contenidos",
    response_model=ContenidoSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_contenido(payload: CreateContenidoSchema, db: Session = Depends(get_db)):
    dto = CreateContenidoDTO(**payload.model_dump())

    return ContenidoService(db).create(dto)


@router.get("/contenidos", response_model=list[ContenidoSchema])
def search_contenidos(
    q: str | None = None,
    tipo: str | None = None,
    genero_id: int | None = None,
    perfil_id: int | None = None,
    ordenar: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return ContenidoService(db).search(
        q=q,
        tipo=tipo,
        genero_id=genero_id,
        perfil_id=perfil_id,
    )


@router.get("/contenidos/top", response_model=list[ContenidoSchema])
def top_contenidos(db: Session = Depends(get_db)):
    return ContenidoService(db).top()


@router.get("/contenidos/{contenido_id}", response_model=ContenidoSchema)
def get_contenido(contenido_id: int, db: Session = Depends(get_db)):
    return ContenidoService(db).get_by_id(contenido_id)


@router.put("/contenidos/{contenido_id}", response_model=ContenidoSchema)
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
    response_model=CreateTemporadaSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_temporada(payload: CreateTemporadaSchema, db: Session = Depends(get_db)):
    dto = CreateTemporadaDTO(**payload.model_dump())

    return TemporadaService(db).create(dto)


@router.get("/contenidos/{contenido_id}/temporadas", response_model=list[CreateTemporadaSchema])
def list_temporadas(contenido_id: int, db: Session = Depends(get_db)):
    return TemporadaService(db).list_by_contenido(contenido_id)


@router.post(
    "/episodios",
    response_model=CreateEpisodioSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_episodio(payload: CreateEpisodioSchema, db: Session = Depends(get_db)):
    dto = CreateEpisodioDTO(**payload.model_dump())

    return EpisodioService(db).create(dto)


@router.get("/temporadas/{temporada_id}/episodios", response_model=list[CreateEpisodioSchema])
def list_episodios(temporada_id: int, db: Session = Depends(get_db)):
    return EpisodioService(db).list_by_temporada(temporada_id)


@router.post(
    "/vistas",
    response_model=VistaSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_vista(payload: CreateVistaSchema, db: Session = Depends(get_db)):
    dto = CreateVistaDTO(**payload.model_dump())

    return VistaService(db).create_or_update(dto)


@router.get("/perfiles/{perfil_id}/continuar", response_model=list[VistaSchema])
def continuar_viendo(perfil_id: int, db: Session = Depends(get_db)):
    return VistaService(db).continuar_viendo(perfil_id)


@router.post("/perfiles/{perfil_id}/mi-lista", response_model=list[ContenidoSchema])
def add_to_mi_lista(
    perfil_id: int,
    contenido_id: int,
    db: Session = Depends(get_db),
):
    return MiListaService(db).add(perfil_id, contenido_id)


@router.get("/perfiles/{perfil_id}/mi-lista", response_model=list[ContenidoSchema])
def get_mi_lista(perfil_id: int, db: Session = Depends(get_db)):
    return MiListaService(db).list(perfil_id)


@router.delete("/perfiles/{perfil_id}/mi-lista/{contenido_id}", response_model=list[ContenidoSchema])
def remove_from_mi_lista(
    perfil_id: int,
    contenido_id: int,
    db: Session = Depends(get_db),
):
    return MiListaService(db).remove(perfil_id, contenido_id)


@router.post(
    "/calificaciones",
    response_model=CalificacionSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_calificacion(
    payload: CreateCalificacionSchema,
    db: Session = Depends(get_db),
):
    dto = CreateCalificacionDTO(**payload.model_dump())

    return CalificacionService(db).create_or_update(dto)