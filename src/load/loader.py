"""Carga idempotente de registros validados a PostgreSQL."""

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from src.load.models import Base, Contract, Entity, PipelineMeta, RejectedRecord, Supplier

logger = logging.getLogger(__name__)


def get_engine(database_url: str):
    return create_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,  # reconecta automáticamente si la conexión cayó
    )


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


def _get_or_create_entity(
    session: Session, nombre_canonico: str, cache: dict
) -> int:
    """Retorna el id de la entidad, creándola si no existe. Cachea solo el id."""
    if nombre_canonico in cache:
        return cache[nombre_canonico]
    stmt = select(Entity).where(Entity.nombre_canonico == nombre_canonico)
    entity = session.scalars(stmt).first()
    if not entity:
        entity = Entity(nombre_canonico=nombre_canonico)
        session.add(entity)
        session.flush()
    cache[nombre_canonico] = entity.id
    return entity.id


def _get_or_create_supplier(
    session: Session, nombre: str, nit: str | None, cache: dict
) -> int:
    """Retorna el id del proveedor, creándolo si no existe. Cachea solo el id."""
    if nombre in cache:
        return cache[nombre]
    stmt = select(Supplier).where(Supplier.nombre == nombre)
    supplier = session.scalars(stmt).first()
    if not supplier:
        supplier = Supplier(nombre=nombre, nit_o_id_fiscal=nit)
        session.add(supplier)
        session.flush()
    cache[nombre] = supplier.id
    return supplier.id


def _persist_rejected(session: Session, records: list[dict]) -> None:
    for rec in records:
        payload = {k: v for k, v in (rec.get("_raw") or rec).items()
                   if not k.startswith("_")}
        session.add(RejectedRecord(
            fuente=rec.get("fuente", "UNKNOWN"),
            payload_crudo=payload,
            motivo_rechazo=rec.get("_motivo_rechazo", "desconocido"),
        ))


def load_batch(
    engine,
    valid: list[dict],
    rejected: list[dict],
    entity_cache: dict,
    supplier_cache: dict,
) -> tuple[int, int]:
    """Carga un lote en su propia transacción. Retorna (insertados, omitidos)."""
    inserted = skipped = 0

    with Session(engine) as session:
        with session.begin():
            for rec in valid:
                entity_id = _get_or_create_entity(
                    session, rec["entidad_canonica"], entity_cache
                )
                supplier_id = _get_or_create_supplier(
                    session,
                    rec.get("contratista", "DESCONOCIDO"),
                    rec.get("identificacion_proveedor"),
                    supplier_cache,
                )
                stmt = (
                    pg_insert(Contract)
                    .values(
                        entity_id=entity_id,
                        supplier_id=supplier_id,
                        valor=Decimal(str(rec["valor"])),
                        fecha=_parse_date(rec.get("fecha")),
                        estado=rec.get("estado"),
                        fuente=rec.get("fuente", "UNKNOWN"),
                    )
                    .on_conflict_do_nothing(constraint="uq_contract_idempotent")
                )
                if session.execute(stmt).rowcount:
                    inserted += 1
                else:
                    skipped += 1

            _persist_rejected(session, rejected)

    return inserted, skipped


def get_last_run_at(engine) -> datetime | None:
    """Retorna el timestamp de la última corrida exitosa, o None si no existe."""
    with Session(engine) as session:
        row = session.get(PipelineMeta, "last_run_at")
        return datetime.fromisoformat(row.value) if row else None


def set_last_run_at(engine, dt: datetime) -> None:
    """Persiste el timestamp de la corrida actual como la última exitosa."""
    with Session(engine) as session:
        with session.begin():
            stmt = (
                pg_insert(PipelineMeta)
                .values(key="last_run_at", value=dt.isoformat(), updated_at=dt)
                .on_conflict_do_update(
                    index_elements=["key"],
                    set_={"value": dt.isoformat(), "updated_at": dt},
                )
            )
            session.execute(stmt)


def run_load(database_url: str, valid: list[dict], rejected: list[dict]) -> None:
    """Compatibilidad hacia atrás: carga todo en un único lote."""
    engine = get_engine(database_url)
    create_tables(engine)
    inserted, skipped = load_batch(engine, valid, rejected, {}, {})
    logger.info(
        "Transacción completada: %d contratos nuevos, %d duplicados, %d rechazos.",
        inserted, skipped, len(rejected),
    )
