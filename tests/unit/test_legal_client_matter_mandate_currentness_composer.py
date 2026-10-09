"""Direct certificate for the L9B12-P2 mandate-currentness composer.

TITLE: WILSY OS Legal Client Matter Mandate Currentness Composer Certificate
VERSION: v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact tenant-scoped mandate reads, caller-owned transaction
         propagation, upstream currentness delegation and pure projection
         construction without Mongo, lifecycle mutation or downstream legal
         authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_currentness_composer.py
COLLABORATION / OWNERSHIP: The mandate registry, grant-currentness composer,
                            acknowledgment-currentness composer and pure
                            currentness domain remain sovereign authorities.
                            This certificate covers only their composition.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER-CERT
           covers all published state mappings, exact lineage, explicit-time
           and same-session propagation, corruption/ambiguity blocking,
           transaction ownership and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Recording fakes and synthetic immutable values only;
                       no canonical Mongo or network access.
FAIL-CLOSED DECLARATION: Missing sessions, corrupt reads, cross-tenant
                         requests, unavailable upstream evidence and malformed
                         projections never become CURRENT.
"""
from __future__ import annotations

import ast
import inspect
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    LegalClientMatterMandateCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessReason,
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_mandate_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import (
    LegalClientMatterMandateCurrentnessComposer,
    LegalClientMatterMandateCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_registry as mandate_registry,
)
from tests.unit.test_legal_client_matter_mandate_currentness import (
    acknowledgment_projection,
    grant_projection,
    source_mandate,
)
from tests.unit import test_legal_client_matter_mandate_grant_currentness as grant_certificate


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b12"
MANDATE_ID = "mandate-l9b3"


class RecordingSession:
    """Active caller-owned transaction sentinel with no lifecycle methods."""

    in_transaction = True


def build_composer() -> LegalClientMatterMandateCurrentnessComposer:
    """Bind isolated collection sentinels; all reads are monkeypatched."""
    return LegalClientMatterMandateCurrentnessComposer(
        mandate_collection=object(),
        grant_collection=object(),
        grant_lifecycle_collection=object(),
        matter_lifecycle_collection=object(),
        acknowledgment_collection=object(),
    )


def install_sources(
    monkeypatch: pytest.MonkeyPatch,
    *,
    mandate: Any | None = None,
    mandate_missing: bool = False,
    grant_value: Any | None = None,
    acknowledgment_value: Any | None = None,
    mandate_error: BaseException | None = None,
    grant_error: BaseException | None = None,
    acknowledgment_error: BaseException | None = None,
    observed: list[tuple[Any, ...]] | None = None,
) -> None:
    """Install recording registry/upstream-composer seams."""
    records: list[tuple[Any, ...]] = observed if observed is not None else []
    source = mandate if mandate is not None else source_mandate()
    grant = grant_value if grant_value is not None else grant_projection()
    acknowledgment = (
        acknowledgment_value
        if acknowledgment_value is not None
        else acknowledgment_projection()
    )

    def read_mandate(tenant_id: str, mandate_id: str, collection: Any, *, session: Any) -> Any:
        records.append(("mandate", tenant_id, mandate_id, session))
        if mandate_error is not None:
            raise mandate_error
        if mandate_missing:
            raise mandate_registry.LegalClientMatterMandateRegistryNotFoundError(
                "L9B11_MANDATE_NOT_FOUND"
            )
        return source

    def read_grant(
        self: Any, tenant_id: str, grant_id: str, at: datetime, session: Any
    ) -> Any:
        records.append(("grant", tenant_id, grant_id, session, at))
        if grant_error is not None:
            raise grant_error
        return grant

    def read_ack(
        self: Any, tenant_id: str, grant_id: str, at: datetime, session: Any
    ) -> Any:
        records.append(("acknowledgment", tenant_id, grant_id, session, at))
        if acknowledgment_error is not None:
            raise acknowledgment_error
        return acknowledgment

    monkeypatch.setattr(mandate_registry, "get_mandate", read_mandate)
    monkeypatch.setattr(
        composer_module.grant_composer.LegalClientMatterMandateGrantCurrentnessComposer,
        "compose_currentness",
        read_grant,
    )
    monkeypatch.setattr(
        composer_module.acknowledgment_composer.LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
        "compose_currentness",
        read_ack,
    )


