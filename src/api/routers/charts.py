"""GET /api/charts — datos agregados para visualizaciones."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import BarItem, MonthlyPoint
from src.load.models import Contract, Entity, Supplier

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/top-entidades", response_model=list[BarItem])
def top_entidades(
    limit: int = Query(15, ge=1, le=50),
    entidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> list[BarItem]:
    stmt = (
        select(
            Entity.nombre_canonico.label("nombre"),
            func.sum(Contract.valor).label("valor_total"),
        )
        .join(Contract, Contract.entity_id == Entity.id)
        .join(Supplier, Contract.supplier_id == Supplier.id)
        .group_by(Entity.nombre_canonico)
        .order_by(func.sum(Contract.valor).desc())
        .limit(limit)
    )
    if entidad:
        stmt = stmt.where(Entity.nombre_canonico == entidad)
    if estado:
        stmt = stmt.where(Contract.estado == estado)
    if desde:
        stmt = stmt.where(Contract.fecha >= desde)
    if hasta:
        stmt = stmt.where(Contract.fecha <= hasta)

    rows = db.execute(stmt).mappings().all()
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


@router.get("/evolucion", response_model=list[MonthlyPoint])
def evolucion(
    entidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> list[MonthlyPoint]:
    stmt = (
        select(
            extract("year", Contract.fecha).label("anio"),
            extract("month", Contract.fecha).label("mes"),
            func.sum(Contract.valor).label("valor_total"),
            func.count(Contract.id).label("cantidad"),
        )
        .join(Entity, Contract.entity_id == Entity.id)
        .join(Supplier, Contract.supplier_id == Supplier.id)
        .group_by("anio", "mes")
        .order_by("anio", "mes")
    )
    if entidad:
        stmt = stmt.where(Entity.nombre_canonico == entidad)
    if estado:
        stmt = stmt.where(Contract.estado == estado)
    if desde:
        stmt = stmt.where(Contract.fecha >= desde)
    if hasta:
        stmt = stmt.where(Contract.fecha <= hasta)

    rows = db.execute(stmt).mappings().all()
    return [
        MonthlyPoint(
            periodo=f"{int(r['anio'])}-{int(r['mes']):02d}",
            valor_total=r["valor_total"],
            cantidad=r["cantidad"],
        )
        for r in rows
    ]
