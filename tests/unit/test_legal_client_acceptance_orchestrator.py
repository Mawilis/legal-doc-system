"""Direct certificate for context-bound L9A3 ClientAcceptance issuance.

TITLE: L9A3-R1 Context-Bound ClientAcceptance Certificate
VERSION: v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove that issuance accepts only authenticated identity, opaque
         context, explicit confirmation, bounded idempotency and a caller-owned
         transaction while deriving every authority-bearing acceptance field.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_orchestrator.py
COLLABORATION / OWNERSHIP: The certificate exercises the L9A3 orchestrator;
                            P2C1/P2C2/P2C3 and P2D remain read-only authorities.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.1.0 certifies the narrowed request surface, context derivation,
           dependency revalidation seam, explicit confirmation, exact replay,
           divergent replay rejection and caller-session propagation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no secrets or PII.
TENANT BOUNDARY: Tenant/principal are taken only from SovereignIdentity.
AUTHORITY BOUNDARY: Certificate evidence only; no downstream authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_client_acceptance_registry import (
    LegalClientAcceptanceRegistryConflictError,
    LegalClientAcceptanceRegistryNotFoundError,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_acceptance_orchestrator as orchestrator,
)


TENANT = "tenant-p2e-unit"
PRINCIPAL = "principal-p2e-unit"
CONTEXT_ID = "context-p2e-unit"
MATTER_ID = "matter-p2e-unit"
PARTY_ID = "party-p2e-unit"
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class AuthorizationIssuer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def issue(self, **kwargs: object) -> Any:
        self.calls.append(dict(kwargs))
        return SimpleNamespace(
            tenant_id=kwargs["tenant_id"],
            principal_id=kwargs["principal_id"],
            operation=kwargs["operation"],
            permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
        )


class AcceptanceStore:
    def __init__(self) -> None:
        self.value: Any = None

    def get(self, *_args: object, **_kwargs: object) -> Any:
        if self.value is None:
            raise LegalClientAcceptanceRegistryNotFoundError()
        return self.value

    def persist(self, value: Any, *_args: object, **_kwargs: object) -> Any:
        if self.value is None:
            self.value = value
            return value
        if self.value.to_dict() == value.to_dict():
            return self.value
        raise LegalClientAcceptanceRegistryConflictError()


class DependencyError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic-test",
        status=status,
    )


def context(*, actor: str = PRINCIPAL, expired: bool = False) -> Any:
    return SimpleNamespace(
        acceptance_context_id=CONTEXT_ID,
        tenant_id=TENANT,
        actor_principal_id=actor,
        case_matter_id=MATTER_ID,
        matter_fingerprint=FP_A,
        party_id=PARTY_ID,
        subject_reference="client:subject-p2e",
        subject_identity_fingerprint=FP_B,
        acceptance_scope="client-information-review:v1",
        capacity_id="capacity-p2e-unit",
        capacity_fingerprint=FP_A,
        instrument_id="instrument-p2e-unit",
        instrument_version="1.0.0",
        instrument_fingerprint=FP_B,
        content_fingerprint=FP_C,
        content_reference="server://never-returned",
        replay_key="context-replay-p2e",
        fingerprint=FP_C,
        issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=9) if not expired else NOW - timedelta(seconds=1),
    )


def invoke(
    *,
    issuer: AuthorizationIssuer,
    store: AcceptanceStore,
    session: Any = None,
    confirmed: object = True,
    context_value: Any | None = None,
    revalidation_code: str | None = None,
    **overrides: Any,
) -> Any:
    session = Session() if session is None else session
    value = context_value if context_value is not None else context()
    orchestrator.context_registry.get_valid_context = (  # type: ignore[method-assign]
        lambda *args, **kwargs: None if value.expires_at <= NOW else value
    )
    if revalidation_code is None:
        orchestrator._revalidate_dependencies = lambda **kwargs: None  # type: ignore[method-assign]
    else:
        orchestrator._revalidate_dependencies = (  # type: ignore[method-assign]
            lambda **kwargs: (_ for _ in ()).throw(DependencyError(revalidation_code))
        )
    matter = CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="p2e-unit-matter",
        opened_at=NOW,
        evidence_reference="matter-source:p2e-unit",
    )
    orchestrator._matter = lambda **kwargs: matter  # type: ignore[method-assign]
    orchestrator.LegalClientAcceptanceRegistry.get_acceptance = staticmethod(store.get)  # type: ignore[reportAttributeAccessIssue]
    orchestrator.LegalClientAcceptanceRegistry.persist_acceptance = staticmethod(store.persist)
    values: dict[str, Any] = dict(
        identity=identity(),
        acceptance_context_id=CONTEXT_ID,
        confirmed=confirmed,
        idempotency_key="intent-p2e-unit",
        context_collection=object(),
        matter_lifecycle_collection=object(),
        visibility_collection=object(),
        party_collection=object(),
        capacity_collection=object(),
        instrument_collection=object(),
        instrument_lifecycle_collection=object(),
        approval_collection=object(),
        acceptance_collection=object(),
        authorization_evidence_registry=issuer,
        principal_repository=object(),
        membership_repository=object(),
        business_role_repository=object(),
        role_assignment_repository=object(),
        session=session,
        clock=lambda: NOW,
    )
    values.update(overrides)
    return orchestrator.issue_legal_client_acceptance(**values)


@pytest.fixture(autouse=True)
def restore_registry() -> Any:
    original_context = orchestrator.context_registry.get_valid_context
    original_revalidate = orchestrator._revalidate_dependencies
    original_matter = orchestrator._matter
    yield
    orchestrator.context_registry.get_valid_context = original_context
    orchestrator._revalidate_dependencies = original_revalidate
    orchestrator._matter = original_matter


def test_request_surface_is_minimal_and_old_authority_fields_are_removed() -> None:
    parameters = set(inspect.signature(orchestrator.issue_legal_client_acceptance).parameters)
    assert parameters == {
        "identity", "acceptance_context_id", "confirmed", "idempotency_key",
        "context_collection", "matter_lifecycle_collection", "visibility_collection",
        "party_collection", "capacity_collection", "instrument_collection",
        "instrument_lifecycle_collection", "approval_collection", "acceptance_collection",
        "authorization_evidence_registry", "principal_repository", "membership_repository",
        "business_role_repository", "role_assignment_repository", "session", "clock",
    }
    assert "tenant_id" not in parameters
    assert "case_matter_id" not in parameters
    assert "party_id" not in parameters
    assert "source_evidence_fingerprint" not in parameters


def test_authenticated_context_derived_issue_replay_and_session_propagation() -> None:
    issuer, store, session = AuthorizationIssuer(), AcceptanceStore(), Session()
    first = invoke(issuer=issuer, store=store, session=session)
    replay = invoke(issuer=issuer, store=store, session=session)
    assert first.to_dict() == replay.to_dict()
    assert first.tenant_id == TENANT
    assert first.actor_principal_id == PRINCIPAL
    assert first.case_matter_id == MATTER_ID
    assert first.party_id == PARTY_ID
    assert first.acceptance_scope == "client-information-review:v1"
    assert first.source_evidence_fingerprint == FP_C
    assert "server://never-returned" not in first.source_evidence_reference
    assert issuer.calls and all(call["session"] is session for call in issuer.calls)


def test_divergent_intent_context_actor_and_confirmation_fail_closed() -> None:
    issuer, store = AuthorizationIssuer(), AcceptanceStore()
    invoke(issuer=issuer, store=store)
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="REPLAY_CONFLICT"):
        invoke(issuer=issuer, store=store, idempotency_key="different-intent")
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="CONFIRMATION"):
        invoke(issuer=AuthorizationIssuer(), store=AcceptanceStore(), confirmed=False)
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="ACTOR_MISMATCH"):
        invoke(issuer=AuthorizationIssuer(), store=AcceptanceStore(), context_value=context(actor="other-principal"))


@pytest.mark.parametrize("bad", [None, "yes", 1, False])
def test_confirmation_is_strictly_true(bad: object) -> None:
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError):
        invoke(issuer=AuthorizationIssuer(), store=AcceptanceStore(), confirmed=bad)


def test_missing_or_expired_context_and_inactive_identity_fail_before_write() -> None:
    issuer, store = AuthorizationIssuer(), AcceptanceStore()
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="CONTEXT_EXPIRED"):
        invoke(issuer=issuer, store=store, context_value=context(expired=True))
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="PRINCIPAL_INACTIVE"):
        invoke(issuer=issuer, store=store, identity=identity(PrincipalStatus.SUSPENDED))
    assert store.value is None


def test_same_context_different_tenant_is_not_authoritative() -> None:
    issuer, store = AuthorizationIssuer(), AcceptanceStore()
    with pytest.raises(TypeError):
        invoke(issuer=issuer, store=store, tenant_id="caller-controlled")


@pytest.mark.parametrize(
    "field",
    [
        "tenant_id",
        "principal_id",
        "case_matter_id",
        "matter_fingerprint",
        "party_id",
        "subject_reference",
        "subject_identity_fingerprint",
        "acceptance_scope",
        "source_evidence_reference",
        "source_evidence_fingerprint",
        "accepted_at",
        "instrument_fingerprint",
    ],
)
def test_authority_bearing_caller_fields_are_not_accepted(field: str) -> None:
    with pytest.raises(TypeError):
        invoke(
            issuer=AuthorizationIssuer(),
            store=AcceptanceStore(),
            **{field: "caller-controlled"},
        )


@pytest.mark.parametrize(
    "code",
    [
        "L9A4_P2D_ACTIVE_VISIBILITY_REQUIRED",
        "L9A4_P2D_VISIBILITY_SCOPE_MISMATCH",
        "L9A4_P2D_MATTER_NOT_OPEN",
        "L9A4_P2D_MATTER_FINGERPRINT_STALE",
        "L9A4_P2D_PARTY_CAPACITY_NOT_FOUND",
        "L9A4_P2D_PARTY_CAPACITY_AMBIGUOUS",
        "L9A4_P2D_PARTY_CAPACITY_STALE",
        "L9A4_P2D_INSTRUMENT_NOT_FOUND",
        "L9A4_P2D_INSTRUMENT_STALE",
        "L9A4_P2D_INSTRUMENT_NOT_ACTIVE",
        "L9A4_P2D_LIFECYCLE_STALE",
        "L9A4_P2D_APPROVAL_REQUIRED",
        "L9A4_P2D_APPROVAL_STALE",
        "L9A4_P2D_IAM_UNAVAILABLE",
        "L9A4_P2D_LEGAL_CLIENT_AUTHORIZATION_REQUIRED",
        "L9A4_P2D_PARTY_CAPACITY_UNAVAILABLE",
        "L9A4_P2D_INSTRUMENT_UNAVAILABLE",
        "L9A4_P2D_LIFECYCLE_UNAVAILABLE",
        "L9A4_P2D_APPROVAL_UNAVAILABLE",
        "L9A4_P2D_MATTER_UNAVAILABLE",
        "L9A4_P2D_LIFECYCLE_TERMINAL",
        "L9A4_P2D_APPROVAL_REJECTED",
    ],
)
def test_every_revalidated_dependency_failure_rejects_before_acceptance_write(
    code: str,
) -> None:
    issuer, store = AuthorizationIssuer(), AcceptanceStore()
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError):
        invoke(
            issuer=issuer,
            store=store,
            revalidation_code=code,
        )
    assert store.value is None


def test_missing_transaction_and_bad_clock_fail_closed() -> None:
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="ACTIVE_TRANSACTION"):
        invoke(issuer=AuthorizationIssuer(), store=AcceptanceStore(), session=SimpleNamespace(in_transaction=False))
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError, match="SERVER_CLOCK"):
        invoke(issuer=AuthorizationIssuer(), store=AcceptanceStore(), clock=lambda: "not-a-time")


# ARTIFACT: test_legal_client_acceptance_orchestrator.py
# VERSION: v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE-CERT
# AUTHORITY BOUNDARY: direct narrowing certificate only
# TENANT POSTURE: identity-derived tenant and context-derived acceptance fields
# FAIL-CLOSED POSTURE: malformed, stale, divergent and unauthorized requests reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
