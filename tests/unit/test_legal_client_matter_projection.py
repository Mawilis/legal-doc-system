"""Direct certificate for bounded Legal client matter projection.

TITLE: WILSY OS Legal Client Matter Projection Certificate
VERSION: v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-CERT
AUTHORITY: Direct adversarial certification of D5 projection composition only.
EPITOME: Prove active-transaction precedence, exact D4 authorization gating,
         ACTIVE visibility-only matter membership, current P1 CaseMatter
         projection, deterministic ordering, safe field whitelisting, session
         propagation, empty visibility, and whole-result failure on corruption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_projection.py
COLLABORATION / OWNERSHIP: D4 IAM, L8-7B visibility and L8-5/P1 matter truth
                            remain independent canonical authorities; this
                            certificate proves only their sanitized D5 composition.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-CERT establishes
           exact authorized projection, empty-visible-set behavior, current
           OPEN->CLOSED reflection, deterministic ordering, session propagation,
           IAM short-circuit, visibility corruption/outage, bound-matter absence,
           public-constructor invariants and exact serialized-field exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque matter data only.
TENANT BOUNDARY: Exact tenant/principal scope across all projection seams.
AUTHORITY BOUNDARY: Projection certificate only; no HTTP or mutation authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Fake caller-owned active session marker only.
FAIL-CLOSED DECLARATION: Denied IAM, visibility or bound-matter failure rejects
                         without broad/partial fallback.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.legal_operations.domain.legal_client_matter_projection as projection
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_projection import (
    OPERATION,
    PERMISSION,
    SCHEMA,
    VERSION as PRODUCTION_VERSION,
    VISIBILITY,
    LegalClientMatterProjection,
    LegalClientMatterProjectionError,
    LegalClientMatterProjectionSet,
    LegalClientMatterProjectionTransactionRequiredError,
    get_legal_client_matter_projection,
)
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsEntityReadModel,
    LegalOperationsReadModelError,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    LegalClientMatterVisibilityPersistedRecordInvalidError,
    LegalClientMatterVisibilityRegistryError,
)


VERSION = "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-CERT"
NOW = datetime(2026, 9, 23, 21, 0, tzinfo=timezone.utc)
TENANT = "tenant-d5"
PRINCIPAL = "principal-client"


class FakeSession:
    """Caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def _matter(
    matter_id: str,
    *,
    reference: str | None = None,
) -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=matter_id,
        matter_reference=reference or f"CLIENT-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-evidence-{matter_id}",
    )


def _binding(
    matter: CaseMatter,
) -> LegalClientMatterVisibilityBinding:
    return LegalClientMatterVisibilityBinding.grant(
        client_principal_id=PRINCIPAL,
        case_matter=matter,
        granted_by_principal_id="principal-partner",
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference=f"visibility-{matter.case_matter_id}",
    )


def _model(current: CaseMatter) -> LegalOperationsEntityReadModel:
    opened = _matter(
        current.case_matter_id,
        reference=current.matter_reference,
    )
    history = (
        (opened,)
        if current.state is CaseMatterState.OPEN
        else (opened, current)
    )
    return LegalOperationsEntityReadModel(
        tenant_id=TENANT,
        entity_type="CaseMatter",
        entity_identity=current.case_matter_id,
        current=current,
        history=history,
    )


def _authorized() -> TenantAuthorizationDecision:
    return TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_client",
        "LEGAL_CLIENT",
    )


def _install(
    monkeypatch: pytest.MonkeyPatch,
    *,
    bindings: tuple[LegalClientMatterVisibilityBinding, ...],
    models: dict[str, LegalOperationsEntityReadModel],
    decision: TenantAuthorizationDecision | None = None,
    session_seen: list[object] | None = None,
) -> list[object]:
    seen = session_seen if session_seen is not None else []

    def authorize(**kwargs: object) -> TenantAuthorizationDecision:
        assert kwargs["tenant_id"] == TENANT
        assert kwargs["principal_id"] == PRINCIPAL
        assert kwargs["permission_id"] == PERMISSION
        assert kwargs["operation"] == OPERATION
        seen.append(kwargs["session"])
        return decision or _authorized()

    def list_active(
        tenant_id: str,
        principal_id: str,
        _collection: object,
        *,
        session: object = None,
    ) -> tuple[LegalClientMatterVisibilityBinding, ...]:
        assert tenant_id == TENANT
        assert principal_id == PRINCIPAL
        seen.append(session)
        return bindings

    def read_model(
        *,
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        lifecycle_collection: object,
        session: object = None,
    ) -> LegalOperationsEntityReadModel:
        assert tenant_id == TENANT
        assert entity_type == "CaseMatter"
        assert lifecycle_collection == "lifecycle"
        seen.append(session)
        if entity_identity not in models:
            raise LegalOperationsReadModelError("L8_5_ENTITY_NOT_FOUND")
        return models[entity_identity]

    monkeypatch.setattr(projection, "authorize_tenant_operation", authorize)
    monkeypatch.setattr(
        projection.LegalClientMatterVisibilityRegistry,
        "list_active_for_principal",
        staticmethod(list_active),
    )
    monkeypatch.setattr(projection, "get_entity_read_model", read_model)
    return seen


