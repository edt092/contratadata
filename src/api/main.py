"""Aplicación FastAPI — ContrataData API."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.deps import PremiumRequiredError
from src.api.routers import (
    alerts, chart_images, charts, competitors, contratistas, contracts,
    entidades, estados, feedback, me, pipeline, premium, reports,
)

load_dotenv()

app = FastAPI(
    title="ContrataData API",
    description="API REST para datos de contratación pública colombiana (SECOP + datos.gov.co).",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
_origins = [
    "http://localhost:3000",   # Next.js dev
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]
extra = os.getenv("CORS_ORIGINS", "")
if extra:
    _origins.extend(o.strip() for o in extra.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
    # Content-Disposition no se expone a JS cross-origin por defecto — el
    # frontend lo necesita para nombrar el archivo al descargar reportes
    # (ver frontend/lib/api.ts::authGetBlob).
    expose_headers=["Content-Disposition"],
)


# ── Errores ──────────────────────────────────────────────────────────────────
@app.exception_handler(PremiumRequiredError)
async def premium_required_handler(request: Request, exc: PremiumRequiredError) -> JSONResponse:
    # Shape plano ({"error": ..., "plan_required": ..., "message": ...}), no
    # el {"detail": {...}} por defecto de FastAPI — así el frontend lo lee
    # directo para mostrar el paywall (ver auth.md).
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


# ── Routers ──────────────────────────────────────────────────────────────────
PREFIX = "/api"
app.include_router(contracts.router,    prefix=PREFIX)
app.include_router(entidades.router,    prefix=PREFIX)
app.include_router(contratistas.router, prefix=PREFIX)
app.include_router(charts.router,       prefix=PREFIX)
app.include_router(chart_images.router, prefix=PREFIX)
app.include_router(pipeline.router,     prefix=PREFIX)
app.include_router(estados.router,      prefix=PREFIX)
app.include_router(feedback.router,     prefix=PREFIX)
app.include_router(me.router,           prefix=PREFIX)
app.include_router(premium.router,      prefix=PREFIX)
app.include_router(alerts.router,       prefix=PREFIX)
app.include_router(competitors.router,  prefix=PREFIX)
app.include_router(reports.router,      prefix=PREFIX)


# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
