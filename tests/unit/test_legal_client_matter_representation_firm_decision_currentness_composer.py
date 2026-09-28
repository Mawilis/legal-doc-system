"""Direct certificate for the L9C11-P22 read-only composer.

TITLE: WILSY OS Legal Firm Representation Decision Currentness Composer Certificate
VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove one exact P9 history read, caller-session propagation, explicit
         evaluation time and pure P22 delegation with zero writes or lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_firm_decision_currentness_composer.py
COLLABORATION / OWNERSHIP: P9 and P2 remain read-only precedents. This test
                            exercises only the P22 composer adapter.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Synthetic registry seam; no Mongo, network or writes.
FAIL-CLOSED DECLARATION: Invalid scope, inactive sessions and registry errors
                         reject without starting or mutating a transaction.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    VERSION as DOMAIN_VERSION,
    LegalClientMatterRepresentationFirmDecisionCurrentnessState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_currentness_composer import (
    VERSION,
    LegalClientMatterRepresentationFirmDecisionCurrentnessComposer,
    LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError,
    compose_currentness,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_representation_firm_decision_currentness_composer as composer_module,
)


BASE = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
TENANT = "tenant-l9c11-p22"
MATTER = "matter-l9c11-p22"
PARTY = "party-l9c11-p22"
SUBJECT = "b" * 128
MATTER_FP = "a" * 128


class Session:
    """Minimal active caller-owned transaction seam."""

    def __init__(self, active: bool = True) -> None:
        self.active = active

    def in_transaction(self) -> bool:
        return self.active


class Collection:
    """Opaque collection seam proving composer does not write it."""


_UNSET = object()


def authority() -> LegalClientMatterRepresentationAuthority:
    return LegalClientMatterRepresentationAuthority(
        authority_id="authority-l9c11-p22",
        tenant_id=TENANT,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_reference="client:subject-p22",
        subject_identity_fingerprint=SUBJECT,
        engagement_id="engagement-l9c11-p22",
        engagement_fingerprint="c" * 128,
        mandate_id="mandate-l9c11-p22",
        mandate_fingerprint="d" * 128,
        mandate_scope_reference="scope:p22",
        mandate_scope_fingerprint="e" * 128,
        mandate_capabilities=("ADVISORY",),
        acting_capacity_id="capacity-p22",
        acting_capacity_fingerprint="f" * 128,
        representative_principal_id="principal-p22",
        representative_role="LEGAL_PRACTITIONER",
        representation_scope_capabilities=("ADVISORY",),
        decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        appointing_principal_id="client-principal-p22",
        source_evidence_reference="source:appointment-p22",
        source_evidence_fingerprint="1" * 128,
        authorization_evidence_reference="authorization:appointment-p22",
        authorization_evidence_fingerprint="2" * 128,
        occurred_at=BASE,
        effective_from=BASE,
        effective_until=BASE + timedelta(days=30),
        idempotency_key="idempotency:appointment-p22",
    )


def decision(value: str = "ACCEPTED", suffix: str = "one", effective: datetime = BASE) -> LegalClientMatterRepresentationFirmDecision:
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority(),
        decision=value,
        decision_actor_principal_id=f"firm-principal-{suffix}",
        authorization_evidence_reference=f"authorization:firm-{suffix}",
        authorization_evidence_fingerprint="3" * 128,
        source_evidence_reference=f"source:firm-{suffix}",
        source_evidence_fingerprint="4" * 128,
        occurred_at=effective,
        effective_from=effective,
        idempotency_key=f"idempotency:firm-{suffix}",
    )


def _args(at: datetime = BASE + timedelta(hours=1), session: Any = _UNSET) -> dict[str, object]:
    return {
        "tenant_id": TENANT,
        "case_matter_id": MATTER,
        "matter_fingerprint": MATTER_FP,
        "client_party_id": PARTY,
        "subject_identity_fingerprint": SUBJECT,
        "representation_authority_id": authority().authority_id,
        "representation_authority_fingerprint": authority().fingerprint,
        "representative_principal_id": "principal-p22",
        "representative_role": "LEGAL_PRACTITIONER",
        "evaluated_at": at,
        "session": Session() if session is _UNSET else session,
    }


def run_compose(monkeypatch: pytest.MonkeyPatch, history: tuple[Any, ...], *, at: datetime = BASE + timedelta(hours=1), session: Any = _UNSET) -> tuple[Any, list[tuple[tuple[Any, ...], dict[str, Any]]]]:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        calls.append((args, kwargs))
        return history

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", fake)
    composer = LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=Collection())
    result = composer.compose_currentness(**cast(Any, _args(at, session)))
    return result, calls


def test_versions_and_explicit_composer_type() -> None:
    assert VERSION == "v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-COMPOSER"
    assert DOMAIN_VERSION == "v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS"
    assert LegalClientMatterRepresentationFirmDecisionCurrentnessComposer is not None


def test_one_p9_read_exact_lineage_and_same_session(monkeypatch: pytest.MonkeyPatch) -> None:
    session = Session()
    result, calls = run_compose(monkeypatch, (decision(),), session=session)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[:8] == (TENANT, MATTER, MATTER_FP, PARTY, SUBJECT, authority().authority_id, authority().fingerprint, "principal-p22")
    assert kwargs["session"] is session


def test_explicit_evaluated_at_excludes_future_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _ = run_compose(monkeypatch, (decision(effective=BASE + timedelta(days=1)),), at=BASE)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION


@pytest.mark.parametrize("value,expected", [("ACCEPTED", "ACCEPTED"), ("DECLINED", "DECLINED"), ("REQUIRES_REVIEW", "REQUIRES_REVIEW")])
def test_single_states_delegate_to_p22(monkeypatch: pytest.MonkeyPatch, value: str, expected: str) -> None:
    result, _ = run_compose(monkeypatch, (decision(value),))
    assert result.state.value == expected


def test_empty_history_is_no_decision(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _ = run_compose(monkeypatch, ())
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION


def test_ambiguous_and_corrupt_history_delegate(monkeypatch: pytest.MonkeyPatch) -> None:
    ambiguous, calls = run_compose(monkeypatch, (decision(suffix="a"), decision(value="DECLINED", suffix="b")))
    assert ambiguous.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS
    assert len(calls) == 1
    corrupt, _ = run_compose(monkeypatch, (cast(Any, object()),))
    assert corrupt.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


@pytest.mark.parametrize("session", [None, Session(active=False)])
def test_missing_or_inactive_transaction_rejected(monkeypatch: pytest.MonkeyPatch, session: Any) -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as error:
        run_compose(monkeypatch, (), session=session)
    assert error.value.code == "L9C11_P22_COMPOSER_ACTIVE_TRANSACTION_REQUIRED"


def test_invalid_evaluation_time_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as error:
        run_compose(monkeypatch, (), at=datetime(2026, 9, 28, 10, 0))
    assert error.value.code.endswith("EVALUATED_AT_INVALID")


def test_registry_failure_is_mapped_without_write(monkeypatch: pytest.MonkeyPatch) -> None:
    class RegistryFailure(composer_module.decision_registry.LegalClientMatterRepresentationFirmDecisionRegistryError):
        def __init__(self) -> None:
            super().__init__("P9_FAILURE")

    def fail(*args: Any, **kwargs: Any) -> Any:
        raise RegistryFailure()

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", fail)
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as error:
        LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=Collection()).compose_currentness(**cast(Any, _args()))
    assert error.value.code == "L9C11_P22_COMPOSER_HISTORY_READ_FAILED"


def test_collection_is_required() -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as error:
        LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=None)
    assert error.value.code.endswith("COLLECTION_REQUIRED")


def test_missing_session_causes_zero_registry_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []
    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", lambda *a, **k: calls.append(1))
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError):
        LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=Collection()).compose_currentness(**cast(Any, _args(session=None)))
    assert calls == []


def test_functional_boundary_matches_class(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        calls.append(1)
        return (decision(),)

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", fake)
    result = compose_currentness(decision_collection=Collection(), **cast(Any, _args()))
    assert result.is_currently_accepted is True
    assert calls == [1]


@pytest.mark.parametrize("forbidden", ["insert_one", "update_one", "delete_one", "start_transaction", ".commit(", ".abort(", "MongoClient", "RepresentationFormation"])
def test_forbidden_mutation_or_downstream_surface_is_absent(forbidden: str) -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_representation_firm_decision_currentness_composer.py").read_text()
    assert forbidden not in source


def test_explicit_evaluation_time_is_forwarded_to_projection(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[datetime] = []

    def fake_read(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        return ()

    original = composer_module.project_legal_client_matter_representation_firm_decision_currentness

    def capture(**kwargs: Any) -> Any:
        captured.append(kwargs["evaluated_at"])
        return original(**kwargs)

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", fake_read)
    monkeypatch.setattr(composer_module, "project_legal_client_matter_representation_firm_decision_currentness", capture)
    supplied = BASE + timedelta(minutes=7)
    run_compose(monkeypatch, (), at=supplied)
    assert captured == [supplied]


def test_role_and_p1_authority_are_not_dropped_from_public_call_shape() -> None:
    signature = __import__("inspect").signature(LegalClientMatterRepresentationFirmDecisionCurrentnessComposer.compose_currentness)
    names = tuple(signature.parameters)
    assert "representation_authority_id" in names
    assert "representation_authority_fingerprint" in names
    assert "representative_principal_id" in names
    assert "representative_role" in names


def test_source_has_no_transaction_lifecycle_or_downstream_surfaces() -> None:
    path = Path("tools/eos/legal_operations/orchestration/legal_client_matter_representation_firm_decision_currentness_composer.py")
    source = path.read_text()
    tree = ast.parse(source)
    assert not {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} & {"MongoClient", "start_transaction"}
    assert ".commit(" not in source
    assert ".abort(" not in source
    assert "insert_one" not in source
    assert "update_one" not in source
    assert "RepresentationFormation" not in source
    assert "Court" in source


def test_role_is_validated_after_p9_read_without_merging_role_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def fake(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        calls.append(1)
        return (decision(),)

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", fake)
    args = _args(); args["representative_role"] = "OTHER_ROLE"
    result = LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=Collection()).compose_currentness(**cast(Any, args))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED
    assert calls == [1]


def test_composer_has_no_clock_reads_or_network_ui_finance() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_representation_firm_decision_currentness_composer.py").read_text()
    assert "datetime.now" not in source
    assert "MongoClient" not in source
    assert "HTTP" not in source
    assert "financial" in source.lower()


# ARTIFACT: test_legal_client_matter_representation_firm_decision_currentness_composer.py
# VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct read-only P22 composer certificate only
# TENANT POSTURE: exact P9 lineage and caller-session propagation
# FAIL-CLOSED POSTURE: no transaction lifecycle or persistence mutation
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
