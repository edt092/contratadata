"""GET /api/contratistas — detalle de proveedores y contratistas."""

from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import BarItem, ContractItem, ContractListResponse, ContractorByEstado, ContractorSummary
from src.load.models import Contract, Entity, Supplier

router = APIRouter(prefix="/contratistas", tags=["contratistas"])


@router.get("/{nombre}/summary", response_model=ContractorSummary)
def contractor_summary(nombre: str, db: Session = Depends(get_db)) -> ContractorSummary:
    supplier = db.execute(
        select(Supplier).where(Supplier.nombre == nombre)
    ).scalars().first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Contratista no encontrado")

    agg = db.execute(
        select(
            func.count(Contract.id).label("total"),
            func.coalesce(func.sum(Contract.valor), 0).label("valor_total"),
            func.count(Contract.entity_id.distinct()).label("entidades_unicas"),
        ).where(Contract.supplier_id == supplier.id)
    ).mappings().one()

    return ContractorSummary(
        nombre=supplier.nombre,
        nit_o_id_fiscal=supplier.nit_o_id_fiscal,
        total_contratos=agg["total"],
        valor_total=agg["valor_total"],
        entidades_unicas=agg["entidades_unicas"],
    )


@router.get("/{nombre}/contracts", response_model=ContractListResponse)
def contractor_contracts(
    nombre: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ContractListResponse:
    supplier = db.execute(
        select(Supplier).where(Supplier.nombre == nombre)
    ).scalars().first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Contratista no encontrado")

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
        .where(Contract.supplier_id == supplier.id)
    )

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


@router.get("/{nombre}/top-entidades", response_model=list[BarItem])
def contractor_top_entidades(
    nombre: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[BarItem]:
    supplier = db.execute(
        select(Supplier).where(Supplier.nombre == nombre)
    ).scalars().first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Contratista no encontrado")

    rows = db.execute(
        select(
            Entity.nombre_canonico.label("nombre"),
            func.sum(Contract.valor).label("valor_total"),
        )
        .join(Contract, Contract.entity_id == Entity.id)
        .where(Contract.supplier_id == supplier.id)
        .group_by(Entity.nombre_canonico)
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


@router.get("/{nombre}/by-estado", response_model=list[ContractorByEstado])
def contractor_by_estado(nombre: str, db: Session = Depends(get_db)) -> list[ContractorByEstado]:
    supplier = db.execute(
        select(Supplier).where(Supplier.nombre == nombre)
    ).scalars().first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Contratista no encontrado")

    rows = db.execute(
        select(
            Contract.estado,
            func.count(Contract.id).label("cantidad"),
        )
        .where(Contract.supplier_id == supplier.id, Contract.estado.isnot(None))
        .group_by(Contract.estado)
        .order_by(func.count(Contract.id).desc())
    ).mappings().all()

    return [ContractorByEstado(estado=r["estado"], cantidad=r["cantidad"]) for r in rows]
