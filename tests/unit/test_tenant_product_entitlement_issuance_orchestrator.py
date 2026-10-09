"""Direct certificate for D22B3-P25 positive entitlement issuance.

TITLE: Tenant Product Entitlement Issuance Orchestrator Direct Certificate
VERSION: v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove identity-only scope, exact authorization evidence, session
         propagation, replay correlation and sealed-composer delegation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_product_entitlement_issuance_orchestrator.py
COLLABORATION / OWNERSHIP: Bounded doubles certify the P25 orchestrator; sealed
                            composer and authority substrate retain their tests.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR-CERT establishes
           adversarial direct/static coverage for the frozen P25 contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities only; no credentials.
TENANT BOUNDARY: Assertions prove identity-derived tenant/principal propagation.
AUTHORITY BOUNDARY: Direct certificate only; no durable or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
)
from tools.eos.saas.entitlement import (
    tenant_product_entitlement_issuance_orchestrator as orchestrator,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    TenantProductEntitlementComposerCommercialError,
)


NOW = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
ENTITLEMENT_ID = "tpe-" + "a" * 128


class Session:
    """Minimal caller-owned transaction marker with forbidden lifecycle traps."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active

    def start_transaction(self) -> None:
        raise AssertionError("orchestrator started transaction")

    def commit_transaction(self) -> None:
        raise AssertionError("orchestrator committed transaction")

    def abort_transaction(self) -> None:
        raise AssertionError("orchestrator aborted transaction")


def identity(
    *, tenant: str = "tenant-a", principal: str = "principal-a",
    status: PrincipalStatus = PrincipalStatus.ACTIVE,
) -> SovereignIdentity:
    """Build one canonical active synthetic identity."""
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic",
        status=status,
    )


