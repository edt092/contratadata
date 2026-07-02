"""GET /api/contracts — lista paginada con filtros y agrupado agregado."""

from datetime import date
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import ContractAggregate, ContractItem, ContractListResponse
from src.load.models import Contract, Entity, Supplier

router = APIRouter(prefix="/contracts", tags=["contracts"])


def _base_stmt(
    entidad: Optional[str],
    contratista: Optional[str],
    estado: Optional[str],
    desde: Optional[date],
    hasta: Optional[date],
):
    stmt = (
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
    )
    if entidad:
        stmt = stmt.where(Entity.nombre_canonico == entidad)
    if contratista:
        stmt = stmt.where(Supplier.nombre.ilike(f"%{contratista}%"))
    if estado:
        stmt = stmt.where(Contract.estado == estado)
    if desde:
        stmt = stmt.where(Contract.fecha >= desde)
    if hasta:
        stmt = stmt.where(Contract.fecha <= hasta)
    return stmt


@router.get("/aggregate", response_model=ContractAggregate)
def contracts_aggregate(
    entidad: Optional[str] = Query(None),
    contratista: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> ContractAggregate:
    stmt = (
        select(
            func.count(Contract.id).label("total_contratos"),
            func.coalesce(func.sum(Contract.valor), 0).label("valor_total"),
            func.count(distinct(Contract.entity_id)).label("entidades_unicas"),
            func.count(distinct(Contract.supplier_id)).label("contratistas_unicos"),
        )
        .join(Entity, Contract.entity_id == Entity.id)
        .join(Supplier, Contract.supplier_id == Supplier.id)
    )
    if entidad:
        stmt = stmt.where(Entity.nombre_canonico == entidad)
    if contratista:
        stmt = stmt.where(Supplier.nombre.ilike(f"%{contratista}%"))
    if estado:
        stmt = stmt.where(Contract.estado == estado)
    if desde:
        stmt = stmt.where(Contract.fecha >= desde)
    if hasta:
        stmt = stmt.where(Contract.fecha <= hasta)

    row = db.execute(stmt).mappings().one()
    return ContractAggregate(
        total_contratos=row["total_contratos"],
        valor_total=float(row["valor_total"]),
        entidades_unicas=row["entidades_unicas"],
        contratistas_unicos=row["contratistas_unicos"],
    )


@router.get("", response_model=ContractListResponse)
def list_contracts(
    entidad: Optional[str] = Query(None, description="Nombre exacto de la entidad"),
    contratista: Optional[str] = Query(None, description="Búsqueda parcial en nombre del contratista"),
    estado: Optional[str] = Query(None, description="Estado del contrato"),
    desde: Optional[date] = Query(None, description="Fecha mínima (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Fecha máxima (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=10000),
    db: Session = Depends(get_db),
) -> ContractListResponse:
    count_stmt = select(func.count()).select_from(
        _base_stmt(entidad, contratista, estado, desde, hasta).subquery()
    )
    total = db.execute(count_stmt).scalar_one()

    data_stmt = (
        _base_stmt(entidad, contratista, estado, desde, hasta)
        .order_by(Contract.fecha.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    rows = db.execute(data_stmt).mappings().all()

    return ContractListResponse(
        items=[ContractItem.model_validate(dict(r)) for r in rows],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=max(1, ceil(total / per_page)),
    )
