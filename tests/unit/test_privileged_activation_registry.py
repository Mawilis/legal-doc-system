"""TITLE: WILSY OS P4-R2 Privileged Activation Registry Direct Certificate.
VERSION: v1.0.0-P4-R2-DIRECT-CERTIFICATE
AUTHORITY: Direct persistence-contract certification only.
EPITOME: Proves immutable history, exact replay, isolation, currentness,
corruption rejection, transaction ownership, no TTL, and authority walls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_privileged_activation_registry.py
COLLABORATION / OWNERSHIP: P4-R1 domain and future real-Mongo R3 certificate.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P4-R2 establishes the direct registry certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / TENANT POSTURE: Synthetic secret-free exact-scope records only.
AUTHORITY BOUNDARY: Registry persistence is not activation issuance or use.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.eos.auth.privileged_activation import PrivilegedActivation
from tools.eos.auth.privileged_activation_registry import (
    ACTIVATION_REVISION_INDEX, SCOPE_OPERATION_IDEMPOTENCY_INDEX,
    SCOPE_TIMELINE_INDEX, PrivilegedActivationConflictError,
    PrivilegedActivationPersistedInvalidError, PrivilegedActivationRegistry,
    PrivilegedActivationTransactionRequiredError,
)
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose


NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []

    def create_index(self, keys: list[tuple[str, int]], **options: object) -> str:
        self.indexes.append((keys, options)); return str(options["name"])

    @staticmethod
    def match(row: dict[str, object], query: dict[str, object]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        return next((deepcopy(row) for row in self.rows if self.match(row, query)), None)

    def find(self, query: dict[str, object], *, session: object = None) -> list[dict[str, object]]:
        return [deepcopy(row) for row in self.rows if self.match(row, query)]

    def insert_one(self, row: dict[str, object], *, session: object) -> object:
        self.rows.append(deepcopy(row)); return object()


def activation(**changes: object) -> PrivilegedActivation:
    values: dict[str, object] = {
        "activation_id": "activation-a", "tenant_id": "tenant-a",
        "principal_id": "principal-a", "actor_principal_id": "principal-a",
        "privileged_role_id": "ENTERPRISE_ADMIN",
        "target_class": PrivilegedTargetClass.TENANT_PRIVILEGED,
        "eligibility_evidence_id": "eligibility-a",
        "eligibility_evidence_fingerprint": "a" * 128,
        "assurance_evidence_id": "assurance-a",
        "assurance_evidence_fingerprint": "b" * 128,
        "creation_assurance_purpose": PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION,
        "activated_at": NOW, "effective_until": NOW + timedelta(minutes=15),
        "issuance_idempotency_key": "issue-a",
    }
    values.update(changes)
    return PrivilegedActivation.issue(**values)  # type: ignore[arg-type]


def owner() -> tuple[PrivilegedActivationRegistry, Collection]:
    collection = Collection(); return PrivilegedActivationRegistry(collection), collection


def test_index_contract_has_three_indexes_and_no_ttl() -> None:
    registry, collection = owner(); registry.ensure_indexes()
    assert {options["name"] for _, options in collection.indexes} == {ACTIVATION_REVISION_INDEX, SCOPE_OPERATION_IDEMPOTENCY_INDEX, SCOPE_TIMELINE_INDEX}
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)
    assert [options["unique"] for _, options in collection.indexes] == [True, True, False]


def test_active_persist_hydrate_and_exact_replay() -> None:
    registry, collection = owner(); value = activation()
    assert registry.create_or_replay(value, session=Session()) == value
    assert registry.create_or_replay(value, session=Session()) == value
    assert len(collection.rows) == 1 and registry.get_history(value.activation_id) == (value,)


def test_divergent_replay_and_activation_identity_collision_deny() -> None:
    registry, _ = owner(); first = activation(); registry.create_or_replay(first, session=Session())
    with pytest.raises(PrivilegedActivationConflictError, match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY"):
        registry.create_or_replay(activation(activation_id="activation-b", assurance_evidence_id="assurance-b"), session=Session())
    with pytest.raises(PrivilegedActivationConflictError, match="ACTIVATION_ID_COLLISION"):
        registry.create_or_replay(activation(issuance_idempotency_key="issue-b", assurance_evidence_id="assurance-b"), session=Session())


@pytest.mark.parametrize("field,value", [("tenant_id", "tenant-b"), ("principal_id", "principal-b"), ("privileged_role_id", "SOVEREIGN_ARCHITECT")])
def test_scope_isolation(field: str, value: str) -> None:
    registry, _ = owner(); item = activation(); registry.create_or_replay(item, session=Session())
    query = {"tenant_id": "tenant-a", "principal_id": "principal-a", "privileged_role_id": "ENTERPRISE_ADMIN", "target_class": PrivilegedTargetClass.TENANT_PRIVILEGED, "at": NOW}
    query[field] = value
    assert registry.resolve_current(**query) is None  # type: ignore[arg-type]


def test_target_class_isolation() -> None:
    registry, _ = owner(); registry.create_or_replay(activation(), session=Session())
    assert registry.resolve_current(tenant_id=None, principal_id="principal-a", privileged_role_id="ENTERPRISE_ADMIN", target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT, at=NOW) is None


def test_revocation_history_exact_replay_and_currentness() -> None:
    registry, collection = owner(); first = activation(); registry.create_or_replay(first, session=Session())
    revoked = first.revoke(revoked_at=NOW + timedelta(minutes=1))
    assert registry.revoke_or_replay(revoked, revocation_idempotency_key="revoke-a", session=Session()) == revoked
    assert registry.revoke_or_replay(revoked, revocation_idempotency_key="revoke-a", session=Session()) == revoked
    assert registry.get_history(first.activation_id) == (first, revoked)
    assert registry.resolve_current(tenant_id="tenant-a", principal_id="principal-a", privileged_role_id="ENTERPRISE_ADMIN", target_class=PrivilegedTargetClass.TENANT_PRIVILEGED, at=NOW) is None
    assert len(collection.rows) == 2


def test_expiry_boundary_denies_but_history_remains() -> None:
    registry, collection = owner(); value = activation(); registry.create_or_replay(value, session=Session())
    args = {"tenant_id": "tenant-a", "principal_id": "principal-a", "privileged_role_id": "ENTERPRISE_ADMIN", "target_class": PrivilegedTargetClass.TENANT_PRIVILEGED}
    assert registry.resolve_current(at=value.effective_until - timedelta(microseconds=1), **args) == value
    assert registry.resolve_current(at=value.effective_until, **args) is None
    assert len(collection.rows) == 1 and registry.get_history(value.activation_id) == (value,)


@pytest.mark.parametrize("field,bad", [("status", "BROKEN"), ("activated_at", "not-time"), ("activation_fingerprint", "0" * 128), ("revision", 7), ("previous_activation_fingerprint", "c" * 128)])
def test_corrupt_persisted_material_rejects(field: str, bad: object) -> None:
    registry, collection = owner(); value = activation(); registry.create_or_replay(value, session=Session()); collection.rows[0][field] = bad
    with pytest.raises(PrivilegedActivationPersistedInvalidError):
        registry.get_history(value.activation_id)


def test_default_bson_naive_datetimes_hydrate_as_aware_utc() -> None:
    registry, collection = owner(); value = activation(); registry.create_or_replay(value, session=Session())
    collection.rows[0]["activated_at"] = NOW.replace(tzinfo=None)
    collection.rows[0]["effective_until"] = (NOW + timedelta(minutes=15)).replace(tzinfo=None)
    assert registry.get_history(value.activation_id)[0].activated_at.tzinfo is timezone.utc


def test_write_requires_active_caller_transaction() -> None:
    registry, collection = owner()
    with pytest.raises(PrivilegedActivationTransactionRequiredError, match="ACTIVE_TRANSACTION_REQUIRED"):
        registry.create_or_replay(activation(), session=None)
    assert collection.rows == []


def test_no_secret_p5_break_glass_or_financial_authority_surface() -> None:
    source = Path("tools/eos/auth/privileged_activation_registry.py").read_text()
    for forbidden in ("expireAfterSeconds", "password_hash", "mfa_secret", "raw_signature", "bearer_token", "break_glass_registry", "authorize_privileged_use", "execute_payment", "settle("):
        assert forbidden not in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_privileged_activation_registry.py
# VERSION: v1.0.0-P4-R2-DIRECT-CERTIFICATE
# AUTHORITY BOUNDARY: registry contract only; no issuance/use/break-glass/finance
# END OF WILSY OS SOVEREIGN ARTIFACT
