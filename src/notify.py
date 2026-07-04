"""Notificación de feedback de usuarios — capa desacoplada del guardado en DB.

Todavía no hay servicio de email configurado en producción. Si SMTP_HOST está
presente en el entorno, intenta enviar por SMTP; si no, solo loguea. Cualquier
falla queda contenida acá: nunca debe hacer perder un feedback ya guardado en
la base de datos (ver src/api/routers/feedback.py).
"""

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

FEEDBACK_NOTIFY_EMAIL = os.getenv("FEEDBACK_NOTIFY_EMAIL", "feedback@contratadata.xyz")


def notify_feedback(
    feedback_id: int,
    feedback_type: str,
    comment: str,
    email: str | None,
    importance: str,
) -> None:
    """Intenta notificar sobre un feedback nuevo. Nunca lanza."""
    smtp_host = os.getenv("SMTP_HOST")
    if not smtp_host:
        logger.info(
            "Feedback #%d recibido (%s, importancia=%s) — SMTP_HOST no está "
            "configurado, no se envía notificación por email. Revisar tabla "
            "'feedback' en la base de datos.",
            feedback_id, feedback_type, importance,
        )
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[ContrataData] Nuevo feedback ({importance}) — {feedback_type}"
        msg["From"] = os.getenv("SMTP_FROM", FEEDBACK_NOTIFY_EMAIL)
        msg["To"] = FEEDBACK_NOTIFY_EMAIL
        msg.set_content(
            f"Feedback #{feedback_id}\n"
            f"Tipo: {feedback_type}\n"
            f"Importancia: {importance}\n"
            f"Email de contacto: {email or '(no proporcionado)'}\n\n"
            f"{comment}"
        )
        with smtplib.SMTP(smtp_host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as server:
            server.starttls()
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Notificación de feedback #%d enviada a %s.", feedback_id, FEEDBACK_NOTIFY_EMAIL)
    except Exception as exc:
        logger.error("No se pudo notificar el feedback #%d: %s", feedback_id, exc)
