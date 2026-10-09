"""Direct certificate for the L9C11-P21A currentness composer.

TITLE: WILSY OS Legal Client Representation Authority Currentness Composer Certificate
VERSION: v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify one exact P7 history read, caller-session propagation,
         explicit evaluation-time propagation and unchanged pure P21A
         delegation without writes or transaction lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authority_currentness_composer.py
COLLABORATION / OWNERSHIP: P1 authority and P7 registry are read-only
                            precedents. This certificate covers only the P21A
                            composer seam and introduces no IAM, firm decision,
                            Representation, Court or financial authority.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Recording fakes only; no Mongo or network access.
FAIL-CLOSED DECLARATION: Missing transactions, registry failures and
                         projection failures never become a positive result.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentnessState,
    project_legal_client_matter_representation_authority_currentness,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_representation_authority_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import (
    VERSION,
    LegalClientMatterRepresentationAuthorityCurrentnessComposer,
    LegalClientMatterRepresentationAuthorityCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_authority_registry as authority_registry,
)


BASE = datetime(2026, 9, 28, 10, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9c11-p21a-composer"
MATTER = "matter-l9c11-p21a-composer"
PARTY = "party-l9c11-p21a-composer"
SUBJECT = "b" * 128
MATTER_FP = "a" * 128
REPRESENTATIVE = "principal-l9c11-p21a-composer"


def authority(
    *,
    authority_id: str = "authority-l9c11-p21a-composer-1",
    decision: str = "APPOINTED",
    effective_from: datetime = BASE,
) -> LegalClientMatterRepresentationAuthority:
    """Build valid immutable P1 evidence for the exact composer lineage."""
    return LegalClientMatterRepresentationAuthority(
        authority_id=authority_id,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_reference="client:subject-l9c11-p21a-composer",
        subject_identity_fingerprint=SUBJECT,
        engagement_id="engagement-l9c11-p21a-composer",
        engagement_fingerprint="c" * 128,
        mandate_id="mandate-l9c11-p21a-composer",
        mandate_fingerprint="d" * 128,
        mandate_scope_reference="scope:l9c11:p21a:composer",
        mandate_scope_fingerprint="e" * 128,
        mandate_capabilities=("ADVISORY", "NEGOTIATION"),
        acting_capacity_id="capacity-l9c11-p21a-composer",
        acting_capacity_fingerprint="f" * 128,
        representative_principal_id=REPRESENTATIVE,
        representative_role="LEGAL_PRACTITIONER",
        representation_scope_capabilities=("ADVISORY",),
        decision=decision,
        appointing_principal_id="principal-client-l9c11-p21a-composer",
        source_evidence_reference=f"source:{authority_id}",
        source_evidence_fingerprint="1" * 128,
        authorization_evidence_reference=f"authorization:{authority_id}",
        authorization_evidence_fingerprint="2" * 128,
        occurred_at=effective_from,
        effective_from=effective_from,
        effective_until=effective_from + timedelta(days=30),
        idempotency_key=f"idempotency:{authority_id}",
    )


class RecordingSession:
    """Active caller-owned transaction with lifecycle counters."""

    in_transaction = True

    def __init__(self) -> None:
        self.starts = 0
        self.commits = 0
        self.aborts = 0

    def start_transaction(self) -> None:
        self.starts += 1

    def commit_transaction(self) -> None:
        self.commits += 1

    def abort_transaction(self) -> None:
        self.aborts += 1


def build_composer(
    monkeypatch: pytest.MonkeyPatch,
    history: tuple[Any, ...] = (),
) -> tuple[LegalClientMatterRepresentationAuthorityCurrentnessComposer, list[tuple[tuple[Any, ...], dict[str, Any]]]]:
    """Install one recording P7 seam and return the call log."""
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def read(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        calls.append((args, kwargs))
        return history

    monkeypatch.setattr(composer_module.authority_registry, "list_representation_authorities_for_context", read)
    return LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=object()), calls


def compose(
    composer: LegalClientMatterRepresentationAuthorityCurrentnessComposer,
    session: Any,
    **changes: Any,
) -> Any:
    """Invoke the composer with the exact P7 lineage."""
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "case_matter_id": MATTER,
        "matter_fingerprint": MATTER_FP,
        "client_party_id": PARTY,
        "subject_identity_fingerprint": SUBJECT,
        "representative_principal_id": REPRESENTATIVE,
        "evaluated_at": BASE + timedelta(hours=1),
    }
    values.update(changes)
    return composer.compose_currentness(**values, session=session)


def test_contract_one_read_exact_lineage_and_same_session(monkeypatch: pytest.MonkeyPatch) -> None:
    composer, calls = build_composer(monkeypatch, (authority(),))
    session = RecordingSession()
    result = compose(composer, session)
    assert VERSION == "v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-COMPOSER"
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
    assert result.representative_role == "LEGAL_PRACTITIONER"
    assert result.representation_scope_capabilities == ("ADVISORY",)
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[:6] == (TENANT, MATTER, MATTER_FP, PARTY, SUBJECT, REPRESENTATIVE)
    assert kwargs["session"] is session
    assert session.starts == session.commits == session.aborts == 0


@pytest.mark.parametrize("session", [None, type("Inactive", (), {"in_transaction": False})()])
def test_active_transaction_required_before_read(monkeypatch: pytest.MonkeyPatch, session: Any) -> None:
    composer, calls = build_composer(monkeypatch, (authority(),))
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError) as raised:
        compose(composer, session)
    assert raised.value.code == "L9C11_P21A_COMPOSER_ACTIVE_TRANSACTION_REQUIRED"
    assert calls == []


@pytest.mark.parametrize(
    ("state", "expected"),
    [("APPOINTED", "APPOINTED"), ("DECLINED", "DECLINED"), ("REQUIRES_REVIEW", "REQUIRES_REVIEW")],
)
def test_empty_and_state_passthrough(monkeypatch: pytest.MonkeyPatch, state: str, expected: str) -> None:
    empty, _ = build_composer(monkeypatch, ())
    assert compose(empty, RecordingSession()).state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    empty_result = compose(empty, RecordingSession())
    assert empty_result.representative_role is None
    assert empty_result.representation_scope_capabilities == ()
    value, _ = build_composer(monkeypatch, (authority(decision=state),))
    result = compose(value, RecordingSession())
    assert result.state is getattr(LegalClientMatterRepresentationAuthorityCurrentnessState, expected)
    if state != "APPOINTED":
        assert result.representative_role is None
        assert result.representation_scope_capabilities == ()


def test_explicit_evaluation_time_and_future_semantics_are_owned_by_domain(monkeypatch: pytest.MonkeyPatch) -> None:
    future = authority(effective_from=BASE + timedelta(days=1))
    composer, _ = build_composer(monkeypatch, (future,))
    result = compose(composer, RecordingSession(), evaluated_at=BASE)
    direct = project_legal_client_matter_representation_authority_currentness(
        tenant_id=TENANT,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_identity_fingerprint=SUBJECT,
        representative_principal_id=REPRESENTATIVE,
        evaluated_at=BASE,
        authorities=(future,),
    )
    assert result == direct
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_ambiguous_and_corrupt_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    ambiguous, _ = build_composer(monkeypatch, (authority(), authority(authority_id="authority-conflict", decision="DECLINED")))
    ambiguous_result = compose(ambiguous, RecordingSession())
    assert ambiguous_result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert ambiguous_result.representative_role is None
    assert ambiguous_result.representation_scope_capabilities == ()
    invalid = cast(Any, object())
    corrupt, _ = build_composer(monkeypatch, (invalid,))
    corrupt_result = compose(corrupt, RecordingSession())
    assert corrupt_result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert corrupt_result.representative_role is None
    assert corrupt_result.representation_scope_capabilities == ()


def test_registry_failure_is_bounded_and_no_write_or_transaction_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Any, ...]] = []

    def fail(*args: Any, **kwargs: Any) -> Any:
        calls.append(args)
        raise authority_registry.LegalClientMatterRepresentationAuthorityRegistryError("synthetic")

    monkeypatch.setattr(composer_module.authority_registry, "list_representation_authorities_for_context", fail)
    composer = LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=object())
    session = RecordingSession()
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError) as raised:
        compose(composer, session)
    assert raised.value.code == "L9C11_P21A_COMPOSER_HISTORY_READ_FAILED"
    assert len(calls) == 1
    assert session.starts == session.commits == session.aborts == 0


def test_collection_required_and_invalid_time_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError):
        LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=None)
    composer, calls = build_composer(monkeypatch, (authority(),))
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError) as raised:
        compose(composer, RecordingSession(), evaluated_at=datetime(2026, 9, 28, 10, 0))
    assert raised.value.code == "L9C11_P21A_COMPOSER_EVALUATED_AT_INVALID"
    assert calls == []


def test_source_has_no_duplicate_currentness_or_downstream_authority_logic() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_representation_authority_currentness_composer.py").read_text()
    tree = ast.parse(source)
    assert "insert_one" not in source
    assert "update_one" not in source
    assert "delete_one" not in source
    assert "start_transaction" not in {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "commit_transaction" not in {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "abort_transaction" not in {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def test_registry_contract_is_exactly_the_p7_representative_specific_api() -> None:
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_representation_authority_registry.py").read_text()
    assert "def list_representation_authorities_for_context" in source
    assert "representative_principal_id" in source
    assert "without calculating currentness" in source


# ARTIFACT: test_legal_client_matter_representation_authority_currentness_composer.py
# VERSION: v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-COMPOSER-CERT
# AUTHORITY BOUNDARY: one bounded P7 history read plus pure P21A delegation
# TENANT POSTURE: exact representative-specific lineage propagation
# FAIL-CLOSED POSTURE: inactive transaction and registry failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
