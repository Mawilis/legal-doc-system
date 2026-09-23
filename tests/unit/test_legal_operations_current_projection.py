"""Direct certificate for deterministic Legal Operations current projection.

TITLE: Wilsy OS Legal Operations Current Snapshot Projection Certificate
VERSION: v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove linear-history current selection, exact replay tolerance and
         fail-closed rejection of forks, static drift, tenant/identity/type
         mismatch, immutable-fact divergence and empty/unsupported input.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_current_projection.py
COLLABORATION / OWNERSHIP: Direct certificate for
                            legal_operations_current_projection.py only; P1
                            remains lifecycle authority and P2 remains
                            persistence/hydration authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION-CERT
           establishes adversarial direct coverage for the L8-0 pure
           current-history projection contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic in-memory values only; no database,
                             network, provider, credential, secret or customer
                             data access.
TENANT BOUNDARY: Fixtures use explicit non-global tenants and certify
                 cross-tenant rejection.
AUTHORITY BOUNDARY: Certificate only; no lifecycle mutation or persistence.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution
                              and settlement authority.
FAIL-CLOSED DECLARATION: Any ambiguous or divergent current projection must
                         raise one stable L8-0 error rather than selecting a row.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, cast

import pytest

from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    District,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
    ServiceAttempt,
    ServiceAttemptState,
)


NOW = datetime(2026, 9, 23, 6, 0, tzinfo=timezone.utc)
FP = "a" * 128


def instruction(**overrides: object) -> LegalInstruction:
    """Build one synthetic instruction baseline."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "instruction_id": "instruction-1",
        "case_matter_id": "matter-1",
        "document_id": "document-1",
        "registered_at": NOW,
        "evidence_reference": "instruction-registration",
    }
    values.update(overrides)
    return cast(Any, LegalInstruction)(**values)


def document(**overrides: object) -> ProcessDocument:
    """Build one synthetic document baseline."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "document_id": "document-1",
        "case_matter_id": "matter-1",
        "document_type": "summons",
        "registered_at": NOW,
        "registration_evidence_reference": "document-registration",
    }
    values.update(overrides)
    return cast(Any, ProcessDocument)(**values)


def attempt(**overrides: object) -> ServiceAttempt:
    """Build one synthetic attempt baseline."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "attempt_id": "attempt-1",
        "instruction_id": "instruction-1",
        "document_id": "document-1",
        "deputy_id": "deputy-1",
        "allocated_at": NOW,
        "allocation_evidence_reference": "allocation-1",
    }
    values.update(overrides)
    return cast(Any, ServiceAttempt)(**values)


def expect_code(code: str, operation: Callable[[], object]) -> None:
    """Assert one stable L8-0 failure code."""
    with pytest.raises(LegalOperationsCurrentProjectionError) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_instruction_linear_history_resolves_unique_longest_snapshot() -> None:
    """Unordered complete linear history resolves the unique current instruction."""
    registered = instruction()
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="instruction-accepted",
        occurred_at=NOW + timedelta(minutes=1),
    )
    closed = accepted.transition_to(
        LegalInstructionState.CLOSED,
        evidence_reference="instruction-closed",
        occurred_at=NOW + timedelta(minutes=2),
    )

    current = resolve_current_lifecycle_snapshot(
        (accepted, registered, closed),
        expected_type=LegalInstruction,
    )

    assert current is closed
    assert current.state is LegalInstructionState.CLOSED
    assert len(current.transition_history) == 2


def test_document_and_attempt_histories_resolve_without_collapsing_semantics() -> None:
    """Document receipt and attempt outcome remain separate linear projections."""
    registered = document()
    received = registered.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="document-received",
        occurred_at=NOW + timedelta(minutes=1),
    )
    allocated = received.transition_to(
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        evidence_reference="document-allocated",
        occurred_at=NOW + timedelta(minutes=2),
    )

    initial_attempt = attempt()
    attempted = initial_attempt.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-observation",
        occurred_at=NOW + timedelta(minutes=3),
    )
    terminal = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="service-evidence",
        evidence_fingerprint=FP,
        occurred_at=NOW + timedelta(minutes=4),
    )

    assert resolve_current_lifecycle_snapshot(
        (registered, allocated, received),
        expected_type=ProcessDocument,
    ) is allocated
    assert resolve_current_lifecycle_snapshot(
        (attempted, terminal, initial_attempt),
        expected_type=ServiceAttempt,
    ) is terminal


