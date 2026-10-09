"""Direct certificate for the L9A4-P2C1 client-acceptance context domain.

TITLE: WILSY OS Legal Client Acceptance Context Certificate
VERSION: v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify one immutable server-composed client review context with
         exact matter-party-capacity-instrument-lifecycle-approval binding,
         bounded chronology, strict hydration and deterministic integrity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_context.py
COLLABORATION / OWNERSHIP: Synthetic in-memory canonical predecessor domains
                            only. No registry, composer, IAM, Mongo, HTTP,
                            browser, content delivery or acceptance mutation.
CERTIFICATION / UPDATE DATE: 2026-09-26.
CHANGELOG: v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT-CERT proves valid
           construction, immutable exact bindings, chronology, replay identity,
           deterministic fingerprinting, strict hydration, adversarial scope
           rejection and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no credentials, tokens, raw body, email or client
                             PII are required or emitted.
TENANT BOUNDARY: Every fixture is one exact tenant and matter; cross-scope
                 substitutions must reject.
AUTHORITY BOUNDARY: Certificate evidence for pure context semantics only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Pure deterministic in-memory tests; no database or I/O.
FAIL-CLOSED DECLARATION: Malformed, stale, ambiguous, terminal, rejected,
                         future-effective and tampered evidence rejects.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    CONTEXT_FIELDS,
    VERSION,
    LegalClientAcceptanceContext,
    LegalClientAcceptanceContextError,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
    record_legal_client_matter_acceptance_instrument_approval,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
    record_legal_client_matter_acceptance_instrument_lifecycle,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


UTC = timezone.utc
BASE = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
TENANT = "tenant-l9a4-p2c1"
OTHER_TENANT = "tenant-l9a4-p2c1-other"
ACTOR = "principal-client-l9a4-p2c1"
OTHER_ACTOR = "principal-client-l9a4-p2c1-other"
MATTER_FP = "a" * 128
SUBJECT_FP = "b" * 128
CAPACITY_SOURCE_FP = "c" * 128
LIFECYCLE_EVIDENCE_FP = "d" * 128
AUTHORIZATION_FP = "e" * 128
APPROVAL_EVIDENCE_FP = "f" * 128
ISSUER_EVIDENCE_FP = "0" * 128


def matter(*, tenant_id: str = TENANT, suffix: str = "001") -> CaseMatter:
    """Return one synthetic canonical OPEN CaseMatter."""
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=f"matter-l9a4-p2c1-{suffix}",
        matter_reference=f"CASE-L9A4-P2C1-{suffix}",
        opened_at=BASE,
        evidence_reference=f"matter-registration:l9a4-p2c1-{suffix}",
    )


def party(*, source_matter: CaseMatter | None = None, suffix: str = "001"):
    """Return one exact represented matter party."""
    source = source_matter or matter(suffix=suffix)
    return register_legal_matter_party(
        matter=source,
        party_id=f"party-l9a4-p2c1-{suffix}",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference=f"organization:client-l9a4-p2c1-{suffix}",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic review subject",
        registered_at=BASE,
        source_evidence_reference=f"party-registration:l9a4-p2c1-{suffix}",
        source_evidence_fingerprint=CAPACITY_SOURCE_FP,
    )


def capacity(*, source_matter: CaseMatter | None = None, source_party: Any = None, **changes: object):
    """Return one exact capacity valid during the issuance instant."""
    source = source_matter or matter()
    subject = source_party or party(source_matter=source)
    values: dict[str, object] = {
        "case_matter": source,
        "party": subject,
        "capacity_id": "capacity-l9a4-p2c1-001",
        "principal_id": ACTOR,
        "capacity_type": LegalClientActingCapacityType.AUTHORIZED_AGENT,
        "effective_from": BASE + timedelta(minutes=1),
        "effective_until": BASE + timedelta(days=7),
        "source_evidence_reference": "capacity-source:l9a4-p2c1-001",
        "source_evidence_fingerprint": CAPACITY_SOURCE_FP,
    }
    values.update(changes)
    return record_legal_client_acting_capacity(**cast(Any, values))


def instrument(*, source_matter: CaseMatter | None = None, **changes: object):
    """Return one exact client-reviewable instrument."""
    source = source_matter or matter()
    values: dict[str, object] = {
        "case_matter": source,
        "instrument_id": "instrument-l9a4-p2c1-001",
        "version": "1.0.0",
        "instrument_kind": "CLIENT_REVIEW",
        "title": "Synthetic matter review instrument",
        "review_scope": "Review the exact bounded matter material.",
        "content_reference": "artifact:l9a4-p2c1-001/instrument/v1",
        "content_fingerprint": MATTER_FP,
        "created_at": BASE + timedelta(minutes=1),
        "effective_from": BASE + timedelta(minutes=2),
        "approval_evidence_reference": "authoring-evidence:l9a4-p2c1-001",
        "approval_evidence_fingerprint": APPROVAL_EVIDENCE_FP,
    }
    values.update(changes)
    return record_legal_client_matter_acceptance_instrument(**cast(Any, values))


def lifecycle(*, source_matter: CaseMatter | None = None, source_instrument: Any = None, **changes: object):
    """Return one ACTIVE lifecycle fact for the exact instrument."""
    source = source_matter or matter()
    source_value = source_instrument or instrument(source_matter=source)
    values: dict[str, object] = {
        "tenant_id": source.tenant_id,
        "case_matter_id": source.case_matter_id,
        "matter_fingerprint": source.fingerprint,
        "instrument_id": source_value.instrument_id,
        "version": source_value.version,
        "instrument_fingerprint": source_value.fingerprint,
        "status": LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
        "occurred_at": BASE + timedelta(minutes=3),
        "lifecycle_evidence_reference": "lifecycle-evidence:l9a4-p2c1-001",
        "lifecycle_evidence_fingerprint": LIFECYCLE_EVIDENCE_FP,
    }
    values.update(changes)
    return record_legal_client_matter_acceptance_instrument_lifecycle(**cast(Any, values))


def approval(*, source_matter: CaseMatter | None = None, source_instrument: Any = None, **changes: object):
    """Return one current APPROVED firm decision."""
    source = source_matter or matter()
    source_value = source_instrument or instrument(source_matter=source)
    values: dict[str, object] = {
        "case_matter": source,
        "instrument": source_value,
        "approval_id": "approval-l9a4-p2c1-001",
        "decision": LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED,
        "approver_principal_id": "principal-firm-l9a4-p2c1",
        "approver_capacity_reference": "capacity:firm-l9a4-p2c1-001",
        "authorization_evidence_reference": "authorization:firm-approval-l9a4-p2c1-001",
        "authorization_evidence_fingerprint": AUTHORIZATION_FP,
        "approval_evidence_reference": "approval-evidence:l9a4-p2c1-001",
        "approval_evidence_fingerprint": APPROVAL_EVIDENCE_FP,
        "occurred_at": BASE + timedelta(minutes=4),
        "effective_from": BASE + timedelta(minutes=4),
        "idempotency_key": "idempotency:approval-l9a4-p2c1-001",
    }
    values.update(changes)
    return record_legal_client_matter_acceptance_instrument_approval(**cast(Any, values))


def context(**changes: object) -> LegalClientAcceptanceContext:
    """Build one valid factory-derived context, applying source overrides."""
    source_matter = cast(CaseMatter, changes.pop("case_matter", matter()))
    source_party = changes.pop("party", None)
    if source_party is None:
        source_party = party(source_matter=source_matter)
    source_capacity = changes.pop("acting_capacity", None)
    if source_capacity is None:
        source_capacity = capacity(source_matter=source_matter, source_party=source_party)
    source_instrument = changes.pop("instrument", None)
    if source_instrument is None:
        source_instrument = instrument(source_matter=source_matter)
    source_lifecycle = changes.pop("lifecycle", None)
    if source_lifecycle is None:
        source_lifecycle = lifecycle(source_matter=source_matter, source_instrument=source_instrument)
    source_approval = changes.pop("approval", None)
    if source_approval is None:
        source_approval = approval(source_matter=source_matter, source_instrument=source_instrument)
    values: dict[str, object] = {
        "acceptance_context_id": "ctx-l9a4-p2c1-opaque-001",
        "actor_principal_id": ACTOR,
        "case_matter": source_matter,
        "party": source_party,
        "acting_capacity": source_capacity,
        "instrument": source_instrument,
        "lifecycle": source_lifecycle,
        "approval": source_approval,
        "issued_at": BASE + timedelta(minutes=5, microseconds=123),
        "expires_at": BASE + timedelta(hours=1),
        "replay_key": "replay:l9a4-p2c1-001",
        "issuer_evidence_reference": "issuer-evidence:l9a4-p2c1-001",
        "issuer_evidence_fingerprint": ISSUER_EVIDENCE_FP,
    }
    values.update(changes)
    return LegalClientAcceptanceContext.from_canonical(**cast(Any, values))


def test_valid_context_binds_every_canonical_source_exactly() -> None:
    value = context()
    source_matter = matter()
    source_party = party(source_matter=source_matter)
    source_capacity = capacity(source_matter=source_matter, source_party=source_party)
    source_instrument = instrument(source_matter=source_matter)
    source_lifecycle = lifecycle(source_matter=source_matter, source_instrument=source_instrument)
    source_approval = approval(source_matter=source_matter, source_instrument=source_instrument)
    assert value.tenant_id == source_matter.tenant_id
    assert value.case_matter_id == source_matter.case_matter_id
    assert value.matter_fingerprint == source_matter.fingerprint
    assert value.party_id == source_party.party_id
    assert value.subject_reference == source_party.subject_reference
    assert value.subject_identity_fingerprint == source_party.subject_identity_fingerprint
    assert value.capacity_id == source_capacity.capacity_id
    assert value.capacity_fingerprint == source_capacity.fingerprint
    assert value.capacity_type is source_capacity.capacity_type
    assert value.instrument_id == source_instrument.instrument_id
    assert value.instrument_version == source_instrument.version
    assert value.instrument_fingerprint == source_instrument.fingerprint
    assert value.content_fingerprint == source_instrument.content_fingerprint
    assert value.lifecycle_status is source_lifecycle.status
    assert value.lifecycle_fingerprint == source_lifecycle.fingerprint
    assert value.approval_id == source_approval.approval_id
    assert value.approval_decision is LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED
    assert value.approval_fingerprint == source_approval.fingerprint
    assert value.acceptance_scope == source_instrument.review_scope
    assert value.content_reference == source_instrument.content_reference


def test_context_is_frozen_and_context_id_is_opaque() -> None:
    value = context()
    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "tenant-other"  # type: ignore[misc]
    assert TENANT not in value.acceptance_context_id
    assert value.case_matter_id not in value.acceptance_context_id
    assert value.actor_principal_id not in value.acceptance_context_id


def test_utc_chronology_preserves_microseconds_and_expiry_order() -> None:
    value = context(
        issued_at="2026-09-26T14:05:00.123456+02:00",
        expires_at="2026-09-26T15:05:00.123456+02:00",
    )
    assert value.issued_at == datetime(2026, 9, 26, 12, 5, 0, 123456, tzinfo=UTC)
    assert value.expires_at.microsecond == 123456
    assert value.to_dict()["issued_at"] == "2026-09-26T12:05:00.123456Z"
    with pytest.raises(LegalClientAcceptanceContextError):
        context(expires_at=BASE + timedelta(minutes=5))
    with pytest.raises(LegalClientAcceptanceContextError):
        context(issued_at=BASE.replace(tzinfo=None))


def test_deterministic_fingerprint_and_semantic_mutations() -> None:
    first = context()
    second = context()
    assert first.fingerprint == second.fingerprint
    assert replace(first, review_scope="A different bounded review scope.", fingerprint="").fingerprint != first.fingerprint
    assert replace(first, replay_key="replay:l9a4-p2c1-002", fingerprint="").fingerprint != first.fingerprint
    assert replace(first, expires_at=first.expires_at + timedelta(seconds=1), fingerprint="").fingerprint != first.fingerprint


def test_exact_hydration_and_schema_fingerprint_tampering_reject() -> None:
    value = context()
    assert LegalClientAcceptanceContext.from_dict(value.to_dict()) == value
    payload = value.to_dict()
    payload["review_scope"] = "tampered"
    with pytest.raises(LegalClientAcceptanceContextError):
        LegalClientAcceptanceContext.from_dict(payload)
    payload = value.to_dict()
    payload["unexpected"] = "field"
    with pytest.raises(LegalClientAcceptanceContextError):
        LegalClientAcceptanceContext.from_dict(payload)
    payload = value.to_dict()
    payload.pop("approval_id")
    with pytest.raises(LegalClientAcceptanceContextError):
        LegalClientAcceptanceContext.from_dict(payload)


def test_open_matter_and_exact_party_capacity_actor_correlation_are_required() -> None:
    closed = matter().transition_to(
        type(matter().state).CLOSED,
        evidence_reference="matter-close:l9a4-p2c1",
        occurred_at=BASE + timedelta(hours=1),
    )
    with pytest.raises(LegalClientAcceptanceContextError, match="L9A4_P2C1_OPEN_CASE_MATTER_REQUIRED"):
        context(
            case_matter=closed,
            party=party(),
            acting_capacity=capacity(),
            instrument=instrument(),
            lifecycle=lifecycle(),
            approval=approval(),
        )
    wrong_party = party(source_matter=matter(suffix="002"), suffix="002")
    with pytest.raises(LegalClientAcceptanceContextError):
        context(party=wrong_party, acting_capacity=capacity())
    with pytest.raises(LegalClientAcceptanceContextError):
        context(actor_principal_id=OTHER_ACTOR)
    mismatched_capacity = capacity(principal_id=OTHER_ACTOR)
    with pytest.raises(LegalClientAcceptanceContextError):
        context(acting_capacity=mismatched_capacity)


def test_capacity_validity_at_issuance_is_fail_closed() -> None:
    expired = capacity(effective_until=BASE + timedelta(minutes=4))
    future = capacity(effective_from=BASE + timedelta(hours=1))
    with pytest.raises(LegalClientAcceptanceContextError):
        context(acting_capacity=expired)
    with pytest.raises(LegalClientAcceptanceContextError):
        context(acting_capacity=future)


def test_instrument_matter_effective_time_and_content_binding_are_exact() -> None:
    other_matter = matter(suffix="002")
    wrong_matter = instrument(source_matter=other_matter)
    wrong_lifecycle = lifecycle(source_matter=other_matter, source_instrument=wrong_matter)
    wrong_approval = approval(source_matter=other_matter, source_instrument=wrong_matter)
    with pytest.raises(LegalClientAcceptanceContextError):
        context(instrument=wrong_matter, lifecycle=wrong_lifecycle, approval=wrong_approval)
    future = instrument(effective_from=BASE + timedelta(hours=1))
    with pytest.raises(LegalClientAcceptanceContextError):
        context(instrument=future)
    changed = instrument(content_fingerprint="1" * 128)
    changed_lifecycle = lifecycle(source_instrument=changed)
    old_approval = approval(source_instrument=instrument())
    with pytest.raises(LegalClientAcceptanceContextError):
        context(instrument=changed, lifecycle=changed_lifecycle, approval=old_approval)


@pytest.mark.parametrize(
    "status",
    [
        LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED,
        LegalClientMatterAcceptanceInstrumentLifecycleStatus.RETIRED,
        LegalClientMatterAcceptanceInstrumentLifecycleStatus.WITHDRAWN,
    ],
)
def test_non_active_lifecycle_is_rejected(status: LegalClientMatterAcceptanceInstrumentLifecycleStatus) -> None:
    source_matter = matter()
    source_instrument = instrument(source_matter=source_matter)
    changes: dict[str, object] = {
        "status": status,
        "prior_status": LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE,
    }
    if status is LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED:
        changes.update(
            superseding_version_id=f"{source_instrument.instrument_id}:2.0.0",
            superseding_instrument_fingerprint="1" * 128,
        )
    terminal = lifecycle(source_matter=source_matter, source_instrument=source_instrument, **changes)
    with pytest.raises(LegalClientAcceptanceContextError):
        context(lifecycle=terminal)


def test_only_approved_current_decision_is_accepted() -> None:
    rejected = approval(decision=LegalClientMatterAcceptanceInstrumentApprovalDecision.REJECTED)
    with pytest.raises(LegalClientAcceptanceContextError):
        context(approval=rejected)
    future = approval(effective_from=BASE + timedelta(hours=1), occurred_at=BASE + timedelta(hours=1))
    with pytest.raises(LegalClientAcceptanceContextError):
        context(approval=future)
    changed = replace(approval(), content_fingerprint="1" * 128, fingerprint="")
    with pytest.raises(LegalClientAcceptanceContextError):
        context(approval=changed)


def test_required_bindings_and_fingerprints_are_strict() -> None:
    value = context()
    invalid_values = {
        "tenant_id": "default",
        "actor_principal_id": " actor-invalid",
        "matter_fingerprint": "bad",
        "subject_identity_fingerprint": "bad",
        "capacity_fingerprint": "bad",
        "instrument_fingerprint": "bad",
        "content_fingerprint": "bad",
        "lifecycle_fingerprint": "bad",
        "approval_fingerprint": "bad",
        "issuer_evidence_fingerprint": "bad",
    }
    for field in invalid_values:
        with pytest.raises(LegalClientAcceptanceContextError):
            replacement = invalid_values[field] if isinstance(invalid_values[field], str) else "bad"
            replace(value, **{field: replacement, "fingerprint": ""})
    with pytest.raises(LegalClientAcceptanceContextError):
        context(replay_key=" replay-invalid")
    with pytest.raises(LegalClientAcceptanceContextError):
        context(issuer_evidence_reference="issuer\ninvalid")


def test_no_pii_credentials_or_forbidden_authority_is_in_domain_surface() -> None:
    fields = set(CONTEXT_FIELDS)
    assert "display_name" not in fields
    assert "email" not in fields
    assert "password" not in fields
    assert "client_acceptance" not in fields
    assert "engagement_id" not in fields
    assert "representation_id" not in fields
    assert "court_authority" not in fields
    source = Path("tools/eos/legal_operations/domain/legal_client_acceptance_context.py").read_text()
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(
        alias.name
        for node in imports
        for alias in (node.names if isinstance(node, (ast.Import, ast.ImportFrom)) else ())
    )
    assert "pymongo" not in imported
    assert "httpx" not in imported
    assert "fastapi" not in imported
    assert "legal_client_acceptance_registry" not in imported
    assert "kenn el" not in imported


def test_public_domain_is_pure_and_does_not_issue_acceptance() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_acceptance_context.py").read_text()
    assert "def persist" not in source
    assert "def issue" not in source
    assert "datetime.now" not in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "MongoClient" not in source


def test_version_schema_and_seal_are_present() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_acceptance_context.py").read_text()
    assert source.count(VERSION) >= 3
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
