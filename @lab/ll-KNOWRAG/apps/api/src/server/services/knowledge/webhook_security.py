"""HMAC-SHA256 verification for inbound Gitea webhooks.

Gitea sends ``X-Gitea-Signature`` as the lowercase hex-encoded HMAC-SHA256 of
the raw request body, keyed by the webhook secret configured per-hook.

Constant-time comparison via :func:`hmac.compare_digest` to avoid timing
oracles.
"""
from __future__ import annotations

import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)


class WebhookVerificationError(Exception):
    """Raised when an inbound webhook fails authenticity verification."""


def verify_gitea_signature(
    *,
    secret: str,
    payload: bytes,
    signature_header: str | None,
) -> None:
    """Verify a Gitea webhook signature. Raises ``WebhookVerificationError``
    on any failure (missing secret, missing header, mismatch).
    """
    if not secret:
        raise WebhookVerificationError("server-side webhook secret not configured")
    if not isinstance(payload, (bytes, bytearray)):
        raise WebhookVerificationError("payload must be bytes")
    if not signature_header:
        raise WebhookVerificationError("missing X-Gitea-Signature header")

    received = signature_header.strip().lower()
    # Tolerate the "sha256=" prefix some senders include.
    if received.startswith("sha256="):
        received = received[len("sha256="):]

    expected = hmac.new(
        secret.encode("utf-8"),
        bytes(payload),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, received):
        # Don't log the received signature — could be misused for replay.
        logger.warning("Gitea webhook signature mismatch (payload size=%d)", len(payload))
        raise WebhookVerificationError("signature mismatch")


__all__ = ["WebhookVerificationError", "verify_gitea_signature"]
