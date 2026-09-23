"""Direct certificate for the L8-7D11 Legal operator workspace projection.

TITLE: WILSY OS Legal Operator Workspace Direct Certificate
VERSION: v1.0.0-L8-7D11-LEGAL-OPERATOR-WORKSPACE-CERT
AUTHORITY: Deterministic unit certificate only.
EPITOME: Proves graph-coherent matter/instruction/document/custody/service/return
         composition, curated serialization, tenant/type fail-closed behavior,
         terminal-execution requirements, and upstream read-model failure mapping.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operator_workspace.py
COLLABORATION / OWNERSHIP: Production projection remains authoritative for
                            composition semantics; this file supplies synthetic
                            deterministic evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-24
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant-only evidence; no cross-tenant fallback.
AUTHORITY BOUNDARY: Test evidence only; no lifecycle, IAM, billing, or finance authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tools.eos.legal_operations.domain.legal_operator_workspace as workspace
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    ProcessDocument,
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
)


TENANT = "tenant-operator"
BASE = datetime(2026, 9, 24, 0, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class _Model:
    tenant_id: str
    entity_type: str
    current: Any


def _graph() -> dict[str, tuple[Any, ...]]:
    matter = CaseMatter(
        tenant_id=TENANT,
        case_matter_id="matter-1",
        matter_reference="MAT-2026-001",
        opened_at=BASE,
        evidence_reference="matter-open",
    )
    instruction = LegalInstruction(
        tenant_id=TENANT,
        instruction_id="instruction-1",
        case_matter_id=matter.case_matter_id,
        document_id="document-1",
        registered_at=BASE + timedelta(minutes=1),
        evidence_reference="instruction-register",
    )
    document = ProcessDocument(
        tenant_id=TENANT,
        document_id=instruction.document_id,
        case_matter_id=matter.case_matter_id,
        document_type="SUMMONS",
        registered_at=BASE + timedelta(minutes=2),
        registration_evidence_reference="document-register",
    )
    custody_registered = DocumentCustodyEvent(
        tenant_id=TENANT,
        custody_event_id="custody-1",
        document_id=document.document_id,
        event_type=DocumentCustodyEventType.REGISTERED,
        occurred_at=BASE + timedelta(minutes=2),
        sequence_number=1,
        evidence_reference="custody-register",
    )
    custody_received = DocumentCustodyEvent(
        tenant_id=TENANT,
        custody_event_id="custody-2",
        document_id=document.document_id,
        event_type=DocumentCustodyEventType.RECEIVED_IN_OFFICE,
        occurred_at=BASE + timedelta(minutes=3),
        sequence_number=2,
        evidence_reference="custody-receive",
        from_holder_reference="intake",
        to_holder_reference="office-1",
    )
    allocated = ServiceAttempt(
        tenant_id=TENANT,
        attempt_id="attempt-1",
        instruction_id=instruction.instruction_id,
        document_id=document.document_id,
        deputy_id="deputy-1",
        allocated_at=BASE + timedelta(minutes=4),
        allocation_evidence_reference="allocation-1",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempted-1",
        occurred_at=BASE + timedelta(minutes=5),
    )
    terminal = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="served-1",
        evidence_fingerprint="a" * 128,
        occurred_at=BASE + timedelta(minutes=6),
    )
    execution = ServiceExecution.from_attempt(
        attempt=terminal,
        service_execution_id="execution-1",
        executed_at=BASE + timedelta(minutes=7),
    )
    returned = ReturnOfService.from_service_execution(
        instruction_id=instruction.instruction_id,
        service_execution=execution,
        return_id="return-1",
        generated_at=BASE + timedelta(minutes=8),
    )
    return {
        "CaseMatter": (matter,),
        "LegalInstruction": (instruction,),
        "ProcessDocument": (document,),
        "DocumentCustodyEvent": (custody_received, custody_registered),
        "ServiceAttempt": (terminal,),
        "ServiceExecution": (execution,),
        "ReturnOfService": (returned,),
    }


def _install(monkeypatch: pytest.MonkeyPatch, graph: dict[str, tuple[Any, ...]]) -> None:
    def fake_list(
        *,
        tenant_id: str,
        entity_type: str,
        lifecycle_collection: Any,
        session: Any = None,
    ) -> tuple[_Model, ...]:
        assert tenant_id == TENANT
        assert lifecycle_collection == "collection"
        assert session == "session"
        return tuple(
            _Model(TENANT, entity_type, value)
            for value in graph.get(entity_type, ())
        )

    monkeypatch.setattr(workspace, "list_entity_read_models", fake_list)


def test_complete_workspace_is_coherent_ordered_and_curated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = _graph()
    _install(monkeypatch, graph)

    result = workspace.get_legal_operator_workspace(
        tenant_id=TENANT,
        lifecycle_collection="collection",
        session="session",
    )
    payload = result.to_dict()

    assert payload["schema"] == workspace.SCHEMA
    assert payload["version"] == workspace.VERSION
    assert payload["tenant_id"] == TENANT
    assert payload["visibility"] == workspace.VISIBILITY
    assert payload["matters"][0]["matter_reference"] == "MAT-2026-001"
    assert payload["instructions"][0]["instruction_id"] == "instruction-1"
    assert payload["documents"][0]["document_type"] == "SUMMONS"
    assert [row["sequence_number"] for row in payload["custody_events"]] == [1, 2]
    assert payload["attempts"][0]["state"] == "COMPLETED"
    assert payload["executions"][0]["outcome"] == "COMPLETED"
    assert payload["returns"][0]["state"] == "GENERATED"

    serialized = repr(payload)
    assert "evidence_fingerprint" not in serialized
    assert "evidence_reference" not in serialized
    assert "transition_history" not in serialized
    assert "payment" not in serialized.lower()
    assert "settlement" not in serialized.lower()


def test_instruction_requires_matching_matter_and_document(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = _graph()
    graph["CaseMatter"] = ()
    _install(monkeypatch, graph)

    with pytest.raises(workspace.LegalOperatorWorkspaceError) as caught:
        workspace.get_legal_operator_workspace(
            tenant_id=TENANT,
            lifecycle_collection="collection",
            session="session",
        )
    assert caught.value.code == "L8_7D11_DOCUMENT_MATTER_MISSING"


def test_every_process_document_requires_valid_custody(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = _graph()
    graph["DocumentCustodyEvent"] = ()
    _install(monkeypatch, graph)

    with pytest.raises(workspace.LegalOperatorWorkspaceError) as caught:
        workspace.get_legal_operator_workspace(
            tenant_id=TENANT,
            lifecycle_collection="collection",
            session="session",
        )
    assert caught.value.code == "L8_7D11_CUSTODY_REQUIRED"


def test_terminal_attempt_requires_certified_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = _graph()
    graph["ServiceExecution"] = ()
    graph["ReturnOfService"] = ()
    _install(monkeypatch, graph)

    with pytest.raises(workspace.LegalOperatorWorkspaceError) as caught:
        workspace.get_legal_operator_workspace(
            tenant_id=TENANT,
            lifecycle_collection="collection",
            session="session",
        )
    assert caught.value.code == "L8_7D11_TERMINAL_EXECUTION_REQUIRED"


def test_return_requires_matching_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = _graph()
    original = graph["ReturnOfService"][0]
    graph["ServiceExecution"] = ()

    # Keep a return but remove its source execution: the projection must reject.
    graph["ReturnOfService"] = (original,)
    _install(monkeypatch, graph)

    with pytest.raises(workspace.LegalOperatorWorkspaceError) as caught:
        workspace.get_legal_operator_workspace(
            tenant_id=TENANT,
            lifecycle_collection="collection",
            session="session",
        )
    assert caught.value.code == "L8_7D11_TERMINAL_EXECUTION_REQUIRED"


def test_cross_tenant_read_model_drift_rejects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = _graph()

    def fake_list(**kwargs: Any) -> tuple[_Model, ...]:
        entity_type = kwargs["entity_type"]
        values = graph.get(entity_type, ())
        if entity_type == "CaseMatter":
            return tuple(
                _Model("foreign-tenant", entity_type, value)
                for value in values
            )
        return tuple(_Model(TENANT, entity_type, value) for value in values)

    monkeypatch.setattr(workspace, "list_entity_read_models", fake_list)

    with pytest.raises(workspace.LegalOperatorWorkspaceError) as caught:
        workspace.get_legal_operator_workspace(
            tenant_id=TENANT,
            lifecycle_collection="collection",
        )
    assert caught.value.code == "L8_7D11_READ_MODEL_SCOPE_INVALID"


def test_upstream_read_model_failure_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(**_: Any) -> tuple[Any, ...]:
        raise LegalOperationsReadModelError("L8_5_EVIDENCE_UNAVAILABLE")

    monkeypatch.setattr(workspace, "list_entity_read_models", unavailable)

    with pytest.raises(workspace.LegalOperatorWorkspaceError) as caught:
        workspace.get_legal_operator_workspace(
            tenant_id=TENANT,
            lifecycle_collection="collection",
        )
    assert caught.value.code == "L8_7D11_READ_MODEL_UNAVAILABLE"


# ARTIFACT: test_legal_operator_workspace.py
# VERSION: v1.0.0-L8-7D11-LEGAL-OPERATOR-WORKSPACE-CERT
# AUTHORITY BOUNDARY: deterministic direct certificate only
# TENANT POSTURE: synthetic exact-tenant graph evidence only
# FAIL-CLOSED POSTURE: partial, divergent, foreign, or unavailable evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