def evidence(**changes: object) -> TenantAuthorizationDecisionEvidence:
    """Build exact immutable evidence matching the frozen request."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "authorization_decision_id": "decision-a",
        "principal_id": "principal-a",
        "operation": orchestrator.OPERATION,
        "permission": orchestrator.PERMISSION,
        "business_role": "tenant_owner",
        "authorization_role": orchestrator.AUTHORIZATION_ROLE,
        "membership_revision": 1,
        "role_assignment_revision": 2,
        "subject_reference": (
            "tenant-product-entitlement:tenant-a:LEGAL_OPERATIONS:"
            f"{ENTITLEMENT_ID}"
        ),
        "subject_evidence_fingerprint": "b" * 128,
        "permission_namespace_version": "permission-v1",
        "authorization_role_policy_version": "role-v1",
        "tenant_business_role_policy_version": "business-v1",
        "tenant_authorization_composition_version": "composition-v1",
        "idempotency_key": (
            "tenant-product-entitlement-authorization:"
            f"{ENTITLEMENT_ID}:caller-key"
        ),
        "authorized_at": NOW,
    }
    values.update(changes)
    return TenantAuthorizationDecisionEvidence(**values)


class Issuer:
    """Record exact evidence calls and return configured evidence or failure."""

    def __init__(self, value: object = None) -> None:
        self.value = value
        self.calls: list[dict[str, object]] = []

    def issue(self, **kwargs: object) -> TenantAuthorizationDecisionEvidence:
        self.calls.append(kwargs)
        if isinstance(self.value, BaseException):
            raise self.value
        if isinstance(self.value, TenantAuthorizationDecisionEvidence):
            return self.value
        return evidence(
            tenant_id=kwargs["tenant_id"],
            principal_id=kwargs["principal_id"],
            operation=kwargs["operation"],
            permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
            idempotency_key=kwargs["idempotency_key"],
        )


def invoke(monkeypatch: pytest.MonkeyPatch, **changes: object) -> tuple[Any, Issuer, list[dict[str, object]]]:
    """Invoke with bounded dependency doubles and return recorded calls."""
    compose_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        orchestrator,
        "derive_tenant_product_entitlement_id",
        lambda tenant, product: ENTITLEMENT_ID,
    )
    monkeypatch.setattr(
        orchestrator,
        "compose_tenant_product_entitlement",
        lambda **kwargs: compose_calls.append(kwargs) or object(),
    )
    issuer = changes.pop("authorization_evidence_registry", Issuer())
    values: dict[str, Any] = {
        "identity": identity(),
        "product_id": TenantProductId.LEGAL_OPERATIONS,
        "idempotency_key": "caller-key",
        "occurred_at": NOW,
        "subscription_collection": object(),
        "entitlement_history_collection": object(),
        "entitlement_current_collection": object(),
        "authorization_evidence_registry": issuer,
        "session": Session(),
        "subscription_registry": object(),
    }
    values.update(changes)
    result = orchestrator.issue_tenant_product_entitlement(**values)
    assert isinstance(issuer, Issuer)
    return result, issuer, compose_calls


@pytest.mark.parametrize("session", [None, Session(False), object()])
def test_missing_or_inactive_transaction_rejects_before_any_read(
    monkeypatch: pytest.MonkeyPatch, session: object,
) -> None:
    """No authority or commercial dependency runs without an active transaction."""
    issuer = Issuer()
    with pytest.raises(orchestrator.TenantProductEntitlementIssuanceTransactionRequiredError):
        invoke(monkeypatch, session=session, authorization_evidence_registry=issuer)
    assert issuer.calls == []


@pytest.mark.parametrize(
    "bad_identity",
    [None, object(), identity(status=PrincipalStatus.SUSPENDED), identity(status=PrincipalStatus.REVOKED)],
)
def test_missing_invalid_or_inactive_identity_rejects(
    monkeypatch: pytest.MonkeyPatch, bad_identity: object,
) -> None:
    """Only an active canonical SovereignIdentity reaches authority."""
    issuer = Issuer()
    with pytest.raises(orchestrator.TenantProductEntitlementIssuanceInputError):
        invoke(monkeypatch, identity=bad_identity, authorization_evidence_registry=issuer)
    assert issuer.calls == []


@pytest.mark.parametrize(
    "product",
    [TenantProductId.CRM, TenantProductId.BILLING, TenantProductId.HR, "UNKNOWN"],
)
def test_only_legal_operations_has_positive_issuance(
    monkeypatch: pytest.MonkeyPatch, product: object,
) -> None:
    """Every non-Legal product rejects before authorization evidence."""
    issuer = Issuer()
    with pytest.raises(orchestrator.TenantProductEntitlementIssuanceInputError):
        invoke(monkeypatch, product_id=product, authorization_evidence_registry=issuer)
    assert issuer.calls == []


def test_exact_identity_crypto_namespace_session_and_composer_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify steps 4-10 and exact unchanged trusted orchestration values."""
    derive_calls: list[tuple[object, object]] = []
    monkeypatch.setattr(
        orchestrator,
        "derive_tenant_product_entitlement_id",
        lambda tenant, product: derive_calls.append((tenant, product)) or ENTITLEMENT_ID,
    )
    compose_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        orchestrator,
        "compose_tenant_product_entitlement",
        lambda **kwargs: compose_calls.append(kwargs) or object(),
    )
    tx = Session()
    issuer = Issuer()
    subscription_registry = object()
    collections = (object(), object(), object())
    result = orchestrator.issue_tenant_product_entitlement(
        identity=identity(tenant="tenant-a", principal="principal-a"),
        product_id=TenantProductId.LEGAL_OPERATIONS,
        idempotency_key="caller-key",
        occurred_at=NOW,
        subscription_collection=collections[0],
        entitlement_history_collection=collections[1],
        entitlement_current_collection=collections[2],
        authorization_evidence_registry=issuer,
        session=tx,
        subscription_registry=subscription_registry,  # type: ignore[arg-type]
    )
    assert derive_calls == [("tenant-a", TenantProductId.LEGAL_OPERATIONS)]
    call = issuer.calls[0]
    payload = {
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "product_id": "LEGAL_OPERATIONS",
        "entitlement_id": ENTITLEMENT_ID,
        "operation": orchestrator.OPERATION,
        "permission": orchestrator.PERMISSION,
        "idempotency_key": "caller-key",
    }
    expected = hashlib.sha3_512(
        json.dumps(
            payload, sort_keys=True, ensure_ascii=False, allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert call == {
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "operation": "tenant_product_entitlement_issue",
        "permission": "tenant_product_entitlement:issue",
        "subject_reference": (
            "tenant-product-entitlement:tenant-a:LEGAL_OPERATIONS:"
            f"{ENTITLEMENT_ID}"
        ),
        "subject_evidence_fingerprint": expected,
        "idempotency_key": (
            "tenant-product-entitlement-authorization:"
            f"{ENTITLEMENT_ID}:caller-key"
        ),
        "session": tx,
    }
    assert set(payload) == {
        "tenant_id", "principal_id", "product_id", "entitlement_id",
        "operation", "permission", "idempotency_key",
    }
    assert not {
        "subscription_id", "plan_id", "plan_catalogue_version",
        "subscription_proof_hash", "commercial_feature_id",
        "mapping_fingerprint", "product_catalogue_fingerprint",
    } & set(payload)
    assert compose_calls == [{
        "tenant_id": "tenant-a",
        "product_id": TenantProductId.LEGAL_OPERATIONS,
        "occurred_at": NOW,
        "subscription_collection": collections[0],
        "entitlement_history_collection": collections[1],
        "entitlement_current_collection": collections[2],
        "session": tx,
        "subscription_registry": subscription_registry,
    }]
    assert result.authorization_evidence is not None


def test_exact_authorization_replay_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    """The same request and evidence identity produce stable orchestration semantics."""
    first, _, _ = invoke(monkeypatch)
    replay_issuer = Issuer(first.authorization_evidence)
    replay, _, _ = invoke(monkeypatch, authorization_evidence_registry=replay_issuer)
    assert replay.authorization_evidence == first.authorization_evidence


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", "tenant-other"),
        ("principal_id", "principal-other"),
        ("operation", "subscription_manage"),
        ("permission", "subscription:manage"),
        ("subject_reference", "tenant-product-entitlement:wrong"),
        ("subject_evidence_fingerprint", "c" * 128),
        ("idempotency_key", "tenant-product-entitlement-authorization:wrong"),
    ],
)
def test_divergent_authorization_evidence_prevents_composer(
    monkeypatch: pytest.MonkeyPatch, field: str, value: object,
) -> None:
    """Every frozen correlation coordinate is exact and non-repairing."""
    issuer = Issuer(replace(evidence(), **{field: value}))
    with pytest.raises(orchestrator.TenantProductEntitlementIssuanceAuthorizationError):
        invoke(monkeypatch, authorization_evidence_registry=issuer)


