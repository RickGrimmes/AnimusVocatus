import uuid
from datetime import datetime, timezone
import pytest
from app.models import Event, MediaItem, User, ZipJob
from app.routers.auth import create_jwt_token
from app.services.mailer import mailer_service
from app.services.zip_packager import build_editorial_email_html, process_zip_job
from tests.conftest import TestingSessionLocal


async def setup_host_event_with_media(session) -> tuple[User, Event, str]:
    host = User(
        id=uuid.uuid4(),
        email="anfitrion_vip@test.com",
        password_hash="hash_secreto",
        full_name="Carlos Morales",
    )
    session.add(host)
    await session.flush()

    event = Event(
        id=uuid.uuid4(),
        host_id=host.id,
        slug="boda-carlos-y-sofia-zip",
        title="Boda Carlos & Sofia",
        event_date=datetime(2026, 10, 25, 18, 0, 0, tzinfo=timezone.utc),
        event_type="boda",
        tier="sincronia_total",
        pin_code="4821",
        storage_limit_bytes=100 * 1024 * 1024,
        storage_used_bytes=5 * 1024 * 1024,
        is_active=True,
    )
    session.add(event)
    await session.flush()

    # Agregar dos elementos multimedia aprobados
    media1 = MediaItem(
        id=uuid.uuid4(),
        event_id=event.id,
        r2_key=f"events/{event.slug}/media/foto1.jpg",
        thumb_r2_key=f"events/{event.slug}/thumbs/foto1.webp",
        filename="ceremonia_anillos.jpg",
        content_type="image/jpeg",
        size_bytes=2 * 1024 * 1024,
        guest_author="Familia Morales",
        moderation_status="approved",
    )
    media2 = MediaItem(
        id=uuid.uuid4(),
        event_id=event.id,
        r2_key=f"events/{event.slug}/media/clip1.mp4",
        thumb_r2_key=None,
        filename="vals_novios.mp4",
        content_type="video/mp4",
        size_bytes=3 * 1024 * 1024,
        guest_author="Sofia G.",
        moderation_status="approved",
    )
    session.add_all([media1, media2])
    await session.commit()

    token = create_jwt_token({"sub": str(host.id), "role": "host"})
    return host, event, token


@pytest.mark.asyncio
async def test_request_zip_export_endpoint(client, db_session):
    _, event, token = await setup_host_event_with_media(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/admin/events/{event.slug}/request-zip",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == str(event.id)
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_process_zip_job_execution(db_session):
    _, event, _ = await setup_host_event_with_media(db_session)

    # Crear trabajo manual en estado pending
    job_id = uuid.uuid4()
    job = ZipJob(id=job_id, event_id=event.id, status="pending")
    db_session.add(job)
    await db_session.commit()

    # Ejecutar el empaquetador asincrono
    await process_zip_job(job_id, TestingSessionLocal)

    # Re-consultar el estado del trabajo
    await db_session.refresh(job)
    assert job.status == "ready"
    assert job.r2_zip_key == f"events/{event.slug}/exports/recuerdos-completos.zip"
    assert job.download_url is not None
    assert "download=true" in job.download_url or "http" in job.download_url
    assert job.zip_size_bytes == 5 * 1024 * 1024
    assert job.expires_at is not None


@pytest.mark.asyncio
async def test_list_and_get_zip_jobs(client, db_session):
    _, event, token = await setup_host_event_with_media(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # Solicitar trabajo
    post_res = await client.post(
        f"/api/admin/events/{event.slug}/request-zip",
        headers=headers,
    )
    job_id = post_res.json()["id"]

    # Procesar para que quede en estado ready
    await process_zip_job(uuid.UUID(job_id), TestingSessionLocal)

    # Listar trabajos
    list_res = await client.get(
        f"/api/admin/events/{event.slug}/zip-jobs",
        headers=headers,
    )
    assert list_res.status_code == 200
    jobs_list = list_res.json()
    assert len(jobs_list) >= 1
    assert any(j["id"] == job_id for j in jobs_list)

    # Consultar trabajo especifico
    detail_res = await client.get(
        f"/api/admin/events/{event.slug}/zip-jobs/{job_id}",
        headers=headers,
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == job_id
    assert detail["status"] == "ready"
    assert detail["download_url"] is not None


@pytest.mark.asyncio
async def test_mailer_service_resend_mock():
    # Validar envio exitoso con clave simulada
    sent = await mailer_service.send_email(
        to="anfitrion@test.com",
        subject="Tus recuerdos estan listos",
        html_body="<p>Prueba</p>",
    )
    assert sent is True


def test_build_editorial_email_html():
    html = build_editorial_email_html(
        event_title="Boda Carlos & Sofia",
        download_url="https://storage.local/download.zip",
        media_count=42,
        size_mb=128.5,
    )
    assert "Boda Carlos & Sofia" in html
    assert "42 recuerdos" in html
    assert "128.5 MB" in html
    assert "https://storage.local/download.zip" in html
    assert "7 dias naturales" in html
    # Validacion estricta de ausencia de emojis
    for char in html:
        assert ord(char) < 0x1F300 or ord(char) > 0x1F9FF