def _project(
    session: FakeSession,
) -> LegalClientMatterProjectionSet:
    return get_legal_client_matter_projection(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        visibility_collection="visibility",
        lifecycle_collection="lifecycle",
        principal_repository=SimpleNamespace(),
        membership_repository=SimpleNamespace(),
        business_role_repository=SimpleNamespace(),
        role_assignment_repository=SimpleNamespace(),
        session=session,
    )


def test_exact_active_visibility_projects_current_matters_and_same_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only explicit bindings become sorted safe cards under one transaction."""
    matter_b = _matter("matter-b")
    matter_a = _matter("matter-a")
    session = FakeSession()
    seen = _install(
        monkeypatch,
        bindings=(_binding(matter_b), _binding(matter_a)),
        models={
            "matter-a": _model(matter_a),
            "matter-b": _model(matter_b),
        },
    )

    result = _project(session)

    assert result.tenant_id == TENANT
    assert [value.case_matter_id for value in result.matters] == [
        "matter-a",
        "matter-b",
    ]
    assert seen == [session, session, session, session]
    assert result.to_dict() == {
        "schema": SCHEMA,
        "version": PRODUCTION_VERSION,
        "tenant_id": TENANT,
        "visibility": VISIBILITY,
        "matters": [
            {
                "case_matter_id": "matter-a",
                "matter_reference": "CLIENT-matter-a",
                "opened_at": NOW.isoformat(),
                "state": "OPEN",
            },
            {
                "case_matter_id": "matter-b",
                "matter_reference": "CLIENT-matter-b",
                "opened_at": NOW.isoformat(),
                "state": "OPEN",
            },
        ],
    }


def test_authorized_client_with_no_active_visibility_gets_empty_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = _install(monkeypatch, bindings=(), models={})
    result = _project(FakeSession())

    assert result.matters == ()
    assert result.to_dict()["matters"] == []
    assert len(seen) == 2


def test_visibility_relation_tracks_identity_while_current_matter_can_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Grant-time provenance does not pin the client to a stale OPEN snapshot."""
    opened = _matter("matter-close")
    binding = _binding(opened)
    closed = opened.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close-evidence",
        occurred_at=NOW + timedelta(hours=1),
    )
    assert closed.fingerprint != binding.source_case_matter_fingerprint

    _install(
        monkeypatch,
        bindings=(binding,),
        models={"matter-close": _model(closed)},
    )
    result = _project(FakeSession())

    assert result.matters[0].case_matter_id == "matter-close"
    assert result.matters[0].state is CaseMatterState.CLOSED
    assert result.to_dict()["matters"] == [
        {
            "case_matter_id": "matter-close",
            "matter_reference": "CLIENT-matter-close",
            "opened_at": NOW.isoformat(),
            "state": "CLOSED",
        }
    ]


def test_inactive_transaction_rejects_before_iam_or_visibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        projection,
        "authorize_tenant_operation",
        lambda **_kwargs: calls.append("iam") or _authorized(),
    )
    monkeypatch.setattr(
        projection.LegalClientMatterVisibilityRegistry,
        "list_active_for_principal",
        staticmethod(lambda *_args, **_kwargs: calls.append("visibility") or ()),
    )

    with pytest.raises(
        LegalClientMatterProjectionTransactionRequiredError
    ) as caught:
        _project(FakeSession(False))

    assert caught.value.code == "L8_7D5_ACTIVE_TRANSACTION_REQUIRED"
    assert calls == []


def test_denied_iam_short_circuits_visibility_and_matter_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    visibility_calls: list[str] = []
    denied = TenantAuthorizationDecision(
        False,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        "tenant_legal_client",
    )
    _install(
        monkeypatch,
        bindings=(),
        models={},
        decision=denied,
    )
    monkeypatch.setattr(
        projection.LegalClientMatterVisibilityRegistry,
        "list_active_for_principal",
        staticmethod(
            lambda *_args, **_kwargs: visibility_calls.append("called") or ()
        ),
    )

    with pytest.raises(LegalClientMatterProjectionError) as caught:
        _project(FakeSession())

    assert caught.value.code == (
        "L8_7D5_CLIENT_AUTHORIZATION_DENIED_ROLE_ASSIGNMENT_INACTIVE"
    )
    assert visibility_calls == []


