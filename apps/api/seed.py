import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models import User, Event, RSVPGuest
from app.routers.auth import get_password_hash


async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Verificar si el usuario ya existe
        stmt = select(User).where(User.email == "anfitrion@vocatus-animus.com")
        existing_user = (await session.execute(stmt)).scalar_one_or_none()

        if not existing_user:
            host = User(
                id=uuid.uuid4(),
                email="anfitrion@vocatus-animus.com",
                password_hash=get_password_hash("Secret123!"),
                full_name="Carlos Martinez & Sofia Garza",
            )
            session.add(host)
            await session.flush()
        else:
            host = existing_user

        # Verificar si el evento ya existe
        stmt_event = select(Event).where(Event.slug == "boda-carlos-y-sofia")
        existing_event = (await session.execute(stmt_event)).scalar_one_or_none()

        if not existing_event:
            event = Event(
                id=uuid.uuid4(),
                host_id=host.id,
                slug="boda-carlos-y-sofia",
                title="Boda Carlos & Sofia",
                event_date=datetime(2026, 10, 25, 18, 0, 0, tzinfo=timezone.utc),
                event_type="boda",
                tier="sincronia_total",
                pin_code="4821",
                storage_limit_bytes=16106127360,  # 15 GB
                storage_used_bytes=0,
                location_name="Hacienda de los Morales",
                location_address="Vazquez de Mella 525, Polanco, CDMX",
                location_maps_url="https://maps.google.com/?q=Hacienda+de+los+Morales",
                location_waze_url="https://waze.com/ul?q=Hacienda+de+los+Morales",
                dress_code="Rigurosa Etiqueta / Black Tie",
                gift_registry_info="Liverpool: 51239485 | El Palacio de Hierro: 982341",
                itinerary="18:00 Ceremonia Religiosa | 19:30 Coctel de Bienvenida | 21:00 Cena y Brindis | 23:00 Apertura de Pista",
                is_active=True,
            )
            session.add(event)
            await session.flush()

            # Agregar invitados de prueba
            guests_data = [
                ("Familia Morales Lopez", "morales@ejemplo.com", 4),
                ("Alejandro Gomez", "alejandro@ejemplo.com", 2),
                ("Dra. Valentina Ruiz", "valentina@ejemplo.com", 1),
            ]

            for name, contact, passes in guests_data:
                guest = RSVPGuest(
                    id=uuid.uuid4(),
                    event_id=event.id,
                    guest_name=name,
                    phone_or_email=contact,
                    allocated_passes=passes,
                    confirmed_passes=0,
                    status="pending",
                )
                session.add(guest)

            await session.commit()
            print("Datos semilla creados con exito para evento: boda-carlos-y-sofia")
        else:
            print("El evento demo ya existe en la base de datos.")


if __name__ == "__main__":
    asyncio.run(seed_data())
