# Auth0 — configuración y pruebas (ver auth.md)

ContrataData usa Auth0 para "quién es el usuario" (login con Google,
Microsoft o email) y Neon para "qué plan tiene y qué puede usar"
(`app_users` + `subscriptions` + `premium_entitlements`, ver
`src/load/models.py`). El frontend nunca decide acceso premium de forma
definitiva — todo pasa por el backend (`src/api/deps.py::require_pro` /
`require_feature`).

Esta guía no puede completarse sola: la parte de "crear el tenant y las
apps en Auth0" es manual, en el dashboard de Auth0, con tu propia cuenta.

---

## 1. Configuración en el dashboard de Auth0

### 1.1 Crear el tenant

Si no tienes uno: [auth0.com](https://auth0.com) → Sign up → crear tenant
(región US o la más cercana a Neon/Railway).

### 1.2 Crear la API (para FastAPI)

Applications → APIs → Create API:
- **Name**: `ContrataData API`
- **Identifier** (esto es el `audience`): algo como `https://api.contratadata.xyz`
  (no tiene que ser una URL real y accesible, es solo un identificador único)
- **Signing Algorithm**: RS256

Este Identifier es el valor de `AUTH0_AUDIENCE` en **ambos** `.env` (backend
y frontend) — tiene que coincidir exacto en los dos lados.

### 1.3 Crear la Application (para Next.js)

Applications → Applications → Create Application → **Regular Web
Application** (no SPA — el SDK de Next.js corre server-side):
- **Name**: `ContrataData Web`
- En la pestaña Settings, anotar `Domain`, `Client ID`, `Client Secret`.

Bajo **Application URIs**, configurar (ajustar el dominio en producción):

| Campo | Valor (dev) | Valor (prod) |
|---|---|---|
| Allowed Callback URLs | `http://localhost:3000/api/auth/callback` | `https://contratadata.xyz/api/auth/callback` |
| Allowed Logout URLs | `http://localhost:3000` | `https://contratadata.xyz` |
| Allowed Web Origins | `http://localhost:3000` | `https://contratadata.xyz` |
| Allowed CORS Origins | `http://localhost:3000` | `https://contratadata.xyz` |

Se pueden poner ambas (dev y prod) separadas por coma en el mismo campo
mientras se prueba localmente contra un tenant compartido.

### 1.4 Connections (login social + email)

Authentication → Social:
- Activar **Google** (requiere client id/secret de Google Cloud Console —
  Auth0 trae uno de desarrollo limitado si no se configura uno propio).
- Activar **Microsoft** (Azure AD / cuentas personales, según lo que se
  quiera soportar — Auth0 trae uno de desarrollo también).

Authentication → Database (para email/password) o Passwordless (para
magic link real): activar la que se prefiera. Passwordless con email es
más fiel a "preferiblemente passwordless/magic link" del alcance, pero
requiere configurar un proveedor de email en Auth0 (o usar el de prueba,
limitado). Database connection con email+password es la opción más simple
de arrancar y se puede migrar a passwordless después sin tocar el código
del SDK (es configuración de Auth0, no del backend/frontend).

En Applications → [ContrataData Web] → Connections, habilitar las
connections que se activaron arriba para esta Application específica.

### 1.5 Universal Login

Branding → Universal Login: dejar en modo **New** (no Classic) — es lo que
usa `handleLogin()` del SDK por defecto, no requiere configuración extra
más allá de personalizar logo/colores si se quiere.

### 1.6 RBAC (roles internos, no el plan pago)

User Management → Roles → crear `admin` y `support` si se necesitan para
uso interno del equipo (soporte, moderación). **No usar RBAC para el plan
Pro** — eso vive en Neon (`subscriptions`), nunca en un rol de Auth0, tal
como pide auth.md.

---

## 2. Variables de entorno

### Backend (`.env`, ver `.env.example`)

```
AUTH0_DOMAIN=tu-tenant.us.auth0.com
AUTH0_AUDIENCE=https://api.contratadata.xyz
AUTH0_ISSUER=                # vacío = usa https://{AUTH0_DOMAIN}/ automáticamente
AUTH0_ALGORITHMS=RS256
```

### Frontend (`frontend/.env.local`, ver `frontend/.env.example`)

```
AUTH0_SECRET=<openssl rand -hex 32>
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://tu-tenant.us.auth0.com
AUTH0_CLIENT_ID=<de la Application>
AUTH0_CLIENT_SECRET=<de la Application>
AUTH0_AUDIENCE=https://api.contratadata.xyz   # el mismo Identifier que arriba
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

En Railway/Vercel, agregar las mismas variables en la configuración de
cada servicio (backend en Railway, frontend en Vercel) — `AUTH0_BASE_URL`
en producción debe ser la URL real (`https://contratadata.xyz`).

---

## 3. Marcar un usuario como Pro para pruebas

No hay backoffice ni pagos automatizados todavía (ver auth.md). El usuario
tiene que haber iniciado sesión **al menos una vez** — el primer request
autenticado (`GET /api/me`, o cualquier endpoint que dependa de
`require_auth0_user`) crea su fila en `app_users`. Después:

```bash
python admin_set_pro.py usuario@ejemplo.com --status active
# o con fecha de corte:
python admin_set_pro.py usuario@ejemplo.com --status active --until 2026-12-31
# revertir a free:
python admin_set_pro.py usuario@ejemplo.com --plan free --status expired
```

Si el script falla con "No existe un app_user con email=...", el usuario
todavía no inició sesión — pedirle que entre una vez a la app primero.

---

## 4. Cómo probar el flujo completo

1. Configurar Auth0 (sección 1) y ambos `.env` (sección 2).
2. Levantar backend y frontend:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   cd frontend && npm run dev
   ```
3. Entrar a `localhost:3000`, clic en "Ingresar" → Universal Login → elegir
   Google/Microsoft/email → vuelve a la app ya logueado (avatar + nombre en
   el Navbar).
4. Confirmar que `GET /api/me` valida el token y sincroniza el usuario:
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
           print(u.id, u.auth0_sub, u.email, u.last_login_at)
   "
   ```
5. Sin ser Pro, ir a "Mis alertas" o intentar "Guardar alerta"/"Seguir
   competidor"/"Exportar reporte" → debe mostrar el paywall suave (precio
   COP $149.000/mes beta, botón "Solicitar acceso Pro").
