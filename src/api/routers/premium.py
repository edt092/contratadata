"""Premium (ver auth.md): status del plan del usuario autenticado, captura
de interés en Pro, y creación de checkouts de Wompi. La fuente de verdad del
plan vive en Neon (Subscription/PremiumEntitlement) — Auth0 solo confirma la
identidad."""

import os
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db, is_pro_user, require_auth0_user
from src.api.routers.me import resolve_entitlements
from src.api.schemas import (
    CheckoutCreate, CheckoutResponse, PremiumLeadCreate, PremiumLeadResponse,
    PremiumStatusResponse,
)
from src.api.wompi import build_integrity_signature
from src.load.models import AppUser, PaymentReference, PremiumLead

router = APIRouter(prefix="/premium", tags=["premium"])

# Precios en centavos de peso colombiano — servidos solo desde el backend,
# nunca confiamos en un monto que mande el cliente (ver auth.md/plan Wompi).
# $149.000/mes; $1.490.000/año (= 10 meses, "2 meses gratis").
PLAN_PRICES_COP_CENTS = {"monthly": 14_900_000, "annual": 149_000_000}
PLAN_PERIOD_DAYS = {"monthly": 30, "annual": 365}


@router.get("/status", response_model=PremiumStatusResponse)
def premium_status(
    user: AppUser = Depends(require_auth0_user), db: Session = Depends(get_db),
) -> PremiumStatusResponse:
    pro = is_pro_user(db, user)
    return PremiumStatusResponse(
        plan="pro" if pro else "free",
        premium_status="active" if pro else "none",
        is_pro=pro,
        entitlements=resolve_entitlements(db, user, pro),
    )


@router.post("/request-access", response_model=PremiumLeadResponse)
def request_access(
    payload: PremiumLeadCreate,
    user: AppUser = Depends(require_auth0_user),
    db: Session = Depends(get_db),
) -> PremiumLeadResponse:
    """Registra interés en Pro para un usuario ya autenticado pero Free —
    no otorga acceso; es la señal de demanda hasta tener pagos automatizados."""
    row = PremiumLead(user_id=user.id, email=user.email or "", feature=payload.feature)
    db.add(row)
    db.commit()
    db.refresh(row)
    return PremiumLeadResponse(id=row.id, email=row.email)


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    payload: CheckoutCreate,
    user: AppUser = Depends(require_auth0_user),
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    """Crea la referencia de pago y la firma de integridad para el widget de
    checkout de Wompi (ver auth.md). El webhook (POST /webhooks/wompi)
    correlaciona la respuesta de Wompi con este usuario vía 'reference'."""
    amount = PLAN_PRICES_COP_CENTS[payload.plan]
    reference = f"pro-{user.id}-{payload.plan}-{uuid4().hex[:10]}"

    db.add(PaymentReference(
        user_id=user.id, reference=reference, plan=payload.plan, amount_in_cents=amount,
    ))
    db.commit()

    signature = build_integrity_signature(reference, amount)
    frontend_base = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    return CheckoutResponse(
        public_key=os.environ["WOMPI_PUBLIC_KEY"],
        reference=reference,
        amount_in_cents=amount,
        currency="COP",
        signature=signature,
        redirect_url=f"{frontend_base}/cuenta?checkout=return",
    )
