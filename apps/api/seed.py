import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models import Event, MediaItem, RSVPGuest, User, ZipJob
from app.routers.auth import get_password_hash
from app.services.storage import storage_service

DEMO_MEDIA = [
    {
        "filename": "ceremonia.jpg",
        "content_type": "image/jpeg",
        "guest_author": "Carlos M.",
        "url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=1600&auto=format&fit=crop&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=400&auto=format&fit=crop&q=80",
        "size_bytes": 2450000,
    },
    {
        "filename": "novios_brindis.jpg",
        "content_type": "image/jpeg",
        "guest_author": "Sofia G.",
        "url": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=1600&auto=format&fit=crop&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=400&auto=format&fit=crop&q=80",
        "size_bytes": 3100000,
    },
    {
        "filename": "baile.jpg",
        "content_type": "image/jpeg",
        "guest_author": "Tia Carmen",
        "url": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=1600&auto=format&fit=crop&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=400&auto=format&fit=crop&q=80",
        "size_bytes": 1890000,
    },
    {
        "filename": "recepcion.jpg",
        "content_type": "image/jpeg",
        "guest_author": "Alejandro",
        "url": "https://images.unsplash.com/photo-1520854221256-17451cc331bf?w=1600&auto=format&fit=crop&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1520854221256-17451cc331bf?w=400&auto=format&fit=crop&q=80",
        "size_bytes": 4200000,
    },
    {
        "filename": "anillos.jpg",
        "content_type": "image/jpeg",
        "guest_author": "Familia Morales",
        "url": "https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=1600&auto=format&fit=crop&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=400&auto=format&fit=crop&q=80",
        "size_bytes": 1950000,
    },
    {
        "filename": "pastel.jpg",
        "content_type": "image/jpeg",
        "guest_author": "Roberto",
        "url": "https://images.unsplash.com/photo-1535295972055-1c762f4483e5?w=1600&auto=format&fit=crop&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1535295972055-1c762f4483e5?w=400&auto=format&fit=crop&q=80",
        "size_bytes": 2800000,
    },
]


async def seed():
    # 1. Asegurar tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 2. Host
        stmt = select(User).where(User.email == "carlos@ejemplo.com")
        host = (await db.execute(stmt)).scalar_one_or_none()
        if not host:
            host = User(
                id=uuid.uuid4(),
                email="carlos@ejemplo.com",
                password_hash=get_password_hash("admin123"),
                full_name="Carlos Morales",
            )
            db.add(host)
            await db.flush()

        # 3. Evento
        event_stmt = select(Event).where(Event.slug == "boda-carlos-y-sofia")
        event = (await db.execute(event_stmt)).scalar_one_or_none()
        if not event:
            total_media_size = sum(m["size_bytes"] for m in DEMO_MEDIA)
            event = Event(
                id=uuid.uuid4(),
                host_id=host.id,
                slug="boda-carlos-y-sofia",
                title="Boda Carlos & Sofia",
                event_date=datetime(2026, 10, 25, 18, 0, 0, tzinfo=timezone.utc),
                event_type="boda",
                tier="legado_pro",
                pin_code="4821",
                storage_limit_bytes=50 * 1024 * 1024 * 1024,  # 50 GB
                storage_used_bytes=total_media_size,
                is_active=True,
            )
            db.add(event)
            await db.flush()

        # 4. Invitados RSVP
        guests_data = [
            ("Familia Morales", "morales@familia.com", 4, 4, "confirmed", "Sin mariscos", "Muchas felicidades a los dos"),
            ("Sofia Gutierrez", "sofia@amiga.com", 2, 2, "confirmed", "Vegetariana", "Los queremos mucho"),
            ("Tia Carmen", "carmen@tia.com", 2, 1, "confirmed", None, "Que viva el amor"),
            ("Alejandro Ruiz", "alex@amigo.com", 1, 0, "pending", None, None),
            ("Roberto Gomez", "roberto@compa.com", 2, 0, "pending", None, None),
        ]

        for name, email, allocated, confirmed, status, dietary, msg in guests_data:
            g_check = (await db.execute(
                select(RSVPGuest).where(RSVPGuest.event_id == event.id, RSVPGuest.guest_name == name)
            )).scalar_one_or_none()
            if not g_check:
                g = RSVPGuest(
                    id=uuid.uuid4(),
                    event_id=event.id,
                    guest_name=name,
                    phone_or_email=email,
                    allocated_passes=allocated,
                    confirmed_passes=confirmed,
                    status=status,
                    dietary_restrictions=dietary,
                    message=msg,
                )
                db.add(g)

        # 5. Fotos del evento
        for m in DEMO_MEDIA:
            m_check = (await db.execute(
                select(MediaItem).where(MediaItem.event_id == event.id, MediaItem.filename == m["filename"])
            )).scalar_one_or_none()
            if not m_check:
                item = MediaItem(
                    id=uuid.uuid4(),
                    event_id=event.id,
                    r2_key=f"events/{event.slug}/media/{m['filename']}",
                    thumb_r2_key=f"events/{event.slug}/thumbs/{m['filename']}",
                    filename=m["filename"],
                    content_type=m["content_type"],
                    size_bytes=m["size_bytes"],
                    guest_author=m["guest_author"],
                    moderation_status="approved",
                )
                db.add(item)

        await db.commit()
        print("Base de datos inicializada y sembrada con exito:")
        print(f"- Anfitrion: {host.email} (Contrasena: admin123)")
        print(f"- Evento: {event.title} (Slug: {event.slug}, PIN: {event.pin_code})")
        print(f"- Invitados RSVP y recuerdos multimedia cargados.")


if __name__ == "__main__":
    asyncio.run(seed())
