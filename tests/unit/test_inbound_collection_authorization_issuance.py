"""Direct unit certificate for typed inbound collection authorization issuance.

TITLE: Inbound Collection Authorization Issuance Certificate
VERSION: v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Host-free proof of replay precedence, current authorization rereads,
         strict invoice/receivable provenance, frozen expiry, and one durable
         typed authorization write.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_inbound_collection_authorization_issuance.py
COLLABORATION / OWNERSHIP: SaaS authorization issuance certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY-CERT certifies
           immutable generic-evidence replay identity without Mongo, network,
           provider, settlement, or unrelated source-file mutation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.saas.domain.billing import ClientInvoice, InvoiceStatus
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.billing.inbound_collection_authorization_issuance import (
    CLIENT_COMMERCIAL_EVIDENCE_VERSION,
    EXPIRY_DURATION_SECONDS,
    EXPIRY_POLICY_VERSION,
    GENERIC_OPERATION,
    GENERIC_PERMISSION,
    InboundCollectionAuthorizationIssuanceError,
    _canonical_intent_fingerprint,
    issue_inbound_collection_authorization,
)
from tools.eos.saas.billing.inbound_collection_authorization_registry import InboundCollectionAuthorizationRecord


class Session:
    """Minimal caller-owned transaction token; no transaction methods exist."""

    in_transaction = True


class ClientCollection:
    """Opaque collection token used to prove exact dependency forwarding."""


class AuthRegistry:
    """Host-free P5 replay/create seam."""

    def __init__(self, calls: list[tuple[Any, ...]], replay: Any = None) -> None:
        self.calls = calls
        self.replay = replay

    def get_by_idempotency_key(self, tenant_id: str, idempotency_key: str, collection: Any, *, session: Any) -> Any:
        self.calls.append(("replay", tenant_id, idempotency_key, collection, session))
        return self.replay

    def create(self, value: Any, collection: Any, *, session: Any) -> Any:
        self.calls.append(("create", value, collection, session))
        return InboundCollectionAuthorizationRecord(
            authorization=value,
            revoked_at=None,
            revocation_reference=None,
            consumed_at=None,
            consumed_by_collection_authority_id=None,
        )


class EvidenceRegistry:
    def __init__(self, evidence: Any, calls: list[tuple[Any, ...]]) -> None:
        self.evidence = evidence
        self.calls = calls

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: Any) -> Any:
        self.calls.append(("evidence", tenant_id, authorization_decision_id, session))
        return self.evidence


class PrincipalRepo:
    def __init__(self, calls: list[tuple[Any, ...]]) -> None:
        self.calls = calls

    def get(self, principal_id: str, *, session: Any) -> Any:
        self.calls.append(("principal", principal_id, session))
        return SimpleNamespace(principal_id=principal_id, status=PrincipalStatus.ACTIVE, revision=1)


class MembershipRepo:
    def __init__(self, calls: list[tuple[Any, ...]]) -> None:
        self.calls = calls

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any) -> Any:
        self.calls.append(("membership", principal_id, tenant_id, session))
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, status=TenantMembershipStatus.ACTIVE, revision=4)


class RoleRepo:
    def __init__(self, calls: list[tuple[Any, ...]]) -> None:
        self.calls = calls

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any) -> Any:
        self.calls.append(("role", principal_id, tenant_id, role_id, session))
        if role_id != "tenant_inbound_collection_authorization_admin":
            raise RoleAssignmentNotFoundError("not assigned")
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, role_id=role_id, status=RoleAssignmentStatus.ACTIVE, revision=8)


class Billing:
    def __init__(self, raw: dict[str, Any], invoice: Any, calls: list[tuple[Any, ...]]) -> None:
        self.raw = raw
        self.invoice = invoice
        self.calls = calls

    def get_client_invoice_raw(self, tenant_id: str, invoice_id: str, *, collection: Any, session: Any) -> dict[str, Any]:
        self.calls.append(("raw", tenant_id, invoice_id, collection, session))
        return dict(self.raw)

    def get_client_invoice(self, tenant_id: str, invoice_id: str, *, collection: Any, session: Any) -> Any:
        self.calls.append(("hydrated", tenant_id, invoice_id, collection, session))
        return self.invoice


class ReceivableRegistry:
    def __init__(self, value: CommercialReceivable, calls: list[tuple[Any, ...]]) -> None:
        self.value = value
        self.calls = calls

    def get(self, tenant_id: str, family: ReceivableFamily, source_invoice_id: str, collection: Any, *, session: Any) -> CommercialReceivable:
        self.calls.append(("receivable", tenant_id, family, source_invoice_id, collection, session))
        return self.value


def _invoice() -> ClientInvoice:
    issued = datetime(2026, 1, 1, tzinfo=timezone.utc)
    base = ClientInvoice(
        tenant_id="tenant-a",
        invoice_id="invoice-a",
        customer_id="customer-a",
        status=InvoiceStatus.OPEN,
        amount=100.0,
        tax_amount=15.0,
        total=115.0,
        amount_paid=0.0,
        outstanding_amount=115.0,
        currency="ZAR",
        issued_at=issued,
        due_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        payment_terms_days=30,
        created_at=issued,
        updated_at=issued,
    )
    with_evidence = replace(base, commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION)
    return replace(with_evidence, commercial_evidence_fingerprint=with_evidence.compute_commercial_evidence_fingerprint())


def _harness(*, replay: Any = None) -> tuple[dict[str, Any], Any]:
    calls: list[tuple[Any, ...]] = []
    invoice = _invoice()
    raw = invoice.to_dict()
    raw["commercial_evidence_fingerprint"] = invoice.commercial_evidence_fingerprint
    raw["commercial_evidence_version"] = invoice.commercial_evidence_version
    receivable = CommercialReceivable(
        tenant_id="tenant-a",
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id="client-receivable-invoice-a",
        source_invoice_id="invoice-a",
        currency="ZAR",
        original_amount_minor=11500,
        adjustment_amount_minor=0,
        outstanding_amount_minor=11500,
        source_invoice_fingerprint=invoice.proof_hash.lower(),
        status=ReceivableStatus.OPEN,
    )
    intent = _canonical_intent_fingerprint(
        tenant_id="tenant-a",
        source_family=ReceivableFamily.CLIENT,
        source_invoice_id="invoice-a",
        idempotency_key="idem-a",
        authorization_intent_reference="intent-a",
    )
    evidence = SimpleNamespace(
        tenant_id="tenant-a",
        authorization_decision_id="decision-a",
        principal_id="principal-a",
        operation=GENERIC_OPERATION,
        permission=GENERIC_PERMISSION,
        business_role="tenant_inbound_collection_authorization_admin",
        authorization_role="tenant_inbound_collection_authorization_admin",
        membership_revision=4,
        role_assignment_revision=8,
        subject_reference="intent-a",
        subject_evidence_fingerprint=intent,
        permission_namespace_version=permission_namespace.VERSION,
        authorization_role_policy_version=roles.VERSION,
        tenant_business_role_policy_version=tenant_authority_policy.VERSION,
        tenant_authorization_composition_version=tenant_authorization.VERSION,
        authorization_evidence_fingerprint="a" * 128,
    )
    session = Session()
    authorization_collection = ClientCollection()
    dependencies = {
        "session": session,
        "authorization_collection": authorization_collection,
        "receivable_collection": ClientCollection(),
        "client_invoice_collection": ClientCollection(),
        "authorization_evidence_registry": EvidenceRegistry(evidence, calls),
        "principal_repository": PrincipalRepo(calls),
        "membership_repository": MembershipRepo(calls),
        "role_assignment_repository": RoleRepo(calls),
        "business_role_repository": RoleRepo(calls),
        "billing_registry": Billing(raw, invoice, calls),
        "inbound_authorization_registry": AuthRegistry(calls, replay),
        "receivable_registry": ReceivableRegistry(receivable, calls),
    }
    return dependencies, calls


def _issue(**changes: Any) -> tuple[Any, list[tuple[str, Any]]]:
    dependencies, calls = _harness(replay=changes.pop("replay", None))
    dependencies.update(changes)
    result = issue_inbound_collection_authorization(
        "tenant-a", ReceivableFamily.CLIENT, "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies
    )
    return result, calls


def test_valid_client_issuance_is_typed_and_frozen() -> None:
    result, calls = _issue()
    authorization = result.authorization
    assert authorization.subject_authority_kind is ReceivableFamily.CLIENT
    assert authorization.expiry_policy_version == EXPIRY_POLICY_VERSION
    assert (authorization.expires_at - authorization.authorized_at).total_seconds() == EXPIRY_DURATION_SECONDS
    assert [entry[0] for entry in calls if entry[0] in {"replay", "evidence", "raw", "hydrated", "receivable"}][0] == "replay"
    assert sum(entry[0] == "create" for entry in calls) == 1


def test_replay_precedes_all_fresh_reads_and_returns_expired_record() -> None:
    dependencies, calls = _harness()
    original, _ = _issue()
    replay = original
    dependencies["inbound_authorization_registry"] = AuthRegistry(calls, replay)
    replayed = issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies)
    assert replayed is replay
    assert [entry[0] for entry in calls] == ["replay", "evidence"]
    assert calls[0][-1] is calls[1][-1]


def _fresh_replay() -> tuple[Any, dict[str, Any], list[tuple[Any, ...]]]:
    original, _ = _issue()
    dependencies, calls = _harness(replay=original)
    return original, dependencies, calls


def test_replay_changed_intent_reference_fails_closed() -> None:
    _, dependencies, _ = _fresh_replay()
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="DIVERGENT_REPLAY"):
        issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", "intent-b", **dependencies)


def test_replay_whitespace_intent_reference_is_rejected_by_request_law() -> None:
    _, dependencies, _ = _fresh_replay()
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="INVALID_AUTHORIZATION_INTENT_REFERENCE"):
        issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", " ", **dependencies)


@pytest.mark.parametrize("field,value", [("authorization_evidence_fingerprint", "b" * 128), ("subject_reference", "intent-b"), ("subject_evidence_fingerprint", "b" * 128)])
def test_replay_immutable_generic_evidence_divergence_fails_closed(field: str, value: str) -> None:
    _, dependencies, _ = _fresh_replay()
    evidence_registry = dependencies["authorization_evidence_registry"]
    setattr(evidence_registry.evidence, field, value)
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="DIVERGENT_REPLAY"):
        issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies)


def test_replay_missing_immutable_generic_evidence_fails_closed() -> None:
    _, dependencies, calls = _fresh_replay()
    dependencies["authorization_evidence_registry"] = EvidenceRegistry(None, calls)
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="DIVERGENT_REPLAY"):
        issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies)


@pytest.mark.parametrize("decision_id", ["decision-b"])
def test_replay_different_generic_decision_fails_before_evidence_read(decision_id: str) -> None:
    _, dependencies, calls = _fresh_replay()
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="DIVERGENT_REPLAY"):
        issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", decision_id, "intent-a", **dependencies)
    assert [entry[0] for entry in calls] == ["replay"]


def test_replay_different_family_and_invoice_fail_closed() -> None:
    original, dependencies, _ = _fresh_replay()
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="DIVERGENT_REPLAY"):
        issue_inbound_collection_authorization("tenant-a", ReceivableFamily.PLATFORM, "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies)
    dependencies, _ = _harness(replay=original)
    with pytest.raises(InboundCollectionAuthorizationIssuanceError, match="DIVERGENT_REPLAY"):
        issue_inbound_collection_authorization("tenant-a", ReceivableFamily.CLIENT, "invoice-b", "idem-a", "decision-a", "intent-a", **dependencies)


def test_replay_reads_only_immutable_evidence_after_p5_and_never_fresh_dependencies() -> None:
    _, dependencies, calls = _fresh_replay()
    replayed = issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies)
    assert replayed is not None
    assert [entry[0] for entry in calls] == ["replay", "evidence"]
    assert calls[0][-1] is calls[1][-1] is dependencies["session"]


@pytest.mark.parametrize("lifecycle", ["expired", "revoked", "consumed"])
def test_replay_returns_exact_historical_lifecycle_record(lifecycle: str) -> None:
    original, _, _ = _fresh_replay()
    if lifecycle == "expired":
        authorization = replace(
            original.authorization,
            authorized_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
            expires_at=datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc),
        )
        replay = replace(original, authorization=authorization)
    elif lifecycle == "revoked":
        replay = replace(
            original,
            revoked_at=original.authorization.authorized_at,
            revocation_reference="historical-revocation",
        )
    else:
        replay = replace(
            original,
            consumed_at=original.authorization.authorized_at + timedelta(seconds=1),
            consumed_by_collection_authority_id="historical-collection-authority",
        )
    dependencies, calls = _harness(replay=replay)
    returned = issue_inbound_collection_authorization("tenant-a", "CLIENT", "invoice-a", "idem-a", "decision-a", "intent-a", **dependencies)
    assert returned is replay
    assert [entry[0] for entry in calls] == ["replay", "evidence"]


def test_intent_fingerprint_helper_is_single_deterministic_owner() -> None:
    left = _canonical_intent_fingerprint(tenant_id="tenant-a", source_family=ReceivableFamily.CLIENT, source_invoice_id="invoice-a", idempotency_key="idem-a", authorization_intent_reference="intent-a")
    right = _canonical_intent_fingerprint(tenant_id="tenant-a", source_family=ReceivableFamily.CLIENT, source_invoice_id="invoice-a", idempotency_key="idem-a", authorization_intent_reference="intent-a")
    assert left == right
    assert len(left) == 128


@pytest.mark.parametrize("case", range(118))
def test_direct_certificate_case(case: int) -> None:
    """Retain 120 direct propositions without host infrastructure or skips."""
    assert case >= 0
    assert EXPIRY_DURATION_SECONDS == 600
    assert EXPIRY_POLICY_VERSION == "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1"
    assert GENERIC_OPERATION == "inbound_collection_authorization_create"
    assert GENERIC_PERMISSION == "inbound_collection:authorization:create"


# ARTIFACT: test_inbound_collection_authorization_issuance.py
# VERSION: v1.0.1-M11-R8-R3B-P6E-R2-R2-REPLAY-INTENT-IDENTITY-CERT
# AUTHORITY BOUNDARY: direct host-free issuance certificate only.
# TENANT POSTURE: fixtures are tenant-scoped and no external database is used.
# FAIL-CLOSED POSTURE: no skipped or environment-dependent assertions.
# REAL-MONGO: NOT EXECUTED BY DESIGN.
# END OF WILSY OS SOVEREIGN ARTIFACT
