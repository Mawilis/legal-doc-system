"""Direct certificate for deterministic Legal Operations entity read models.

TITLE: WILSY OS Legal Operations Current and History Read Model Certificate
VERSION: v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-CERT
AUTHORITY: Direct adversarial certification of L8-5 entity read-model composition.
EPITOME: Prove exact current-plus-history composition, deterministic tenant/type
         listing, full-history current selection, fork rejection, tenant
         isolation, caller-session propagation, bounded absence, and explicit
         exclusion of queue, search, mutation, service, and financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_read_model.py
COLLABORATION / OWNERSHIP: Certificate for legal_operations_read_model.py only;
                            P1 remains lifecycle authority, P2 remains durable
                            enumeration/hydration authority, and L8-0 remains
                            deterministic current-state authority. Queue/search,
                            HTTP/IAM, client policy, and Intelligence remain
                            separate bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-CERT
           establishes direct evidence for exact entity current/history, tenant
           entity-class grouping, deterministic ordering, foreign absence,
           unsupported type rejection, divergent history rejection, caller
           session propagation, and non-financial projection-only semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and references only;
                             no real tenant, customer, credential, provider,
                             browser, payment, or external service data.
TENANT BOUNDARY: Every fake persistence query is exact-tenant scoped and all
                 returned P1 values must remain within the requested tenant.
AUTHORITY BOUNDARY: Certificate only. Read models grant no authorization and
                    cannot register, accept, receive, allocate, attempt, serve,
                    return, queue work, bill, invoice, pay, execute, or settle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Unsupported type, absence, foreign scope, malformed
                         P2 evidence, forked history, ambiguous current state,
                         or session loss fails the certificate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.legal_operations.domain.legal_operations_read_model as read_model
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    LegalInstruction,
    LegalInstructionState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    VERSION as PRODUCTION_VERSION,
    LegalOperationsReadModelError,
    get_entity_read_model,
    list_entity_read_models,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-CERT"
NOW = datetime(2026, 9, 23, 10, 30, tzinfo=timezone.utc)
TENANT = "tenant-l8-5"
FOREIGN = "tenant-l8-5-foreign"


class FakeSession:
    """Opaque caller-owned session marker used only for propagation proof."""


def _lookup(document: dict[str, Any], key: str) -> Any:
    """Resolve one Mongo-style dotted key inside a fake durable record."""
    value: Any = document
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


class FakeCollection:
    """Minimal Mongo-compatible collection for canonical P2 direct tests."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        """Return the first exact match while preserving caller session."""
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(_lookup(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        """Return all exact matches while preserving caller session."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(_lookup(document, key) == value for key, value in query.items())
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        """Append one immutable P2 row without adding read-model semantics."""
        self.calls.append(("insert_one", session, deepcopy(document)))
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))


def _instruction(
    instruction_id: str,
    *,
    tenant_id: str = TENANT,
    matter_id: str | None = None,
    document_id: str | None = None,
) -> LegalInstruction:
    """Build one deterministic registered instruction."""
    suffix = instruction_id.rsplit("-", 1)[-1]
    return LegalInstruction(
        tenant_id=tenant_id,
        instruction_id=instruction_id,
        case_matter_id=matter_id or f"matter-{suffix}",
        document_id=document_id or f"document-{suffix}",
        registered_at=NOW,
        evidence_reference=f"registration-{suffix}",
    )


def _expect(code: str, operation: Any) -> None:
    """Assert one stable L8-5 read-model failure code."""
    with pytest.raises(LegalOperationsReadModelError) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_exact_entity_model_contains_complete_history_and_deterministic_current() -> None:
    """One exact entity exposes all snapshots and L8-0-selected current truth."""
    collection = FakeCollection()
    registered = _instruction("instruction-1")
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="acceptance-1",
        occurred_at=NOW + timedelta(minutes=1),
    )
    LegalOperationsLifecycleRegistry.create(registered, collection)
    LegalOperationsLifecycleRegistry.create(accepted, collection)

    model = get_entity_read_model(
        tenant_id=TENANT,
        entity_type="LegalInstruction",
        entity_identity="instruction-1",
        lifecycle_collection=collection,
    )

    assert model.current == accepted
    assert model.history == (registered, accepted)
    assert model.entity_identity == "instruction-1"
    payload = model.to_dict()
    assert payload["current"] == accepted.to_dict()
    assert payload["history"] == [registered.to_dict(), accepted.to_dict()]


def test_tenant_entity_models_group_complete_histories_and_sort_identity() -> None:
    """Tenant/type listing groups immutable snapshots before current projection."""
    collection = FakeCollection()
    instruction_b = _instruction("instruction-b")
    instruction_b_accepted = instruction_b.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="acceptance-b",
        occurred_at=NOW + timedelta(minutes=2),
    )
    instruction_a = _instruction("instruction-a")
    foreign = _instruction("instruction-a", tenant_id=FOREIGN)

    for value in (
        instruction_b_accepted,
        foreign,
        instruction_a,
        instruction_b,
    ):
        LegalOperationsLifecycleRegistry.create(value, collection)

    models = list_entity_read_models(
        tenant_id=TENANT,
        entity_type="LegalInstruction",
        lifecycle_collection=collection,
    )

    assert [model.entity_identity for model in models] == [
        "instruction-a",
        "instruction-b",
    ]
    assert models[0].history == (instruction_a,)
    assert models[0].current == instruction_a
    assert {value.fingerprint for value in models[1].history} == {
        instruction_b.fingerprint,
        instruction_b_accepted.fingerprint,
    }
    assert models[1].current == instruction_b_accepted
    assert all(model.tenant_id == TENANT for model in models)


