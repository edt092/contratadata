"""GET /api/me — perfil del usuario autenticado y su plan (ver auth.md)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_latest_subscription, is_pro_user, require_auth0_user
from src.api.schemas import MeResponse
from src.load.models import AppUser, PremiumEntitlement

router = APIRouter(prefix="/me", tags=["me"])

FEATURE_KEYS = ["saved_alerts", "competitor_monitor", "reports"]


def resolve_entitlements(db: Session, user: AppUser, pro: bool) -> dict[str, bool]:
    if pro:
        return {k: True for k in FEATURE_KEYS}
    enabled = set(db.execute(
        select(PremiumEntitlement.feature_key).where(
            PremiumEntitlement.user_id == user.id,
            PremiumEntitlement.is_enabled.is_(True),
        )
    ).scalars().all())
    return {k: (k in enabled) for k in FEATURE_KEYS}


@router.get("", response_model=MeResponse)
def me(user: AppUser = Depends(require_auth0_user), db: Session = Depends(get_db)) -> MeResponse:
    pro = is_pro_user(db, user)
    sub = get_latest_subscription(db, user.id)
    return MeResponse(
        id=user.id,
        auth0_sub=user.auth0_sub,
        email=user.email,
        name=user.name,
        picture=user.picture,
        plan="pro" if pro else "free",
        premium_status=sub.status if sub else "none",
        entitlements=resolve_entitlements(db, user, pro),
    )
