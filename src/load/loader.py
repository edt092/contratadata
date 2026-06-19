"""Carga idempotente de registros validados a PostgreSQL."""

import json
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from src.load.models import Base, Contract, Entity, RejectedRecord, Supplier

logger = logging.getLogger(__name__)


def get_engine(database_url: str):
    return create_engine(database_url, echo=False, future=True)


def create_tables(engine) -> None:
    Base.metadata.create_all(engine)
    logger.info("Tablas verificadas/creadas.")


def _parse_date(raw):
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.date()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(raw)[:19], fmt[:len(fmt)]).date()
        except ValueError:
            continue
    return None


def _get_or_create_entity(session: Session, nombre_canonico: str) -> Entity:
    stmt = select(Entity).where(Entity.nombre_canonico == nombre_canonico)
    entity = session.scalars(stmt).first()
    if entity:
        return entity
    entity = Entity(nombre_canonico=nombre_canonico)
    session.add(entity)
    session.flush()  # obtiene el id sin hacer commit todavía
    return entity


def _get_or_create_supplier(session: Session, nombre: str, nit: str | None = None) -> Supplier:
    stmt = select(Supplier).where(Supplier.nombre == nombre)
    supplier = session.scalars(stmt).first()
    if supplier:
        return supplier
    supplier = Supplier(nombre=nombre, nit_o_id_fiscal=nit)
    session.add(supplier)
    session.flush()
    return supplier


def _persist_rejected(session: Session, records: list[dict]) -> None:
    for rec in records:
        # Serializa el payload crudo eliminando claves internas del pipeline
        payload = {k: v for k, v in (rec.get("_raw") or rec).items()
                   if not k.startswith("_")}
        rr = RejectedRecord(
            fuente=rec.get("fuente", "UNKNOWN"),
            payload_crudo=payload,
            motivo_rechazo=rec.get("_motivo_rechazo", "desconocido"),
        )
        session.add(rr)


def load_valid(session: Session, records: list[dict]) -> tuple[int, int]:
    """Carga registros válidos. Retorna (insertados, omitidos_duplicados)."""
    inserted = skipped = 0

    for rec in records:
        entity = _get_or_create_entity(session, rec["entidad_canonica"])
        supplier = _get_or_create_supplier(
            session,
            rec.get("contratista", "DESCONOCIDO"),
            rec.get("_raw", {}).get("identificacion_proveedor"),
        )
        fecha = _parse_date(rec.get("fecha"))
        valor = Decimal(str(rec["valor"]))

        # INSERT … ON CONFLICT DO NOTHING para idempotencia
        stmt = (
            pg_insert(Contract)
            .values(
                entity_id=entity.id,
                supplier_id=supplier.id,
                valor=valor,
                fecha=fecha,
                estado=rec.get("estado"),
                fuente=rec.get("fuente", "UNKNOWN"),
            )
            .on_conflict_do_nothing(constraint="uq_contract_idempotent")
        )
        result = session.execute(stmt)
        if result.rowcount:
            inserted += 1
        else:
            skipped += 1

    logger.info("Carga: %d insertados, %d omitidos (duplicados).", inserted, skipped)
    return inserted, skipped


def run_load(database_url: str, valid: list[dict], rejected: list[dict]) -> None:
    engine = get_engine(database_url)
    create_tables(engine)

    with Session(engine) as session:
        with session.begin():
            inserted, skipped = load_valid(session, valid)
            _persist_rejected(session, rejected)
            logger.info(
                "Transacción completada: %d contratos nuevos, %d rechazos persistidos.",
                inserted, len(rejected),
            )