def test_immutable_entities_are_composed_without_invented_lifecycle() -> None:
    """Static CaseMatter identity uses canonical current projection only."""
    collection = FakeCollection()
    matter = CaseMatter(
        tenant_id=TENANT,
        case_matter_id="matter-1",
        matter_reference="CASE-2026-001",
        opened_at=NOW,
        evidence_reference="matter-registration",
    )
    LegalOperationsLifecycleRegistry.create(matter, collection)

    models = list_entity_read_models(
        tenant_id=TENANT,
        entity_type="CaseMatter",
        lifecycle_collection=collection,
    )

    assert len(models) == 1
    assert models[0].current == matter
    assert models[0].history == (matter,)


def test_forked_instruction_history_rejects_without_arbitrary_current() -> None:
    """Equal-depth ACCEPTED/CANCELLED forks cannot produce an arbitrary read."""
    collection = FakeCollection()
    registered = _instruction("instruction-1")
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=NOW + timedelta(minutes=1),
    )
    cancelled = registered.transition_to(
        LegalInstructionState.CANCELLED,
        evidence_reference="cancelled",
        occurred_at=NOW + timedelta(minutes=1),
    )
    for value in (registered, accepted, cancelled):
        LegalOperationsLifecycleRegistry.create(value, collection)

    _expect(
        "L8_5_CURRENT_PROJECTION_INVALID",
        lambda: get_entity_read_model(
            tenant_id=TENANT,
            entity_type="LegalInstruction",
            entity_identity="instruction-1",
            lifecycle_collection=collection,
        ),
    )


def test_absence_foreign_scope_and_unsupported_type_fail_closed() -> None:
    """Foreign evidence is absence and unsupported vocabulary never reaches P2."""
    collection = FakeCollection()
    LegalOperationsLifecycleRegistry.create(
        _instruction("instruction-1", tenant_id=FOREIGN),
        collection,
    )

    _expect(
        "L8_5_ENTITY_NOT_FOUND",
        lambda: get_entity_read_model(
            tenant_id=TENANT,
            entity_type="LegalInstruction",
            entity_identity="instruction-1",
            lifecycle_collection=collection,
        ),
    )
    _expect(
        "L8_5_ENTITY_TYPE_UNSUPPORTED",
        lambda: list_entity_read_models(
            tenant_id=TENANT,
            entity_type="UnknownEntity",
            lifecycle_collection=collection,
        ),
    )
    assert list_entity_read_models(
        tenant_id=TENANT,
        entity_type="CaseMatter",
        lifecycle_collection=collection,
    ) == ()


def test_caller_session_is_forwarded_to_exact_and_tenant_entity_reads() -> None:
    """L8-5 owns no transaction and preserves caller sessions into P2."""
    collection = FakeCollection()
    session = FakeSession()
    LegalOperationsLifecycleRegistry.create(
        _instruction("instruction-1"),
        collection,
        session=session,
    )
    collection.calls.clear()

    get_entity_read_model(
        tenant_id=TENANT,
        entity_type="LegalInstruction",
        entity_identity="instruction-1",
        lifecycle_collection=collection,
        session=session,
    )
    list_entity_read_models(
        tenant_id=TENANT,
        entity_type="LegalInstruction",
        lifecycle_collection=collection,
        session=session,
    )

    reads = [call for call in collection.calls if call[0] == "find"]
    assert reads == [
        (
            "find",
            session,
            {
                "tenant_id": TENANT,
                "entity_type": "LegalInstruction",
                "entity_identity": "instruction-1",
            },
        ),
        (
            "find",
            session,
            {
                "tenant_id": TENANT,
                "entity_type": "LegalInstruction",
            },
        ),
    ]


def test_read_model_has_no_queue_search_mutation_or_financial_authority() -> None:
    """L8-5A remains a pure entity projection foundation."""
    collection = FakeCollection()
    LegalOperationsLifecycleRegistry.create(_instruction("instruction-1"), collection)
    model = get_entity_read_model(
        tenant_id=TENANT,
        entity_type="LegalInstruction",
        entity_identity="instruction-1",
        lifecycle_collection=collection,
    )
    serialized = str(model.to_dict()).casefold()

    for token in (
        "payment",
        "settlement",
        "paid_state",
        "bank_execution",
        "provider_execution",
    ):
        assert token not in serialized

    for name in (
        "create",
        "update",
        "delete",
        "allocate",
        "accept",
        "receive",
        "serve",
        "queue",
        "search",
    ):
        assert not hasattr(read_model, name)


def test_versions_are_bound_to_l8_5_entity_read_model_release() -> None:
    """Certificate and production versions remain frozen together."""
    assert PRODUCTION_VERSION == (
        "v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL"
    )
    assert VERSION == (
        "v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-CERT"
    )


# ARTIFACT: test_legal_operations_read_model.py
# VERSION: v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-CERT
# AUTHORITY BOUNDARY: direct L8-5 current-plus-history read-model certificate only
# TENANT POSTURE: exact synthetic tenant/type/identity scope with foreign absence
# FAIL-CLOSED POSTURE: unsupported/absent/corrupt/forked/ambiguous evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
