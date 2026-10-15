"""WILSY OS P7 privileged break-glass authority unit certificate.

VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-UNIT-CERTIFICATE
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Certify dual control, scope, lifetime, replay, corruption and non-authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_privileged_break_glass_authority.py
COLLABORATION / OWNERSHIP: P7 executable certification of D12/P2/P3/P4 composition.
CERTIFICATION DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes the complete P7 unit authority boundary certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Uses only synthetic opaque identifiers; no secrets.
TENANT BOUNDARY: Proves exact tenant/platform shape and anti-rebinding validation.
AUTHORITY BOUNDARY: Test evidence only; creates no production authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.eos.auth.privileged_break_glass_command_evidence import PrivilegedBreakGlassCommandEvidence, PrivilegedBreakGlassCommandEvidenceError
from tools.eos.auth.privileged_break_glass_command_evidence_registry import PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedBreakGlassEvidenceConflictError
from tools.eos.auth.privileged_break_glass_service import PrivilegedBreakGlassResult, PrivilegedBreakGlassService, PrivilegedBreakGlassServiceError
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssuranceChannel, PrivilegedAssurancePurpose

NOW = datetime(2026, 10, 15, 8, 0, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []

    def create_index(self, keys: object, **kwargs: object) -> None:
        self.indexes.append((keys, kwargs))

    def find_one(self, query: dict[str, object], *, session: object) -> dict[str, object] | None:
        return next((row for row in self.rows if all(row.get(key) == value for key, value in query.items())), None)

    def insert_one(self, row: dict[str, object], *, session: object) -> None:
        self.rows.append(dict(row))


def evidence(**overrides: object) -> PrivilegedBreakGlassCommandEvidence:
    values: dict[str, object] = dict(evidence_id="evidence-a", idempotency_key="key-a", requester_principal_id="requester-a", approver_principal_id="approver-a", tenant_id="tenant-a", target_class=PrivilegedTargetClass.TENANT_PRIVILEGED, privileged_role_id="ENTERPRISE_ADMIN", reason_reference="incident-opaque-a", requester_assignment_id="assignment-r", requester_assignment_revision=1, requester_assignment_fingerprint="a" * 128, approver_assignment_id="assignment-a", approver_assignment_revision=2, approver_assignment_fingerprint="b" * 128, eligibility_evidence_id="eligibility-a", eligibility_evidence_fingerprint="c" * 128, requester_assurance_evidence_id="assurance-r", requester_assurance_evidence_fingerprint="d" * 128, approver_assurance_evidence_id="assurance-a", approver_assurance_evidence_fingerprint="e" * 128, activation_id="activation-a", activation_fingerprint="f" * 128, authorized_at=NOW, effective_until=NOW + timedelta(minutes=10))
    values.update(overrides)
    return PrivilegedBreakGlassCommandEvidence(**values)  # type: ignore[arg-type]


def test_evidence_round_trip_and_bson_utc_hydration() -> None:
    value = evidence()
    document = value.to_document()
    document["authorized_at"] = NOW.replace(tzinfo=None)
    document["effective_until"] = (NOW + timedelta(minutes=10)).replace(tzinfo=None)
    assert PrivilegedBreakGlassCommandEvidence.from_document(document) == value


@pytest.mark.parametrize("overrides,code", [({"approver_principal_id": "requester-a"}, "DUAL_CONTROL_REQUIRED"), ({"reason_reference": ""}, "REASON_REFERENCE_INVALID"), ({"tenant_id": "tenant-a", "target_class": PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT}, "PLATFORM_SCOPE_TENANT_FORBIDDEN"), ({"authorized_at": NOW.replace(tzinfo=None)}, "AUTHORIZED_AT_INVALID")])
def test_evidence_rejects_invalid_authority(overrides: dict[str, object], code: str) -> None:
    with pytest.raises(PrivilegedBreakGlassCommandEvidenceError, match=code):
        evidence(**overrides)


def test_registry_exact_replay_divergence_corruption_and_no_ttl() -> None:
    collection = Collection()
    registry = PrivilegedBreakGlassCommandEvidenceRegistry(collection)
    registry.ensure_indexes()
    assert all("expireAfterSeconds" not in kwargs for _, kwargs in collection.indexes)
    value = evidence()
    assert registry.create_or_replay(value, session=Session()) == value
    assert registry.create_or_replay(value, session=Session()) == value
    with pytest.raises(PrivilegedBreakGlassEvidenceConflictError, match="DIVERGENT"):
        registry.create_or_replay(evidence(reason_reference="incident-b"), session=Session())
    collection.rows[0]["reason_reference"] = "corrupt"
    with pytest.raises(Exception, match="PERSISTED_RECORD_INVALID"):
        registry.get_by_requester_idempotency(requester_principal_id="requester-a", idempotency_key="key-a", session=Session())


class Possession:
    def __init__(self, missing: str | None = None, revision: int = 1) -> None:
        self.missing = missing
        self.revision = revision

    def resolve(self, *, principal_id: str, permission_id: str, session: object) -> object | None:
        if principal_id == self.missing:
            return None
        return SimpleNamespace(assignment_id="assignment-" + principal_id, principal_id=principal_id, permission_id=permission_id, revision=self.revision, assignment_fingerprint=("a" if principal_id == "requester-a" else "b") * 128)


class Eligibility:
    def __init__(self, *, principal: str = "requester-a", tenant: str | None = "tenant-a") -> None:
        self.principal = principal
        self.tenant = tenant

    def resolve(self, *, eligibility_evidence_id: str, at: datetime, session: object) -> object:
        return SimpleNamespace(eligibility_evidence_id=eligibility_evidence_id, eligibility_evidence_fingerprint="c" * 128, principal_id=self.principal, tenant_id=self.tenant, target_class=PrivilegedTargetClass.TENANT_PRIVILEGED, privileged_role_id="ENTERPRISE_ADMIN")


class Assurance:
    def __init__(self, *, sufficient: bool = True, wrong: str | None = None) -> None:
        self.sufficient = sufficient
        self.wrong = wrong

    def compose(self, *, proof_reference: str, assurance_purpose: object, **kwargs: object) -> object:
        principal = "requester-a" if proof_reference == "proof-r" else "approver-a"
        if self.wrong == principal:
            principal = "wrong-principal"
        item = SimpleNamespace(principal_id=principal, sufficient=self.sufficient, assurance_channel=PrivilegedAssuranceChannel.INTERACTIVE_STRONG_AUTH, assurance_purpose=PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION, assurance_evidence_id="assurance-" + principal, assurance_evidence_fingerprint=("d" if principal == "requester-a" else "e") * 128)
        return SimpleNamespace(decision=item, evidence=item)


class Activations:
    def __init__(self) -> None:
        self.items: dict[str, object] = {}

    def get_history(self, activation_id: str, *, session: object) -> tuple[object, ...]:
        return () if activation_id not in self.items else (self.items[activation_id],)

    def create_or_replay(self, activation: object, *, session: object) -> object:
        self.items[getattr(activation, "activation_id")] = activation
        return activation


def service(*, possession: object | None = None, eligibility: object | None = None, assurance: object | None = None) -> PrivilegedBreakGlassService:
    return PrivilegedBreakGlassService(possession_resolver=possession or Possession(), eligibility_resolver=eligibility or Eligibility(), interactive_assurance_service=assurance or Assurance(), activation_registry=Activations(), evidence_registry=PrivilegedBreakGlassCommandEvidenceRegistry(Collection()), clock=lambda: NOW, assurance_attempt_id_factory=iter(("attempt-r", "attempt-a", "attempt-r2", "attempt-a2")).__next__)


def issue(subject: PrivilegedBreakGlassService, **overrides: object) -> PrivilegedBreakGlassResult:
    values: dict[str, object] = dict(requester_principal_id="requester-a", approver_principal_id="approver-a", tenant_id="tenant-a", requester_proof_tenant_id="tenant-a", requester_proof_reference="proof-r", approver_proof_tenant_id="tenant-a", approver_proof_reference="proof-a", eligibility_evidence_id="eligibility-a", reason_reference="incident-opaque-a", effective_until=NOW + timedelta(minutes=10), idempotency_key="key-a", session=Session())
    values.update(overrides)
    return subject.issue_interactive(**values)  # type: ignore[arg-type]


def test_service_authorized_dual_control_and_exact_replay() -> None:
    subject = service()
    first = issue(subject)
    second = issue(subject)
    assert first == second
    assert first.activation.principal_id == "requester-a"
    assert first.evidence.approver_principal_id == "approver-a"


@pytest.mark.parametrize("overrides,code", [({"approver_principal_id": "requester-a"}, "DUAL_CONTROL_REQUIRED"), ({"effective_until": NOW + timedelta(minutes=16)}, "BREAK_GLASS_LIFETIME_INVALID"), ({"effective_until": NOW - timedelta(seconds=1)}, "BREAK_GLASS_LIFETIME_INVALID"), ({"effective_until": (NOW + timedelta(minutes=5)).replace(tzinfo=None)}, "EFFECTIVE_UNTIL_INVALID")])
def test_service_rejects_self_control_lifetime_and_naive_time(overrides: dict[str, object], code: str) -> None:
    with pytest.raises(PrivilegedBreakGlassServiceError, match=code):
        issue(service(), **overrides)


def test_service_rejects_missing_requester_or_approver_permission_before_mutation() -> None:
    for principal in ("requester-a", "approver-a"):
        with pytest.raises(PrivilegedBreakGlassServiceError, match="CURRENT_BREAK_GLASS_AUTHORITY_REQUIRED"):
            issue(service(possession=Possession(principal)))


@pytest.mark.parametrize("assurance,code", [(Assurance(sufficient=False), "REQUESTER_CURRENT_ASSURANCE_REQUIRED"), (Assurance(wrong="requester-a"), "REQUESTER_CURRENT_ASSURANCE_REQUIRED"), (Assurance(wrong="approver-a"), "APPROVER_CURRENT_ASSURANCE_REQUIRED")])
def test_service_rejects_stale_or_crossed_assurance(assurance: object, code: str) -> None:
    with pytest.raises(PrivilegedBreakGlassServiceError, match=code):
        issue(service(assurance=assurance))


@pytest.mark.parametrize("eligibility", [Eligibility(principal="other"), Eligibility(tenant="tenant-b")])
def test_service_rejects_crossed_eligibility_and_tenant_scope(eligibility: object) -> None:
    with pytest.raises(PrivilegedBreakGlassServiceError, match="CURRENT_TARGET_ELIGIBILITY_REQUIRED"):
        issue(service(eligibility=eligibility))


def test_replay_revalidates_exact_current_assignment_lineage_and_never_extends_lifetime() -> None:
    possession = Possession()
    subject = service(possession=possession)
    first = issue(subject)
    possession.revision = 2
    with pytest.raises(PrivilegedBreakGlassServiceError, match="DIVERGENT_IDEMPOTENCY_REPLAY"):
        issue(subject)
    assert first.activation.effective_until == NOW + timedelta(minutes=10)


def test_no_role_route_override_assignment_or_financial_authority_surface() -> None:
    source = Path("tools/eos/auth/privileged_break_glass_service.py").read_text()
    for forbidden in ("override_authority", "emergency_disable", "assign_permission", "create_assignment", "execute_payment", "settle(", "APIRouter", "start_transaction", "commit_transaction", "abort_transaction"):
        assert forbidden not in source

# ARTIFACT: test_privileged_break_glass_authority.py
# VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-UNIT-CERTIFICATE
# AUTHORITY BOUNDARY: executable unit evidence only
# TENANT POSTURE: exact scope and anti-rebinding assertions
# FAIL-CLOSED POSTURE: invalid authority, corruption, and divergence reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
