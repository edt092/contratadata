"""POST /api/webhooks/clerk — recibe los eventos de identidad de Clerk (ver
auth2.md FASE 6): user.created, user.updated, user.deleted. Endpoint público
(Clerk no manda un session token propio en sus webhooks): la autenticidad se
valida con la firma Svix (CLERK_WEBHOOK_SECRET), no con
require_authenticated_user.

Estos webhooks NUNCA tocan subscriptions/premium_entitlements — solo
identidad (ver src/api/deps.py::link_or_create_app_user). user.deleted
desactiva al AppUser, no borra pagos ni historial."""

import logging
import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError

from src.api.clerk import parse_clerk_user_payload
from src.api.deps import get_db, link_or_create_app_user
from src.load.models import AppUser

logger = logging.getLogger("webhooks.clerk")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/clerk")
async def clerk_event(request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    secret = os.getenv("CLERK_WEBHOOK_SECRET")
    if not secret:
        logger.error("CLERK_WEBHOOK_SECRET no está configurada — no se puede validar el webhook.")
        return JSONResponse(status_code=500, content={"error": "server_misconfigured"})

    # La firma Svix es sensible al byte exacto del body — no se puede leer
    # request.json() y re-serializar (ver Wompi para el otro webhook público
    # de este API, que usa un checksum propio en vez de Svix).
    payload = await request.body()
    try:
        event = Webhook(secret).verify(payload, dict(request.headers))
    except WebhookVerificationError:
        logger.warning("Firma de webhook de Clerk inválida — evento descartado.")
        return JSONResponse(status_code=400, content={"error": "invalid_signature"})

    event_type = event.get("type")
    data = event.get("data") or {}
    sub = data.get("id")
    if not sub:
        return JSONResponse(status_code=200, content={"received": True})

    if event_type in ("user.created", "user.updated"):
        profile = parse_clerk_user_payload(data)
        link_or_create_app_user(db, sub, profile)
        logger.info("%s procesado para sub=%s", event_type, sub)

    elif event_type == "user.deleted":
        # Reprocesar el mismo evento (reintentos de Svix) es un no-op seguro:
        # desactivar dos veces no tiene efecto adicional.
        user = db.execute(
            select(AppUser).where(AppUser.auth_provider == "clerk", AppUser.auth_provider_user_id == sub)
        ).scalar_one_or_none()
        if user is not None and user.is_active:
            user.is_active = False
            db.commit()
            logger.info("Usuario desactivado (user.deleted) sub=%s user_id=%s", sub, user.id)

    return JSONResponse(status_code=200, content={"received": True})
