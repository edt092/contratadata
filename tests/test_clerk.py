"""Tests de validación de session tokens de Clerk (src/api/clerk.py) — sin
instancia real (ver auth2.md FASE 9, reemplaza a tests/test_auth0.py).

Genera un keypair RSA de prueba y firma tokens localmente, simulando lo que
haría Clerk. El JWKS de Clerk (fetch por red) se reemplaza por un stub que
devuelve la clave pública del keypair de prueba, para no depender de
credenciales ni de internet.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

import src.api.clerk as clerk_module
from src.api.clerk import decode_clerk_token

ISSUER = "https://contratadata-test.clerk.accounts.dev"
AUTHORIZED_PARTIES = ["http://localhost:3000", "https://contratadata.xyz"]


@pytest.fixture()
def keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


class _FakeSigningKey:
    def __init__(self, key):
        self.key = key


class _FakeJWKClient:
    def __init__(self, public_key):
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token):
        return _FakeSigningKey(self._public_key)


@pytest.fixture(autouse=True)
def _configure_clerk(monkeypatch, keypair):
    _, public_key = keypair
    monkeypatch.setattr(clerk_module, "CLERK_JWKS_URL", "https://contratadata-test.clerk.accounts.dev/.well-known/jwks.json")
    monkeypatch.setattr(clerk_module, "CLERK_ISSUER", ISSUER)
    monkeypatch.setattr(clerk_module, "CLERK_ALGORITHMS", ["RS256"])
    monkeypatch.setattr(clerk_module, "CLERK_AUTHORIZED_PARTIES", AUTHORIZED_PARTIES)
    monkeypatch.setattr(clerk_module, "_jwks_client", lambda: _FakeJWKClient(public_key))


def _make_token(private_key, **claim_overrides) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": "user_test123",
        "azp": "http://localhost:3000",
        "iss": ISSUER,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=60),
    }
    claims.update(claim_overrides)
    return jwt.encode(claims, private_key, algorithm="RS256")


def test_decode_valid_token_returns_claims(keypair):
    private_key, _ = keypair
    token = _make_token(private_key)

    claims = decode_clerk_token(token)

    assert claims["sub"] == "user_test123"
    assert claims["azp"] == "http://localhost:3000"


def test_decode_expired_token_raises_401(keypair):
    private_key, _ = keypair
    now = datetime.now(timezone.utc)
    token = _make_token(private_key, iat=now - timedelta(hours=2), nbf=now - timedelta(hours=2), exp=now - timedelta(hours=1))

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(token)
    assert exc_info.value.status_code == 401


def test_decode_not_yet_valid_token_raises_401(keypair):
    private_key, _ = keypair
    now = datetime.now(timezone.utc)
    token = _make_token(private_key, nbf=now + timedelta(minutes=10))

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(token)
    assert exc_info.value.status_code == 401


def test_decode_wrong_issuer_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key, iss="https://otra-instancia.clerk.accounts.dev")

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(token)
    assert exc_info.value.status_code == 401


def test_decode_unauthorized_azp_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key, azp="https://sitio-malicioso.example.com")

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(token)
    assert exc_info.value.status_code == 401


def test_decode_missing_azp_is_allowed(keypair):
    """Si el token no trae 'azp', se omite esa validación (ver doc oficial
    de Clerk: no todos los flujos lo incluyen)."""
    private_key, _ = keypair
    claims = {
        "sub": "user_test123",
        "iss": ISSUER,
        "iat": datetime.now(timezone.utc),
        "nbf": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    token = jwt.encode(claims, private_key, algorithm="RS256")

    result = decode_clerk_token(token)
    assert result["sub"] == "user_test123"


def test_decode_missing_sub_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key, sub=None)

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(token)
    assert exc_info.value.status_code == 401


def test_decode_tampered_signature_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key)
    tampered = token[:-4] + ("abcd" if not token.endswith("abcd") else "efgh")

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(tampered)
    assert exc_info.value.status_code == 401


def test_decode_missing_config_raises_500(keypair, monkeypatch):
    private_key, _ = keypair
    monkeypatch.setattr(clerk_module, "CLERK_JWKS_URL", None)
    token = _make_token(private_key)

    with pytest.raises(HTTPException) as exc_info:
        decode_clerk_token(token)
    assert exc_info.value.status_code == 500
