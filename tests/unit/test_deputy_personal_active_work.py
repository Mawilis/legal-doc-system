"""Direct certificate for binding-scoped deputy personal active work.

TITLE: WILSY OS Deputy Personal Active Work Projection Certificate
VERSION: v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-CERT
AUTHORITY: Direct adversarial certification of L8-6C personal queue membership.
EPITOME: Prove exact binding-derived deputy identity, ALLOCATED/ATTEMPTED-only
         membership, other-deputy and terminal exclusion, deterministic upstream
         ordering, session propagation, fail-closed binding/evidence errors,
         constructor invariants, and absence of IAM/financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_deputy_personal_active_work.py
COLLABORATION / OWNERSHIP: Certificate for deputy_personal_active_work.py only;
                            L8-6B binding, L8-5 read models and IAM remain
                            independent canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-CERT
           adds direct public-aggregate identity and immutable tuple-shape
           rejection and rebinds the certificate to production v1.0.1.
           2026-09-23 v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-CERT
           establishes exact bound-deputy active membership, exclusion, error,
           session, aggregate-invariant and authority-boundary proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque attempt/deputy identifiers only.
TENANT BOUNDARY: Exact tenant/principal binding and same-tenant attempt models.
AUTHORITY BOUNDARY: Read-projection certificate only; binding is not IAM.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Binding/read-model/type/tenant/deputy/state drift
                         rejects without tenant-wide or fixture fallback.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.legal_operations.domain.deputy_personal_active_work as work
from tools.eos.legal_operations.domain.deputy_personal_active_work import (
    VERSION as PRODUCTION_VERSION,
    DeputyPersonalActiveWork,
    DeputyPersonalActiveWorkError,
    get_deputy_personal_active_work,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsEntityReadModel,
    LegalOperationsReadModelError,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingNotFoundError,
    DeputyPrincipalBindingPersistedRecordInvalidError,
)


VERSION = "v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-CERT"
NOW = datetime(2026, 9, 23, 19, 0, tzinfo=timezone.utc)
TENANT = "tenant-a"
PRINCIPAL = "principal-1"
DEPUTY = "deputy-1"


def _attempt(
    attempt_id: str,
    *,
    deputy_id: str = DEPUTY,
    state: ServiceAttemptState = ServiceAttemptState.ALLOCATED,
) -> ServiceAttempt:
    """Build one valid canonical attempt in the requested current state."""
    allocated = ServiceAttempt(
        tenant_id=TENANT,
        attempt_id=attempt_id,
        instruction_id=f"instruction-{attempt_id}",
        document_id=f"document-{attempt_id}",
        deputy_id=deputy_id,
        allocated_at=NOW,
        allocation_evidence_reference=f"allocation-{attempt_id}",
    )
    if state is ServiceAttemptState.ALLOCATED:
        return allocated
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference=f"attempted-{attempt_id}",
        occurred_at=NOW + timedelta(minutes=1),
    )
    if state is ServiceAttemptState.ATTEMPTED:
        return attempted
    if state is ServiceAttemptState.CANCELLED:
        return allocated.transition_to(
            ServiceAttemptState.CANCELLED,
            evidence_reference=f"cancelled-{attempt_id}",
            occurred_at=NOW + timedelta(minutes=1),
        )
    return attempted.transition_to(
        state,
        evidence_reference=f"terminal-{attempt_id}",
        evidence_fingerprint="a" * 128,
        occurred_at=NOW + timedelta(minutes=2),
    )


def _model(value: ServiceAttempt) -> LegalOperationsEntityReadModel:
    """Build one valid L8-5 model whose current value is the supplied snapshot."""
    allocated = _attempt(value.attempt_id, deputy_id=value.deputy_id)
    history: tuple[ServiceAttempt, ...]
    if value.state is ServiceAttemptState.ALLOCATED:
        history = (allocated,)
    elif value.state is ServiceAttemptState.CANCELLED:
        history = (allocated, value)
    else:
        attempted = allocated.transition_to(
            ServiceAttemptState.ATTEMPTED,
            evidence_reference=f"attempted-{value.attempt_id}",
            occurred_at=NOW + timedelta(minutes=1),
        )
        if value.state is ServiceAttemptState.ATTEMPTED:
            history = (allocated, attempted)
            value = attempted
        else:
            history = (allocated, attempted, value)
    return LegalOperationsEntityReadModel(
        tenant_id=TENANT,
        entity_type="ServiceAttempt",
        entity_identity=value.attempt_id,
        current=value,
        history=history,
    )


def _install_sources(
    monkeypatch: pytest.MonkeyPatch,
    models: tuple[LegalOperationsEntityReadModel, ...],
    *,
    session_seen: list[object],
) -> None:
    """Install binding/read-model spies while retaining real projection logic."""
    def resolve_binding(
        tenant_id: str,
        principal_id: str,
        _collection: object,
        *,
        session: object = None,
    ) -> object:
        assert tenant_id == TENANT
        assert principal_id == PRINCIPAL
        session_seen.append(session)
        return SimpleNamespace(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            deputy_id=DEPUTY,
        )

    def list_models(
        *,
        tenant_id: str,
        entity_type: str,
        lifecycle_collection: object,
        session: object = None,
    ) -> tuple[LegalOperationsEntityReadModel, ...]:
        assert tenant_id == TENANT
        assert entity_type == "ServiceAttempt"
        assert lifecycle_collection == "lifecycle"
        session_seen.append(session)
        return models

    monkeypatch.setattr(
        work.DeputyPrincipalBindingRegistry,
        "resolve_by_principal",
        staticmethod(resolve_binding),
    )
    monkeypatch.setattr(work, "list_entity_read_models", list_models)


def test_exact_bound_deputy_active_work_and_session_propagation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only bound-deputy ALLOCATED/ATTEMPTED current work survives."""
    models = (
        _model(_attempt("attempt-1")),
        _model(_attempt("attempt-2", state=ServiceAttemptState.ATTEMPTED)),
        _model(_attempt("attempt-3", deputy_id="deputy-other")),
        _model(_attempt("attempt-4", state=ServiceAttemptState.COMPLETED)),
        _model(_attempt("attempt-5", state=ServiceAttemptState.NOT_COMPLETED)),
        _model(_attempt("attempt-6", state=ServiceAttemptState.CANCELLED)),
    )
    session = object()
    seen: list[object] = []
    _install_sources(monkeypatch, models, session_seen=seen)

    result = get_deputy_personal_active_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        binding_collection="binding",
        lifecycle_collection="lifecycle",
        session=session,
    )

    assert result.tenant_id == TENANT
    assert result.principal_id == PRINCIPAL
    assert result.deputy_id == DEPUTY
    assert [
        model.entity_identity for model in result.active_attempts
    ] == ["attempt-1", "attempt-2"]
    assert seen == [session, session]


