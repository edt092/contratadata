"""GET /api/entidades — listado y detalle de entidades públicas."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import BarItem, ContractItem, ContractListResponse, EntitySummary
from src.load.models import Contract, Entity, Supplier

router = APIRouter(prefix="/entidades", tags=["entidades"])


@router.get("", response_model=list[str])
def list_entidades(db: Session = Depends(get_db)) -> list[str]:
    """Nombres de todas las entidades (para el select de filtros)."""
    rows = db.execute(
        select(Entity.nombre_canonico).order_by(Entity.nombre_canonico)
    ).scalars().all()
    return list(rows)


@router.get("/{nombre}/summary", response_model=EntitySummary)
def entity_summary(nombre: str, db: Session = Depends(get_db)) -> EntitySummary:
    entity = db.execute(
        select(Entity).where(Entity.nombre_canonico == nombre)
    ).scalars().first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    agg = db.execute(
        select(
            func.count(Contract.id).label("total"),
            func.coalesce(func.sum(Contract.valor), 0).label("valor_total"),
            func.count(Contract.supplier_id.distinct()).label("contratistas_unicos"),
        ).where(Contract.entity_id == entity.id)
    ).mappings().one()

    return EntitySummary(
        nombre=entity.nombre_canonico,
        sigla=entity.sigla,
        total_contratos=agg["total"],
        valor_total=agg["valor_total"],
        contratistas_unicos=agg["contratistas_unicos"],
    )


@router.get("/{nombre}/contracts", response_model=ContractListResponse)
def entity_contracts(
    nombre: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ContractListResponse:
    entity = db.execute(
        select(Entity).where(Entity.nombre_canonico == nombre)
    ).scalars().first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    base = (
        select(
            Contract.id,
            Entity.nombre_canonico.label("entidad"),
            Supplier.nombre.label("contratista"),
            Contract.valor,
            Contract.fecha,
            Contract.estado,
            Contract.fuente,
            Contract.extraido_en,
        )
        .join(Entity, Contract.entity_id == Entity.id)
        .join(Supplier, Contract.supplier_id == Supplier.id)
        .where(Contract.entity_id == entity.id)
    )

    from math import ceil
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    rows = db.execute(
        base.order_by(Contract.fecha.desc()).offset((page - 1) * per_page).limit(per_page)
    ).mappings().all()

    return ContractListResponse(
        items=[ContractItem.model_validate(dict(r)) for r in rows],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=max(1, ceil(total / per_page)),
    )


@router.get("/{nombre}/top-contratistas", response_model=list[BarItem])
def entity_top_contratistas(
    nombre: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[BarItem]:
    entity = db.execute(
        select(Entity).where(Entity.nombre_canonico == nombre)
    ).scalars().first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")

    rows = db.execute(
        select(
            Supplier.nombre.label("nombre"),
            func.sum(Contract.valor).label("valor_total"),
        )
        .join(Contract, Contract.supplier_id == Supplier.id)
        .where(Contract.entity_id == entity.id)
        .group_by(Supplier.nombre)
        .order_by(func.sum(Contract.valor).desc())
        .limit(limit)
    ).mappings().all()

    if not rows:
        return []

    max_val = rows[0]["valor_total"] or 1
    return [
        BarItem(
            nombre=r["nombre"],
            valor_total=r["valor_total"],
            porcentaje=round(float(r["valor_total"]) / float(max_val) * 100, 1),
        )
        for r in rows
    ]
