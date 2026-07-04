"""Premium (ver auth.md): status del plan del usuario autenticado y captura
de interés en Pro. La fuente de verdad del plan vive en Neon (Subscription/
PremiumEntitlement) — Auth0 solo confirma la identidad."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db, is_pro_user, require_auth0_user
from src.api.routers.me import resolve_entitlements
from src.api.schemas import PremiumLeadCreate, PremiumLeadResponse, PremiumStatusResponse
from src.load.models import AppUser, PremiumLead

router = APIRouter(prefix="/premium", tags=["premium"])


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
