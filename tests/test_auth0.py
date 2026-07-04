"""Tests de validación de JWT Auth0 (src/api/auth0.py) — sin tenant real.

Genera un keypair RSA de prueba y firma tokens localmente, simulando lo que
haría Auth0. El JWKS de Auth0 (fetch por red) se reemplaza por un stub que
devuelve la clave pública del keypair de prueba, para no depender de
credenciales ni de internet.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

import src.api.auth0 as auth0_module
from src.api.auth0 import decode_auth0_token

AUDIENCE = "https://api.contratadata.test"
ISSUER = "https://contratadata-test.us.auth0.com/"


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
def _configure_auth0(monkeypatch, keypair):
    _, public_key = keypair
    monkeypatch.setattr(auth0_module, "AUTH0_DOMAIN", "contratadata-test.us.auth0.com")
    monkeypatch.setattr(auth0_module, "AUTH0_AUDIENCE", AUDIENCE)
    monkeypatch.setattr(auth0_module, "AUTH0_ISSUER", ISSUER)
    monkeypatch.setattr(auth0_module, "AUTH0_ALGORITHMS", ["RS256"])
    monkeypatch.setattr(auth0_module, "_jwks_client", lambda: _FakeJWKClient(public_key))


def _make_token(private_key, **claim_overrides) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": "auth0|test-user-123",
        "email": "test@example.com",
        "email_verified": True,
        "name": "Test User",
        "picture": "https://example.com/pic.png",
        "aud": AUDIENCE,
        "iss": ISSUER,
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    claims.update(claim_overrides)
    return jwt.encode(claims, private_key, algorithm="RS256")


def test_decode_valid_token_returns_claims(keypair):
    private_key, _ = keypair
    token = _make_token(private_key)

    claims = decode_auth0_token(token)

    assert claims["sub"] == "auth0|test-user-123"
    assert claims["email"] == "test@example.com"
    assert claims["email_verified"] is True


def test_decode_expired_token_raises_401(keypair):
    private_key, _ = keypair
    now = datetime.now(timezone.utc)
    token = _make_token(private_key, iat=now - timedelta(hours=2), exp=now - timedelta(hours=1))

    with pytest.raises(HTTPException) as exc_info:
        decode_auth0_token(token)
    assert exc_info.value.status_code == 401


def test_decode_wrong_audience_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key, aud="https://otra-api.example.com")

    with pytest.raises(HTTPException) as exc_info:
        decode_auth0_token(token)
    assert exc_info.value.status_code == 401


def test_decode_wrong_issuer_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key, iss="https://otro-tenant.us.auth0.com/")

    with pytest.raises(HTTPException) as exc_info:
        decode_auth0_token(token)
    assert exc_info.value.status_code == 401


def test_decode_tampered_signature_raises_401(keypair):
    private_key, _ = keypair
    token = _make_token(private_key)
    tampered = token[:-4] + ("abcd" if not token.endswith("abcd") else "efgh")

    with pytest.raises(HTTPException) as exc_info:
        decode_auth0_token(tampered)
    assert exc_info.value.status_code == 401


def test_decode_missing_config_raises_500(keypair, monkeypatch):
    private_key, _ = keypair
    monkeypatch.setattr(auth0_module, "AUTH0_DOMAIN", None)
    token = _make_token(private_key)

    with pytest.raises(HTTPException) as exc_info:
        decode_auth0_token(token)
    assert exc_info.value.status_code == 500