def test_empty_personal_queue_is_valid_and_non_inventing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    models = (
        _model(_attempt("attempt-1", deputy_id="deputy-other")),
        _model(_attempt("attempt-2", state=ServiceAttemptState.COMPLETED)),
    )
    seen: list[object] = []
    _install_sources(monkeypatch, models, session_seen=seen)

    result = get_deputy_personal_active_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        binding_collection="binding",
        lifecycle_collection="lifecycle",
    )

    assert result.active_attempts == ()
    assert result.to_dict()["active_attempts"] == []


def test_missing_and_corrupt_binding_fail_before_attempt_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reads: list[str] = []
    monkeypatch.setattr(
        work,
        "list_entity_read_models",
        lambda **_kwargs: reads.append("attempts") or (),
    )

    for error, code in (
        (
            DeputyPrincipalBindingNotFoundError("L8_6B_BINDING_NOT_FOUND"),
            "L8_6C_BINDING_REQUIRED",
        ),
        (
            DeputyPrincipalBindingPersistedRecordInvalidError(
                "L8_6B_BINDING_PERSISTED_RECORD_INVALID"
            ),
            "L8_6C_BINDING_INVALID",
        ),
    ):
        monkeypatch.setattr(
            work.DeputyPrincipalBindingRegistry,
            "resolve_by_principal",
            staticmethod(lambda *_args, error=error, **_kwargs: (_ for _ in ()).throw(error)),
        )
        with pytest.raises(DeputyPersonalActiveWorkError) as caught:
            get_deputy_personal_active_work(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                binding_collection="binding",
                lifecycle_collection="lifecycle",
            )
        assert caught.value.code == code
        assert reads == []


