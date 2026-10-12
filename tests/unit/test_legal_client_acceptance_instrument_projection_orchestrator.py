"""Direct certificate for the Legal Client actionable-instrument projection.

TITLE: Legal Client Acceptance Instrument Projection Orchestrator Certificate
VERSION: v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations certification
EPITOME: Certify exact client IAM/visibility/capacity gating, ACTIVE+APPROVED
         currentness filtering, bounded projection fields and no write authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_instrument_projection_orchestrator.py
COLLABORATION / OWNERSHIP: Synthetic registry seams only; no Mongo or HTTP.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION-CERT
           establishes the direct adversarial certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Exact tenant/principal/matter correlation is asserted.
AUTHORITY BOUNDARY: Read-only presentation composition certificate only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision as ApprovalDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus as LifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.orchestration import (
    legal_client_acceptance_instrument_projection_orchestrator as projection,
)

TENANT = "tenant-client"
PRINCIPAL = "principal-client"
MATTER = "matter-1"
NOW = datetime(2026, 10, 12, 7, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


class Session:
    """Synthetic active caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def _identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic",
        status=PrincipalStatus.ACTIVE,
    )


def _matter() -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER,
        matter_reference="CLIENT-001",
        opened_at=NOW - timedelta(days=10),
        evidence_reference="matter-source:1",
        state=CaseMatterState.OPEN,
    )


def _sources() -> dict[str, Any]:
    matter = _matter()
    party = SimpleNamespace(
        tenant_id=TENANT,
        case_matter_id=MATTER,
        matter_fingerprint=matter.fingerprint,
        party_id="party-1",
        subject_reference="client:subject-1",
        subject_identity_fingerprint=FP_A,
    )
    capacity = SimpleNamespace(
        principal_id=PRINCIPAL,
        party_id="party-1",
        subject_reference="client:subject-1",
        subject_identity_fingerprint=FP_A,
    )
    instrument = SimpleNamespace(
        instrument_id="instrument-1",
        version="1.0.0",
        instrument_kind="CLIENT_REVIEW_TERMS",
        title="Client review terms",
        review_scope="client-information-review:v1",
        effective_from=NOW - timedelta(days=1),
        fingerprint=FP_A,
        content_fingerprint=FP_B,
    )
    lifecycle = SimpleNamespace(
        status=LifecycleStatus.ACTIVE,
        instrument_fingerprint=FP_A,
    )
    approval = SimpleNamespace(
        decision=ApprovalDecision.APPROVED,
    )
    visibility = SimpleNamespace(
        tenant_id=TENANT,
        client_principal_id=PRINCIPAL,
        case_matter_id=MATTER,
    )
    return {
        "matter": matter,
        "party": party,
        "capacity": capacity,
        "instrument": instrument,
        "lifecycle": lifecycle,
        "approval": approval,
        "visibility": visibility,
    }


@pytest.fixture
def harness(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    source = _sources()
    monkeypatch.setattr(
        projection,
        "authorize_tenant_operation",
        lambda **_kwargs: TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_legal_client",
            "LEGAL_CLIENT",
        ),
    )
    monkeypatch.setattr(
        projection.visibility_registry.LegalClientMatterVisibilityRegistry,
        "resolve_current_active",
        lambda *_args, **_kwargs: source["visibility"],
    )
    monkeypatch.setattr(
        projection.matter_registry.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        lambda *_args, **_kwargs: (source["matter"],),
    )
    monkeypatch.setattr(
        projection,
        "resolve_current_lifecycle_snapshot",
        lambda *_args, **_kwargs: source["matter"],
    )
    monkeypatch.setattr(
        projection.party_registry,
        "list_matter_parties",
        lambda *_args, **_kwargs: (source["party"],),
    )
    monkeypatch.setattr(
        projection.capacity_registry,
        "list_valid_capacities_at",
        lambda *_args, **_kwargs: (source["capacity"],),
    )
    monkeypatch.setattr(
        projection.instrument_registry,
        "list_matter_instruments",
        lambda *_args, **_kwargs: (source["instrument"],),
    )
    monkeypatch.setattr(
        projection.instrument_registry,
        "get_latest_effective_version",
        lambda *_args, **_kwargs: source["instrument"],
    )
    monkeypatch.setattr(
        projection.lifecycle_registry,
        "get_current_lifecycle",
        lambda *_args, **_kwargs: source["lifecycle"],
    )
    monkeypatch.setattr(
        projection.approval_registry,
        "get_current_approval",
        lambda *_args, **_kwargs: source["approval"],
    )
    return source


