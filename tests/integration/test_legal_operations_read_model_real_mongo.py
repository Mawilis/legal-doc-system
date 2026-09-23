"""Host-backed certificate for Legal Operations entity read models.

TITLE: WILSY OS Legal Operations Entity Read Model Real-Mongo Certificate
VERSION: v1.0.1-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-RM-CERT
AUTHORITY: Host-backed certification of L8-5 deterministic current/history read models.
EPITOME: Prove exact tenant/entity current-plus-history composition, tenant-wide
         entity listing, deterministic identity ordering, fork rejection,
         caller-session compatibility, foreign absence, and non-financial
         projection semantics against the writable Wilsy Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_read_model_real_mongo.py
COLLABORATION / OWNERSHIP: P1 owns lifecycle values; P2 owns persistence and
                            tenant/entity enumeration; L8-0 owns current-state
                            selection; L8-5 owns read-model composition only.
                            HTTP/IAM, queues, search, client policy, and
                            Intelligence remain separate bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-RM-CERT
           corrects the CaseMatter certificate wording to preserve canonical
           OPEN/CLOSED lifecycle semantics; runtime assertions are unchanged.
           2026-09-23 v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-RM-CERT
           establishes real-Mongo evidence for complete exact history,
           deterministic current selection, multiple-entity listing,
           foreign-tenant absence, history-fork rejection, caller-session
           propagation, and projection-only/non-financial output.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque legal
                             identities only; no real customer, provider,
                             credential, secret, browser, or payment data.
TENANT BOUNDARY: All writes and reads are exact-tenant scoped through canonical
                 P2 APIs; foreign tenant evidence is represented only as absence.
AUTHORITY BOUNDARY: Certificate only. Read models cannot register, accept,
                    receive, allocate, attempt, serve, return, queue work,
                    search clients, bill, invoice, pay, execute, or settle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: The certificate owns Mongo sessions/transactions; the
                      L8-5 read model forwards caller sessions and owns none.
FAIL-CLOSED DECLARATION: Wrong/unavailable Mongo runtime, corrupt P2 evidence,
                         foreign scope, history forks, ambiguous current state,
                         or financial-authority leakage fails certification.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

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
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 11, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; runtime failure is fatal."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_5_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_5_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_5_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_5_read_model_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _instruction(
    tenant_id: str,
    instruction_id: str,
) -> LegalInstruction:
    """Build one deterministic registered instruction."""
    suffix = instruction_id.rsplit("-", 1)[-1]
    return LegalInstruction(
        tenant_id=tenant_id,
        instruction_id=instruction_id,
        case_matter_id=f"matter-{suffix}",
        document_id=f"document-{suffix}",
        registered_at=NOW,
        evidence_reference=f"registration-{suffix}",
    )


def test_real_mongo_exact_current_history_and_tenant_listing(
    mongo_context: dict[str, Any],
) -> None:
    """Certify complete history current selection and deterministic entity listing."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"

    instruction_b = _instruction(tenant, "instruction-b")
    instruction_b_accepted = instruction_b.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="acceptance-b",
        occurred_at=NOW + timedelta(minutes=2),
    )
    instruction_a = _instruction(tenant, "instruction-a")
    for value in (
        instruction_b_accepted,
        instruction_a,
        instruction_b,
    ):
        LegalOperationsLifecycleRegistry.create(value, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        exact = get_entity_read_model(
            tenant_id=tenant,
            entity_type="LegalInstruction",
            entity_identity="instruction-b",
            lifecycle_collection=lifecycle,
            session=session,
        )
        models = list_entity_read_models(
            tenant_id=tenant,
            entity_type="LegalInstruction",
            lifecycle_collection=lifecycle,
            session=session,
        )
        session.commit_transaction()

    assert exact.current == instruction_b_accepted
    assert {value.fingerprint for value in exact.history} == {
        instruction_b.fingerprint,
        instruction_b_accepted.fingerprint,
    }
    assert [model.entity_identity for model in models] == [
        "instruction-a",
        "instruction-b",
    ]
    assert models[1].current == instruction_b_accepted


def test_real_mongo_foreign_tenant_is_absence(
    mongo_context: dict[str, Any],
) -> None:
    """Foreign tenant evidence cannot satisfy an exact local read/list scope."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    LegalOperationsLifecycleRegistry.create(
        _instruction(foreign, "instruction-1"),
        lifecycle,
    )

    with pytest.raises(LegalOperationsReadModelError) as caught:
        get_entity_read_model(
            tenant_id=tenant,
            entity_type="LegalInstruction",
            entity_identity="instruction-1",
            lifecycle_collection=lifecycle,
        )
    assert caught.value.code == "L8_5_ENTITY_NOT_FOUND"

    assert list_entity_read_models(
        tenant_id=tenant,
        entity_type="LegalInstruction",
        lifecycle_collection=lifecycle,
    ) == ()


def test_real_mongo_history_fork_rejects_without_arbitrary_current(
    mongo_context: dict[str, Any],
) -> None:
    """Divergent equal-depth histories never produce an arbitrary current row."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    registered = _instruction(tenant, "instruction-1")
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
        LegalOperationsLifecycleRegistry.create(value, lifecycle)

    with pytest.raises(LegalOperationsReadModelError) as caught:
        get_entity_read_model(
            tenant_id=tenant,
            entity_type="LegalInstruction",
            entity_identity="instruction-1",
            lifecycle_collection=lifecycle,
        )
    assert caught.value.code == "L8_5_CURRENT_PROJECTION_INVALID"


def test_real_mongo_open_matter_projection_and_financial_boundary(
    mongo_context: dict[str, Any],
) -> None:
    """OPEN matter read stays canonical and contains no financial authority."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    matter = CaseMatter(
        tenant_id=tenant,
        case_matter_id="matter-1",
        matter_reference="CASE-2026-001",
        opened_at=NOW,
        evidence_reference="matter-registration",
    )
    LegalOperationsLifecycleRegistry.create(matter, lifecycle)

    models = list_entity_read_models(
        tenant_id=tenant,
        entity_type="CaseMatter",
        lifecycle_collection=lifecycle,
    )
    assert len(models) == 1
    assert models[0].current == matter
    serialized = str(models[0].to_dict()).casefold()
    for forbidden in (
        "payment",
        "settlement",
        "paid_state",
        "bank_execution",
        "provider_execution",
    ):
        assert forbidden not in serialized

    assert PRODUCTION_VERSION == (
        "v1.0.0-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL"
    )
    assert VERSION == (
        "v1.0.1-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-RM-CERT"
    )


# ARTIFACT: test_legal_operations_read_model_real_mongo.py
# VERSION: v1.0.1-L8-5-LEGAL-OPERATIONS-ENTITY-READ-MODEL-RM-CERT
# AUTHORITY BOUNDARY: host-backed L8-5 current-plus-history read-model certificate only
# TENANT POSTURE: exact UUID-isolated tenant/type/identity scope with foreign absence
# FAIL-CLOSED POSTURE: runtime/corruption/fork/ambiguity/financial leakage fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT