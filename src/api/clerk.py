"""Validación de session tokens de Clerk (ver auth2.md — reemplaza a
src/api/auth0.py).

Clerk responde 'quién es el usuario' — este módulo solo verifica que el
token sea genuino (firma RS256 contra el JWKS de la instancia de Clerk,
issuer, expiración/nbf, authorized parties) y devuelve los claims. La
decisión de qué puede usar ese usuario vive en Neon
(src/api/deps.py::require_pro/require_feature), nunca acá.

Verificación "networkless" (JWKS local vía CLERK_JWKS_URL) en vez de pegarle
a la Backend API de Clerk en cada request — mismo patrón que ya usaba
auth0.py con PyJWKClient. Ver https://clerk.com/docs/guides/sessions/manual-jwt-verification.
"""

import os
from functools import lru_cache

import jwt
import requests
from fastapi import HTTPException
from jwt import PyJWKClient

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_BACKEND_API_URL = "https://api.clerk.com/v1"

# CLERK_JWKS_URL: Frontend API de la instancia + /.well-known/jwks.json
# (ej. https://xxx.clerk.accounts.dev/.well-known/jwks.json, o el dominio
# custom de producción) — público, no requiere CLERK_SECRET_KEY.
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
# Issuer casi siempre es la Frontend API sin el sufijo /.well-known/... —
# se permite override explícito por si difiere del JWKS URL derivado.
CLERK_ISSUER = os.getenv("CLERK_ISSUER")
CLERK_ALGORITHMS = [a.strip() for a in os.getenv("CLERK_ALGORITHMS", "RS256").split(",") if a.strip()]
# Lista explícita de orígenes permitidos a generar tokens (ver auth2.md
# regla obligatoria) — valida el claim 'azp' cuando está presente.
CLERK_AUTHORIZED_PARTIES = [
    o.strip() for o in os.getenv("CLERK_AUTHORIZED_PARTIES", "").split(",") if o.strip()
]


class ClerkConfigError(RuntimeError):
    """CLERK_JWKS_URL/CLERK_ISSUER no están configurados en el servidor."""


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    if not CLERK_JWKS_URL:
        raise ClerkConfigError("CLERK_JWKS_URL no está configurada.")
    # cache_jwk_set=True: PyJWT cachea el JWKS por 'lifespan' segundos
    # (default 300) en vez de golpear el endpoint en cada request.
    return PyJWKClient(CLERK_JWKS_URL, cache_jwk_set=True)


def decode_clerk_token(token: str) -> dict:
    """Valida firma (RS256 contra el JWKS de Clerk), issuer, expiración/nbf
    y — si el token trae 'azp' — que sea uno de CLERK_AUTHORIZED_PARTIES.

    Lanza HTTPException: 500 si Clerk no está configurado en el servidor
    (error nuestro, no del cliente), 401 si el token es inválido/expiró/azp
    no autorizado/no trae 'sub'.
    """
    if not CLERK_JWKS_URL or not CLERK_ISSUER:
        raise HTTPException(status_code=500, detail="Clerk no está configurado en el servidor.")
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=CLERK_ALGORITHMS,
            issuer=CLERK_ISSUER,
            # Clerk no emite 'aud' en el session token por defecto — la
            # verificación de origen se hace vía 'azp', no 'audience'.
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Token inválido: {exc}") from exc

    if not claims.get("sub"):
        raise HTTPException(status_code=401, detail="Token sin 'sub'.")

    azp = claims.get("azp")
    if azp and CLERK_AUTHORIZED_PARTIES and azp not in CLERK_AUTHORIZED_PARTIES:
        raise HTTPException(status_code=401, detail="Token con 'azp' no autorizado.")

    return claims


def parse_clerk_user_payload(data: dict) -> dict:
    """Extrae email primario (solo si verificado), nombre e imagen de un
    objeto 'User' de Clerk — mismo shape en la respuesta de la Backend API
    (GET /v1/users/{id}) y en el payload de los webhooks user.created/
    user.updated (ver src/api/routers/clerk_webhooks.py), así que esta
    lógica de parseo vive en un solo lugar."""
    email = None
    email_verified = False
    primary_id = data.get("primary_email_address_id")
    for addr in data.get("email_addresses") or []:
        if addr.get("id") == primary_id:
            email = addr.get("email_address")
            email_verified = (addr.get("verification") or {}).get("status") == "verified"
            break

    name = " ".join(p for p in (data.get("first_name"), data.get("last_name")) if p) or None

    return {
        "email": email,
        "email_verified": email_verified,
        "name": name,
        "picture": data.get("image_url"),
    }


def fetch_clerk_user(clerk_user_id: str) -> dict:
    """Consulta server-side la Backend API de Clerk (ver auth2.md FASE 6)
    para un usuario nuevo — el session token no trae email/nombre/foto por
    defecto, a diferencia del ID token de Auth0. Solo se llama al crear o
    vincular un AppUser en el camino de login (ver src/api/deps.py); los
    webhooks ya traen el mismo payload y no necesitan este fetch.

    Devuelve el email primario SOLO si está verificado — nunca se usa un
    email no verificado para vincular cuentas (regla obligatoria de
    auth2.md)."""
    if not CLERK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="CLERK_SECRET_KEY no está configurada en el servidor.")

    try:
        resp = requests.get(
            f"{CLERK_BACKEND_API_URL}/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo consultar el perfil en Clerk: {exc}") from exc

    return parse_clerk_user_payload(data)
