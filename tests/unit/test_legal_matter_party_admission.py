"""Direct certificate for L8-8C legal matter-party admission orchestration.

VERSION: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_party_admission.py
AUTHORITY BOUNDARY: Admission composition evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration import legal_matter_party_admission as admission
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    LegalMatterPartyRegistryConflictError,
    LegalMatterPartyRegistryRetryRequiredError,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistryError,
)


NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def matter() -> CaseMatter:
    return CaseMatter(
        tenant_id="tenant-law",
        case_matter_id="matter-1",
        matter_reference="MAT-001",
        opened_at=NOW,
        evidence_reference="intake:1",
    )


def kwargs(session: Any = None) -> dict[str, Any]:
    return {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "party_id": "party-1",
        "party_kind": LegalMatterPartyKind.ORGANIZATION,
        "party_side": LegalMatterPartySide.CLIENT_SIDE,
        "matter_role": LegalMatterPartyRole.CLIENT,
        "subject_reference": "organization:acme",
        "subject_identity_fingerprint": FP_A,
        "display_name": "Acme Legal",
        "registered_at": NOW + timedelta(minutes=1),
        "source_evidence_reference": "party-source:1",
        "source_evidence_fingerprint": FP_B,
        "lifecycle_collection": object(),
        "party_collection": object(),
        "session": session if session is not None else Session(),
    }


def install_happy(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, Any]]:
    calls: list[tuple[str, Any]] = []
    source = matter()

    def history(
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        collection: Any,
        *,
        session: Any,
    ) -> tuple[CaseMatter, ...]:
        del collection
        calls.append(("history", session))
        assert tenant_id == source.tenant_id
        assert entity_type == "CaseMatter"
        assert entity_identity == source.case_matter_id
        return (source,)

    def project(values: Any, *, expected_type: type[Any] | None = None) -> CaseMatter:
        calls.append(("projection", tuple(values)))
        assert expected_type is CaseMatter
        return source

    def persist(value: Any, collection: Any, *, session: Any) -> Any:
        del collection
        calls.append(("persist", session))
        assert value.matter_fingerprint == source.fingerprint
        assert value.tenant_id == source.tenant_id
        assert value.case_matter_id == source.case_matter_id
        return value

    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        history,
    )
    monkeypatch.setattr(admission, "resolve_current_lifecycle_snapshot", project)
    monkeypatch.setattr(admission, "persist_party", persist)
    return calls


def test_valid_admission_derives_current_matter_and_propagates_one_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = Session()
    calls = install_happy(monkeypatch)
    result = admission.admit_legal_matter_party(**kwargs(session))
    assert result.matter == matter()
    assert result.party.matter_fingerprint == result.matter.fingerprint
    assert result.party.party_id == "party-1"
    assert calls[0] == ("history", session)
    assert calls[-1] == ("persist", session)


def test_active_transaction_required_before_any_durable_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def history(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return ()

    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        history,
    )
    with pytest.raises(
        admission.LegalMatterPartyAdmissionTransactionRequiredError
    ):
        admission.admit_legal_matter_party(**kwargs(Session(False)))
    assert called is False


def test_missing_exact_matter_fails_before_party_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    persisted = False
    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        lambda *_args, **_kwargs: (),
    )

    def persist(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal persisted
        persisted = True
        raise AssertionError("must not persist")

    monkeypatch.setattr(admission, "persist_party", persist)
    with pytest.raises(admission.LegalMatterPartyAdmissionMatterNotFoundError):
        admission.admit_legal_matter_party(**kwargs())
    assert persisted is False


def test_current_closed_matter_cannot_admit_party(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initial = matter()
    closed = initial.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="closure:1",
        occurred_at=NOW + timedelta(hours=1),
    )
    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        lambda *_args, **_kwargs: (initial, closed),
    )
    monkeypatch.setattr(
        admission,
        "resolve_current_lifecycle_snapshot",
        lambda *_args, **_kwargs: closed,
    )
    with pytest.raises(admission.LegalMatterPartyAdmissionMatterNotOpenError):
        admission.admit_legal_matter_party(**kwargs())


def test_current_projection_ambiguity_is_authority_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        lambda *_args, **_kwargs: (matter(),),
    )
    error = LegalOperationsCurrentProjectionError(
        "L8_0_CURRENT_SNAPSHOT_AMBIGUOUS"
    )
    monkeypatch.setattr(
        admission,
        "resolve_current_lifecycle_snapshot",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        admission.LegalMatterPartyAdmissionAuthorityUnavailableError
    ) as raised:
        admission.admit_legal_matter_party(**kwargs())
    assert raised.value.code == "L8_8C_CASE_MATTER_CURRENTNESS_INVALID"
    assert raised.value.__cause__ is error


def test_p2_whole_transaction_retry_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = LegalOperationsLifecycleRegistryError(
        "M2_RETRY_TRANSACTION_REQUIRED"
    )
    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        admission.LegalMatterPartyAdmissionRetryRequiredError
    ) as raised:
        admission.admit_legal_matter_party(**kwargs())
    assert raised.value.code == "L8_8C_WHOLE_TRANSACTION_RETRY_REQUIRED"
    assert raised.value.__cause__ is error


def test_l8_8b_whole_transaction_retry_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_happy(monkeypatch)
    error = LegalMatterPartyRegistryRetryRequiredError()
    monkeypatch.setattr(
        admission,
        "persist_party",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        admission.LegalMatterPartyAdmissionRetryRequiredError
    ) as raised:
        admission.admit_legal_matter_party(**kwargs())
    assert raised.value.__cause__ is error


def test_party_registry_conflict_is_not_healed_or_overwritten(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_happy(monkeypatch)
    error = LegalMatterPartyRegistryConflictError()
    monkeypatch.setattr(
        admission,
        "persist_party",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(admission.LegalMatterPartyAdmissionConflictError) as raised:
        admission.admit_legal_matter_party(**kwargs())
    assert raised.value.__cause__ is error


@pytest.mark.parametrize(
    "registered_at",
    [
        NOW - timedelta(microseconds=1),
        datetime(2026, 9, 25, 12, 1),
    ],
)
def test_party_registration_chronology_rejects_before_persistence(
    monkeypatch: pytest.MonkeyPatch,
    registered_at: datetime,
) -> None:
    install_happy(monkeypatch)
    persisted = False

    def persist(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal persisted
        persisted = True
        raise AssertionError("must not persist")

    monkeypatch.setattr(admission, "persist_party", persist)
    inputs = kwargs()
    inputs["registered_at"] = registered_at
    with pytest.raises(admission.LegalMatterPartyAdmissionInputError) as raised:
        admission.admit_legal_matter_party(**inputs)
    assert raised.value.code == "L8_8C_REGISTERED_AT_INVALID"
    assert persisted is False


def test_pseudo_tenant_rejects_before_history_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def history(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return ()

    monkeypatch.setattr(
        admission.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        history,
    )
    inputs = kwargs()
    inputs["tenant_id"] = "GLOBAL_ROOT"
    with pytest.raises(admission.LegalMatterPartyAdmissionInputError) as raised:
        admission.admit_legal_matter_party(**inputs)
    assert raised.value.code == "L8_8C_TENANT_REQUIRED"
    assert called is False


def test_public_api_does_not_accept_caller_matter_currentness_or_fingerprint() -> None:
    parameters = set(
        inspect.signature(admission.admit_legal_matter_party).parameters
    )
    assert "tenant_id" in parameters
    assert "case_matter_id" in parameters
    assert "matter_fingerprint" not in parameters
    assert "matter_state" not in parameters
    assert "current" not in parameters
    assert "is_current" not in parameters


def test_result_rejects_party_not_bound_to_exact_current_matter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_happy(monkeypatch)
    result = admission.admit_legal_matter_party(**kwargs())
    assert calls
    other = CaseMatter(
        tenant_id="tenant-law",
        case_matter_id="matter-2",
        matter_reference="MAT-002",
        opened_at=NOW,
        evidence_reference="intake:2",
    )
    with pytest.raises(
        admission.LegalMatterPartyAdmissionAuthorityUnavailableError
    ) as raised:
        admission.LegalMatterPartyAdmissionResult(
            matter=other,
            party=result.party,
        )
    assert raised.value.code == "L8_8C_RESULT_CORRELATION_INVALID"


# ARTIFACT: test_legal_matter_party_admission.py
# VERSION: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION-CERT
# AUTHORITY BOUNDARY: deterministic admission-composition evidence only
# TENANT POSTURE: durable current matter is server-derived under the caller transaction
# FAIL-CLOSED POSTURE: missing/closed/ambiguous/raced/conflicting/stale evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