def compose(
    value: LegalClientMatterMandateCurrentnessComposer,
    session: Any,
    *,
    at: datetime = BASE + timedelta(hours=3),
    tenant_id: str = TENANT,
    mandate_id: str = MANDATE_ID,
) -> Any:
    """Invoke the narrow public composition boundary."""
    return value.compose_currentness(tenant_id, mandate_id, at, session)


def expect_code(code: str, operation: Any) -> None:
    """Assert one stable non-sensitive composer failure."""
    with pytest.raises(LegalClientMatterMandateCurrentnessComposerError) as raised:
        operation()
    assert raised.value.code == code
    assert str(raised.value) == code


def valid_grant_state(state: str) -> Any:
    """Build each upstream grant state with exact mandate lineage."""
    source = source_mandate()
    base: dict[str, object] = {
        "currentness_id": "grant-currentness-l9b12",
        "tenant_id": TENANT,
        "client_grant_id": source.client_grant_reference,
        "client_grant_fingerprint": source.client_grant_fingerprint,
        "case_matter_id": source.case_matter_id,
        "matter_fingerprint": source.matter_fingerprint,
        "client_party_id": source.client_party_id,
        "subject_identity_fingerprint": source.subject_identity_fingerprint,
        "evaluation_time": BASE,
        "matter_state_evidence_fingerprint": source.matter_fingerprint,
        "formation_fingerprint": source.client_grant_fingerprint,
    }
    parsed = LegalClientMatterMandateGrantCurrentnessState(state)
    if parsed is LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED:
        return grant_certificate.projection(
            **base,
            state=parsed,
            reason=LegalClientMatterMandateGrantCurrentnessReason.MATTER_CLOSED,
            matter_state="CLOSED",
            lifecycle_evidence_fingerprints=(),
            decisive_lifecycle_evidence_fingerprints=(),
        )
    if parsed is LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED:
        return grant_certificate.invalid_state(
            parsed,
            LegalClientMatterMandateGrantCurrentnessReason.SUPERSEDED,
            **base,
            successor_client_grant_id="successor-l9b12",
            successor_client_grant_fingerprint="b" * 128,
        )
    if parsed is LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS:
        return grant_certificate.projection(
            **base,
            state=parsed,
            reason=LegalClientMatterMandateGrantCurrentnessReason.AMBIGUOUS_LIFECYCLE,
            lifecycle_evidence_fingerprints=("a" * 128, "b" * 128),
            decisive_lifecycle_evidence_fingerprints=("a" * 128, "b" * 128),
        )
    if parsed is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED:
        corrupt_base = dict(base)
        corrupt_base["client_grant_fingerprint"] = None
        corrupt_base["formation_fingerprint"] = None
        return grant_certificate.projection(
            **corrupt_base,
            state=parsed,
            reason=LegalClientMatterMandateGrantCurrentnessReason.CORRUPT_EVIDENCE,
            lifecycle_evidence_fingerprints=("f" * 128,),
            decisive_lifecycle_evidence_fingerprints=(),
        )
    return grant_certificate.invalid_state(
        parsed,
        LegalClientMatterMandateGrantCurrentnessReason(parsed.value),
        **base,
    )


