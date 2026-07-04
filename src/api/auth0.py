"""Validación de Access Tokens de Auth0 (ver auth.md).

Auth0 responde 'quién es el usuario' — este módulo solo verifica que el
token sea genuino (firma RS256 contra el JWKS de Auth0, issuer, audience,
expiración) y devuelve los claims. La decisión de qué puede usar ese usuario
vive en Neon (src/api/deps.py::require_pro/require_feature), nunca acá.
"""

import os
from functools import lru_cache

import jwt
from fastapi import HTTPException
from jwt import PyJWKClient

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
# Issuer casi siempre es https://{domain}/ — se permite override explícito
# por si el tenant usa un dominio custom distinto del de la API de gestión.
AUTH0_ISSUER = os.getenv("AUTH0_ISSUER") or (f"https://{AUTH0_DOMAIN}/" if AUTH0_DOMAIN else None)
AUTH0_ALGORITHMS = [a.strip() for a in os.getenv("AUTH0_ALGORITHMS", "RS256").split(",") if a.strip()]


class Auth0ConfigError(RuntimeError):
    """AUTH0_DOMAIN/AUTH0_AUDIENCE no están configurados en el servidor."""


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    if not AUTH0_DOMAIN:
        raise Auth0ConfigError("AUTH0_DOMAIN no está configurada.")
    # cache_jwk_set=True: no golpea el endpoint de Auth0 en cada request:
    # PyJWT cachea el JWKS por 'lifespan' segundos (default 300).
    return PyJWKClient(
        f"https://{AUTH0_DOMAIN}/.well-known/jwks.json",
        cache_jwk_set=True,
    )


def decode_auth0_token(token: str) -> dict:
    """Valida firma (RS256 contra el JWKS), issuer, audience y expiración.

    Lanza HTTPException: 500 si Auth0 no está configurado en el servidor
    (error nuestro, no del cliente), 401 si el token es inválido/expiró.
    """
    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
        raise HTTPException(status_code=500, detail="Auth0 no está configurado en el servidor.")
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Token inválido: {exc}") from exc
