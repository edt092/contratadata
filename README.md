# ContrataData

Pipeline ETL para consolidar datos de contratación pública colombiana desde SECOP y datos.gov.co, con visualización en dashboard.

## Stack

Python 3.12 · Requests · BeautifulSoup · Pandas · PostgreSQL 16 · SQLAlchemy · Docker · GitHub Actions · Streamlit

## Arquitectura

```
Fuentes Públicas → Extractor → Normalizador → Validador → Cargador → PostgreSQL → Dashboard
```

Cada etapa es un módulo independiente en `src/`. La orquestación corre en GitHub Actions; el entorno es 100% reproducible vía Docker.

## Ejecución local

```bash
# 1. Copia y completa las variables de entorno
cp .env.example .env

# 2. Levanta la base de datos
docker compose up -d db

# 3. Ejecuta el pipeline ETL una vez
docker compose run etl

# 4. Abre el dashboard
docker compose up dashboard
# → http://localhost:8080
```

## Tests

```bash
pip install -r requirements-dev.txt

# Tests unitarios (sin base de datos)
pytest tests/test_extract.py tests/test_transform.py -v

# Tests e2e (requiere el contenedor db corriendo)
docker compose up -d db
pytest tests/test_pipeline_e2e.py -v
```

## Estructura

```
src/
  extract/
    base.py              # Interfaz BaseExtractor
    secop_socrata.py     # Adaptador API SODA (datos.gov.co)
    secop_scraper.py     # Adaptador scraping HTML SECOP
  transform/
    normalize.py         # Resolución de nombres de entidades
    validate.py          # Reglas de calidad + enrutamiento de rechazos
  load/
    models.py            # Modelos SQLAlchemy
    loader.py            # Carga idempotente a PostgreSQL
  dashboard/
    queries.py           # Consultas de solo lectura
    app.py               # Interfaz Streamlit
pipeline.py              # Orquestador ETL
scripts/
  init_db.sql            # Esquema inicial de base de datos
.github/workflows/
  test.yml               # CI: tests en cada push
  run_pipeline.yml       # Ejecución programada (cron 3 AM UTC)
```

## Variables de entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | URL de conexión PostgreSQL | Sí |
| `SOCRATA_APP_TOKEN` | App Token para mayor cuota en datos.gov.co | Opcional |
| `MAX_RECORDS` | Límite de registros a extraer (0 = sin límite) | Opcional |
| `LOG_LEVEL` | Nivel de logging (DEBUG/INFO/WARNING) | Opcional |

## Competencias demostradas

- Web scraping (Requests, BeautifulSoup) y consumo de APIs REST (SODA)
- Pipeline ETL completo con manejo de rechazos y trazabilidad
- Modelado relacional en PostgreSQL con SQLAlchemy
- Calidad de datos: normalización de entidades, validación declarativa, idempotencia
- Arquitectura por componentes (pipeline desacoplado, adaptadores intercambiables)
- Containerización con Docker y Docker Compose
- CI/CD con GitHub Actions (tests + ejecución programada)
- Dashboard interactivo con Streamlit y Plotly