def test_missing_inactive_and_naive_inputs_reject_before_any_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records: list[tuple[Any, ...]] = []
    install_sources(monkeypatch, observed=records)
    value = build_composer()
    expect_code("L9B12_P2_ACTIVE_TRANSACTION_REQUIRED", lambda: compose(value, None))
    expect_code(
        "L9B12_P2_ACTIVE_TRANSACTION_REQUIRED",
        lambda: compose(value, type("Inactive", (), {"in_transaction": False})()),
    )
    expect_code(
        "L9B12_P2_EVALUATION_TIME_INVALID",
        lambda: compose(value, RecordingSession(), at=BASE.replace(tzinfo=None)),
    )
    assert records == []


def test_public_inputs_exclude_all_authority_assertions() -> None:
    parameters = inspect.signature(
        LegalClientMatterMandateCurrentnessComposer.compose_currentness
    ).parameters
    assert set(parameters) == {"self", "tenant_id", "mandate_id", "evaluation_time", "session"}
    forbidden = {
        "mandate_fingerprint", "client_grant_id", "client_grant_fingerprint",
        "firm_acknowledgment_id", "firm_acknowledgment_fingerprint",
        "case_matter_id", "client_party_id", "subject_identity_fingerprint",
        "state", "scope", "capabilities",
    }
    assert forbidden.isdisjoint(parameters)


def test_absent_mandate_returns_formation_absent_without_other_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records: list[tuple[Any, ...]] = []
    install_sources(monkeypatch, mandate_missing=True, observed=records)
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT
    assert records == [("mandate", TENANT, MANDATE_ID, records[0][3])]


def test_corrupt_mandate_and_unavailable_upstream_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records: list[tuple[Any, ...]] = []
    install_sources(
        monkeypatch,
        mandate_error=mandate_registry.LegalClientMatterMandateRegistryPersistedRecordInvalidError(
            "L9B11_PERSISTED_RECORD_INVALID"
        ),
        observed=records,
    )
    expect_code("L9B12_P2_MANDATE_READ_FAILED", lambda: compose(build_composer(), RecordingSession()))
    install_sources(
        monkeypatch,
        grant_error=composer_module.grant_composer.LegalClientMatterMandateGrantCurrentnessComposerError(
            "L9B9_P2_FORMATION_UNAVAILABLE"
        ),
        observed=records,
    )
    expect_code("L9B12_P2_GRANT_CURRENTNESS_READ_FAILED", lambda: compose(build_composer(), RecordingSession()))
    install_sources(
        monkeypatch,
        acknowledgment_error=composer_module.acknowledgment_composer.LegalClientMatterMandateAcknowledgmentCurrentnessComposerError(
            "L9B10_P3_ACKNOWLEDGMENT_HISTORY_READ_FAILED"
        ),
        observed=records,
    )
    expect_code("L9B12_P2_ACKNOWLEDGMENT_CURRENTNESS_READ_FAILED", lambda: compose(build_composer(), RecordingSession()))


def test_exact_bound_grant_is_derived_from_mandate_and_one_session_time_is_propagated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records: list[tuple[Any, ...]] = []
    install_sources(monkeypatch, observed=records)
    session = RecordingSession()
    at = BASE + timedelta(hours=4)
    value = compose(build_composer(), session, at=at)
    assert value.state is LegalClientMatterMandateCurrentnessState.CURRENT
    assert [row[0] for row in records] == ["mandate", "grant", "acknowledgment"]
    assert records[0][1:3] == (TENANT, MANDATE_ID)
    assert records[1][1:3] == (TENANT, "client-grant:l9b3")
    assert records[2][1:3] == (TENANT, "client-grant:l9b3")
    assert all(row[3] is session for row in records)
    assert records[1][4] == at and records[2][4] == at


@pytest.mark.parametrize(
    "state",
    ["NOT_YET_EFFECTIVE", "EXPIRED", "REVOKED", "SUPERSEDED", "MATTER_CLOSED", "AMBIGUOUS", "CORRUPT_BLOCKED"],
)
def test_every_grant_non_current_state_reaches_pure_projection(
    monkeypatch: pytest.MonkeyPatch, state: str
) -> None:
    lifecycle = ("a" * 128,) if state not in {"AMBIGUOUS"} else ("a" * 128, "b" * 128)
    grant = valid_grant_state(state)
    install_sources(monkeypatch, grant_value=grant)
    value = compose(build_composer(), RecordingSession())
    assert value.is_current is False
    assert value.state is not LegalClientMatterMandateCurrentnessState.CURRENT


