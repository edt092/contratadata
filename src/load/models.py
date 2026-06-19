"""Modelos SQLAlchemy para el esquema relacional de ContrataData."""

from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Entity(Base):
    __tablename__ = "entities"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    nombre_canonico = Column(String(500), unique=True, nullable=False)
    sigla           = Column(String(50))
    creado_en       = Column(DateTime, nullable=False, default=func.now())

    contracts = relationship("Contract", back_populates="entity")

    def __repr__(self) -> str:
        return f"<Entity id={self.id} nombre='{self.nombre_canonico}'>"


class Supplier(Base):
    __tablename__ = "suppliers"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    nombre          = Column(String(500), nullable=False)
    nit_o_id_fiscal = Column(String(50))
    creado_en       = Column(DateTime, nullable=False, default=func.now())

    contracts = relationship("Contract", back_populates="supplier")

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} nombre='{self.nombre}'>"


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        UniqueConstraint("fuente", "entity_id", "supplier_id", "valor", "fecha",
                         name="uq_contract_idempotent"),
        CheckConstraint("valor > 0", name="ck_valor_positivo"),
    )

    id          = Column(Integer, primary_key=True, autoincrement=True)
    entity_id   = Column(Integer, ForeignKey("entities.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    valor       = Column(Numeric(18, 2), nullable=False)
    fecha       = Column(Date, nullable=False)
    estado      = Column(String(100))
    fuente      = Column(String(100), nullable=False)
    extraido_en = Column(DateTime, nullable=False, default=func.now())

    entity   = relationship("Entity", back_populates="contracts")
    supplier = relationship("Supplier", back_populates="contracts")

    def __repr__(self) -> str:
        return f"<Contract id={self.id} valor={self.valor} fecha={self.fecha}>"


class RejectedRecord(Base):
    __tablename__ = "rejected_records"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    fuente         = Column(String(100), nullable=False)
    payload_crudo  = Column(JSONB, nullable=False)
    motivo_rechazo = Column(String(100), nullable=False)
    fecha_rechazo  = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<RejectedRecord id={self.id} motivo='{self.motivo_rechazo}'>"