def test_read_model_failure_is_bounded_without_partial_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[object] = []
    _install_sources(monkeypatch, (), session_seen=seen)

    def reject(**_kwargs: object) -> tuple[LegalOperationsEntityReadModel, ...]:
        raise LegalOperationsReadModelError("L8_5_EVIDENCE_UNAVAILABLE")

    monkeypatch.setattr(work, "list_entity_read_models", reject)

    with pytest.raises(DeputyPersonalActiveWorkError) as caught:
        get_deputy_personal_active_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            binding_collection="binding",
            lifecycle_collection="lifecycle",
        )
    assert caught.value.code == "L8_6C_ATTEMPT_EVIDENCE_UNAVAILABLE"


def test_aggregate_rejects_wrong_deputy_or_terminal_membership() -> None:
    wrong = _model(_attempt("attempt-wrong", deputy_id="deputy-other"))
    with pytest.raises(DeputyPersonalActiveWorkError) as caught:
        DeputyPersonalActiveWork(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            deputy_id=DEPUTY,
            active_attempts=(wrong,),
        )
    assert caught.value.code == "L8_6C_DEPUTY_SCOPE_MISMATCH"

    terminal = _model(
        _attempt("attempt-terminal", state=ServiceAttemptState.COMPLETED)
    )
    with pytest.raises(DeputyPersonalActiveWorkError) as caught:
        DeputyPersonalActiveWork(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            deputy_id=DEPUTY,
            active_attempts=(terminal,),
        )
    assert caught.value.code == "L8_6C_ACTIVE_MEMBERSHIP_INVALID"


def test_aggregate_rejects_malformed_identity_and_mutable_queue_shape() -> None:
    """Public construction is fail-closed even outside the normal binding path."""
    for field, value, code in (
        ("tenant_id", "global", "L8_6C_TENANT_ID_INVALID"),
        ("principal_id", " principal", "L8_6C_PRINCIPAL_ID_INVALID"),
        ("deputy_id", "deputy 1", "L8_6C_DEPUTY_ID_INVALID"),
    ):
        kwargs: dict[str, Any] = {
            "tenant_id": TENANT,
            "principal_id": PRINCIPAL,
            "deputy_id": DEPUTY,
            "active_attempts": (),
        }
        kwargs[field] = value
        with pytest.raises(DeputyPersonalActiveWorkError) as caught:
            DeputyPersonalActiveWork(**kwargs)
        assert caught.value.code == code

    with pytest.raises(DeputyPersonalActiveWorkError) as caught:
        DeputyPersonalActiveWork(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            deputy_id=DEPUTY,
            active_attempts=[],  # type: ignore[arg-type]
        )
    assert caught.value.code == "L8_6C_ACTIVE_ATTEMPTS_INVALID"


def test_projection_contains_no_iam_financial_or_invented_queue_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[object] = []
    _install_sources(
        monkeypatch,
        (_model(_attempt("attempt-1")),),
        session_seen=seen,
    )
    payload = get_deputy_personal_active_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        binding_collection="binding",
        lifecycle_collection="lifecycle",
    ).to_dict()

    serialized = str(payload).casefold()
    for forbidden in (
        "permission",
        "role_id",
        "business_role",
        "authorized",
        "urgent",
        "distance",
        "gps",
        "billing",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "ai_score",
        "client_name",
    ):
        assert forbidden not in serialized

    assert PRODUCTION_VERSION == "v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK"
    assert VERSION == "v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-CERT"


# ARTIFACT: test_deputy_personal_active_work.py
# VERSION: v1.0.1-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-CERT
# AUTHORITY BOUNDARY: direct binding-scoped personal active-work projection certificate only
# TENANT POSTURE: exact tenant/principal binding and bound-deputy attempt membership
# FAIL-CLOSED POSTURE: binding/evidence/type/tenant/deputy/state drift rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
