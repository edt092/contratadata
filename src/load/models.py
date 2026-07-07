"""Modelos SQLAlchemy para el esquema relacional de ContrataData."""

from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey,
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
    __table_args__ = (
        # Requerido para el INSERT ... ON CONFLICT DO NOTHING masivo en
        # load_batch (src/load/loader.py). En bases existentes hay que
        # correr migrate_supplier_unique.py antes de desplegar este cambio.
        UniqueConstraint("nombre", name="uq_supplier_nombre"),
    )

    id              = Column(Integer, primary_key=True, autoincrement=True)
    nombre          = Column(String(500), nullable=False)
    # 150 en vez de 50: un NIT/id fiscal más largo de lo esperado no debe
    # tumbar el INSERT masivo del lote entero (ver migrate_widen_nit.py).
    nit_o_id_fiscal = Column(String(150))
    creado_en       = Column(DateTime, nullable=False, default=func.now())

    contracts = relationship("Contract", back_populates="supplier")

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} nombre='{self.nombre}'>"


class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = (
        # Clave natural real del contrato (id de proceso SECOP), no una combinación
        # de campos de negocio: permite detectar altas Y actualizaciones de estado.
        # Nullable a nivel de columna porque filas cargadas antes de este cambio
        # no tienen proceso_de_compra; NULL no colisiona consigo mismo en Postgres.
        UniqueConstraint("fuente", "proceso_de_compra", name="uq_contract_idempotent"),
        CheckConstraint("valor > 0", name="ck_valor_positivo"),
    )

    id                = Column(Integer, primary_key=True, autoincrement=True)
    entity_id         = Column(Integer, ForeignKey("entities.id"), nullable=False)
    supplier_id       = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    valor             = Column(Numeric(18, 2), nullable=False)
    fecha             = Column(Date, nullable=False)
    estado            = Column(String(100))
    fuente            = Column(String(100), nullable=False)
    proceso_de_compra = Column(String(150))
    extraido_en       = Column(DateTime, nullable=False, default=func.now())

    entity   = relationship("Entity", back_populates="contracts")
    supplier = relationship("Supplier", back_populates="contracts")

    def __repr__(self) -> str:
        return f"<Contract id={self.id} valor={self.valor} fecha={self.fecha}>"


class PipelineMeta(Base):
    """Metadatos del pipeline (ej. timestamp de la última corrida exitosa)."""
    __tablename__ = "pipeline_meta"

    key        = Column(String(100), primary_key=True)
    value      = Column(String(500), nullable=False)
    updated_at = Column(DateTime, nullable=False, default=func.now())


class PipelineRun(Base):
    """Una fila por corrida de pipeline.py — reemplaza a errors.md (que vive
    y muere con el runner efímero de GitHub Actions) como fuente de verdad
    de si una corrida realmente cargó datos o solo *pareció* exitosa."""
    __tablename__ = "pipeline_runs"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    started_at       = Column(DateTime, nullable=False)
    finished_at      = Column(DateTime)
    # running | success | success_with_errors | degraded_aborted | failed
    status           = Column(String(30), nullable=False, default="running")
    modo             = Column(String(80))
    extracted_count  = Column(Integer, nullable=False, default=0)
    inserted_count   = Column(Integer, nullable=False, default=0)
    updated_count    = Column(Integer, nullable=False, default=0)
    rejected_count   = Column(Integer, nullable=False, default=0)
    failed_batches   = Column(Integer, nullable=False, default=0)
    total_batches    = Column(Integer, nullable=False, default=0)
    error_summary    = Column(String(2000))
    created_at       = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<PipelineRun id={self.id} status='{self.status}'>"


class PipelineBatchError(Base):
    """Detalle por lote fallido de una corrida — permite diagnosticar sin
    tener que ir a buscar en los logs crudos de GitHub Actions."""
    __tablename__ = "pipeline_batch_errors"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    run_id         = Column(Integer, ForeignKey("pipeline_runs.id"), nullable=False)
    batch_number   = Column(Integer, nullable=False)
    approx_offset  = Column(Integer)
    error_type     = Column(String(200))
    error_message  = Column(String(2000))
    created_at     = Column(DateTime, nullable=False, default=func.now())


class Feedback(Base):
    """Feedback de usuarios en fase de user testing — no requiere login."""
    __tablename__ = "feedback"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    feedback_type   = Column(String(50), nullable=False)
    comment         = Column(String(4000), nullable=False)
    email           = Column(String(255))
    importance      = Column(String(20), nullable=False)
    consent_contact = Column(Boolean, nullable=False, default=False)
    page_url        = Column(String(1000))
    route           = Column(String(500))
    filters_json    = Column(JSONB)
    user_agent      = Column(String(500))
    viewport        = Column(String(50))
    referrer        = Column(String(1000))
    status          = Column(String(30), nullable=False, default="new")
    # 'pending' si dejó email (candidato a créditos premium de la beta), 'none' si no.
    reward_status   = Column(String(30), nullable=False, default="none")
    created_at      = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} type='{self.feedback_type}'>"


