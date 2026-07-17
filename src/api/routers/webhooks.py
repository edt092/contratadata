"""POST /api/webhooks/wompi — recibe los eventos de transacción de Wompi y
activa el plan Pro (ver auth2.md). Endpoint público (Wompi no manda un
session token de Clerk): la autenticidad se valida con el checksum de
eventos, no con require_authenticated_user. Ver clerk_webhooks.py para los
webhooks de identidad (user.created/updated/deleted)."""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.routers.premium import PLAN_PERIOD_DAYS
from src.api.wompi import verify_event_checksum
from src.load.models import PaymentReference, Subscription

logger = logging.getLogger("webhooks.wompi")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/wompi")
async def wompi_event(request: Request, db: Session = Depends(get_db)) -> JSONResponse:
    payload = await request.json()

    try:
        valid = verify_event_checksum(payload)
    except (KeyError, TypeError):
        logger.warning("Evento de Wompi con estructura inesperada: %s", payload)
        return JSONResponse(status_code=400, content={"error": "malformed_event"})

    if not valid:
        logger.warning("Checksum inválido en evento de Wompi — descartado.")
        return JSONResponse(status_code=400, content={"error": "invalid_checksum"})

    if payload.get("event") != "transaction.updated":
        return JSONResponse(status_code=200, content={"received": True})

    transaction = payload["data"]["transaction"]
    reference = transaction["reference"]
    status = transaction["status"]
    wompi_transaction_id = str(transaction["id"])

    payment_ref = db.execute(
        select(PaymentReference).where(PaymentReference.reference == reference)
    ).scalar_one_or_none()

    if payment_ref is None:
        logger.warning("Evento de Wompi con reference desconocida: %s", reference)
        return JSONResponse(status_code=200, content={"received": True})

    if payment_ref.status == "approved":
        # Wompi puede reenviar el mismo evento — no reprocesar un pago ya activado.
        return JSONResponse(status_code=200, content={"received": True})

    payment_ref.status = status.lower()
    payment_ref.wompi_transaction_id = wompi_transaction_id

    if status == "APPROVED":
        now = datetime.utcnow()
        sub = db.execute(
            select(Subscription)
            .where(Subscription.user_id == payment_ref.user_id)
            .order_by(Subscription.updated_at.desc())
        ).scalars().first()
        if sub is None:
            sub = Subscription(user_id=payment_ref.user_id)
            db.add(sub)

        is_active_pro = sub.plan == "pro" and sub.status in ("active", "trialing")
        base = sub.current_period_end if (is_active_pro and sub.current_period_end and sub.current_period_end > now) else now
        period_days = PLAN_PERIOD_DAYS[payment_ref.plan]

        sub.plan = "pro"
        sub.status = "active"
        sub.provider = "wompi"
        sub.provider_subscription_id = wompi_transaction_id
        sub.provider_customer_id = transaction.get("customer_email")
        sub.current_period_end = base + timedelta(days=period_days)

    db.commit()

    return JSONResponse(status_code=200, content={"received": True})
