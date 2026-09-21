import uuid
from datetime import datetime, timezone
import pytest
from app.models import Event, RSVPGuest, User


async def create_demo_event(session) -> tuple[Event, list[RSVPGuest]]:
    host = User(
        id=uuid.uuid4(),
        email="host@test.com",
        password_hash="hashed_pw",
        full_name="Host Test",
    )
    session.add(host)
    await session.flush()

    event = Event(
        id=uuid.uuid4(),
        host_id=host.id,
        slug="boda-carlos-y-sofia",
        title="Boda Carlos & Sofia",
        event_date=datetime(2026, 10, 25, 18, 0, 0, tzinfo=timezone.utc),
        event_type="boda",
        tier="sincronia_total",
        pin_code="4821",
        storage_limit_bytes=16106127360,
        storage_used_bytes=0,
        location_name="Hacienda de los Morales",
        location_address="Vazquez de Mella 525, Polanco",
        location_maps_url="https://maps.google.com/?q=hacienda",
        location_waze_url="https://waze.com/ul?q=hacienda",
        dress_code="Rigurosa Etiqueta",
        itinerary="18:00 Misa | 20:00 Recepcion",
        gift_registry_info="Mesa Liverpool 12345",
        is_active=True,
    )
    session.add(event)
    await session.flush()

    guest1 = RSVPGuest(
        id=uuid.uuid4(),
        event_id=event.id,
        guest_name="Familia Morales Lopez",
        phone_or_email="morales@test.com",
        allocated_passes=4,
        confirmed_passes=0,
        status="pending",
    )
    guest2 = RSVPGuest(
        id=uuid.uuid4(),
        event_id=event.id,
        guest_name="Alejandro Gomez",
        phone_or_email="alejandro@test.com",
        allocated_passes=2,
        confirmed_passes=0,
        status="pending",
    )
    session.add_all([guest1, guest2])
    await session.commit()

    return event, [guest1, guest2]


@pytest.mark.asyncio
async def test_get_public_invitation_success(client, db_session):
    event, _ = await create_demo_event(db_session)

    response = await client.get(f"/api/v/{event.slug}")
    assert response.status_code == 200
    data = response.json()

    assert data["slug"] == event.slug
    assert data["title"] == "Boda Carlos & Sofia"
    assert data["location_name"] == "Hacienda de los Morales"
    assert data["dress_code"] == "Rigurosa Etiqueta"
    assert data["is_active"] is True

    # Comprobacion de privacidad: no debe exponer pin_code ni host_id
    assert "pin_code" not in data
    assert "host_id" not in data
    assert "storage_limit_bytes" not in data


@pytest.mark.asyncio
async def test_get_public_invitation_not_found(client):
    response = await client.get("/api/v/evento-inexistente")
    assert response.status_code == 404
    assert response.json()["detail"] == "Evento no encontrado o inactivo"


@pytest.mark.asyncio
async def test_search_guests_by_name(client, db_session):
    event, guests = await create_demo_event(db_session)

    # Busqueda parcial case-insensitive
    response = await client.get(f"/api/v/{event.slug}/search?q=morales")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["guest_name"] == "Familia Morales Lopez"
    assert data[0]["allocated_passes"] == 4
    assert data[0]["confirmed_passes"] == 0


@pytest.mark.asyncio
async def test_search_guests_min_length_validation(client, db_session):
    event, _ = await create_demo_event(db_session)

    # Parametro menor a 2 caracteres debe ser rechazado
    response = await client.get(f"/api/v/{event.slug}/search?q=a")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_guest_passes_by_id(client, db_session):
    event, guests = await create_demo_event(db_session)
    guest = guests[0]

    response = await client.get(f"/api/v/{event.slug}/guests/{guest.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["guest_name"] == guest.guest_name
    assert data["allocated_passes"] == 4
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_submit_rsvp_confirmation_success(client, db_session):
    event, guests = await create_demo_event(db_session)
    guest = guests[0]  # allocated_passes: 4

    payload = {
        "guest_id": str(guest.id),
        "confirmed_passes": 3,
        "status": "confirmed",
        "dietary_restrictions": "Sin gluten",
        "message": "Felicidades a los novios!",
    }

    response = await client.post(f"/api/v/{event.slug}/rsvp", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "confirmed"
    assert data["confirmed_passes"] == 3
    assert data["dietary_restrictions"] == "Sin gluten"
    assert data["message"] == "Felicidades a los novios!"
    assert data["confirmed_at"] is not None


@pytest.mark.asyncio
async def test_submit_rsvp_over_allocation_rejected(client, db_session):
    event, guests = await create_demo_event(db_session)
    guest = guests[1]  # allocated_passes: 2

    payload = {
        "guest_id": str(guest.id),
        "confirmed_passes": 3,  # Excede los 2 asignados
        "status": "confirmed",
    }

    response = await client.post(f"/api/v/{event.slug}/rsvp", json=payload)
    assert response.status_code == 400
    assert "no pueden exceder los asignados" in response.json()["detail"]


@pytest.mark.asyncio
async def test_submit_rsvp_declined_resets_passes(client, db_session):
    event, guests = await create_demo_event(db_session)
    guest = guests[0]

    payload = {
        "guest_id": str(guest.id),
        "confirmed_passes": 2,
        "status": "declined",
        "message": "Lamentablemente no podremos asistir",
    }

    response = await client.post(f"/api/v/{event.slug}/rsvp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "declined"
    assert data["confirmed_passes"] == 0


@pytest.mark.asyncio
async def test_submit_rsvp_by_name_without_id(client, db_session):
    event, _ = await create_demo_event(db_session)

    payload = {
        "guest_name": "Alejandro Gomez",
        "confirmed_passes": 2,
        "status": "confirmed",
        "message": "Ahi estare con gusto!",
    }

    response = await client.post(f"/api/v/{event.slug}/rsvp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["guest_name"] == "Alejandro Gomez"
    assert data["confirmed_passes"] == 2
    assert data["status"] == "confirmed"