def test_exact_duplicate_input_is_tolerated_without_creating_ambiguity() -> None:
    """Transport-level duplicate exact values do not become false divergence."""
    value = instruction()
    current = resolve_current_lifecycle_snapshot((value, value), expected_type=LegalInstruction)
    assert current is value


def test_forked_instruction_history_rejects_instead_of_selecting_a_branch() -> None:
    """Sibling transitions from one source are ambiguous current truth."""
    registered = instruction()
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

    expect_code(
        "L8_0_CURRENT_SNAPSHOT_AMBIGUOUS",
        lambda: resolve_current_lifecycle_snapshot(
            (registered, accepted, cancelled),
            expected_type=LegalInstruction,
        ),
    )


def test_divergent_ancestor_history_rejects_even_when_one_branch_is_longer() -> None:
    """A longer branch cannot hide a conflicting shorter durable lineage."""
    registered = instruction()
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=NOW + timedelta(minutes=1),
    )
    closed = accepted.transition_to(
        LegalInstructionState.CLOSED,
        evidence_reference="closed",
        occurred_at=NOW + timedelta(minutes=2),
    )
    cancelled = registered.transition_to(
        LegalInstructionState.CANCELLED,
        evidence_reference="cancelled",
        occurred_at=NOW + timedelta(minutes=1),
    )

    expect_code(
        "L8_0_HISTORY_DIVERGENCE",
        lambda: resolve_current_lifecycle_snapshot(
            (registered, cancelled, closed),
            expected_type=LegalInstruction,
        ),
    )


def test_static_payload_drift_rejects_for_same_entity_identity() -> None:
    """Static registration evidence may not mutate across one lifecycle lineage."""
    original = instruction()
    drifted = instruction(evidence_reference="different-registration")
    expect_code(
        "L8_0_STATIC_PAYLOAD_DIVERGENCE",
        lambda: resolve_current_lifecycle_snapshot(
            (original, drifted),
            expected_type=LegalInstruction,
        ),
    )


def test_tenant_identity_type_and_expected_type_mismatch_reject() -> None:
    """Projection scope cannot cross tenant, identity or concrete P1 type."""
    own = instruction()
    foreign = instruction(tenant_id="tenant-b")
    other_identity = instruction(instruction_id="instruction-2")
    process_document = document()

    expect_code(
        "L8_0_TENANT_MISMATCH",
        lambda: resolve_current_lifecycle_snapshot((own, foreign)),
    )
    expect_code(
        "L8_0_ENTITY_IDENTITY_MISMATCH",
        lambda: resolve_current_lifecycle_snapshot((own, other_identity)),
    )
    expect_code(
        "L8_0_ENTITY_TYPE_MISMATCH",
        lambda: resolve_current_lifecycle_snapshot(cast(Any, (own, process_document))),
    )
    expect_code(
        "L8_0_EXPECTED_TYPE_MISMATCH",
        lambda: resolve_current_lifecycle_snapshot((own,), expected_type=ProcessDocument),
    )


def test_immutable_fact_divergence_rejects_and_exact_duplicate_is_safe() -> None:
    """Immutable directory identities cannot have competing durable facts."""
    district = District(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
    )
    duplicate = District(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
    )
    divergent = District(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source-2",
    )

    assert resolve_current_lifecycle_snapshot((district, duplicate), expected_type=District) == district
    expect_code(
        "L8_0_IMMUTABLE_FACT_DIVERGENCE",
        lambda: resolve_current_lifecycle_snapshot((district, divergent), expected_type=District),
    )


def test_empty_and_unsupported_inputs_fail_closed() -> None:
    """Absence or non-P1 input never produces an invented current snapshot."""
    expect_code("L8_0_HISTORY_REQUIRED", lambda: resolve_current_lifecycle_snapshot(()))
    expect_code(
        "L8_0_ENTITY_TYPE_UNSUPPORTED",
        lambda: resolve_current_lifecycle_snapshot(cast(Any, (object(),))),
    )


# ARTIFACT: test_legal_operations_current_projection.py
# VERSION: v1.0.0-L8-0-LEGAL-OPERATIONS-CURRENT-PROJECTION-CERT
# AUTHORITY BOUNDARY: direct projection certificate only; no mutation authority
# TENANT POSTURE: explicit synthetic tenant scope; cross-tenant input rejects
# FAIL-CLOSED POSTURE: ambiguity, forks, drift and unsupported input must reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
