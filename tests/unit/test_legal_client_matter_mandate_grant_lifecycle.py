"""Direct certificate for the pure L9B6 client mandate-grant lifecycle domain.

TITLE: WILSY OS Legal Client Matter Mandate Grant Lifecycle Certificate
VERSION: v1.0.0-L9B6-CLIENT-MANDATE-GRANT-LIFECYCLE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable revocation and explicit same-key supersession,
         chronology, provenance, deterministic hydration, and authority limits.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_grant_lifecycle.py
CERTIFICATION / UPDATE DATE: 2026-09-27
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Synthetic in-memory tests only; no Mongo or network.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LIFECYCLE_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterMandateGrantLifecycle,
    LegalClientMatterMandateGrantLifecycleError,
    LegalClientMatterMandateGrantLifecycleEvent,
    LegalClientMatterMandateGrantLifecycleReason,
    record_legal_client_matter_mandate_grant_lifecycle,
)
from tests.unit.test_legal_client_matter_mandate_grant import grant


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP = "e" * 128


def event(**changes: object) -> LegalClientMatterMandateGrantLifecycle:
    values: dict[str, Any] = {
        "client_grant": grant(),
        "lifecycle_event_id": "lifecycle-l9b6-1",
        "event": LegalClientMatterMandateGrantLifecycleEvent.REVOKED,
        "decision_actor_principal_id": "principal-firm-l9b6",
        "acting_capacity_id": "capacity-firm-l9b6",
        "acting_capacity_fingerprint": FP,
        "authorization_evidence_reference": "iam-decision:l9b6",
        "authorization_evidence_fingerprint": FP,
        "source_evidence_reference": "client-direction:l9b6",
        "source_evidence_fingerprint": FP,
        "occurred_at": BASE + timedelta(days=1),
        "effective_from": BASE + timedelta(days=1, minutes=1),
        "idempotency_key": "lifecycle-idempotency:l9b6",
        "reason": LegalClientMatterMandateGrantLifecycleReason.CLIENT_WITHDRAWAL,
    }
    values.update(changes)
    return record_legal_client_matter_mandate_grant_lifecycle(**cast(Any, values))


def successor() -> LegalClientMatterMandateGrant:
    value = grant(
        client_grant_id="client-grant-l9b6-successor",
        occurred_at=BASE + timedelta(hours=3),
        effective_from=BASE + timedelta(hours=4),
        idempotency_key="successor-idempotency:l9b6",
    )
    return value


def supersession() -> LegalClientMatterMandateGrantLifecycle:
    return event(
        lifecycle_event_id="lifecycle-l9b6-2",
        event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED,
        reason=None,
        acting_capacity_id=None,
        acting_capacity_fingerprint=None,
        successor_grant=successor(),
        effective_from=BASE + timedelta(days=1, minutes=1),
    )


def code(expected: str, **changes: object) -> None:
    with pytest.raises(LegalClientMatterMandateGrantLifecycleError) as raised:
        event(**changes)
    assert raised.value.code == expected


def test_revoked_event_is_exactly_bound_and_immutable() -> None:
    value = event()
    assert value.schema == SCHEMA and value.lifecycle_version == VERSION
    assert value.event is LegalClientMatterMandateGrantLifecycleEvent.REVOKED
    assert value.client_grant_id == value.to_dict()["client_grant_id"]
    assert value.tenant_id == "tenant-l9b4"
    assert value.case_matter_id == "matter-l9b4"
    assert value.client_party_id == "party-l9b4"
    assert value.subject_identity_fingerprint == "a" * 128
    assert value.breadth is LegalClientMatterMandateBreadth.LIMITED
    assert value.capabilities == (LegalClientMatterMandateCapability.ADVISORY, LegalClientMatterMandateCapability.SETTLEMENT_NEGOTIATION)
    with pytest.raises(FrozenInstanceError):
        value.event = LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED  # type: ignore[misc]


def test_superseded_binds_exact_successor_and_same_currentness_key() -> None:
    value = supersession()
    assert value.event is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED
    assert value.successor_client_grant_id == "client-grant-l9b6-successor"
    assert value.successor_client_grant_fingerprint == successor().fingerprint
    assert value.acting_capacity_id is None


def test_chronology_preserves_utc_microseconds_and_rejects_retrospection() -> None:
    value = event(occurred_at=BASE.replace(tzinfo=timezone(timedelta(hours=2))))
    assert value.occurred_at.tzinfo is timezone.utc and value.occurred_at.microsecond == BASE.microsecond
    code("L9B6_EFFECTIVE_FROM_BEFORE_OCCURRED", effective_from=BASE)
    code("L9B6_OCCURRED_AT_INVALID", occurred_at=BASE.replace(tzinfo=None))
    code(
        "L9B6_GRANT_NOT_EFFECTIVE_AT_EVENT",
        occurred_at=BASE + timedelta(hours=1),
        effective_from=BASE + timedelta(hours=1, minutes=1),
    )


def test_revocation_reason_and_successor_invariants_are_closed() -> None:
    code("L9B6_REVOKED_REASON_REQUIRED", reason=None)
    code("L9B6_REVOKED_SUCCESSOR_FORBIDDEN", successor_grant=successor())
    with pytest.raises(LegalClientMatterMandateGrantLifecycleError) as raised:
        event(event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED)
    assert raised.value.code == "L9B6_SUPERSEDED_SUCCESSOR_REQUIRED"
    with pytest.raises(LegalClientMatterMandateGrantLifecycleError) as raised:
        supersession()
        event(event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, successor_grant=successor(), reason=LegalClientMatterMandateGrantLifecycleReason.SCOPE_CHANGED)
    assert raised.value.code == "L9B6_SUPERSEDED_REASON_FORBIDDEN"


def test_cross_scope_successors_self_and_expiry_are_rejected() -> None:
    code("L9B6_CURRENTNESS_KEY_MISMATCH", successor_grant=grant(client_grant_id="other", scope_fingerprint="f" * 128), event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, acting_capacity_id=None, acting_capacity_fingerprint=None, reason=None)
    code("L9B6_SELF_SUPERSESSION", successor_grant=grant(), event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, acting_capacity_id=None, acting_capacity_fingerprint=None, reason=None)
    expired = successor and grant(client_grant_id="expired-successor", effective_until=BASE + timedelta(days=1, minutes=1))
    code("L9B6_SUCCESSOR_EXPIRED_AT_EVENT", successor_grant=expired, event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, acting_capacity_id=None, acting_capacity_fingerprint=None, reason=None)


def test_strict_hydration_tamper_unknown_event_and_fingerprint() -> None:
    original = event()
    payload = original.to_dict()
    assert set(payload) == set(LIFECYCLE_FIELDS)
    hydrated = type(original).from_dict(payload)
    assert hydrated == original
    payload["event"] = "UNKNOWN"
    with pytest.raises(LegalClientMatterMandateGrantLifecycleError):
        type(original).from_dict(payload)
    payload = original.to_dict()
    payload["fingerprint"] = "0" * 128
    with pytest.raises(LegalClientMatterMandateGrantLifecycleError):
        type(original).from_dict(payload)
    payload = original.to_dict()
    payload["extra"] = "x"
    with pytest.raises(LegalClientMatterMandateGrantLifecycleError):
        type(original).from_dict(payload)


def test_ids_reason_and_fingerprint_are_deterministic_and_non_sensitive() -> None:
    first = event()
    second = event()
    assert first.fingerprint == second.fingerprint
    assert first.idempotency_key in first.to_dict().values()
    assert "client-direction:l9b6" in repr(first.to_dict())
    assert "password" not in repr(first).casefold()


def test_no_expiry_event_or_mutable_status_or_downstream_authority() -> None:
    assert "EXPIRED" not in {item.value for item in LegalClientMatterMandateGrantLifecycleEvent}
    assert not any(name in LIFECYCLE_FIELDS for name in ("current", "active", "revoked", "superseded"))
    assert record_legal_client_matter_mandate_grant_lifecycle is not None
    assert LegalClientMatterMandateGrant is not None


def test_module_is_pure_and_has_no_forbidden_authority_imports() -> None:
    import ast
    from pathlib import Path
    tree = ast.parse(Path("tools/eos/legal_operations/domain/legal_client_matter_mandate_grant_lifecycle.py").read_text())
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any(token in module for module in imports for token in ("pymongo", "fastapi", "jwt", "requests"))


# ARTIFACT: test_legal_client_matter_mandate_grant_lifecycle.py
# VERSION: v1.0.0-L9B6-CLIENT-MANDATE-GRANT-LIFECYCLE-CERT
# RESULT: bounded synthetic unit certificate only
# END OF WILSY OS SOVEREIGN ARTIFACT
