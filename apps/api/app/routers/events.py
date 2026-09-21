from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventRead, EventPublicVocatus

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("/v/{slug}", response_model=EventPublicVocatus)
async def get_public_event_vocatus(slug: str, db: AsyncSession = Depends(get_db)):
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
