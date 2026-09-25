"""Direct certificate for L8-8F authoritative conflict-screening orchestration.

VERSION: v1.0.0-L8-8F-LEGAL-CONFLICT-SCREENING-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_screening_orchestrator.py
AUTHORITY BOUNDARY: Durable party lookup -> screening -> persistence composition only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration import (
    legal_conflict_screening_orchestrator as orchestrator,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    LegalConflictScreeningRegistryConflictError,
    LegalConflictScreeningRegistryPersistenceUnavailableError,
    LegalConflictScreeningRegistryRetryRequiredError,
)
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    LegalMatterPartyRegistryNotFoundError,
    LegalMatterPartyRegistryPersistenceUnavailableError,
    LegalMatterPartyRegistryRetryRequiredError,
)


NOW = datetime(2026, 9, 25, 19, 0, tzinfo=timezone.utc)
FP_SUBJECT = "a" * 128
FP_EVIDENCE = "b" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def matter(matter_id: str) -> CaseMatter:
    return CaseMatter(
        tenant_id="tenant-law",
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def party(
    *,
    matter_id: str = "matter-1",
    party_id: str = "party-source",
    side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    display_name: str = "Acme Legal",
) -> LegalMatterParty:
    return register_legal_matter_party(
        matter=matter(matter_id),
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=side,
        matter_role=(
            LegalMatterPartyRole.CLIENT
            if side is LegalMatterPartySide.CLIENT_SIDE
            else LegalMatterPartyRole.RESPONDENT
        ),
        subject_reference="organization:acme",
        subject_identity_fingerprint=FP_SUBJECT,
        display_name=display_name,
        registered_at=NOW,
        source_evidence_reference=f"party-source:{party_id}",
        source_evidence_fingerprint=FP_EVIDENCE,
    )


def inputs(session: Any | None = None) -> dict[str, Any]:
    return {
        "tenant_id": "tenant-law",
        "source_party_id": "party-source",
        "screening_id": "screening-1",
        "screened_at": NOW + timedelta(minutes=1),
        "source_evidence_reference": "screening-request:1",
        "source_evidence_fingerprint": FP_EVIDENCE,
        "party_collection": object(),
        "screening_collection": object(),
        "session": session if session is not None else Session(),
    }


def install(
    monkeypatch: pytest.MonkeyPatch,
    *,
    occurrences: tuple[LegalMatterParty, ...] | None = None,
) -> tuple[LegalMatterParty, list[tuple[str, Any]]]:
    source = party()
    values = occurrences if occurrences is not None else (source,)
    calls: list[tuple[str, Any]] = []

    def get(
        tenant_id: str,
        party_id: str,
        collection: Any,
        *,
        session: Any,
    ) -> LegalMatterParty:
        del collection
        calls.append(("get", session))
        assert tenant_id == "tenant-law"
        assert party_id == source.party_id
        return source

    def find(
        tenant_id: str,
        subject_identity_fingerprint: str,
        collection: Any,
        *,
        session: Any,
    ) -> tuple[LegalMatterParty, ...]:
        del collection
        calls.append(("find", session))
        assert tenant_id == "tenant-law"
        assert subject_identity_fingerprint == FP_SUBJECT
        return values

    def persist(value: Any, collection: Any, *, session: Any) -> Any:
        del collection
        calls.append(("persist", session))
        return value

    monkeypatch.setattr(orchestrator, "get_party", get)
    monkeypatch.setattr(orchestrator, "find_subject_occurrences", find)
    monkeypatch.setattr(orchestrator, "persist_screening", persist)
    return source, calls


def test_no_match_screening_is_derived_from_registry_evidence_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = Session()
    source, calls = install(monkeypatch)
    result = orchestrator.run_legal_conflict_screening(**inputs(session))
    assert result.status is LegalConflictScreeningStatus.NO_MATCH_FOUND
    assert result.matches == ()
    assert result.subject_identity_fingerprint == source.subject_identity_fingerprint
    assert calls == [
        ("get", session),
        ("find", session),
        ("persist", session),
    ]


def test_opposing_match_is_registry_derived_review_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = party()
    matched = party(
        matter_id="matter-2",
        party_id="party-match",
        side=LegalMatterPartySide.ADVERSE_SIDE,
    )
    install(monkeypatch, occurrences=(matched, source))
    result = orchestrator.run_legal_conflict_screening(**inputs())
    assert result.status is LegalConflictScreeningStatus.REVIEW_REQUIRED
    assert len(result.matches) == 1
    assert (
        result.matches[0].match_kind
        is LegalConflictMatchKind.OPPOSING_SIDE_EXACT_SUBJECT_MATCH
    )


def test_active_transaction_is_required_before_party_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def get(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return party()

    monkeypatch.setattr(orchestrator, "get_party", get)
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorTransactionRequiredError
    ):
        orchestrator.run_legal_conflict_screening(**inputs(Session(False)))
    assert called is False


def test_missing_source_party_is_bounded_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = LegalMatterPartyRegistryNotFoundError()
    monkeypatch.setattr(
        orchestrator,
        "get_party",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorSourcePartyNotFoundError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.__cause__ is error


@pytest.mark.parametrize("stage", ("source", "occurrences"))
def test_party_registry_retry_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
) -> None:
    error = LegalMatterPartyRegistryRetryRequiredError()
    source = party()
    if stage == "source":
        monkeypatch.setattr(
            orchestrator,
            "get_party",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )
    else:
        monkeypatch.setattr(orchestrator, "get_party", lambda *_args, **_kwargs: source)
        monkeypatch.setattr(
            orchestrator,
            "find_subject_occurrences",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
        )
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorRetryRequiredError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.__cause__ is error


def test_party_registry_outage_is_authority_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = LegalMatterPartyRegistryPersistenceUnavailableError()
    monkeypatch.setattr(
        orchestrator,
        "get_party",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorAuthorityUnavailableError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.code == "L8_8F_SOURCE_PARTY_AUTHORITY_UNAVAILABLE"
    assert raised.value.__cause__ is error


def test_authoritative_occurrence_lookup_must_contain_exact_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    matched = party(matter_id="matter-2", party_id="party-match")
    install(monkeypatch, occurrences=(matched,))
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorAuthorityUnavailableError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.code == "L8_8F_SOURCE_OCCURRENCE_CORRELATION_INVALID"


def test_divergent_source_occurrence_rejects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    divergent = party(display_name="Different Name")
    install(monkeypatch, occurrences=(divergent,))
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorAuthorityUnavailableError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.code == "L8_8F_SOURCE_OCCURRENCE_CORRELATION_INVALID"


def test_screening_chronology_rejects_before_occurrence_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = party()
    called = False
    monkeypatch.setattr(orchestrator, "get_party", lambda *_args, **_kwargs: source)

    def find(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return (source,)

    monkeypatch.setattr(orchestrator, "find_subject_occurrences", find)
    payload = inputs()
    payload["screened_at"] = NOW - timedelta(seconds=1)
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorInputError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**payload)
    assert raised.value.code == "L8_8F_SCREENED_AT_INVALID"
    assert called is False


def test_screening_registry_retry_is_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install(monkeypatch)
    error = LegalConflictScreeningRegistryRetryRequiredError()
    monkeypatch.setattr(
        orchestrator,
        "persist_screening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorRetryRequiredError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.__cause__ is error


def test_screening_registry_conflict_is_not_healed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install(monkeypatch)
    error = LegalConflictScreeningRegistryConflictError()
    monkeypatch.setattr(
        orchestrator,
        "persist_screening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorConflictError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.__cause__ is error


def test_screening_registry_outage_is_authority_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install(monkeypatch)
    error = LegalConflictScreeningRegistryPersistenceUnavailableError()
    monkeypatch.setattr(
        orchestrator,
        "persist_screening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error),
    )
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorAuthorityUnavailableError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**inputs())
    assert raised.value.code == "L8_8F_SCREENING_PERSISTENCE_UNAVAILABLE"
    assert raised.value.__cause__ is error


def test_pseudo_tenant_rejects_before_party_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def get(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return party()

    monkeypatch.setattr(orchestrator, "get_party", get)
    payload = inputs()
    payload["tenant_id"] = "GLOBAL_ROOT"
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorInputError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**payload)
    assert raised.value.code == "L8_8F_TENANT_REQUIRED"
    assert called is False


def test_invalid_screening_evidence_rejects_before_party_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def get(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return party()

    monkeypatch.setattr(orchestrator, "get_party", get)
    payload = inputs()
    payload["source_evidence_fingerprint"] = "A" * 128
    with pytest.raises(
        orchestrator.LegalConflictScreeningOrchestratorInputError
    ) as raised:
        orchestrator.run_legal_conflict_screening(**payload)
    assert raised.value.code == "L8_8F_SOURCE_EVIDENCE_FINGERPRINT_INVALID"
    assert called is False


def test_public_api_excludes_caller_match_and_clearance_authority() -> None:
    parameters = set(
        inspect.signature(orchestrator.run_legal_conflict_screening).parameters
    )
    assert {
        "tenant_id",
        "source_party_id",
        "screening_id",
        "screened_at",
        "source_evidence_reference",
        "source_evidence_fingerprint",
        "party_collection",
        "screening_collection",
        "session",
    } == parameters
    forbidden = {
        "subject_identity_fingerprint",
        "occurrences",
        "matches",
        "match_kind",
        "status",
        "conflict",
        "conflict_found",
        "clear",
        "clearance",
        "waiver",
        "resolution",
        "accept_client",
        "authorize_representation",
    }
    assert parameters.isdisjoint(forbidden)


# ARTIFACT: test_legal_conflict_screening_orchestrator.py
# VERSION: v1.0.0-L8-8F-LEGAL-CONFLICT-SCREENING-ORCHESTRATOR-CERT
# AUTHORITY BOUNDARY: durable party lookup/screening/persistence composition evidence only
# TENANT POSTURE: subject fingerprint and occurrences are registry-derived, never caller supplied
# FAIL-CLOSED POSTURE: missing/incomplete/divergent/raced/conflicting authority rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
