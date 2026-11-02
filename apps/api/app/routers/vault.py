import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from jose import JWTError, jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models import Event, MediaItem, GuestbookMessage
from app.schemas import (
    AnimusEventInfo,
    BatchPresignedRequest,
    BatchPresignedResponse,
    GuestAuthResponse,
    GuestEnterRequest,
    GuestbookMessageCreate,
    GuestbookMessageRead,
    MediaItemConfirm,
    MediaItemRead,
    PresignedUrlItem,
)
from app.services.storage import storage_service

router = APIRouter(prefix="/api/a", tags=["Animus Vault"])

ALLOWED_MIME_TYPES = {
    "image/jpeg": {"max_bytes": 25 * 1024 * 1024, "ext": "jpg"},
    "image/png": {"max_bytes": 25 * 1024 * 1024, "ext": "png"},
    "image/webp": {"max_bytes": 25 * 1024 * 1024, "ext": "webp"},
    "video/mp4": {"max_bytes": 150 * 1024 * 1024, "ext": "mp4"},
    "video/quicktime": {"max_bytes": 150 * 1024 * 1024, "ext": "mov"},
    "audio/webm": {"max_bytes": 25 * 1024 * 1024, "ext": "webm"},
    "audio/mp4": {"max_bytes": 25 * 1024 * 1024, "ext": "m4a"},
    "audio/mpeg": {"max_bytes": 25 * 1024 * 1024, "ext": "mp3"},
    "audio/ogg": {"max_bytes": 25 * 1024 * 1024, "ext": "ogg"},
    "audio/wav": {"max_bytes": 25 * 1024 * 1024, "ext": "wav"},
}


def create_guest_token(event_id: str, slug: str) -> str:
    expires = timedelta(hours=settings.GUEST_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": f"guest-{event_id}",
        "event_id": event_id,
        "slug": slug,
        "role": "guest",
        "exp": datetime.now(timezone.utc) + expires,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def verify_guest_or_host(
    slug: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Event:
    stmt = select(Event).where(Event.slug == slug, Event.is_active == True)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o inactivo",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido",
        )

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_role = payload.get("role")
        token_event_id = payload.get("event_id")
        user_id = payload.get("sub")

        if token_role == "guest":
            if token_event_id != str(event.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token no valido para este evento",
                )
        elif token_role == "host":
            if str(event.host_id) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El anfitrion no tiene permisos sobre este evento",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol no autorizado",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    return event


def attach_media_urls(item: MediaItem) -> MediaItemRead:
    read_item = MediaItemRead.model_validate(item)
    read_item.url = storage_service.get_file_url(item.r2_key)
    read_item.thumb_url = storage_service.get_file_url(item.thumb_r2_key) if item.thumb_r2_key else read_item.url
    return read_item


@router.get("/{slug}/info", response_model=AnimusEventInfo)
async def get_vault_public_info(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Informacion basica del evento antes de que el invitado ingrese el PIN."""
    stmt = select(Event).where(Event.slug == slug, Event.is_active == True)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o inactivo",
        )
    return event


@router.post("/{slug}/enter", response_model=GuestAuthResponse)
async def enter_vault_with_pin(
    slug: str,
    payload: GuestEnterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Valida el PIN de 4 digitos y emite el JWT efimero para el invitado."""
    stmt = select(Event).where(Event.slug == slug, Event.is_active == True)
    event = (await db.execute(stmt)).scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o inactivo",
        )

    if event.pin_code != payload.pin.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN incorrecto",
        )

    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    return GuestAuthResponse(access_token=token, event_slug=event.slug)


