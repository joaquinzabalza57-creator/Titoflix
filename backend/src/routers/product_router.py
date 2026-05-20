from datetime import timedelta
import mimetypes
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.db import get_db
from src.db.models import Cuenta, Perfil
from src.dtos import (
    CreateCalificacionDTO,
    CreateContenidoDTO,
    ContinuarViendoDTO,
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
from src.middlewares import get_current_user_from_swagger, get_owned_profile, require_admin
from src.schemas.product_schema import (
    CreateEpisodioSchema,
    CreateTemporadaSchema,
    UpdateEpisodioSchema,
    UpdateTemporadaSchema,
    MiListaSchema,
    UpsertCalificacionSchema,
    UpsertVistaSchema,
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
from src.dtos import UpdateEpisodioDTO, UpdateTemporadaDTO
from src.services.storage_service import StorageService
from src.utils import UnauthorizedError, create_access_token, decode_access_token


router = APIRouter(tags=["products"])


MEDIA_TOKEN_TTL_MINUTES = 10


def _create_media_token(
    current_user: Cuenta,
    resource_type: str,
    resource_id: int,
    quality: str | None,
    action: str,
) -> str:
    """Crea un JWT corto para que el frontend reproduzca media sin exponer storage."""
    return create_access_token(
        {
            "sub": str(current_user.id),
            "scope": "media",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "quality": quality,
            "action": action,
        },
        expires_delta=timedelta(minutes=MEDIA_TOKEN_TTL_MINUTES),
    )


def _verify_media_token(
    token: str,
    resource_type: str,
    resource_id: int,
    quality: str | None,
    action: str,
) -> None:
    """Valida que el token temporal corresponda exactamente al recurso pedido."""
    payload = decode_access_token(token)
    if (
        payload.get("scope") != "media"
        or payload.get("resource_type") != resource_type
        or payload.get("resource_id") != resource_id
        or payload.get("quality") != quality
        or payload.get("action") != action
    ):
        raise UnauthorizedError("Token de media invalido")


def _stream_storage_video(
    file_id: str,
    mime_type: str,
    request: Request,
    filename: str | None = None,
    as_attachment: bool = False,
) -> StreamingResponse:
    """Puente HTTP entre el reproductor del navegador y el objeto guardado en MinIO."""
    stream = StorageService().stream_file(
        object_key=file_id,
        range_header=request.headers.get("range"),
        fallback_mime_type=mime_type,
    )
    headers = dict(stream.headers)
    if as_attachment and filename:
        headers["Content-Disposition"] = _content_disposition(filename, mime_type)
        headers["Cache-Control"] = "private, no-store"
    return StreamingResponse(
        stream.chunks,
        status_code=stream.status_code,
        media_type=mime_type,
        headers=headers,
    )


def _content_disposition(filename: str, mime_type: str) -> str:
    """Genera un nombre seguro para descargas sin confiar en el titulo original."""
    safe_name = re.sub(r"[^a-zA-Z0-9._ -]+", "", filename).strip() or "titoflix-video"
    safe_name = re.sub(r"\s+", "-", safe_name)
    extension = mimetypes.guess_extension(mime_type) or ".mp4"
    if not safe_name.lower().endswith(extension.lower()):
        safe_name = f"{safe_name}{extension}"
    encoded_name = quote(safe_name)
    return f"attachment; filename=\"{safe_name}\"; filename*=UTF-8''{encoded_name}"


def _vista_dto_from_request(
    perfil_id: int,
    payload: UpsertVistaSchema,
    episodio_id: int | None = None,
    contenido_id: int | None = None,
) -> CreateVistaDTO:
    """Normaliza payloads de progreso enviados por el frontend."""
    payload_data = payload.model_dump()
    payload_episodio_id = payload_data.pop("episodio_id")
    payload_contenido_id = payload_data.pop("contenido_id")
    episodio_id = episodio_id if episodio_id is not None else payload_episodio_id
    contenido_id = contenido_id if contenido_id is not None else payload_contenido_id
    return CreateVistaDTO(
        perfil_id=perfil_id,
        episodio_id=episodio_id,
        contenido_id=contenido_id,
        **payload_data,
    )


def _calificacion_dto_from_request(
    perfil_id: int,
    contenido_id: int,
    payload: UpsertCalificacionSchema,
) -> CreateCalificacionDTO:
    """Combina la ruta y el body en el DTO usado por la capa de servicio."""
    payload_data = payload.model_dump()
    return CreateCalificacionDTO(
        perfil_id=perfil_id,
        contenido_id=contenido_id,
        **payload_data,
    )


@router.post(
    "/generos",
    response_model=GeneroResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_genero(
    nombre: str,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return GeneroService(db).create(nombre)


@router.get("/generos", response_model=list[GeneroResponseDTO])
def list_generos(db: Session = Depends(get_db)):
    return GeneroService(db).list_all()


@router.delete("/generos/{genero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genero(
    genero_id: int,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    GeneroService(db).delete(genero_id)


@router.post(
    "/contenidos",
    response_model=ContenidoResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_contenido(
    titulo: str = Form(...),
    tipo: str = Form(...),
    anio: int = Form(...),
    clasificacion_edad: str = Form(...),
    descripcion: str | None = Form(default=None),
    generos_ids: list[int] = Form(...),
    portada: UploadFile | None = File(default=None),
    video: UploadFile | None = File(default=None),
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dto = CreateContenidoDTO(
        titulo=titulo,
        tipo=tipo,
        anio=anio,
        descripcion=descripcion,
        clasificacion_edad=clasificacion_edad,
        generos_ids=generos_ids,
    )

    return ContenidoService(db).create_with_video(dto, video, portada)


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


@router.get("/contenidos/{contenido_id}/playback")
def get_contenido_playback(
    contenido_id: int,
    quality: str | None = None,
    current_user: Cuenta = Depends(get_current_user_from_swagger),
    db: Session = Depends(get_db),
):
    """Devuelve al frontend una URL firmada que luego consume el elemento <video>."""
    video = ContenidoService(db).get_video_source(contenido_id, quality)
    token = _create_media_token(current_user, "contenido", contenido_id, quality, "stream")
    return {
        "stream_url": (
            f"/api/v1/contenidos/{contenido_id}/stream"
            f"?token={quote(token)}"
            + (f"&quality={quote(quality)}" if quality else "")
        ),
        "mime_type": video.mime_type,
    }


@router.get("/contenidos/{contenido_id}/stream")
def stream_contenido_video(
    contenido_id: int,
    request: Request,
    token: str,
    quality: str | None = None,
    db: Session = Depends(get_db),
):
    """Stream real de peliculas; soporta Range requests para seek del reproductor."""
    _verify_media_token(token, "contenido", contenido_id, quality, "stream")
    video = ContenidoService(db).get_video_source(contenido_id, quality)
    return _stream_storage_video(video.file_id, video.mime_type, request)


@router.get("/contenidos/{contenido_id}/download")
def download_contenido_video(
    contenido_id: int,
    request: Request,
    quality: str | None = None,
    _current_user: Cuenta = Depends(get_current_user_from_swagger),
    db: Session = Depends(get_db),
):
    video = ContenidoService(db).get_video_source(contenido_id, quality)
    return _stream_storage_video(
        video.file_id,
        video.mime_type,
        request,
        filename=video.filename,
        as_attachment=True,
    )


@router.put("/contenidos/{contenido_id}", response_model=ContenidoResponseDTO)
def update_contenido(
    contenido_id: int,
    titulo: str = Form(...),
    anio: int = Form(...),
    clasificacion_edad: str = Form(...),
    descripcion: str | None = Form(default=None),
    generos_ids: list[int] = Form(...),
    portada: UploadFile | None = File(default=None),
    video: UploadFile | None = File(default=None),
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dto = UpdateContenidoDTO(
        titulo=titulo,
        anio=anio,
        descripcion=descripcion,
        clasificacion_edad=clasificacion_edad,
        generos_ids=generos_ids,
    )

    return ContenidoService(db).update_with_video(contenido_id, dto, video, portada)


@router.delete("/contenidos/{contenido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contenido(
    contenido_id: int,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ContenidoService(db).delete(contenido_id)


@router.post(
    "/temporadas",
    response_model=TemporadaResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_temporada(
    payload: CreateTemporadaSchema,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dto = CreateTemporadaDTO(**payload.model_dump())

    return TemporadaService(db).create(dto)


@router.get("/contenidos/{contenido_id}/temporadas", response_model=list[TemporadaResponseDTO])
def list_temporadas(contenido_id: int, db: Session = Depends(get_db)):
    return TemporadaService(db).list_by_contenido(contenido_id)


@router.delete("/temporadas/{temporada_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_temporada(
    temporada_id: int,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    TemporadaService(db).delete(temporada_id)


@router.put("/temporadas/{temporada_id}", response_model=TemporadaResponseDTO)
def update_temporada(
    temporada_id: int,
    payload: UpdateTemporadaSchema,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dto = UpdateTemporadaDTO(**payload.model_dump(exclude_unset=True))
    return TemporadaService(db).update(temporada_id, dto)


@router.post(
    "/episodios",
    response_model=EpisodioResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_episodio(
    temporada_id: int = Form(...),
    numero: int = Form(...),
    titulo: str = Form(...),
    video: UploadFile = File(...),
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dto = CreateEpisodioDTO(
        temporada_id=temporada_id,
        numero=numero,
        titulo=titulo,
    )

    return EpisodioService(db).create_with_video(dto, video)


@router.get("/temporadas/{temporada_id}/episodios", response_model=list[EpisodioResponseDTO])
def list_episodios(temporada_id: int, db: Session = Depends(get_db)):
    return EpisodioService(db).list_by_temporada(temporada_id)


@router.get("/episodios/{episodio_id}/playback")
def get_episodio_playback(
    episodio_id: int,
    quality: str | None = None,
    current_user: Cuenta = Depends(get_current_user_from_swagger),
    db: Session = Depends(get_db),
):
    """Mismo contrato que peliculas, pero resolviendo el video desde un episodio."""
    video = EpisodioService(db).get_video_source(episodio_id, quality)
    token = _create_media_token(current_user, "episodio", episodio_id, quality, "stream")
    return {
        "stream_url": (
            f"/api/v1/episodios/{episodio_id}/stream"
            f"?token={quote(token)}"
            + (f"&quality={quote(quality)}" if quality else "")
        ),
        "mime_type": video.mime_type,
    }


@router.get("/episodios/{episodio_id}/stream")
def stream_episodio_video(
    episodio_id: int,
    request: Request,
    token: str,
    quality: str | None = None,
    db: Session = Depends(get_db),
):
    """Stream real de episodios; el token evita compartir URLs permanentes."""
    _verify_media_token(token, "episodio", episodio_id, quality, "stream")
    video = EpisodioService(db).get_video_source(episodio_id, quality)
    return _stream_storage_video(video.file_id, video.mime_type, request)


@router.get("/episodios/{episodio_id}/download")
def download_episodio_video(
    episodio_id: int,
    request: Request,
    quality: str | None = None,
    _current_user: Cuenta = Depends(get_current_user_from_swagger),
    db: Session = Depends(get_db),
):
    video = EpisodioService(db).get_video_source(episodio_id, quality)
    return _stream_storage_video(
        video.file_id,
        video.mime_type,
        request,
        filename=video.filename,
        as_attachment=True,
    )


@router.delete("/episodios/{episodio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_episodio(
    episodio_id: int,
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    EpisodioService(db).delete(episodio_id)


@router.put("/episodios/{episodio_id}", response_model=EpisodioResponseDTO)
def update_episodio(
    episodio_id: int,
    numero: int = Form(...),
    titulo: str = Form(...),
    video: UploadFile | None = File(default=None),
    _admin: Cuenta = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dto = UpdateEpisodioDTO(numero=numero, titulo=titulo)
    return EpisodioService(db).update_with_video(episodio_id, dto, video)


@router.post(
    "/perfiles/{perfil_id}/vistas",
    response_model=VistaResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_vista_recurso(
    perfil_id: int,
    payload: UpsertVistaSchema,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    """Registra progreso de reproduccion para continuar viendo."""
    dto = _vista_dto_from_request(
        perfil_id=profile.id,
        payload=payload,
    )
    return VistaService(db).create_or_update(dto)


@router.put(
    "/perfiles/{perfil_id}/vistas",
    response_model=VistaResponseDTO,
)
def update_vista_recurso(
    perfil_id: int,
    payload: UpsertVistaSchema,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    dto = _vista_dto_from_request(
        perfil_id=profile.id,
        payload=payload,
    )
    return VistaService(db).create_or_update(dto)


@router.delete(
    "/perfiles/{perfil_id}/vistas",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vista_recurso(
    perfil_id: int,
    episodio_id: int | None = None,
    contenido_id: int | None = None,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    VistaService(db).delete(
        perfil_id=profile.id,
        episodio_id=episodio_id,
        contenido_id=contenido_id,
    )


@router.get("/perfiles/{perfil_id}/continuar", response_model=list[ContinuarViendoDTO])
def continuar_viendo(
    perfil_id: int,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    """Lista items incompletos que el frontend muestra en la fila Continuar viendo."""
    return VistaService(db).continuar_viendo(profile.id)


@router.post("/perfiles/{perfil_id}/mi-lista", response_model=list[ContenidoResponseDTO])
def add_to_mi_lista(
    perfil_id: int,
    payload: MiListaSchema,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    """Agrega contenido a la lista personal del perfil autenticado."""
    return MiListaService(db).add(profile.id, payload.contenido_id)


@router.get("/perfiles/{perfil_id}/mi-lista", response_model=list[ContenidoResponseDTO])
def get_mi_lista(
    perfil_id: int,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    return MiListaService(db).list(profile.id)


@router.delete("/perfiles/{perfil_id}/mi-lista/{contenido_id}", response_model=list[ContenidoResponseDTO])
def remove_from_mi_lista(
    perfil_id: int,
    contenido_id: int,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    return MiListaService(db).remove(profile.id, contenido_id)


@router.post(
    "/perfiles/{perfil_id}/calificaciones/{contenido_id}",
    response_model=CalificacionResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_calificacion(
    perfil_id: int,
    contenido_id: int,
    payload: UpsertCalificacionSchema,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    dto = _calificacion_dto_from_request(profile.id, contenido_id, payload)
    return CalificacionService(db).create_or_update(dto)


@router.put(
    "/perfiles/{perfil_id}/calificaciones/{contenido_id}",
    response_model=CalificacionResponseDTO,
)
def update_calificacion(
    perfil_id: int,
    contenido_id: int,
    payload: UpsertCalificacionSchema,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    dto = _calificacion_dto_from_request(profile.id, contenido_id, payload)
    return CalificacionService(db).create_or_update(dto)


@router.delete(
    "/perfiles/{perfil_id}/calificaciones/{contenido_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_calificacion(
    perfil_id: int,
    contenido_id: int,
    profile: Perfil = Depends(get_owned_profile),
    db: Session = Depends(get_db),
):
    CalificacionService(db).delete(profile.id, contenido_id)
