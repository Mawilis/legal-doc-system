"""TITLE: WILSY OS Tenant Legal Workflow Activation Registry Unit Certificate.

VERSION: v1.0.0-G7G-P0A-ACTIVATION-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable tenant-first persistence, strict hydration, replay,
         transaction ownership, lineage/currentness, and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_legal_workflow_activation_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the corresponding P0 registry.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0A-ACTIVATION-REGISTRY-UNIT-CERT establishes the first bounded unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant isolation and foreign-tenant non-disclosure tested.
AUTHORITY BOUNDARY: Tests grant no IAM, assignment, supervision, or execution power.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.tenant_legal_workflow_activation import (
    TenantLegalWorkflowActivation,
)
from tools.eos.legal_operations.registry.tenant_legal_workflow_activation_registry import (
    CURRENTNESS_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    TenantLegalWorkflowActivationRegistry,
    TenantLegalWorkflowActivationRegistryConflictError,
    TenantLegalWorkflowActivationRegistryNotFoundError,
    TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError,
    TenantLegalWorkflowActivationRegistryRetryTransactionError,
    TenantLegalWorkflowActivationRegistryTransactionRequiredError,
)


class FakeCursor:
    def __init__(self, values):
        self._values = list(values)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        return self._values[index]

    def sort(self, keys):
        values = list(self._values)
        for name, direction in reversed(keys):
            values.sort(
                key=lambda row: row[name],
                reverse=direction < 0,
            )
        return FakeCursor(values)


class FakeCollection:
    def __init__(self):
        self.rows = []
        self.indexes = []
        self.raise_duplicate = False

    def create_index(self, keys, **kwargs):
        self.indexes.append((tuple(keys), kwargs))
        return kwargs["name"]

    def find_one(self, query, *, session):
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query, *, session):
        return FakeCursor(
            [dict(row) for row in self.rows
             if all(row.get(key) == value for key, value in query.items())]
        )

    def insert_one(self, document, *, session):
        if self.raise_duplicate:
            raise DuplicateKeyError("race")
        self.rows.append(dict(document))
        return SimpleNamespace(inserted_id="id")


ACTIVE = SimpleNamespace(in_transaction=True)
INACTIVE = SimpleNamespace(in_transaction=False)
FINGERPRINT = "a" * 128


def activation(
    *,
    activation_id="activation-1",
    tenant_id="tenant-a",
    revision=1,
    workflow_definition_id="workflow-a",
    effective_hour=9,
    supersedes=None,
):
    return TenantLegalWorkflowActivation(
        activation_id=activation_id,
        tenant_id=tenant_id,
        activation_revision=revision,
        operating_model_id="tom-1",
        operating_model_revision=1,
        operating_model_fingerprint=FINGERPRINT,
        workflow_definition_id=workflow_definition_id,
        workflow_definition_revision=1,
        workflow_definition_fingerprint="b" * 128,
        workflow_topology_fingerprint="c" * 128,
        commercial_eligibility_evidence_reference="commercial-proof",
        activation_reason_reference="approved-change",
        effective_from=datetime(2026, 10, 15, effective_hour, tzinfo=timezone.utc),
        supersedes_activation_id=supersedes,
    )


def registry():
    collection = FakeCollection()
    return TenantLegalWorkflowActivationRegistry(collection), collection


def test_indexes_are_exact_tenant_first_unique_and_non_ttl():
    value, collection = registry()
    value.ensure_indexes()
    assert {item[1]["name"] for item in collection.indexes} == {
        IDENTITY_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        HISTORY_INDEX_NAME,
        CURRENTNESS_INDEX_NAME,
    }
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)
    assert collection.indexes[0][0][0] == ("tenant_id", 1)


def test_active_transaction_is_required_before_reads_and_writes():
    value, _ = registry()
    with pytest.raises(TenantLegalWorkflowActivationRegistryTransactionRequiredError):
        value.create_or_replay(activation(), session=INACTIVE)
    with pytest.raises(TenantLegalWorkflowActivationRegistryTransactionRequiredError):
        value.list_history("tenant-a", "workflow-a", session=None)


def test_create_and_exact_replay():
    value, collection = registry()
    item = activation()
    assert value.create_or_replay(item, session=ACTIVE) == item
    assert value.create_or_replay(item, session=ACTIVE) == item
    assert len(collection.rows) == 1


def test_divergent_same_identity_rejects():
    value, _ = registry()
    first = activation()
    value.create_or_replay(first, session=ACTIVE)
    different = TenantLegalWorkflowActivation.from_dict({
        **first.to_dict(),
        "activation_reason_reference": "different-reason",
        "fingerprint": "",
    })
    with pytest.raises(TenantLegalWorkflowActivationRegistryConflictError):
        value.create_or_replay(different, session=ACTIVE)


def test_revision_chain_and_supersession_are_exact():
    value, _ = registry()
    first = activation()
    value.create_or_replay(first, session=ACTIVE)
    second = activation(
        activation_id="activation-2",
        revision=2,
        effective_hour=10,
        supersedes=first.activation_id,
    )
    value.create_or_replay(second, session=ACTIVE)
    assert value.list_history("tenant-a", "workflow-a", session=ACTIVE) == (
        first,
        second,
    )


@pytest.mark.parametrize(
    ("revision", "supersedes", "hour"),
    [(3, "activation-1", 10), (2, None, 10), (2, "wrong", 10), (2, "activation-1", 8)],
)
def test_gap_fork_or_chronology_conflict_rejects(revision, supersedes, hour):
    value, _ = registry()
    value.create_or_replay(activation(), session=ACTIVE)
    candidate = activation(
        activation_id=f"activation-{revision}",
        revision=revision,
        effective_hour=hour,
        supersedes=supersedes,
    )
    with pytest.raises(TenantLegalWorkflowActivationRegistryConflictError):
        value.create_or_replay(candidate, session=ACTIVE)


def test_currentness_is_derived_without_mutable_pointer():
    value, collection = registry()
    first = activation()
    second = activation(
        activation_id="activation-2",
        revision=2,
        effective_hour=11,
        supersedes=first.activation_id,
    )
    collection.rows.extend([first.to_dict(), second.to_dict()])
    at = datetime(2026, 10, 15, 10, tzinfo=timezone.utc)
    assert value.resolve_current("tenant-a", "workflow-a", at, session=ACTIVE) == first


def test_currentness_absence_is_tenant_scoped():
    value, collection = registry()
    collection.rows.append(activation(tenant_id="tenant-b").to_dict())
    with pytest.raises(TenantLegalWorkflowActivationRegistryNotFoundError):
        value.resolve_current(
            "tenant-a",
            "workflow-a",
            datetime(2026, 10, 15, 12, tzinfo=timezone.utc),
            session=ACTIVE,
        )


def test_persisted_corruption_rejects():
    value, collection = registry()
    collection.rows.append({**activation().to_dict(), "fingerprint": "0" * 128})
    with pytest.raises(TenantLegalWorkflowActivationRegistryPersistedRecordInvalidError):
        value.list_history("tenant-a", "workflow-a", session=ACTIVE)


def test_duplicate_race_requires_whole_transaction_retry():
    value, collection = registry()
    collection.raise_duplicate = True
    with pytest.raises(TenantLegalWorkflowActivationRegistryRetryTransactionError):
        value.create_or_replay(activation(), session=ACTIVE)


def test_registry_has_no_mutable_pointer_iam_assignment_or_financial_authority():
    import ast
    from pathlib import Path
    from tools.eos.legal_operations.registry import tenant_legal_workflow_activation_registry as module

    tree = ast.parse(Path(module.__file__).read_text())
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert calls.isdisjoint({"update_one", "replace_one", "delete_one", "delete_many"})
    assert "authorize" not in names
# ARTIFACT: test_tenant_legal_workflow_activation_registry.py
# VERSION: v1.0.0-G7G-P0A-ACTIVATION-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: verification only; no runtime authority
# TENANT POSTURE: exact tenant-isolation assertions
# FAIL-CLOSED POSTURE: negative and corruption cases required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
