import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, get_db, get_session_factory
from app.models import Event, MediaItem, RSVPGuest, User, ZipJob
from app.routers.auth import get_current_user
from app.schemas import AdminDashboardMetrics, MediaItemRead, MediaModerateRequest, ZipJobRead
from app.services.zip_packager import process_zip_job

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
    background_tasks: BackgroundTasks,
    event: Event = Depends(get_host_event),
    db: AsyncSession = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Registra una peticion de empaquetado ZIP masivo y la procesa en segundo plano."""
    zip_job = ZipJob(
        event_id=event.id,
        status="pending",
    )
    db.add(zip_job)
    await db.commit()
    await db.refresh(zip_job)

    background_tasks.add_task(process_zip_job, zip_job.id, session_factory)
    return zip_job


@router.get("/events/{slug}/zip-jobs", response_model=List[ZipJobRead])
async def list_zip_jobs(
    slug: str,
    event: Event = Depends(get_host_event),
    db: AsyncSession = Depends(get_db),
):
    """Lista el historial de exportaciones ZIP solicitadas para el evento."""
    stmt = (
        select(ZipJob)
        .where(ZipJob.event_id == event.id)
        .order_by(ZipJob.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/events/{slug}/zip-jobs/{job_id}", response_model=ZipJobRead)
async def get_zip_job_status(
    slug: str,
    job_id: uuid.UUID,
    event: Event = Depends(get_host_event),
    db: AsyncSession = Depends(get_db),
):
    """Consulta el estado y enlace de descarga de una exportacion ZIP especifica."""
    stmt = select(ZipJob).where(ZipJob.id == job_id, ZipJob.event_id == event.id)
    job = (await db.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajo de exportacion ZIP no encontrado",
        )
    return job