@pytest.mark.parametrize(
    ("error", "code"),
    (
        (
            LegalClientMatterVisibilityPersistedRecordInvalidError(
                "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID"
            ),
            "L8_7D5_VISIBILITY_EVIDENCE_INVALID",
        ),
        (
            LegalClientMatterVisibilityRegistryError(
                "L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE"
            ),
            "L8_7D5_VISIBILITY_EVIDENCE_UNAVAILABLE",
        ),
    ),
)
def test_visibility_failure_is_bounded_without_matter_fallback(
    monkeypatch: pytest.MonkeyPatch,
    error: LegalClientMatterVisibilityRegistryError,
    code: str,
) -> None:
    matter_reads: list[str] = []

    monkeypatch.setattr(
        projection,
        "authorize_tenant_operation",
        lambda **_kwargs: _authorized(),
    )
    monkeypatch.setattr(
        projection.LegalClientMatterVisibilityRegistry,
        "list_active_for_principal",
        staticmethod(
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error)
        ),
    )
    monkeypatch.setattr(
        projection,
        "get_entity_read_model",
        lambda **_kwargs: matter_reads.append("called"),
    )

    with pytest.raises(LegalClientMatterProjectionError) as caught:
        _project(FakeSession())

    assert caught.value.code == code
    assert matter_reads == []


def test_missing_bound_matter_rejects_whole_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _matter("matter-present")
    missing = _matter("matter-missing")
    _install(
        monkeypatch,
        bindings=(_binding(first), _binding(missing)),
        models={"matter-present": _model(first)},
    )

    with pytest.raises(LegalClientMatterProjectionError) as caught:
        _project(FakeSession())

    assert caught.value.code == "L8_7D5_BOUND_MATTER_NOT_FOUND"


def test_public_projection_constructor_is_immutable_and_exactly_whitelisted() -> None:
    value = LegalClientMatterProjection(
        case_matter_id="matter-public",
        matter_reference="CLIENT-PUBLIC",
        opened_at=NOW,
        state=CaseMatterState.OPEN,
    )
    assert value.to_dict() == {
        "case_matter_id": "matter-public",
        "matter_reference": "CLIENT-PUBLIC",
        "opened_at": NOW.isoformat(),
        "state": "OPEN",
    }

    aggregate = LegalClientMatterProjectionSet(
        tenant_id=TENANT,
        matters=(value,),
    )
    payload = aggregate.to_dict()
    forbidden = {
        "client_principal_id",
        "principal_id",
        "evidence_reference",
        "fingerprint",
        "transition_history",
        "instruction_id",
        "document_id",
        "deputy_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
        "authorized",
        "business_role",
        "authorization_role",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(payload["matters"][0])

    with pytest.raises(Exception):
        value.state = CaseMatterState.CLOSED  # type: ignore[misc]


def test_aggregate_rejects_mutable_unsorted_or_duplicate_shapes() -> None:
    first = LegalClientMatterProjection(
        "matter-a",
        "CLIENT-A",
        NOW,
        CaseMatterState.OPEN,
    )
    second = LegalClientMatterProjection(
        "matter-b",
        "CLIENT-B",
        NOW,
        CaseMatterState.OPEN,
    )

    with pytest.raises(LegalClientMatterProjectionError) as mutable:
        LegalClientMatterProjectionSet(
            tenant_id=TENANT,
            matters=[first],  # type: ignore[arg-type]
        )
    assert mutable.value.code == "L8_7D5_MATTERS_INVALID"

    with pytest.raises(LegalClientMatterProjectionError) as unordered:
        LegalClientMatterProjectionSet(
            tenant_id=TENANT,
            matters=(second, first),
        )
    assert unordered.value.code == "L8_7D5_MATTER_ORDER_INVALID"

    with pytest.raises(LegalClientMatterProjectionError) as duplicate:
        LegalClientMatterProjectionSet(
            tenant_id=TENANT,
            matters=(first, first),
        )
    assert duplicate.value.code == "L8_7D5_DUPLICATE_MATTER_INVALID"


def test_contract_constants_are_exact_and_nonfinancial() -> None:
    assert VERSION == "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-CERT"
    assert PRODUCTION_VERSION == "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1"
    assert PERMISSION == "legal_operations:client_matter:read"
    assert OPERATION == "legal_client_matter_read"
    assert VISIBILITY == "LEGAL_CLIENT_EXPLICIT_MATTERS"


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_projection.py
# VERSION: v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-CERT
# AUTHORITY BOUNDARY: direct D5 IAM+visibility+current-matter sanitized projection certificate only
# TENANT POSTURE: exact tenant/principal and same active caller session across every projection seam
# FAIL-CLOSED POSTURE: denied IAM, visibility failure, missing bound matter or malformed aggregate rejects whole projection
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
