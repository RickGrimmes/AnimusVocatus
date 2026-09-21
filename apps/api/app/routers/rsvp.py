import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Event, RSVPGuest
from app.schemas import (
    EventPublicVocatus,
    RSVPConfirmSubmit,
    RSVPGuestRead,
    RSVPGuestSearchItem,
)

router = APIRouter(prefix="/api/v", tags=["Vocatus RSVP"])


@router.get("/{slug}", response_model=EventPublicVocatus)
async def get_public_invitation(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la informacion publica de la invitacion para el modulo Vocatus."""
    stmt = select(Event).where(Event.slug == slug, Event.is_active == True)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o inactivo",
        )
    return event


@router.get("/{slug}/search", response_model=List[RSVPGuestSearchItem])
async def search_event_guests(
    slug: str,
    q: str = Query(..., min_length=2, description="Nombre o apellido del invitado a buscar"),
    db: AsyncSession = Depends(get_db),
):
    """Busca invitados asignados a un evento por coincidencia de nombre."""
    stmt_event = select(Event).where(Event.slug == slug, Event.is_active == True)
    event = (await db.execute(stmt_event)).scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o inactivo",
        )

    search_pattern = f"%{q.strip()}%"
    stmt = (
        select(RSVPGuest)
        .where(
            RSVPGuest.event_id == event.id,
            RSVPGuest.guest_name.ilike(search_pattern),
        )
        .order_by(RSVPGuest.guest_name.asc())
        .limit(20)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{slug}/guests/{guest_id}", response_model=RSVPGuestRead)
async def get_guest_passes(
    slug: str,
    guest_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Consulta la informacion y pases asignados a un invitado especifico."""
    stmt = (
        select(RSVPGuest)
        .join(Event)
        .where(Event.slug == slug, Event.is_active == True, RSVPGuest.id == guest_id)
    )
    result = await db.execute(stmt)
    guest = result.scalar_one_or_none()

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitado no encontrado para este evento",
        )
    return guest


@router.post("/{slug}/rsvp", response_model=RSVPGuestRead)
async def submit_rsvp(
    slug: str,
    payload: RSVPConfirmSubmit,
    db: AsyncSession = Depends(get_db),
):
    """Registra o actualiza la confirmacion de asistencia y pases del invitado."""
    stmt_event = select(Event).where(Event.slug == slug, Event.is_active == True)
    event = (await db.execute(stmt_event)).scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado o inactivo",
        )

    guest = None

    if payload.guest_id:
        stmt_guest = select(RSVPGuest).where(
            RSVPGuest.id == payload.guest_id,
            RSVPGuest.event_id == event.id,
        )
        guest = (await db.execute(stmt_guest)).scalar_one_or_none()

    if not guest and payload.guest_name:
        stmt_guest_name = select(RSVPGuest).where(
            RSVPGuest.event_id == event.id,
            func.lower(RSVPGuest.guest_name) == payload.guest_name.strip().lower(),
        )
        guest = (await db.execute(stmt_guest_name)).scalar_one_or_none()

    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontro el pase de invitado especificado",
        )

    if payload.status == "confirmed":
        if payload.confirmed_passes > guest.allocated_passes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Los pases confirmados ({payload.confirmed_passes}) no pueden exceder los asignados ({guest.allocated_passes})",
            )
        guest.confirmed_passes = payload.confirmed_passes
    else:
        guest.confirmed_passes = 0

    guest.status = payload.status
    guest.dietary_restrictions = payload.dietary_restrictions
    guest.message = payload.message
    guest.confirmed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(guest)
    return guest


@router.post("/{slug}/rsvp/{guest_id}", response_model=RSVPGuestRead)
async def submit_rsvp_by_id(
    slug: str,
    guest_id: uuid.UUID,
    payload: RSVPConfirmSubmit,
    db: AsyncSession = Depends(get_db),
):
    """Variante directa para confirmar pasando el ID del invitado en la ruta."""
    payload.guest_id = guest_id
    return await submit_rsvp(slug=slug, payload=payload, db=db)