class AppUser(Base):
    """Usuario autenticado vía Auth0 (ver auth.md). Auth0 responde 'quién es
    el usuario' (auth0_sub es la identidad estable); ContrataData/Neon
    responde 'qué plan tiene' (Subscription/PremiumEntitlement) — nunca al
    revés. Se crea/actualiza en cada sync (GET /api/me o cualquier endpoint
    autenticado), no en el login en sí."""
    __tablename__ = "app_users"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    auth0_sub      = Column(String(255), unique=True, nullable=False)
    email          = Column(String(255), unique=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    name           = Column(String(255))
    picture        = Column(String(1000))
    created_at     = Column(DateTime, nullable=False, default=func.now())
    updated_at     = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    last_login_at  = Column(DateTime)

    def __repr__(self) -> str:
        return f"<AppUser id={self.id} email='{self.email}'>"


class Subscription(Base):
    """Suscripción del usuario — fuente de verdad del plan pago. Sin
    integración de pagos todavía (ver auth.md): 'provider' queda nullable y
    'manual' hasta conectar Stripe/Wompi/MercadoPago por webhook."""
    __tablename__ = "subscriptions"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    user_id                 = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    # free | pro
    plan                    = Column(String(20), nullable=False, default="free")
    # trialing | active | past_due | canceled | expired
    status                  = Column(String(20), nullable=False, default="trialing")
    # stripe | wompi | mercadopago | manual
    provider                = Column(String(30))
    provider_customer_id    = Column(String(255))
    provider_subscription_id = Column(String(255))
    current_period_end      = Column(DateTime)
    created_at              = Column(DateTime, nullable=False, default=func.now())
    updated_at              = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Subscription user_id={self.user_id} plan='{self.plan}' status='{self.status}'>"


class PremiumEntitlement(Base):
    """Acceso a una feature específica fuera de una subscription normal —
    créditos beta, cortesías manuales, etc. Un usuario Free puede tener un
    entitlement puntual sin ser Pro en general (ver require_feature)."""
    __tablename__ = "premium_entitlements"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    # saved_alerts | competitor_monitor | reports
    feature_key = Column(String(50), nullable=False)
    is_enabled  = Column(Boolean, nullable=False, default=True)
    # subscription | manual | beta_credit
    source      = Column(String(30), nullable=False, default="manual")
    expires_at  = Column(DateTime)
    created_at  = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<PremiumEntitlement user_id={self.user_id} feature='{self.feature_key}'>"


class PremiumLead(Base):
    """Interés en el plan Pro desde el paywall suave — antes de tener cobros
    automatizados, esto es la señal de validación de demanda. 'user_id' es
    nullable porque el endpoint autenticado (POST /premium/request-access)
    y el histórico anterior sin login pueden coexistir."""
    __tablename__ = "premium_leads"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("app_users.id"))
    email      = Column(String(255), nullable=False)
    # Feature que disparó el paywall (ej. 'saved_alerts', 'competitor_monitor', 'reports') — nullable.
    feature    = Column(String(50))
    created_at = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<PremiumLead email='{self.email}'>"


class SavedAlert(Base):
    """Alerta guardada por un usuario Pro sobre una búsqueda/filtro."""
    __tablename__ = "saved_alerts"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_email      = Column(String(255), nullable=False)
    name            = Column(String(200), nullable=False)
    entidad         = Column(String(500))
    contratista     = Column(String(500))
    estado          = Column(String(100))
    desde           = Column(Date)
    hasta           = Column(Date)
    valor_min       = Column(Numeric(18, 2))
    valor_max       = Column(Numeric(18, 2))
    # daily | weekly
    frecuencia      = Column(String(20), nullable=False, default="daily")
    is_active       = Column(Boolean, nullable=False, default=True)
    last_checked_at = Column(DateTime)
    created_at      = Column(DateTime, nullable=False, default=func.now())
    updated_at      = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<SavedAlert id={self.id} name='{self.name}' user='{self.user_email}'>"


class CompetitorWatch(Base):
    """Contratista seguido por un usuario Pro (monitor de competidores)."""
    __tablename__ = "competitor_watchlist"
    __table_args__ = (
        UniqueConstraint("user_email", "supplier_name", name="uq_competitor_watch_user_supplier"),
    )

    id            = Column(Integer, primary_key=True, autoincrement=True)
    user_email    = Column(String(255), nullable=False)
    supplier_name = Column(String(500), nullable=False)
    nickname      = Column(String(200))
    is_active     = Column(Boolean, nullable=False, default=True)
    created_at    = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<CompetitorWatch user='{self.user_email}' supplier='{self.supplier_name}'>"


class PaymentReference(Base):
    """Puente entre un checkout de Wompi y el usuario que lo inició — el
    webhook de Wompi (ver src/api/routers/webhooks.py) solo trae 'reference'
    y datos de la transacción, no nuestro user_id, así que esta fila se crea
    *antes* de redirigir al widget para poder correlacionar la respuesta."""
    __tablename__ = "payment_references"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    user_id              = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    reference            = Column(String(120), unique=True, nullable=False)
    # monthly | annual
    plan                 = Column(String(20), nullable=False)
    amount_in_cents      = Column(Integer, nullable=False)
    # pending | approved | declined | voided | error
    status               = Column(String(20), nullable=False, default="pending")
    wompi_transaction_id = Column(String(255))
    created_at           = Column(DateTime, nullable=False, default=func.now())
    updated_at           = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<PaymentReference reference='{self.reference}' status='{self.status}'>"


class RejectedRecord(Base):
    __tablename__ = "rejected_records"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    fuente         = Column(String(100), nullable=False)
    payload_crudo  = Column(JSONB, nullable=False)
    motivo_rechazo = Column(String(100), nullable=False)
    fecha_rechazo  = Column(DateTime, nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<RejectedRecord id={self.id} motivo='{self.motivo_rechazo}'>"