@pytest.mark.parametrize("state", ["NO_DECISION", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED"])
def test_every_acknowledgment_non_positive_state_reaches_pure_projection(
    monkeypatch: pytest.MonkeyPatch, state: str
) -> None:
    if state == "AMBIGUOUS":
        acknowledgment = acknowledgment_projection(
            state=state,
            decisive_ids=("ack-a", "ack-b"),
            decisive_fingerprints=("a" * 128, "b" * 128),
        )
    else:
        acknowledgment = acknowledgment_projection(state=state)
    install_sources(monkeypatch, acknowledgment_value=acknowledgment)
    value = compose(build_composer(), RecordingSession())
    assert value.is_current is False
    assert value.state is not LegalClientMatterMandateCurrentnessState.CURRENT


def test_exact_lineage_and_later_acknowledgment_identity_block_currentness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for grant in (
        grant_projection(client_grant_id="other-grant"),
        grant_projection(client_grant_fingerprint="a" * 128),
        grant_projection(case_matter_id="other-matter"),
        grant_projection(client_party_id="other-party"),
        grant_projection(subject_identity_fingerprint="b" * 128),
    ):
        install_sources(monkeypatch, grant_value=grant)
        assert compose(build_composer(), RecordingSession()).state is LegalClientMatterMandateCurrentnessState.LINEAGE_MISMATCH
    for acknowledgment in (
        acknowledgment_projection(decisive_ids=("other-ack",)),
        acknowledgment_projection(decisive_fingerprints=("a" * 128,)),
        acknowledgment_projection(case_matter_id="other-matter"),
        acknowledgment_projection(client_party_id="other-party"),
        acknowledgment_projection(subject_identity_fingerprint="b" * 128),
    ):
        install_sources(monkeypatch, acknowledgment_value=acknowledgment)
        assert compose(build_composer(), RecordingSession()).state is LegalClientMatterMandateCurrentnessState.LINEAGE_MISMATCH


def test_cross_tenant_absence_has_no_oracle(monkeypatch: pytest.MonkeyPatch) -> None:
    records: list[tuple[Any, ...]] = []
    install_sources(monkeypatch, mandate_missing=True, observed=records)
    value = compose(build_composer(), RecordingSession(), tenant_id="tenant-other")
    assert value.state is LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT
    assert records[0][1:3] == ("tenant-other", MANDATE_ID)
    assert len(records) == 1


def test_repeated_composition_is_deterministic_and_does_not_mutate_mandate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = source_mandate()
    before = source.to_dict()
    install_sources(monkeypatch, mandate=source)
    first = compose(build_composer(), RecordingSession())
    second = compose(build_composer(), RecordingSession())
    assert first == second and first.fingerprint == second.fingerprint
    assert source.to_dict() == before


def test_transaction_ownership_and_negative_authority_audit() -> None:
    path = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_currentness_composer.py")
    tree = ast.parse(path.read_text())
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any(
        token in module
        for module in imports
        for token in ("case_matter", "acting_capacity", "conflict", "client_acceptance", "iam", "engagement", "representation", "court", "fastapi", "pymongo")
    )
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not calls.intersection({"start_transaction", "commit_transaction", "abort_transaction", "insert_one", "update_one", "delete_one", "delete_many", "create_index"})
    source = path.read_text()
    assert "datetime.now" not in source and "utcnow" not in source
    assert "LegalClientMatterMandateCurrentnessState" not in source


# ARTIFACT: test_legal_client_matter_mandate_currentness_composer.py
# VERSION: v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct read-only composition certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