6. Clic en "Solicitar acceso Pro" → confirmar que quedó en `premium_leads`
   (mismo query que el paso 4, cambiando el modelo a `PremiumLead`).
7. Marcar el usuario como Pro (sección 3) y repetir el paso 5 — ahora la
   acción debe completarse (alerta guardada, competidor seguido, reporte
   descargado) sin mostrar paywall.
8. Confirmar que un usuario **sin token** no puede llamar `/api/me`:
   ```bash
   curl -i http://localhost:8000/api/me   # 401 esperado, sin Authorization
   ```
9. Clic en "Cerrar sesión" → confirma que el Navbar vuelve a mostrar
   "Ingresar" y que las páginas premium vuelven a pedir login.

---

## 5. Seguridad — lo que ya está y lo que falta

Ya implementado (ver auth.md, sección Seguridad):
- El SDK de Auth0 guarda la sesión en una cookie httpOnly, nunca en
  localStorage.
- El backend siempre valida el JWT contra el JWKS real de Auth0
  (`src/api/auth0.py`) — firma RS256, issuer, audience y expiración.
- El frontend nunca decide acceso premium por sí solo: `PremiumGate` y
  `useFeatureGate` reflejan lo que ya devolvió el backend, no deciden nada.

Pendiente / conocido (documentado también en la entrega principal):
- El access token SÍ pasa brevemente por JS del cliente (vía `/api/token`)
  para adjuntarlo como `Authorization: Bearer` en llamadas directas del
  navegador a FastAPI. Una versión más estricta proxearía cada llamada
  autenticada a través de Route Handlers de Next.js (usando
  `getAccessToken()` server-side) para que el token nunca toque el
  navegador — no se implementó así en este alcance para no multiplicar
  rutas proxy por cada endpoint premium existente.
- Rate limiting en endpoints sensibles (login, `/api/me`) no está
  implementado — Auth0 ya limita intentos de login a nivel de tenant, pero
  el backend propio no tiene throttling adicional todavía.
- `email_verified` se sincroniza y se expone en `app_users`, pero ningún
  endpoint lo exige todavía (ej. para desbloquear beneficios) — agregar esa
  validación si se conecta un flujo de pago real.
