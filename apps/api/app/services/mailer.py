import httpx
from app.config import settings


class MailerService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM
        self.endpoint = "https://api.resend.com/emails"

    async def send_email(self, to: str, subject: str, html_body: str) -> bool:
        """Envia un correo electronico transaccional via Resend API."""
        if not self.api_key or self.api_key.startswith("re_123456"):
            print(f"[Mailer Mock] Correo simulado a {to} | Asunto: {subject}")
            return True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html_body,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)
            return response.is_success


mailer_service = MailerService()