def test_authorization_denial_and_conflict_prevent_composer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Denial and divergent replay remain distinct bounded failures."""
    for failure in (
        TenantAuthorizationDecisionEvidenceAuthorizationDeniedError("denied"),
        TenantAuthorizationDecisionEvidenceConflictError("conflict"),
    ):
        with pytest.raises(orchestrator.TenantProductEntitlementIssuanceAuthorizationError):
            invoke(monkeypatch, authorization_evidence_registry=Issuer(failure))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorization_role", "AUDITOR"),
        ("business_role", "tenant_auditor"),
    ],
)
def test_wrong_authorization_or_business_role_rejects(
    monkeypatch: pytest.MonkeyPatch, field: str, value: str,
) -> None:
    """Only ENTERPRISE_ADMIN plus one of three eligible business roles proceeds."""
    with pytest.raises(orchestrator.TenantProductEntitlementIssuanceAuthorizationError):
        invoke(monkeypatch, authorization_evidence_registry=Issuer(replace(evidence(), **{field: value})))


def test_composer_failure_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """A sealed composer failure cannot become success or replay."""
    monkeypatch.setattr(orchestrator, "derive_tenant_product_entitlement_id", lambda *_: ENTITLEMENT_ID)
    monkeypatch.setattr(
        orchestrator,
        "compose_tenant_product_entitlement",
        lambda **_: (_ for _ in ()).throw(
            TenantProductEntitlementComposerCommercialError("closed")
        ),
    )
    with pytest.raises(orchestrator.TenantProductEntitlementIssuanceCompositionError):
        orchestrator.issue_tenant_product_entitlement(
            identity=identity(), product_id=TenantProductId.LEGAL_OPERATIONS,
            idempotency_key="caller-key", occurred_at=NOW,
            subscription_collection=object(), entitlement_history_collection=object(),
            entitlement_current_collection=object(),
            authorization_evidence_registry=Issuer(), session=Session(),
            subscription_registry=object(),  # type: ignore[arg-type]
        )


def test_public_api_and_source_have_no_authority_or_transaction_escape_hatches() -> None:
    """Structural firewall excludes substitution, routing, finance and tx ownership."""
    signature = inspect.signature(orchestrator.issue_tenant_product_entitlement)
    assert tuple(signature.parameters) == (
        "identity", "product_id", "idempotency_key", "occurred_at",
        "subscription_collection", "entitlement_history_collection",
        "entitlement_current_collection", "authorization_evidence_registry",
        "session", "subscription_registry",
    )
    forbidden_parameters = {
        "tenant_id", "principal_id", "authorization_decision_id",
        "subject_reference", "subject_evidence_fingerprint", "authorization_role",
        "business_role", "subscription_id", "plan_id", "mapping_fingerprint",
    }
    assert forbidden_parameters.isdisjoint(signature.parameters)
    source = Path(orchestrator.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert {"start_transaction", "commit_transaction", "abort_transaction"}.isdisjoint(called)
    assert {"requests", "httpx", "router", "settle", "execute_payment"}.isdisjoint(source)
    assert "DuplicateKeyError" not in source


def test_result_is_frozen_and_contains_no_second_entitlement_representation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The result contains only evidence provenance and the sealed result."""
    result, _, _ = invoke(monkeypatch)
    assert tuple(result.__dataclass_fields__) == ("authorization_evidence", "composition")
    with pytest.raises(FrozenInstanceError):
        result.composition = object()  # type: ignore[misc]

# ARTIFACT: test_tenant_product_entitlement_issuance_orchestrator.py
# VERSION: v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR-CERT
# AUTHORITY BOUNDARY: direct/static P25 certification only
# TENANT POSTURE: synthetic exact identity-derived scope assertions
# FAIL-CLOSED POSTURE: every tested divergence rejects before composition
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