@router.post("/{slug}/batch-presigned", response_model=BatchPresignedResponse)
async def request_batch_presigned_urls(
    slug: str,
    payload: BatchPresignedRequest,
    event: Event = Depends(verify_guest_or_host),
):
    """Valida cuota y tipos de archivo, generando URLs prefirmadas directas a Cloudflare R2."""
    if not payload.files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La lista de archivos no puede estar vacia",
        )

    total_batch_size = sum(f.size_bytes for f in payload.files)
    if event.storage_used_bytes + total_batch_size > event.storage_limit_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Se ha superado el limite de almacenamiento contratado para este evento",
        )

    items: List[PresignedUrlItem] = []

    for file in payload.files:
        clean_mime = file.content_type.split(";")[0].strip().lower()
        if clean_mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Formato no permitido: {clean_mime}",
            )

        limit = ALLOWED_MIME_TYPES[clean_mime]["max_bytes"]
        if file.size_bytes > limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo {file.filename} excede el tamano maximo permitido ({limit // (1024 * 1024)} MB)",
            )

        file_id = uuid.uuid4()
        ext = ALLOWED_MIME_TYPES[clean_mime]["ext"]
        r2_key = f"events/{slug}/media/{file_id}.{ext}"
        upload_url = storage_service.generate_presigned_upload_url(
            r2_key=r2_key,
            content_type=clean_mime,
        )

        thumb_r2_key = None
        thumb_upload_url = None
        # Miniatura WebP tanto para imagenes como para fotogramas extraidos de videos
        if clean_mime.startswith("image/") or clean_mime.startswith("video/"):
            thumb_r2_key = f"events/{slug}/thumbs/{file_id}.webp"
            thumb_upload_url = storage_service.generate_presigned_upload_url(
                r2_key=thumb_r2_key,
                content_type="image/webp",
            )

        items.append(
            PresignedUrlItem(
                file_id=file_id,
                filename=file.filename,
                upload_url=upload_url,
                r2_key=r2_key,
                thumb_upload_url=thumb_upload_url,
                thumb_r2_key=thumb_r2_key,
            )
        )

    return BatchPresignedResponse(items=items)


@router.post("/{slug}/media/confirm", response_model=MediaItemRead)
async def confirm_media_upload(
    slug: str,
    payload: MediaItemConfirm,
    event: Event = Depends(verify_guest_or_host),
    db: AsyncSession = Depends(get_db),
):
    """Asienta el registro del archivo en base de datos e incrementa el almacenamiento ocupado."""
    # Validacion de idempotencia
    stmt_check = select(MediaItem).where(MediaItem.id == payload.id)
    existing = (await db.execute(stmt_check)).scalar_one_or_none()
    if existing:
        return attach_media_urls(existing)

    media_item = MediaItem(
        id=payload.id,
        event_id=event.id,
        r2_key=payload.r2_key,
        thumb_r2_key=payload.thumb_r2_key,
        filename=payload.filename,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
        guest_author=payload.guest_author,
        moderation_status="approved",
    )
    db.add(media_item)

    event.storage_used_bytes += payload.size_bytes
    await db.commit()
    await db.refresh(media_item)
    return attach_media_urls(media_item)


@router.get("/{slug}/feed", response_model=List[MediaItemRead])
async def get_event_feed(
    slug: str,
    media_type: Optional[str] = Query(None, description="Filtro: photo, video, audio"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Feed publico de medios aprobados (fotos, videos o audios)."""
    conditions = [
        Event.slug == slug,
        Event.is_active == True,
        MediaItem.moderation_status == "approved",
    ]

    if media_type == "photo":
        conditions.append(MediaItem.content_type.like("image/%"))
    elif media_type == "video":
        conditions.append(MediaItem.content_type.like("video/%"))
    elif media_type == "audio":
        conditions.append(MediaItem.content_type.like("audio/%"))

    stmt = (
        select(MediaItem)
        .join(Event)
        .where(*conditions)
        .order_by(MediaItem.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [attach_media_urls(item) for item in items]


@router.get("/{slug}/stats")
async def get_event_vault_stats(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Estadisticas consolidadas de recuerdos: fotos, videos, mensajes y notas de voz."""
    stmt_event = select(Event).where(Event.slug == slug, Event.is_active == True)
    event = (await db.execute(stmt_event)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")

    stmt_photos = select(func.count(MediaItem.id)).where(
        MediaItem.event_id == event.id,
        MediaItem.moderation_status == "approved",
        MediaItem.content_type.like("image/%"),
    )
    stmt_videos = select(func.count(MediaItem.id)).where(
        MediaItem.event_id == event.id,
        MediaItem.moderation_status == "approved",
        MediaItem.content_type.like("video/%"),
    )
    stmt_audios = select(func.count(MediaItem.id)).where(
        MediaItem.event_id == event.id,
        MediaItem.moderation_status == "approved",
        MediaItem.content_type.like("audio/%"),
    )
    stmt_messages = select(func.count(GuestbookMessage.id)).where(
        GuestbookMessage.event_id == event.id,
        GuestbookMessage.moderation_status == "approved",
    )

    photos_count = (await db.execute(stmt_photos)).scalar() or 0
    videos_count = (await db.execute(stmt_videos)).scalar() or 0
    audios_count = (await db.execute(stmt_audios)).scalar() or 0
    messages_count = (await db.execute(stmt_messages)).scalar() or 0

    return {
        "photos": photos_count,
        "videos": videos_count,
        "audios": audios_count,
        "messages": messages_count,
        "total_media": photos_count + videos_count + audios_count,
    }


@router.get("/{slug}/messages", response_model=List[GuestbookMessageRead])
async def get_guestbook_messages(
    slug: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene dedicatorias y firmas dejadas por los invitados."""
    stmt = (
        select(GuestbookMessage)
        .join(Event)
        .where(
            Event.slug == slug,
            Event.is_active == True,
            GuestbookMessage.moderation_status == "approved",
        )
        .order_by(GuestbookMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{slug}/messages", response_model=GuestbookMessageRead)
async def create_guestbook_message(
    slug: str,
    payload: GuestbookMessageCreate,
    event: Event = Depends(verify_guest_or_host),
    db: AsyncSession = Depends(get_db),
):
    """Crea una nueva dedicatoria o mensaje en el libro de firmas."""
    new_message = GuestbookMessage(
        event_id=event.id,
        author_name=payload.author_name.strip(),
        message=payload.message.strip(),
        moderation_status="approved",
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


@router.put("/upload-mock")
async def mock_upload_file(request: Request, key: str = Query(...)):
    """Guarda archivos localmente cuando no hay bucket Cloudflare R2 configurado."""
    from pathlib import Path
    body = await request.body()
    uploads_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
    file_path = uploads_dir / key
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(body)
    return {"status": "ok", "key": key, "bytes": len(body)}

