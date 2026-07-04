# Neon branches — probar sin tocar producción

ContrataData usa Postgres en Neon. La base de producción (`DATABASE_URL` en
`.env` / secrets de Railway y GitHub Actions) **nunca debe recibir pruebas
directas**: ni un ETL de prueba, ni una migración sin validar, ni un feedback
form a medio construir. Para eso existen las *branches* de Neon: una copia
aislada (copy-on-write, se crea en segundos) de la base, con su propio
connection string, que se puede tirar sin dejar rastro.

Esta guía cubre tres flujos manuales (ETL, migraciones, feedback form) y
explica el workflow automático de GitHub Actions para Pull Requests
(`.github/workflows/pr-db-check.yml`).

Referencia oficial: [Neon CLI](https://neon.com/docs/reference/neon-cli) ·
[Neon changelog](https://neon.com/docs/changelog).

---

## 0. Configuración local con Neon CLI

### Instalar

```bash
npm i -g neonctl
# o sin instalar globalmente:
npx neonctl@latest --version
```

### Autenticarse

Interactivo (abre el navegador):

```bash
neonctl auth
```

No interactivo (para scripts locales o CI), exportando la API key:

```bash
export NEON_API_KEY=<tu_api_key_de_neon>
```

La API key se genera en Neon Console → Account → API keys. **No la
compartas ni la pegues en commits, PRs o logs.**

### Crear una branch de prueba

```bash
neonctl branches create \
  --project-id <NEON_PROJECT_ID> \
  --name test-etl-cursor \
  --parent main
```

`--parent main` la crea como copia del estado actual de producción (schema +
datos). Sin `--parent`, usa la branch por defecto del proyecto.

### Obtener el connection string de esa branch

```bash
neonctl connection-string test-etl-cursor --project-id <NEON_PROJECT_ID>
```

Guárdalo en una variable de entorno de tu shell, nunca lo imprimas en un
commit, issue o mensaje de PR:

```bash
export BRANCH_DATABASE_URL="$(neonctl connection-string test-etl-cursor --project-id <NEON_PROJECT_ID>)"
```

### Correr el ETL apuntando a la branch

```bash
DATABASE_URL="$BRANCH_DATABASE_URL" MAX_RECORDS=200 python pipeline.py
```

`MAX_RECORDS` bajo evita esperar una corrida completa (~1-2h) solo para
validar que el código funciona.

### Borrar la branch al terminar

```bash
neonctl branches delete test-etl-cursor --project-id <NEON_PROJECT_ID>
```

Una branch olvidada no rompe nada (Neon las suspende por inactividad), pero
bórrala para mantener el proyecto limpio — sobre todo si contiene datos de
prueba con PII simulada.

---

## 1. Flujo: probar cambios del ETL

Para cualquier cambio en `pipeline.py`, `src/extract/`, `src/transform/` o
`src/load/`:

1. Crear branch desde producción:
   ```bash
   neonctl branches create --project-id <ID> --name test-etl-<tu-cambio> --parent main
   export BRANCH_DATABASE_URL="$(neonctl connection-string test-etl-<tu-cambio> --project-id <ID>)"
   ```
2. Si tu cambio agrega una tabla o columna nueva, correr la migración
   correspondiente (ver flujo 2) o dejar que `pipeline.py` la cree sola
   (`create_tables()` corre `Base.metadata.create_all` al inicio de cada
   corrida — ver `src/load/loader.py`).
3. Correr el ETL con un límite bajo:
   ```bash
   DATABASE_URL="$BRANCH_DATABASE_URL" MAX_RECORDS=200 python pipeline.py
   ```
4. Validar conteos y que no haya duplicados:
   ```bash
   python -c "
   from src.load.loader import get_engine
   from src.load.models import Contract
   from sqlalchemy.orm import Session
   from sqlalchemy import select, func
   engine = get_engine('$BRANCH_DATABASE_URL')
   with Session(engine) as s:
       total = s.scalar(select(func.count(Contract.id)))
       dupes = s.scalar(
           select(func.count()).select_from(
               select(Contract.fuente, Contract.proceso_de_compra, func.count())
               .group_by(Contract.fuente, Contract.proceso_de_compra)
               .having(func.count() > 1)
               .subquery()
           )
       )
       print(f'contratos: {total}, grupos duplicados por (fuente, proceso_de_compra): {dupes}')
   "
   ```
   `dupes` debe ser `0` — la restricción `uq_contract_idempotent` ya lo
   garantiza a nivel de base de datos, pero confirmarlo detecta si el
   upsert está fallando silenciosamente en vez de actualizar.
5. Validar `pipeline_meta` (cursor incremental compuesto, ver
   `src/load/loader.py::get_last_source_cursor`):
   ```bash
   python -c "
   from src.load.loader import get_engine, get_last_source_cursor, get_last_run_at
   engine = get_engine('$BRANCH_DATABASE_URL')
   print('cursor:', get_last_source_cursor(engine))
   print('last_run_at:', get_last_run_at(engine))
   "
   ```
6. Borrar la branch:
   ```bash
   neonctl branches delete test-etl-<tu-cambio> --project-id <ID>
   ```

---

## 2. Flujo: probar migraciones de schema

Este proyecto no usa Alembic — los cambios de schema son scripts one-off
(`migrate_*.py`) que usan `Base.metadata.create_all` (para tablas nuevas) o
`ALTER TABLE` explícito (para cambios de columna), documentado caso por caso
en el docstring de cada script.

1. Crear branch desde producción (misma base que usará la migración real):
   ```bash
   neonctl branches create --project-id <ID> --name test-migracion-<nombre> --parent main
   export BRANCH_DATABASE_URL="$(neonctl connection-string test-migracion-<nombre> --project-id <ID>)"
   ```
2. Aplicar la migración contra la branch, no contra producción:
   ```bash
   DATABASE_URL="$BRANCH_DATABASE_URL" python migrate_tu_cambio.py
   ```
3. Correr los tests contra esa branch (incluye los e2e que necesitan DB real
   y que normalmente se saltan en local por falta de `DATABASE_URL`):
   ```bash
   DATABASE_URL="$BRANCH_DATABASE_URL" pytest tests/ -v
   ```
4. Opcional — comparar el schema de la branch contra producción con
   [`neondatabase/schema-diff-action`](https://github.com/neondatabase/schema-diff-action)
   si la migración se está preparando dentro de un PR (ver sección 4); para
   una comparación manual rápida, `pg_dump --schema-only` a ambas branches y
   `diff` sirve igual de bien.
5. Si todo se ve bien, aplicar la migración a producción de la forma
   habitual (`DATABASE_URL=<producción> python migrate_tu_cambio.py`) y
   borrar la branch de prueba:
   ```bash
   neonctl branches delete test-migracion-<nombre> --project-id <ID>
   ```

---

## 3. Flujo: probar el feedback form

Para cambios en `src/api/routers/feedback.py`, `src/notify.py`, o el modal
del frontend (`frontend/components/FeedbackModal.tsx`):

1. Crear branch y aplicar la tabla `feedback`:
   ```bash
   neonctl branches create --project-id <ID> --name test-feedback-form --parent main
   export BRANCH_DATABASE_URL="$(neonctl connection-string test-feedback-form --project-id <ID>)"
   DATABASE_URL="$BRANCH_DATABASE_URL" python migrate_add_feedback_table.py
   ```
2. Levantar FastAPI apuntando a la branch:
   ```bash
   DATABASE_URL="$BRANCH_DATABASE_URL" uvicorn src.api.main:app --reload --port 8000
   ```
3. Levantar el frontend (`frontend/.env.local` con
   `NEXT_PUBLIC_API_URL=http://localhost:8000/api`) y enviar un feedback real
   desde el modal.
4. Confirmar que quedó guardado:
   ```bash
   python -c "
   from src.load.loader import get_engine
   from src.load.models import Feedback
   from sqlalchemy.orm import Session
   from sqlalchemy import select
   engine = get_engine('$BRANCH_DATABASE_URL')
   with Session(engine) as s:
       for r in s.execute(select(Feedback)).scalars():
           print(r.id, r.feedback_type, r.importance, r.reward_status, r.comment[:60])
   "
   ```
5. Confirmar que la notificación (`src/notify.py::notify_feedback`) no hace
   perder el registro aunque falle: correr sin `SMTP_HOST` (loguea y sigue)
   y, si quieres probar la ruta SMTP, con un `SMTP_HOST` inválido a
   propósito — en ambos casos la fila en `feedback` debe seguir ahí.
6. Borrar la branch:
   ```bash
   neonctl branches delete test-feedback-form --project-id <ID>
   ```

---

## 4. GitHub Actions para Pull Requests

`.github/workflows/pr-db-check.yml` automatiza una versión reducida de los
flujos 1 y 2 en cada Pull Request contra `main`:

1. Crea una branch de Neon temporal, nombrada con el número de PR y el
   `run_id` (para que corridas repetidas del mismo PR no choquen entre sí).
2. Enmascara el connection string en los logs (`::add-mask::`) apenas se
   crea — antes de cualquier otro paso.
3. Instala dependencias y corre `pytest tests/` completo contra esa branch
   (incluye los tests e2e que en local se saltan por falta de
   `DATABASE_URL`).
4. Corre el ETL real pero acotado (`MAX_RECORDS=100`) contra la branch, para
   detectar errores de extracción/carga sin esperar una corrida completa.
5. Publica un resumen en el Job Summary de GitHub Actions.
6. Borra la branch **siempre** (`if: always()`), incluso si algún paso
   anterior falló.

El workflow se salta por completo (`if`) en Pull Requests desde forks, para
no exponer `NEON_API_KEY`/`SOCRATA_APP_TOKEN` a código que no controlamos —
GitHub tampoco los inyecta por defecto en ese caso, pero el `if` explícito
lo deja documentado en vez de depender de ese comportamiento implícito.

### Secrets/variables requeridos en GitHub (Settings → Secrets and variables → Actions)

| Nombre | Tipo | Uso |
|---|---|---|
| `NEON_API_KEY` | Secret | Autenticar las Neon Actions (`create-branch-action` / `delete-branch-action`) |
| `NEON_PROJECT_ID` | Secret o Variable | Proyecto de Neon donde crear/borrar branches. No es sensible — puede vivir como *repository variable* (`vars.NEON_PROJECT_ID`), que es lo que recomienda la documentación oficial de Neon |
| `SOCRATA_APP_TOKEN` | Secret | El mismo token que usa `etl.yml`, para la prueba limitada del ETL |

`DATABASE_URL` **no** es un secret que este workflow use directamente: lo
genera `create-branch-action` en cada corrida (`steps.neon-branch.outputs.db_url`)
y vive solo en memoria del job, nunca en un secret de producción.

### Migraciones dentro de un PR

Si el PR agrega un script `migrate_*.py` nuevo, correrlo contra la branch es
un paso manual (no automático): el workflow no tiene forma de saber qué
migración corresponde a qué PR sin una convención adicional (ej. un archivo
`MIGRATIONS.md` o un manifiesto). Por ahora, seguir el flujo 2 de esta guía
localmente antes de mergear. Si esto se vuelve frecuente, vale la pena
agregar un paso al workflow que corra `migrate_*.py` solo si el diff del PR
toca ese archivo.

---

## 5. Seguridad

- Nunca pegar un connection string completo en un PR, issue, mensaje de
  Slack o log manual — contiene la contraseña del rol de Postgres.
- En CI, el connection string de la branch se enmascara con
  `::add-mask::` apenas se crea (ver `pr-db-check.yml`), antes de usarse en
  cualquier otro paso.
- `NEON_API_KEY` da permisos para crear/borrar branches y leer connection
  strings de *todo* el proyecto — tratarlo como una credencial de
  producción, no como un token de solo-lectura.
- Los workflows de PR desde forks no reciben secrets por defecto en GitHub
  Actions con el evento `pull_request` (a diferencia de
  `pull_request_target`, que este proyecto no usa); el `if` del job lo deja
  explícito igual.
- Nunca correr `FORCE_FULL_LOAD=1` en una branch de PR — no hace falta
  (`MAX_RECORDS=100` ya prueba que el pipeline corre) y una recarga
  completa contra una branch puede tardar tanto como contra producción.
- La branch de producción (`main` en Neon) solo la debe tocar el ETL real
  (`etl.yml`, sin cambios por este trabajo) y las migraciones aplicadas a
  mano después de validarlas en una branch.

---

## 6. Roadmap: features premium

Este mismo mecanismo de branches es la base para probar sin riesgo las
próximas features SaaS (usuarios, créditos premium, watchlists, alertas):
cualquier migración de schema para esas tablas nuevas debería pasar primero
por el flujo 2 de esta guía, y cualquier endpoint nuevo que las use por un
flujo equivalente al 3 (feedback form) — branch temporal, probar en
aislamiento, borrar. Cuando esas features tengan su propio volumen de
cambios, vale la pena revisar si conviene automatizar más de esto en
`pr-db-check.yml` (por ejemplo, ejecutar `migrate_*.py` condicionado al
diff del PR, mencionado arriba).
