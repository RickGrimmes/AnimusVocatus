import io
import json
import uuid
import zipfile
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Event, MediaItem, ZipJob
from app.services.storage import storage_service
from app.services.mailer import mailer_service


def build_editorial_email_html(event_title: str, download_url: str, media_count: int, size_mb: float) -> str:
    """Genera la plantilla HTML con diseno editorial sobrio para la entrega de recuerdos."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recuerdos de {event_title}</title>
</head>
<body style="margin:0;padding:0;background-color:#14161b;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#f3f4f6;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#14161b;padding:40px 15px;">
    <tr>
      <td align="center">
        <table width="100%" max-width="580" border="0" cellspacing="0" cellpadding="0" style="max-width:580px;background-color:#1c1e24;border-radius:16px;border:1px solid rgba(255,255,255,0.1);overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.5);">
          
          <!-- Encabezado -->
          <tr>
            <td style="padding:32px 32px 20px 32px;border-bottom:1px solid rgba(255,255,255,0.08);">
              <span style="font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#34d399;font-weight:600;">Animus &bull; Boveda de Recuerdos</span>
              <h1 style="margin:8px 0 0 0;font-size:24px;font-weight:700;color:#ffffff;line-height:1.3;">{event_title}</h1>
            </td>
          </tr>

          <!-- Cuerpo principal -->
          <tr>
            <td style="padding:28px 32px;line-height:1.6;font-size:15px;color:#d1d5db;">
              <p style="margin:0 0 16px 0;">Tu archivo masivo con todas las fotografias y videos compartidos por tus invitados durante la celebracion esta listo para su descarga.</p>
              
              <!-- Resumen de contenido -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#14161b;border-radius:10px;padding:16px;margin:20px 0;border:1px solid rgba(255,255,255,0.06);">
                <tr>
                  <td style="font-size:13px;color:#9ca3af;padding:4px 0;">Total de archivos:</td>
                  <td align="right" style="font-size:13px;font-weight:700;color:#ffffff;">{media_count} recuerdos</td>
                </tr>
                <tr>
                  <td style="font-size:13px;color:#9ca3af;padding:4px 0;">Tamano aproximado:</td>
                  <td align="right" style="font-size:13px;font-weight:700;color:#ffffff;">{size_mb:.1f} MB</td>
                </tr>
                <tr>
                  <td style="font-size:13px;color:#9ca3af;padding:4px 0;">Vigencia del enlace:</td>
                  <td align="right" style="font-size:13px;font-weight:700;color:#34d399;">7 dias naturales</td>
                </tr>
              </table>

              <!-- Boton de descarga -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin:28px 0 16px 0;">
                <tr>
                  <td align="center">
                    <a href="{download_url}" target="_blank" style="display:inline-block;padding:14px 32px;background-color:#ffffff;color:#121212;text-decoration:none;font-size:14px;font-weight:700;border-radius:50px;box-shadow:0 4px 14px rgba(255,255,255,0.15);letter-spacing:0.5px;">Descargar Archivo ZIP Completo</a>
                  </td>
                </tr>
              </table>

              <p style="margin:24px 0 0 0;font-size:12px;color:#9ca3af;text-align:center;">
                Si el boton no responde, copia y pega este enlace en tu navegador:<br>
                <a href="{download_url}" style="color:#60a5fa;word-break:break-all;font-size:11px;">{download_url}</a>
              </p>
            </td>
          </tr>

          <!-- Pie de pagina -->
          <tr>
            <td style="padding:20px 32px;background-color:#14161b;border-top:1px solid rgba(255,255,255,0.06);font-size:12px;color:#6b7280;text-align:center;">
              Vocatus &amp; Animus &bull; Suite Web para Eventos Sociales de Alta Gama
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


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
            event_stmt = select(Event).options(selectinload(Event.host)).where(Event.id == job.event_id)
            event = (await db.execute(event_stmt)).scalar_one_or_none()
            if not event:
                job.status = "failed"
                await db.commit()
                return

            # Consultar todos los recuerdos aprobados del evento
            media_stmt = select(MediaItem).where(
                MediaItem.event_id == event.id,
                MediaItem.moderation_status == "approved",
            )
            media_items = (await db.execute(media_stmt)).scalars().all()

            # Calcular volumen en bytes
            total_bytes = sum(m.size_bytes for m in media_items)
            if total_bytes == 0 and event.storage_used_bytes > 0:
                total_bytes = event.storage_used_bytes

            size_mb = total_bytes / (1024 * 1024) if total_bytes > 0 else 0.0

            zip_r2_key = f"events/{event.slug}/exports/recuerdos-completos.zip"
            download_url = storage_service.generate_presigned_download_url(
                r2_key=zip_r2_key,
                expires_in=7 * 24 * 3600,  # 7 dias de vigencia
            )

            job.status = "ready"
            job.r2_zip_key = zip_r2_key
            job.zip_size_bytes = total_bytes
            job.download_url = download_url
            job.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            await db.commit()

            # Notificar al anfitrion por correo
            if event.host and event.host.email:
                email_html = build_editorial_email_html(
                    event_title=event.title,
                    download_url=download_url,
                    media_count=len(media_items),
                    size_mb=size_mb,
                )
                await mailer_service.send_email(
                    to=event.host.email,
                    subject=f"Tus recuerdos de {event.title} estan listos para descargar",
                    html_body=email_html,
                )

        except Exception as exc:
            job.status = "failed"
            await db.commit()
            print(f"Error procesando ZIP job {job_id}: {exc}")
