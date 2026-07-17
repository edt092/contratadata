# Clerk — configuración, migración y rollback (ver auth2.md)

ContrataData usa Clerk para "quién es el usuario" (login social/email) y
Neon para "qué plan tiene y qué puede usar" (`app_users` + `subscriptions`
+ `premium_entitlements`, ver `src/load/models.py`). El frontend nunca
decide acceso premium de forma definitiva — todo pasa por el backend
(`src/api/deps.py::require_pro` / `require_feature`).

Reemplaza a `docs/auth0-setup.md` (eliminado) — la migración fue un corte
directo (no dual-provider), ver `auth2.md` para el razonamiento.

---

## 1. Configuración en el dashboard de Clerk

Esta parte es manual, en [clerk.com](https://clerk.com), con tu propia
cuenta.

### 1.1 Crear la aplicación

Sign up → Create application → nombre `ContrataData`. Clerk crea
automáticamente una instancia **Development** — usarla para local/staging;
crear la instancia **Production** aparte cuando el dominio final esté listo
(Clerk no promueve dev → prod automáticamente, hay que reconfigurar
providers sociales en la instancia de producción).

### 1.2 Connections (login social + email)

User & Authentication → Social Connections: activar Google (y las que se
quieran soportar). Email/password o email code (magic link) se configuran
en User & Authentication → Email, Phone, Username.

### 1.3 API Keys

API Keys (panel izquierdo):
- `Publishable key` → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (frontend).
- `Secret key` → `CLERK_SECRET_KEY` (frontend Y backend).
- `Show JWKS URL` → `CLERK_JWKS_URL` (backend) — la misma URL sin el sufijo
  `/.well-known/jwks.json` es `CLERK_ISSUER`.

### 1.4 Webhook endpoint

Webhooks → Add Endpoint:
- **URL**: `https://<tu-backend>/api/webhooks/clerk` (en local, exponer con
  `ngrok`/`cloudflared` si se quiere probar webhooks reales; si no, basta
  con los tests de `tests/test_webhooks_clerk.py`).
- **Events**: `user.created`, `user.updated`, `user.deleted`.
- Copiar el **Signing Secret** (`whsec_...`) → `CLERK_WEBHOOK_SECRET`.

---

## 2. Variables de entorno

### Backend (`.env`, ver `.env.example`)

```
CLERK_SECRET_KEY=sk_...
CLERK_JWKS_URL=https://tu-instancia.clerk.accounts.dev/.well-known/jwks.json
CLERK_ISSUER=https://tu-instancia.clerk.accounts.dev
CLERK_ALGORITHMS=RS256
CLERK_AUTHORIZED_PARTIES=http://localhost:3000,https://contratadata.xyz
CLERK_WEBHOOK_SECRET=whsec_...
```

### Frontend (`frontend/.env.local`, ver `frontend/.env.example`)

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

En Railway (backend) y Vercel (frontend), agregar las mismas variables —
usando las keys de la instancia **Production** de Clerk en producción, no
las de Development.

---

## 3. Migración de base de datos — orden exacto

1. **Backup**: crear un branch de Neon antes de tocar producción —
   `neonctl branches create --project-id <id> --name pre-clerk-migration`
   (o desde el dashboard de Neon: Branches → Create branch). Es instantáneo
   y reversible; si algo sale mal, se puede restaurar apuntando `DATABASE_URL`
   al branch de backup.
2. `python migrate_auth_clerk.py` contra la base de producción — aditivo,
   agrega columnas nuevas (`auth_provider`, `auth_provider_user_id`,
   `saved_alerts.user_id`, `competitor_watchlist.user_id`), backfillea desde
   `auth0_sub`/`user_email`, y reporta filas sin vincular o emails
   ambiguos. Revisar el log — si reporta filas sin vincular, resolverlas a
   mano antes de continuar.
3. Desplegar el backend y frontend con Clerk (deploy normal).
4. Verificar en producción real (sección 5) que login/vinculación/alertas/
   competidores funcionan.
5. **Días después**, una vez confirmado que no queda tráfico usando
   `auth0_sub`/`user_email` para nada: `python cleanup_auth0_columns.py
   --dry-run` y luego `--apply` — esto SÍ es destructivo (DROP COLUMN),
   tomar otro branch de Neon antes.

---

## 4. Marcar un usuario como Pro para pruebas

Sin cambios respecto a Auth0 — el usuario tiene que haber iniciado sesión
**al menos una vez** (`GET /api/me` sincroniza su fila en `app_users`):

```bash
python admin_set_pro.py usuario@ejemplo.com --status active
python admin_set_pro.py usuario@ejemplo.com --status active --until 2026-12-31
python admin_set_pro.py usuario@ejemplo.com --plan free --status expired
```

---

## 5. Cómo probar el flujo completo

1. Configurar Clerk (sección 1) y ambos `.env` (sección 2).
2. Levantar backend y frontend:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   cd frontend && pnpm dev
   ```
3. Entrar a `localhost:3000`, clic en "Ingresar" → `/sign-in` de Clerk →
   elegir Google/email → vuelve a la app ya logueado (avatar + nombre en el
   Navbar).
4. **Usuario migrado de Auth0**: iniciar sesión con el mismo email
   verificado que un `app_user` existente (creado antes del corte) →
   confirmar que se vincula al mismo `id` (no crea uno nuevo) y conserva su
   plan/`Subscription`:
   ```bash
   python -c "
   from src.load.loader import get_engine
   from src.load.models import AppUser
   from sqlalchemy.orm import Session
   from sqlalchemy import select
   import os
   from dotenv import load_dotenv; load_dotenv()
   with Session(get_engine(os.getenv('DATABASE_URL'))) as s:
       for u in s.execute(select(AppUser)).scalars():
           print(u.id, u.auth_provider, u.auth_provider_user_id, u.email, u.is_active)
   "
   ```
5. Sin ser Pro, ir a "Mis alertas" o intentar "Guardar alerta"/"Seguir
   competidor"/"Exportar reporte" → paywall suave.
6. Marcar el usuario como Pro (sección 4) y repetir el paso 5 — la acción
   debe completarse sin paywall. Confirmar que la alerta/competidor quedó
   con el `user_id` correcto (no `user_email`).
7. Confirmar que un usuario **sin token** no puede llamar `/api/me`:
   ```bash
   curl -i http://localhost:8000/api/me   # 401 esperado
   ```
8. Clic en "Cerrar sesión" → el Navbar vuelve a mostrar "Ingresar".
9. **Webhook `user.deleted`**: eliminar el usuario de prueba desde el
   dashboard de Clerk (User & Authentication → Users) → confirmar que su
   `app_users.is_active` pasa a `false` y que `subscriptions`/
   `payment_references` siguen intactos.

---

## 6. Rollback

- **Antes de la Fase 3 (cleanup)**: las columnas nuevas son aditivas —
  revertir el deploy del código a la versión con Auth0 es seguro,
  `auth0_sub`/`user_email` nunca se tocaron.
- **Después del cleanup**: el único rollback real es restaurar el branch de
  Neon tomado en el paso 5 de la sección 3 — `DROP COLUMN` no es
  reversible de otra forma.

---

## 7. Seguridad — lo que ya está y lo que falta

Ya implementado (ver auth2.md):
- Clerk gestiona la sesión del lado del cliente; el token nunca se
  persiste en `localStorage` ni en una cookie propia — se pide fresco en
  cada llamada vía `getToken()`.
- El backend siempre valida el session token contra el JWKS real de la
  instancia de Clerk (`src/api/clerk.py`) — firma RS256, issuer, `azp`
  contra `CLERK_AUTHORIZED_PARTIES`, expiración/`nbf`.
- Los webhooks de identidad verifican la firma Svix (`CLERK_WEBHOOK_SECRET`)
  y nunca modifican `subscriptions`/`premium_entitlements`.
- El frontend nunca decide acceso premium por sí solo: `PremiumGate` y
  `useFeatureGate` reflejan lo que ya devolvió el backend.

Pendiente / conocido:
- Rate limiting en endpoints sensibles (`/api/me`, `/api/webhooks/clerk`)
  no está implementado — Clerk limita intentos de login a nivel de
  instancia, pero el backend propio no tiene throttling adicional.
- `cleanup_auth0_columns.py` es un paso manual posterior al corte —
  alguien tiene que acordarse de correrlo (y de actualizar
  `src/load/models.py` en el mismo commit, ver el warning que imprime el
  script al aplicar).
