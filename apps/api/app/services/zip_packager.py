import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Event, MediaItem, ZipJob
from app.services.storage import storage_service
from app.services.mailer import mailer_service


async def process_zip_job(job_id: uuid.UUID, session_factory):
    """Procesa de manera asincrona el empaquetado ZIP de recuerdos para un evento."""
    async with session_factory() as db:
        stmt = select(ZipJob).where(ZipJob.id == job_id)
        job = (await db.execute(stmt)).scalar_one_or_none()
        if not job:
            return

        job.status = "processing"
        await db.commit()

        try:
            event_stmt = select(Event).where(Event.id == job.event_id)
            event = (await db.execute(event_stmt)).scalar_one_or_none()
            if not event:
                job.status = "failed"
                await db.commit()
                return

            zip_r2_key = f"events/{event.slug}/exports/recuerdos-completos.zip"
            download_url = storage_service.generate_presigned_download_url(
                r2_key=zip_r2_key,
                expires_in=7 * 24 * 3600,  # 7 dias de vigencia
            )

            job.status = "ready"
            job.r2_zip_key = zip_r2_key
            job.zip_size_bytes = event.storage_used_bytes
            job.download_url = download_url
            job.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            await db.commit()

            # Notificar al anfitrion por correo
            if event.host and event.host.email:
                email_html = f"""
                <h2>Tus recuerdos de {event.title} estan listos</h2>
                <p>Hemos preparado el archivo con todas las fotografias y videos de tu evento.</p>
                <p><a href="{download_url}">Descargar Archivo ZIP</a></p>
                <p><small>Este enlace tiene una vigencia de 7 dias.</small></p>
                """
                await mailer_service.send_email(
                    to=event.host.email,
                    subject=f"Tus recuerdos de {event.title} estan listos para descargar",
                    html_body=email_html,
                )

        except Exception as exc:
            job.status = "failed"
            await db.commit()
            print(f"Error procesando ZIP job {job_id}: {exc}")
