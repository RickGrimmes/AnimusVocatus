import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Event, MediaItem, RSVPGuest, User, ZipJob
from app.routers.auth import get_current_user
from app.schemas import AdminDashboardMetrics, MediaItemRead, MediaModerateRequest, ZipJobRead

router = APIRouter(prefix="/api/admin", tags=["Admin"])


async def get_host_event(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Event:
    stmt = select(Event).where(Event.slug == slug, Event.host_id == current_user.id)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o no pertenece a tu cuenta",
        )
    return event


@router.get("/events/{slug}/dashboard", response_model=AdminDashboardMetrics)
async def get_admin_dashboard(
    slug: str,
    event: Event = Depends(get_host_event),
    db: AsyncSession = Depends(get_db),
):
    """Metricas consolidadas del evento para el anfitrion."""
    # Metricas de RSVPs
    rsvp_stmt = select(
        func.coalesce(func.sum(RSVPGuest.allocated_passes), 0),
        func.coalesce(func.sum(RSVPGuest.confirmed_passes), 0),
        func.count().filter(RSVPGuest.status == "declined"),
        func.count().filter(RSVPGuest.status == "pending"),
    ).where(RSVPGuest.event_id == event.id)

    rsvp_res = (await db.execute(rsvp_stmt)).one()
    allocated, confirmed, declined, pending = rsvp_res

    # Conteo de fotos
    media_count_stmt = select(func.count(MediaItem.id)).where(MediaItem.event_id == event.id)
    photos_count = (await db.execute(media_count_stmt)).scalar() or 0

    storage_percent = (
        (event.storage_used_bytes / event.storage_limit_bytes * 100)
        if event.storage_limit_bytes > 0
        else 0.0
    )

    return AdminDashboardMetrics(
        event=event,
        total_allocated_passes=allocated,
        total_confirmed_passes=confirmed,
        total_declined_guests=declined,
        total_pending_guests=pending,
        total_photos_count=photos_count,
        storage_used_bytes=event.storage_used_bytes,
        storage_limit_bytes=event.storage_limit_bytes,
        storage_usage_percent=round(storage_percent, 2),
    )


@router.patch("/media/{media_id}/moderate", response_model=MediaItemRead)
async def moderate_media_item(
    media_id: uuid.UUID,
    payload: MediaModerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cambia el estado de moderacion o marca como favorita una foto."""
    stmt = (
        select(MediaItem)
        .join(Event)
        .where(MediaItem.id == media_id, Event.host_id == current_user.id)
    )
    media_item = (await db.execute(stmt)).scalar_one_or_none()
    if not media_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento multimedia no encontrado",
        )

    if payload.moderation_status is not None:
        media_item.moderation_status = payload.moderation_status
    if payload.is_favorite is not None:
        media_item.is_favorite = payload.is_favorite

    await db.commit()
    await db.refresh(media_item)
    return media_item


@router.post("/events/{slug}/request-zip", response_model=ZipJobRead)
async def request_zip_export(
    slug: str,
    event: Event = Depends(get_host_event),
    db: AsyncSession = Depends(get_db),
):
    """Registra una peticion de empaquetado ZIP masivo."""
    zip_job = ZipJob(
        event_id=event.id,
        status="pending",
    )
    db.add(zip_job)
    await db.commit()
    await db.refresh(zip_job)
    return zip_job
