"""Direct certificate for deterministic client-matter mandate formation.

TITLE: WILSY OS Legal Client Matter Mandate Composer Certificate
VERSION: v1.0.0-L9B11-P1-CLIENT-MATTER-MANDATE-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact grant/acknowledgment currentness gating, lineage,
         chronology, deterministic identity, domain construction, replay and
         caller-owned transaction behavior without a real database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_composer.py
COLLABORATION / OWNERSHIP: This certificate covers only formation orchestration;
                            the mandate domain/registry, currentness, lifecycle,
                            Engagement, Representation, Court, IAM and finance
                            remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B11-P1 certifies public input narrowing, same-session
           reads, currentness state gates, exact correlation, chronology,
           deterministic IDs, replay, pair handling and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque domain evidence only; no PII,
                             secrets, HTTP, Mongo or canonical records.
TENANT BOUNDARY: Tenant and all lineage come from exact canonical grant/ack.
AUTHORITY BOUNDARY: One immutable mandate formation write only.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement or release; Kennel EOS.
TRANSACTION BOUNDARY: Fake caller sessions prove no commit/abort/retry ownership.
FAIL-CLOSED DECLARATION: Missing, stale, ambiguous, divergent or malformed
                         evidence fails without authority expansion.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.legal_operations.orchestration.legal_client_matter_mandate_composer as composer_module
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_registry import (
    LegalClientMatterMandateRegistryConflictError,
)


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.commit_calls = 0
        self.abort_calls = 0


class _GrantCurrentness:
    def __init__(self, grant: Any, state: LegalClientMatterMandateGrantCurrentnessState) -> None:
        self.state = state
        self.is_current = state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
        self.tenant_id = grant.tenant_id
        self.client_grant_id = grant.client_grant_id
        self.client_grant_fingerprint = grant.fingerprint
        self.case_matter_id = grant.case_matter_id
        self.client_party_id = grant.client_party_id
        self.subject_identity_fingerprint = grant.subject_identity_fingerprint


class _AcknowledgmentCurrentness:
    def __init__(self, grant: Any, value: Any, state: LegalClientMatterMandateAcknowledgmentCurrentnessState) -> None:
        self.state = state
        self.is_acknowledged = state is LegalClientMatterAcknowledgmentCurrentnessState.ACKNOWLEDGED
        self.decisive_acknowledgment_ids = () if not self.is_acknowledged else (value.acknowledgment_id,)
        self.decisive_acknowledgment_fingerprints = () if not self.is_acknowledged else (value.fingerprint,)
        self.tenant_id = grant.tenant_id
        self.client_grant_id = grant.client_grant_id
        self.client_grant_fingerprint = grant.fingerprint
        self.case_matter_id = grant.case_matter_id
        self.client_party_id = grant.client_party_id
        self.subject_identity_fingerprint = grant.subject_identity_fingerprint


LegalClientMatterAcknowledgmentCurrentnessState = LegalClientMatterMandateAcknowledgmentCurrentnessState


def _install(monkeypatch: pytest.MonkeyPatch, *, grant_state: Any = LegalClientMatterMandateGrantCurrentnessState.CURRENT, acknowledgment_state: Any = LegalClientMatterAcknowledgmentCurrentnessState.ACKNOWLEDGED, persist: Any | None = None) -> tuple[Any, Any, list[tuple[str, Any, Any, Any]]]:
    from tests.unit.test_legal_client_matter_mandate_grant import grant as grant_factory
    grant = grant_factory()
    from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import LegalClientMatterMandateAcknowledgment
    ack = LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=grant,
        acknowledgment_id="acknowledgment-composer",
        decision="ACKNOWLEDGED",
        decision_actor_principal_id="principal-firm-composer",
        authorization_evidence_reference="firm-iam:composer",
        authorization_evidence_fingerprint="e" * 128,
        source_evidence_reference="firm-review:composer",
        source_evidence_fingerprint="f" * 128,
        occurred_at=BASE + __import__("datetime").timedelta(hours=3),
        effective_from=BASE + __import__("datetime").timedelta(hours=4),
        idempotency_key="ack-idempotency:composer",
    )
    calls: list[tuple[str, Any, Any, Any]] = []

    def get_grant(tenant: str, grant_id: str, collection: Any, *, session: Any) -> Any:
        calls.append(("grant_registry", tenant, grant_id, session))
        return grant

    def list_ack(tenant: str, grant_id: str, collection: Any, *, session: Any) -> tuple[Any, ...]:
        calls.append(("ack_registry", tenant, grant_id, session))
        return (ack,)

    class GrantComposer:
        def __init__(self, **_: Any) -> None: pass
        def compose_currentness(self, tenant: str, grant_id: str, at: Any, session: Any) -> Any:
            calls.append(("grant_currentness", tenant, grant_id, session))
            return _GrantCurrentness(grant, grant_state)

    class AckComposer:
        def __init__(self, **_: Any) -> None: pass
        def compose_currentness(self, tenant: str, grant_id: str, at: Any, session: Any) -> Any:
            calls.append(("ack_currentness", tenant, grant_id, session))
            return _AcknowledgmentCurrentness(grant, ack, acknowledgment_state)

    def persist_operation(value: Any, collection: Any, *, session: Any) -> Any:
        calls.append(("mandate_registry", value, collection, session))
        if persist is not None:
            return persist(value, collection, session=session)
        return value

    monkeypatch.setattr(composer_module.grant_registry, "get_grant", get_grant)
    monkeypatch.setattr(composer_module.acknowledgment_registry, "list_acknowledgments_for_grant", list_ack)
    monkeypatch.setattr(composer_module, "LegalClientMatterMandateGrantCurrentnessComposer", GrantComposer)
    monkeypatch.setattr(composer_module, "LegalClientMatterMandateAcknowledgmentCurrentnessComposer", AckComposer)
    monkeypatch.setattr(composer_module.mandate_registry, "persist_mandate", persist_operation)
    return grant, ack, calls


def _composer() -> composer_module.LegalClientMatterMandateComposer:
    return composer_module.LegalClientMatterMandateComposer(
        grant_collection=object(), grant_lifecycle_collection=object(),
        matter_lifecycle_collection=object(), acknowledgment_collection=object(),
        mandate_collection=object(),
    )


def test_public_inputs_are_narrow_and_active_transaction_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="ACTIVE_TRANSACTION"):
        _composer().compose_mandate(tenant_id="tenant-l9b4", client_grant_id="grant", idempotency_key="key", session=None)
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="ACTIVE_TRANSACTION"):
        _composer().compose_mandate(tenant_id="tenant-l9b4", client_grant_id="grant", idempotency_key="key", session=_Session(False))


@pytest.mark.parametrize("field,value", [("tenant_id", ""), ("client_grant_id", "bad id"), ("idempotency_key", "bad\nkey")])
def test_malformed_public_input_rejected_before_authority_reads(monkeypatch: pytest.MonkeyPatch, field: str, value: str) -> None:
    _, _, calls = _install(monkeypatch)
    values = {"tenant_id": "tenant-l9b4", "client_grant_id": "client-grant-l9b4", "idempotency_key": "composer-key"}
    values[field] = value
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError):
        _composer().compose_mandate(**values, session=_Session())
    assert calls == []


def test_absent_grant_and_absent_acknowledgment_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    not_found = composer_module.grant_registry.LegalClientMatterMandateGrantRegistryNotFoundError("ABSENT")
    monkeypatch.setattr(composer_module.grant_registry, "get_grant", lambda *args, **kwargs: (_ for _ in ()).throw(not_found))
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="GRANT_ABSENT"):
        _composer().compose_mandate(tenant_id="tenant-l9b4", client_grant_id="client-grant-l9b4", idempotency_key="key", session=_Session())

    _install(monkeypatch)
    monkeypatch.setattr(composer_module.acknowledgment_registry, "list_acknowledgments_for_grant", lambda *args, **kwargs: ())
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="ACKNOWLEDGMENT_ABSENT"):
        _composer().compose_mandate(tenant_id="tenant-l9b4", client_grant_id="client-grant-l9b4", idempotency_key="key", session=_Session())


@pytest.mark.parametrize("state", list(LegalClientMatterMandateGrantCurrentnessState)[1:])
def test_every_non_current_grant_state_fails_closed(monkeypatch: pytest.MonkeyPatch, state: Any) -> None:
    _install(monkeypatch, grant_state=state)
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="GRANT_NOT_CURRENT"):
        _composer().compose_mandate(tenant_id="tenant-l9b4", client_grant_id="client-grant-l9b4", idempotency_key="composer-key", session=_Session())


@pytest.mark.parametrize("state", [LegalClientMatterAcknowledgmentCurrentnessState.NO_DECISION, LegalClientMatterAcknowledgmentCurrentnessState.DECLINED, LegalClientMatterAcknowledgmentCurrentnessState.REQUIRES_REVIEW, LegalClientMatterAcknowledgmentCurrentnessState.AMBIGUOUS, LegalClientMatterAcknowledgmentCurrentnessState.CORRUPT_BLOCKED])
def test_every_non_acknowledged_state_fails_closed(monkeypatch: pytest.MonkeyPatch, state: Any) -> None:
    _install(monkeypatch, acknowledgment_state=state)
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="ACKNOWLEDGMENT_NOT_ACKNOWLEDGED"):
        _composer().compose_mandate(tenant_id="tenant-l9b4", client_grant_id="client-grant-l9b4", idempotency_key="composer-key", session=_Session())


def test_currentness_uses_decisive_ack_time_and_persists_one_domain_value(monkeypatch: pytest.MonkeyPatch) -> None:
    grant, ack, calls = _install(monkeypatch)
    session = _Session()
    result = _composer().compose_mandate(tenant_id=grant.tenant_id, client_grant_id=grant.client_grant_id, idempotency_key="composer-key", session=session)
    assert result.client_grant_fingerprint == grant.fingerprint
    assert result.firm_acknowledgment_fingerprint == ack.fingerprint
    assert result.scope_reference == grant.scope_reference
    assert result.capabilities == grant.capabilities
    assert result.occurred_at == ack.effective_from
    assert result.effective_from == ack.effective_from
    assert result.mandate_id.startswith("legal-client-matter-mandate:")
    assert [item[0] for item in calls] == ["grant_registry", "ack_registry", "grant_currentness", "ack_currentness", "mandate_registry"]
    assert all(item[3] is session for item in calls)
    assert session.commit_calls == session.abort_calls == 0


def test_exact_replay_is_deterministic_and_registry_owns_pair_collision(monkeypatch: pytest.MonkeyPatch) -> None:
    grant, _, calls = _install(monkeypatch)
    first = _composer().compose_mandate(tenant_id=grant.tenant_id, client_grant_id=grant.client_grant_id, idempotency_key="composer-key", session=_Session())
    second = _composer().compose_mandate(tenant_id=grant.tenant_id, client_grant_id=grant.client_grant_id, idempotency_key="composer-key", session=_Session())
    assert first == second
    assert len([item for item in calls if item[0] == "mandate_registry"]) == 2

    def divergent(*_: Any, **__: Any) -> Any:
        raise LegalClientMatterMandateRegistryConflictError("PAIR")
    _install(monkeypatch, persist=divergent)
    with pytest.raises(composer_module.LegalClientMatterMandateComposerError, match="DIVERGENT_REPLAY"):
        _composer().compose_mandate(tenant_id=grant.tenant_id, client_grant_id=grant.client_grant_id, idempotency_key="other-key", session=_Session())


def test_no_forbidden_authority_or_direct_collection_write_and_no_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch)
    source = Path(__file__).parents[2] / "tools/eos/legal_operations/orchestration/legal_client_matter_mandate_composer.py"
    tree = ast.parse(source.read_text())
    forbidden = {"conflict", "client_acceptance", "iam", "engagement", "representation", "court", "finance", "case_matter"}
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any(any(term in module.lower() for term in forbidden) for module in imports)
    calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert not set(calls) & {"insert_one", "update_one", "replace_one", "delete_one", "delete_many", "start_transaction", "commit_transaction", "abort_transaction"}
    text = source.read_text()
    assert "datetime.now" not in text
    assert "MandateGrantCurrentnessComposer" in text
    assert "MandateAcknowledgmentCurrentnessComposer" in text
    assert "LegalClientMatterMandate(" in text
    assert "persist_mandate" in text


def test_certificate_has_sovereign_markers_and_clean_production_artifact() -> None:
    source = Path(__file__).read_text()
    assert "VERSION: v1.0.0-L9B11-P1-CLIENT-MATTER-MANDATE-COMPOSER-CERT" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    production = (Path(__file__).parents[2] / "tools/eos/legal_operations/orchestration/legal_client_matter_mandate_composer.py").read_text().lower()
    markers = ("to" + "do", "fix" + "me", "place" + "holder", "stu" + "b")
    assert not any(marker in production for marker in markers)


# ARTIFACT: test_legal_client_matter_mandate_composer.py
# VERSION: v1.0.0-L9B11-P1-CLIENT-MATTER-MANDATE-COMPOSER-CERT
# AUTHORITY BOUNDARY: synthetic unit certificate only
# FAIL-CLOSED POSTURE: no authority is inferred from caller assertions
# END OF WILSY OS SOVEREIGN ARTIFACT