def _invoke(**overrides: object) -> projection.LegalClientAcceptanceInstrumentProjection:
    values: dict[str, object] = {
        "identity": _identity(),
        "case_matter_id": MATTER,
        "matter_lifecycle_collection": object(),
        "visibility_collection": object(),
        "party_collection": object(),
        "capacity_collection": object(),
        "instrument_collection": object(),
        "instrument_lifecycle_collection": object(),
        "approval_collection": object(),
        "principal_repository": object(),
        "membership_repository": object(),
        "business_role_repository": object(),
        "role_assignment_repository": object(),
        "session": Session(),
        "clock": lambda: NOW,
    }
    values.update(overrides)
    return projection.project_legal_client_acceptance_instruments(
        **cast(dict[str, Any], values)
    )


def test_projects_only_bounded_actionable_review_metadata(harness: dict[str, Any]) -> None:
    result = _invoke()
    assert result.tenant_id == TENANT
    assert result.case_matter_id == MATTER
    assert result.visibility == projection.VISIBILITY
    assert len(result.instruments) == 1
    row = result.instruments[0]
    assert row.instrument_id == "instrument-1"
    assert row.title == "Client review terms"
    payload = result.to_dict()
    assert payload["schema"] == projection.SCHEMA
    rendered = cast(list[dict[str, object]], payload["instruments"])
    assert set(rendered[0]) == {
        "instrument_id",
        "version",
        "instrument_kind",
        "title",
        "review_scope",
        "effective_from",
        "instrument_fingerprint",
        "content_fingerprint",
    }
    assert not any(
        token in rendered[0]
        for token in (
            "approval_id",
            "approval_evidence_reference",
            "party_id",
            "capacity_id",
            "content",
            "authorization_evidence_reference",
        )
    )


@pytest.mark.parametrize("gate", ["lifecycle", "approval"])
def test_non_actionable_currentness_is_not_projected(
    harness: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    gate: str,
) -> None:
    if gate == "lifecycle":
        monkeypatch.setattr(
            projection.lifecycle_registry,
            "get_current_lifecycle",
            lambda *_args, **_kwargs: SimpleNamespace(
                status=LifecycleStatus.RETIRED,
                instrument_fingerprint=FP_A,
            ),
        )
    else:
        monkeypatch.setattr(
            projection.approval_registry,
            "get_current_approval",
            lambda *_args, **_kwargs: SimpleNamespace(
                decision=ApprovalDecision.REJECTED
            ),
        )
    assert _invoke().instruments == ()


def test_client_iam_denial_fails_closed(
    harness: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        projection,
        "authorize_tenant_operation",
        lambda **_kwargs: TenantAuthorizationDecision(
            False, TenantAuthorizationReason.PERMISSION_NOT_GRANTED
        ),
    )
    with pytest.raises(projection.LegalClientAcceptanceInstrumentProjectionError) as error:
        _invoke()
    assert error.value.code == "L9A4_P2E_LEGAL_CLIENT_AUTHORIZATION_REQUIRED"


def test_capacity_ambiguity_fails_closed(
    harness: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    capacity = harness["capacity"]
    monkeypatch.setattr(
        projection.capacity_registry,
        "list_valid_capacities_at",
        lambda *_args, **_kwargs: (capacity, capacity),
    )
    with pytest.raises(projection.LegalClientAcceptanceInstrumentProjectionError) as error:
        _invoke()
    assert error.value.code == "L9A4_P2E_PARTY_CAPACITY_AMBIGUOUS"


def test_active_transaction_is_required(harness: dict[str, Any]) -> None:
    with pytest.raises(projection.LegalClientAcceptanceInstrumentProjectionError) as error:
        _invoke(session=Session(False))
    assert error.value.code == "L9A4_P2E_ACTIVE_TRANSACTION_REQUIRED"


def test_source_has_no_write_or_downstream_authority() -> None:
    source = inspect.getsource(projection)
    assert "persist_" not in source
    assert "issue_legal_client_acceptance(" not in source
    assert "compose_legal_client_acceptance_context(" not in source
    assert "engagement" not in source.lower()
    assert "representation" not in source.lower()
    assert "court_authority" not in source.lower()
    assert "payment_execute" not in source.lower()
    assert "settlement_execute" not in source.lower()


# ARTIFACT: test_legal_client_acceptance_instrument_projection_orchestrator.py
# VERSION: v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION-CERT
# AUTHORITY BOUNDARY: direct read-only projection certificate only
# TENANT POSTURE: exact synthetic tenant/principal/matter scope
# FAIL-CLOSED POSTURE: IAM/currentness/capacity/transaction failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
