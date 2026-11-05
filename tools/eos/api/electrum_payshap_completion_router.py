"""Electrum EPC PayShap signed completion ingress.

The HTTP handler verifies the provider's ES256 JWT and exact body digest,
persists a durable inbox event, then returns a signed 202. Financial allocation
runs separately in a caller-owned worker transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import os
from typing import Any, Mapping

from fastapi import APIRouter, Request, Response
from pymongo.write_concern import WriteConcern

from tools.eos.kennel.providers.electrum_payshap_completion import (
    ElectrumCompletionContractError,
    ElectrumMessageAuthenticationError,
    normalize_electrum_payshap_completion,
    sign_electrum_http_message,
    verify_electrum_http_message_signature,
)
from tools.eos.kennel.registry.electrum_payshap_completion_inbox_registry import (
    ElectrumCompletionInboxConflict,
    ElectrumPayShapCompletionInboxEvent,
    ElectrumPayShapCompletionInboxRegistry,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Electrum PayShap Settlement"])
ROUTE_PATH = "/providers/electrum/payshap/completion"
_INBOX_COLLECTION = "electrum_payshap_completion_inbox"


@dataclass(frozen=True, slots=True)
class ElectrumTransportConfiguration:
    verification_keys: Mapping[str, str | bytes]
    signing_private_key: str | bytes
    signing_key_id: str
    signing_issuer: str


@dataclass(frozen=True, slots=True)
class ElectrumCompletionRuntime:
    client: Any
    database: Any


def _transport_configuration() -> ElectrumTransportConfiguration | None:
    """Resolve onboarding key material at request time; never log or persist it."""
    raw_keys = os.getenv("WILSY_ELECTRUM_VERIFICATION_KEYS_JSON", "")
    private_key = os.getenv("WILSY_ELECTRUM_SIGNING_PRIVATE_KEY_PEM", "")
    key_id = os.getenv("WILSY_ELECTRUM_SIGNING_KEY_ID", "")
    issuer = os.getenv("WILSY_ELECTRUM_SIGNING_ISSUER", "")
    if not all(value.strip() for value in (raw_keys, private_key, key_id, issuer)):
        return None
    try:
        keys = json.loads(raw_keys)
    except json.JSONDecodeError:
        return None
    if not isinstance(keys, dict) or not keys:
        return None
    normalized_keys = {
        str(k): str(v).replace("\\n", "\n")
        for k, v in keys.items()
        if isinstance(k, str) and isinstance(v, str) and v.strip()
    }
    if len(normalized_keys) != len(keys):
        return None
    return ElectrumTransportConfiguration(
        verification_keys=normalized_keys,
        signing_private_key=private_key.replace("\\n", "\n"),
        signing_key_id=key_id.strip(),
        signing_issuer=issuer.strip(),
    )


def _runtime() -> ElectrumCompletionRuntime | None:
    from tools.eos.kernel.db import get_client, get_database

    client = get_client()
    database = get_database()
    if client is None or database is None:
        return None
    return ElectrumCompletionRuntime(client=client, database=database)


def _signed_response(
    status_code: int,
    payload: Mapping[str, Any],
    *,
    config: ElectrumTransportConfiguration,
    now: datetime,
) -> Response:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    token = sign_electrum_http_message(
        body,
        private_key=config.signing_private_key,
        key_id=config.signing_key_id,
        issuer=config.signing_issuer,
        issued_at=int(now.timestamp()),
    )
    return Response(
        content=body,
        status_code=status_code,
        media_type="application/json",
        headers={
            "x-jwt-signature": token,
            "cache-control": "no-store",
        },
    )


def _error(status_code: int, code: str, config: ElectrumTransportConfiguration, now: datetime) -> Response:
    return _signed_response(status_code, {"accepted": False, "code": code}, config=config, now=now)


def create_electrum_completion_inbox_event(
    payload: Mapping[str, Any],
    *,
    verified_message,
    received_at: datetime,
) -> ElectrumPayShapCompletionInboxEvent:
    completion = normalize_electrum_payshap_completion(
        payload,
        verified_message=verified_message,
    )
    return ElectrumPayShapCompletionInboxEvent(
        provider_name="ELECTRUM",
        message_id=completion.message_id,
        message_created_at=completion.message_created_at,
        uetr=completion.uetr,
        transaction_reference=completion.transaction_reference,
        outcome=completion.outcome,
        payment_scheme=completion.payment_scheme,
        payment_method=completion.payment_method,
        amount_minor=completion.amount_minor,
        currency=completion.currency,
        settlement_date=completion.settlement_date.isoformat() if completion.settlement_date else None,
        creditor_account_fingerprint=completion.creditor_account_fingerprint,
        content_digest=verified_message.content_digest,
        signature_key_id=verified_message.key_id,
        received_at=received_at,
    )


@router.post(ROUTE_PATH)
async def receive_electrum_payshap_completion(request: Request) -> Response:
    """Verify, durably inbox, and signed-ack one Electrum completion in under 1s."""
    now = datetime.now(timezone.utc)
    config = _transport_configuration()
    if config is None:
        # Not a live integration until the onboarding keys/issuer are provisioned.
        return Response(status_code=503, content=b"ELECTRUM_TRANSPORT_NOT_CONFIGURED")
    if getattr(request.app.state, "electrum_completion_indexes_ready", False) is not True:
        return _error(503, "ELECTRUM_INDEXES_NOT_READY", config, now)
    if getattr(request.app.state, "electrum_settlement_worker_enabled", False) is not True:
        return _error(503, "ELECTRUM_SETTLEMENT_WORKER_NOT_READY", config, now)
    runtime = _runtime()
    if runtime is None:
        return _error(503, "ELECTRUM_RUNTIME_UNAVAILABLE", config, now)

    raw_body = await request.body()
    signature = request.headers.get("x-jwt-signature", "")
    try:
        verified = verify_electrum_http_message_signature(
            raw_body,
            signature,
            verification_keys=config.verification_keys,
            now=now,
        )
    except ElectrumMessageAuthenticationError:
        return _error(401, "ELECTRUM_MESSAGE_AUTHENTICATION_FAILED", config, now)

    try:
        payload = json.loads(raw_body)
        if not isinstance(payload, dict):
            raise ElectrumCompletionContractError("ELECTRUM_PAYLOAD_OBJECT_REQUIRED")
        event = create_electrum_completion_inbox_event(
            payload,
            verified_message=verified,
            received_at=now,
        )
    except (json.JSONDecodeError, ElectrumCompletionContractError, TypeError, ValueError):
        return _error(422, "ELECTRUM_COMPLETION_PAYLOAD_INVALID", config, now)

    try:
        collection = runtime.database.get_collection(_INBOX_COLLECTION).with_options(
            write_concern=WriteConcern(w="majority", j=True)
        )
        _, replayed = ElectrumPayShapCompletionInboxRegistry.create(event, collection)
    except ElectrumCompletionInboxConflict:
        return _error(409, "ELECTRUM_COMPLETION_REPLAY_CONFLICT", config, now)
    except Exception:
        logger.exception("Electrum completion durable inbox write failed")
        return _error(503, "ELECTRUM_COMPLETION_INBOX_UNAVAILABLE", config, now)

    return _signed_response(
        202,
        {
            "accepted": True,
            "provider": "ELECTRUM",
            "payment_scheme": "ZA_RPP",
            "message_id": event.message_id,
            "outcome": event.outcome,
            "settlement_eligible": event.outcome == "APPROVED",
            "replayed": replayed,
            "processing_status": "PENDING",
        },
        config=config,
        now=now,
    )


__all__ = [
    "ROUTE_PATH",
    "ElectrumTransportConfiguration",
    "ElectrumCompletionRuntime",
    "create_electrum_completion_inbox_event",
    "receive_electrum_payshap_completion",
    "router",
]
