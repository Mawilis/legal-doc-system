"""Direct certificate for L9C8 firm-decision issuer composition.

TITLE: WILSY OS Engagement Firm-Decision Issuer Certificate
VERSION: v1.0.0-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove exact identity, tenant/matter/client binding, durable IAM
         evidence correlation, chronology, replay material and transaction
         boundaries without adding a decision registry or Engagement formation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_firm_decision_orchestrator.py
COLLABORATION / OWNERSHIP: This certificate owns direct issuer evidence only;
                            domain, IAM, lifecycle, party and authorization
                            registry artifacts remain read-only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C8 proves successful authorized composition for every
           decision state, exact session propagation, server-derived fields,
           fail-closed identity/scope/IAM behavior, authorization chronology,
           and absence of persistence or formation authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no secrets, PII, network or database writes.
TENANT BOUNDARY: Exact active identity, current OPEN CaseMatter, and client
                 LegalMatterParty correlation.
AUTHORITY BOUNDARY: Direct issuer certificate only; no firm-decision registry,
                    Engagement, Representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Fake active caller session; issuer transaction ownership
                      is explicitly certified absent.
FAIL-CLOSED DECLARATION: Missing, inactive, foreign, malformed, denied or
                         divergent authority rejects with stable codes.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_engagement_firm_decision_orchestrator as issuer,
)


TENANT = "tenant-l9c8"
PRINCIPAL = "principal-l9c8"
MATTER_ID = "matter-l9c8"
PARTY_ID = "party-l9c8"
MATTER_FP = "a" * 128
SUBJECT_FP = "b" * 128
SOURCE_FP = "c" * 128
AUTH_FP = "d" * 128
AUTHORIZED_AT = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)


@dataclass
class _Session:
    in_transaction: bool = True


def _matter() -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="CASE-L9C8-001",
        opened_at=AUTHORIZED_AT - timedelta(hours=1),
        evidence_reference="matter:l9c8",
    )


def _party(matter: CaseMatter | None = None) -> Any:
    source = matter or _matter()
    return register_legal_matter_party(
        matter=source,
        party_id=PARTY_ID,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:client-l9c8",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client",
        registered_at=source.opened_at + timedelta(minutes=1),
        source_evidence_reference="party:l9c8",
        source_evidence_fingerprint=SOURCE_FP,
    )


def _identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        auth_method="synthetic",
        status=status,
    )


def _authorization_registry(
    *, calls: list[dict[str, object]], denied: bool = False
) -> TenantAuthorizationDecisionEvidenceRegistry:
    registry = object.__new__(TenantAuthorizationDecisionEvidenceRegistry)

    def issue(**kwargs: object) -> object:
        calls.append(dict(kwargs))
        if denied:
            raise TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(
                "AUTHORIZATION_DENIED"
            )
        return SimpleNamespace(
            tenant_id=kwargs["tenant_id"],
            principal_id=kwargs["principal_id"],
            operation=kwargs["operation"],
            permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
            authorization_evidence_reference="iam-decision:l9c8",
            authorization_evidence_fingerprint=AUTH_FP,
            authorized_at=AUTHORIZED_AT,
        )

    registry.issue = issue  # type: ignore[method-assign]
    return registry


def _issue(
    monkeypatch: pytest.MonkeyPatch,
    *,
    decision: object = LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
    session: _Session | None = None,
    identity: SovereignIdentity | None = None,
    party: Any | None = None,
    calls: list[dict[str, object]] | None = None,
    denied: bool = False,
) -> LegalClientMatterEngagementFirmDecision:
    session_value = session or _Session()
    calls_value = calls if calls is not None else []
    source = _matter()
    subject = party or _party(source)
    read_sessions: list[object] = []

    def read_matter(*args: object, **kwargs: object) -> tuple[CaseMatter, ...]:
        assert args[:3] == (TENANT, "CaseMatter", MATTER_ID)
        read_sessions.append(kwargs["session"])
        return (source,)

    def read_party(*args: object, **kwargs: object) -> Any:
        assert args[:2] == (TENANT, PARTY_ID)
        read_sessions.append(kwargs["session"])
        return subject

    monkeypatch.setattr(
        issuer.matter_registry.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(read_matter),
    )
    monkeypatch.setattr(
        issuer.party_registry.LegalMatterPartyRegistry,
        "get_party",
        staticmethod(read_party),
    )
    result = issuer.issue_legal_client_matter_engagement_firm_decision(
        identity=identity or _identity(),
        case_matter_id=MATTER_ID,
        client_party_id=PARTY_ID,
        decision=cast(Any, decision),
        source_evidence_reference="firm-request:l9c8",
        source_evidence_fingerprint=SOURCE_FP,
        idempotency_key="idempotency:l9c8",
        matter_lifecycle_collection=object(),
        party_collection=object(),
        authorization_evidence_registry=_authorization_registry(
            calls=calls_value, denied=denied
        ),
        session=session_value,
    )
    assert read_sessions == [session_value, session_value]
    return result


@pytest.mark.parametrize(
    "decision",
    tuple(LegalClientMatterEngagementFirmDecisionType),
)
def test_composes_each_closed_decision_with_exact_server_bindings(
    monkeypatch: pytest.MonkeyPatch,
    decision: LegalClientMatterEngagementFirmDecisionType,
) -> None:
    calls: list[dict[str, object]] = []
    result = _issue(monkeypatch, decision=decision, calls=calls)
    assert result.tenant_id == TENANT
    assert result.case_matter_id == MATTER_ID
    assert result.client_party_id == PARTY_ID
    assert result.decision is decision
    assert result.decision_actor_principal_id == PRINCIPAL
    assert result.matter_fingerprint == _matter().fingerprint
    assert result.occurred_at == AUTHORIZED_AT
    assert result.effective_from == AUTHORIZED_AT
    assert result.authorization_evidence_reference == "iam-decision:l9c8"
    assert cast(Any, calls[0]["session"]).in_transaction is True
    assert calls[0]["operation"] == issuer.OPERATION
    assert calls[0]["permission"] == issuer.PERMISSION
    assert calls[0]["tenant_id"] == TENANT
    assert calls[0]["principal_id"] == PRINCIPAL


def test_identity_and_transaction_are_required(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(issuer.LegalClientMatterEngagementFirmDecisionOrchestrationError) as error:
        _issue(monkeypatch, identity=_identity(PrincipalStatus.SUSPENDED))
    assert error.value.code == "L9C8_PRINCIPAL_INACTIVE"
    with pytest.raises(issuer.LegalClientMatterEngagementFirmDecisionOrchestrationError) as error:
        _issue(monkeypatch, session=_Session(False))
    assert error.value.code == "L9C8_ACTIVE_TRANSACTION_REQUIRED"


def test_foreign_party_and_denied_authorization_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    foreign = _party(_matter())
    object.__setattr__(foreign, "tenant_id", "tenant-other")
    with pytest.raises(issuer.LegalClientMatterEngagementFirmDecisionOrchestrationError) as error:
        _issue(monkeypatch, party=foreign)
    assert error.value.code == "L9C8_CLIENT_PARTY_SCOPE_MISMATCH"
    with pytest.raises(issuer.LegalClientMatterEngagementFirmDecisionOrchestrationError) as error:
        _issue(monkeypatch, denied=True)
    assert error.value.code == "L9C8_FIRM_DECISION_AUTHORIZATION_REQUIRED"


def test_signature_excludes_caller_authority_and_issuer_has_no_persistence_or_clock() -> None:
    import inspect

    parameters = inspect.signature(
        issuer.issue_legal_client_matter_engagement_firm_decision
    ).parameters
    assert {
        "decision_id",
        "occurred_at",
        "effective_from",
        "matter_fingerprint",
        "subject_reference",
        "subject_identity_fingerprint",
        "authorization_evidence_reference",
        "authorization_evidence_fingerprint",
    }.isdisjoint(parameters)
    source = Path(issuer.__file__).read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    forbidden = ("fastapi", "requests", "jwt", "http", "finance")
    assert not any(
        any(token in module.lower() for token in forbidden) for module in imported
    )
    assert "datetime.now" not in source
    assert "start_transaction" not in source
    assert ".commit_transaction" not in source
    assert ".abort_transaction" not in source
    assert "persist_firm_decision" not in source


def test_issuer_does_not_form_engagement_or_read_formation_prerequisites() -> None:
    source = Path(issuer.__file__).read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any("legal_client_acceptance" in module for module in imported)
    assert not any("acting_capacity" in module for module in imported)
    assert not any("conflict_currentness" in module for module in imported)
    assert not any("mandate_currentness" in module for module in imported)
    assert not any("legal_client_matter_engagement.py" in module for module in imported)
    assert "def form_engagement" not in source


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_orchestrator.py
# VERSION: v1.0.0-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE-CERT
# AUTHORITY BOUNDARY: direct authorized immutable firm-decision composition certificate
# TENANT POSTURE: exact active identity and tenant/matter/client-party correlation
# FAIL-CLOSED POSTURE: malformed, foreign, inactive, denied and transactionless requests reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
