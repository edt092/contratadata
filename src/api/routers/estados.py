"""GET /api/estados — valores únicos de estado."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.load.models import Contract

router = APIRouter(prefix="/estados", tags=["estados"])


@router.get("/", response_model=list[str])
def list_estados(db: Session = Depends(get_db)) -> list[str]:
    rows = db.execute(
        select(Contract.estado)
        .where(Contract.estado.isnot(None))
        .distinct()
        .order_by(Contract.estado)
    ).scalars().all()
    return list(rows)
