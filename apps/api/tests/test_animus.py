import uuid
from datetime import datetime, timezone
import pytest
from app.models import Event, MediaItem, User
from app.routers.vault import create_guest_token


async def create_demo_event(session) -> Event:
    host = User(
        id=uuid.uuid4(),
        email="host_animus@test.com",
        password_hash="hashed_pw",
        full_name="Host Animus",
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
        storage_limit_bytes=100 * 1024 * 1024,  # 100 MB para prueba de cuota
        storage_used_bytes=0,
        is_active=True,
    )
    session.add(event)
    await session.commit()
    return event


@pytest.mark.asyncio
async def test_get_vault_info_success(client, db_session):
    event = await create_demo_event(db_session)

    response = await client.get(f"/api/a/{event.slug}/info")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == event.slug
    assert data["title"] == "Boda Carlos & Sofia"
    assert "pin_code" not in data


@pytest.mark.asyncio
async def test_get_vault_info_not_found(client):
    response = await client.get("/api/a/evento-inexistente/info")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_enter_vault_with_valid_pin(client, db_session):
    event = await create_demo_event(db_session)

    response = await client.post(
        f"/api/a/{event.slug}/enter",
        json={"pin": "4821"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "guest"
    assert data["event_slug"] == event.slug


@pytest.mark.asyncio
async def test_enter_vault_with_invalid_pin(client, db_session):
    event = await create_demo_event(db_session)

    response = await client.post(
        f"/api/a/{event.slug}/enter",
        json={"pin": "0000"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "PIN incorrecto"


@pytest.mark.asyncio
async def test_batch_presigned_requires_token(client, db_session):
    event = await create_demo_event(db_session)

    payload = {
        "files": [
            {"filename": "foto1.jpg", "size_bytes": 2048, "content_type": "image/jpeg"}
        ]
    }
    response = await client.post(f"/api/a/{event.slug}/batch-presigned", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_batch_presigned_rejects_foreign_event_token(client, db_session):
    event = await create_demo_event(db_session)
    foreign_token = create_guest_token(event_id=str(uuid.uuid4()), slug="otro-evento")

    headers = {"Authorization": f"Bearer {foreign_token}"}
    payload = {
        "files": [
            {"filename": "foto1.jpg", "size_bytes": 2048, "content_type": "image/jpeg"}
        ]
    }
    response = await client.post(
        f"/api/a/{event.slug}/batch-presigned",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_batch_presigned_success(client, db_session):
    event = await create_demo_event(db_session)
    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "files": [
            {"filename": "fiesta1.jpg", "size_bytes": 3 * 1024 * 1024, "content_type": "image/jpeg"},
            {"filename": "baile.mp4", "size_bytes": 10 * 1024 * 1024, "content_type": "video/mp4"},
        ]
    }

    response = await client.post(
        f"/api/a/{event.slug}/batch-presigned",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2

    photo_item = data["items"][0]
    assert photo_item["filename"] == "fiesta1.jpg"
    assert "upload_url" in photo_item
    assert "r2_key" in photo_item
    assert photo_item["thumb_upload_url"] is not None  # Miniatura WebP generada para fotos

    video_item = data["items"][1]
    assert video_item["filename"] == "baile.mp4"
    assert video_item["thumb_upload_url"] is None  # Sin miniatura WebP generada por canvas para video


@pytest.mark.asyncio
async def test_batch_presigned_unsupported_mime(client, db_session):
    event = await create_demo_event(db_session)
    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "files": [
            {"filename": "virus.exe", "size_bytes": 1024, "content_type": "application/x-msdownload"}
        ]
    }

    response = await client.post(
        f"/api/a/{event.slug}/batch-presigned",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 415
    assert "Formato no permitido" in response.json()["detail"]


@pytest.mark.asyncio
async def test_batch_presigned_file_size_exceeded(client, db_session):
    event = await create_demo_event(db_session)
    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    headers = {"Authorization": f"Bearer {token}"}

    # Foto que supera el limite maximo de 25 MB
    payload = {
        "files": [
            {"filename": "gigante.jpg", "size_bytes": 30 * 1024 * 1024, "content_type": "image/jpeg"}
        ]
    }

    response = await client.post(
        f"/api/a/{event.slug}/batch-presigned",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 400
    assert "excede el tamano maximo permitido" in response.json()["detail"]


@pytest.mark.asyncio
async def test_batch_presigned_storage_quota_exceeded(client, db_session):
    event = await create_demo_event(db_session)  # cuota: 100 MB
    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar subir lote que supera los 100 MB del evento
    payload = {
        "files": [
            {"filename": "clip1.mp4", "size_bytes": 80 * 1024 * 1024, "content_type": "video/mp4"},
            {"filename": "clip2.mp4", "size_bytes": 30 * 1024 * 1024, "content_type": "video/mp4"},
        ]
    }

    response = await client.post(
        f"/api/a/{event.slug}/batch-presigned",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 413
    assert "superado el limite de almacenamiento" in response.json()["detail"]


@pytest.mark.asyncio
async def test_confirm_media_upload_and_feed(client, db_session):
    event = await create_demo_event(db_session)
    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    headers = {"Authorization": f"Bearer {token}"}

    file_id = uuid.uuid4()
    payload = {
        "id": str(file_id),
        "r2_key": f"events/{event.slug}/media/{file_id}.jpg",
        "thumb_r2_key": f"events/{event.slug}/thumbs/{file_id}.webp",
        "filename": "foto_mesa_3.jpg",
        "content_type": "image/jpeg",
        "size_bytes": 4 * 1024 * 1024,
        "guest_author": "Tia Carmen",
    }

    # Confirmar subida
    response = await client.post(
        f"/api/a/{event.slug}/media/confirm",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(file_id)
    assert data["guest_author"] == "Tia Carmen"
    assert data["moderation_status"] == "approved"
    assert data["url"] is not None
    assert data["thumb_url"] is not None

    # Verificar que el almacenamiento ocupado aumento en la base de datos
    await db_session.refresh(event)
    assert event.storage_used_bytes == 4 * 1024 * 1024

    # Consultar el feed publico
    feed_res = await client.get(f"/api/a/{event.slug}/feed")
    assert feed_res.status_code == 200
    feed_items = feed_res.json()
    assert len(feed_items) == 1
    assert feed_items[0]["id"] == str(file_id)
    assert feed_items[0]["guest_author"] == "Tia Carmen"


@pytest.mark.asyncio
async def test_confirm_media_upload_idempotency(client, db_session):
    event = await create_demo_event(db_session)
    token = create_guest_token(event_id=str(event.id), slug=event.slug)
    headers = {"Authorization": f"Bearer {token}"}

    file_id = uuid.uuid4()
    payload = {
        "id": str(file_id),
        "r2_key": f"events/{event.slug}/media/{file_id}.jpg",
        "thumb_r2_key": f"events/{event.slug}/thumbs/{file_id}.webp",
        "filename": "foto.jpg",
        "content_type": "image/jpeg",
        "size_bytes": 2 * 1024 * 1024,
    }

    # Primera confirmacion
    res1 = await client.post(f"/api/a/{event.slug}/media/confirm", json=payload, headers=headers)
    assert res1.status_code == 200

    # Segunda confirmacion con el mismo id no debe duplicar el almacenamiento
    res2 = await client.post(f"/api/a/{event.slug}/media/confirm", json=payload, headers=headers)
    assert res2.status_code == 200

    await db_session.refresh(event)
    assert event.storage_used_bytes == 2 * 1024 * 1024
