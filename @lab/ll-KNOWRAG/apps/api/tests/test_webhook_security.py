"""Tests for Gitea webhook HMAC verification (T7)."""
from __future__ import annotations

import hashlib
import hmac

import pytest

from server.services.knowledge.webhook_security import (
    WebhookVerificationError,
    verify_gitea_signature,
)


def _signed(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def test_valid_signature_passes():
    secret = "supersecret"
    payload = b'{"hello":"world"}'
    sig = _signed(secret, payload)
    verify_gitea_signature(secret=secret, payload=payload, signature_header=sig)


def test_signature_with_sha256_prefix_accepted():
    secret = "s"
    payload = b"data"
    sig = "sha256=" + _signed(secret, payload)
    verify_gitea_signature(secret=secret, payload=payload, signature_header=sig)


def test_signature_case_insensitive():
    secret = "s"
    payload = b"data"
    sig = _signed(secret, payload).upper()
    verify_gitea_signature(secret=secret, payload=payload, signature_header=sig)


def test_signature_with_whitespace_trimmed():
    secret = "s"
    payload = b"data"
    sig = "  " + _signed(secret, payload) + "  "
    verify_gitea_signature(secret=secret, payload=payload, signature_header=sig)


# ── Failure cases ──────────────────────────────────────────────────────────


def test_missing_secret_raises():
    with pytest.raises(WebhookVerificationError, match="not configured"):
        verify_gitea_signature(
            secret="", payload=b"x", signature_header="anything"
        )


def test_missing_signature_header_raises():
    with pytest.raises(WebhookVerificationError, match="missing.*header"):
        verify_gitea_signature(
            secret="s", payload=b"x", signature_header=None
        )


def test_empty_signature_header_raises():
    with pytest.raises(WebhookVerificationError, match="missing.*header"):
        verify_gitea_signature(
            secret="s", payload=b"x", signature_header=""
        )


def test_mismatched_signature_raises():
    with pytest.raises(WebhookVerificationError, match="mismatch"):
        verify_gitea_signature(
            secret="s",
            payload=b"x",
            signature_header="0" * 64,
        )


def test_wrong_secret_produces_mismatch():
    payload = b"data"
    sig = _signed("right-secret", payload)
    with pytest.raises(WebhookVerificationError, match="mismatch"):
        verify_gitea_signature(
            secret="wrong-secret", payload=payload, signature_header=sig
        )


def test_modified_payload_produces_mismatch():
    secret = "s"
    sig = _signed(secret, b"original")
    with pytest.raises(WebhookVerificationError, match="mismatch"):
        verify_gitea_signature(
            secret=secret, payload=b"tampered", signature_header=sig
        )


def test_payload_must_be_bytes():
    sig = _signed("s", b"x")
    with pytest.raises(WebhookVerificationError, match="must be bytes"):
        verify_gitea_signature(
            secret="s",
            payload="string",  # type: ignore[arg-type]
            signature_header=sig,
        )


# ── Constant-time comparison sanity ────────────────────────────────────────


def test_equal_signatures_pass_bytearray_payload():
    """Verify bytearray (not just bytes) is accepted."""
    secret = "s"
    payload = bytearray(b"data")
    sig = _signed(secret, bytes(payload))
    verify_gitea_signature(
        secret=secret, payload=payload, signature_header=sig
    )


def test_signature_with_extra_chars_fails():
    secret = "s"
    payload = b"data"
    sig = _signed(secret, payload) + "0"
    with pytest.raises(WebhookVerificationError, match="mismatch"):
        verify_gitea_signature(
            secret=secret, payload=payload, signature_header=sig
        )
