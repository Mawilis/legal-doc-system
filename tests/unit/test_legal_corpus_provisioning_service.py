"""Direct certificate for the R8H legal-corpus provisioning service.

TITLE: WILSY OS Legal Corpus Draft Provisioning Service Certificate
VERSION: v1.2.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-PROVISIONING-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies canonical-source ownership, active caller transaction
         requirements, pair-state adjudication, staged result semantics, and
         fail-closed composition without a Mongo server.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_provisioning_service.py
COLLABORATION / OWNERSHIP: R8H owns the composition service; this certificate
                            owns only direct non-Mongo evidence. R8J will own
                            the governed operator-command boundary.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.2.0 certifies historical and reviewed-successor admission
           through the source-owned runtime resolver while retaining exact
           replay, partial-state, session, and caller-owned transaction semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque fixtures only; no secrets, network, HTTP,
                            browser, or live persistence are used.
TENANT BOUNDARY: Admission is PLATFORM-scoped institutional corpus authority;
                 tenant/principal authority is not accepted or inferred.
AUTHORITY BOUNDARY: Service composition only; no issuance, review, approval,
                    acceptance, signature, commercial execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Missing transactions, mismatches, partial pairs, write
                     failures, and dependency failures reject with causes intact.
"""
from __future__ import annotations

import inspect
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, cast

import pytest

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_VERSION,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)
from tools.eos.legal_operations.registry.legal_corpus_provisioning_authority_registry import (
    LegalCorpusProvisioningAuthorityRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import LegalDocumentRegistryError
from tools.eos.legal_operations.service import legal_corpus_provisioning_service as service_module


NOW = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)


class Session:
    """Minimal caller-owned session sentinel matching the R8H contract."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class SpyDocumentRegistry:
    """Deterministic document registry double with ordered call evidence."""

    def __init__(self, document: Any = None, events: list[str] | None = None) -> None:
        self.document = document
        self.events = events if events is not None else []
        self.read_sessions: list[Any] = []
        self.write_sessions: list[Any] = []
        self.read_failure: BaseException | None = None
        self.write_failure: BaseException | None = None
        self.ensure_indexes_called = False

    def get(self, document_id: str, version: str, collection: Any = None, *, session: Any = None) -> Any:
        self.events.append("document_read")
        self.read_sessions.append(session)
        if self.read_failure is not None:
            raise self.read_failure
        return self.document

    def register(self, document: Any, collection: Any = None, *, session: Any = None) -> Any:
        self.events.append("document_write")
        self.write_sessions.append(session)
        if self.write_failure is not None:
            raise self.write_failure
        self.document = document
        return document

    def ensure_indexes(self, *_args: Any, **_kwargs: Any) -> None:
        self.ensure_indexes_called = True
        raise AssertionError("service must not deploy indexes")


class SpyAuthorityRegistry:
    """Deterministic authority registry double with ordered call evidence."""

    def __init__(self, evidence: Any = None, events: list[str] | None = None) -> None:
        self.evidence = evidence
        self.events = events if events is not None else []
        self.read_sessions: list[Any] = []
        self.write_sessions: list[Any] = []
        self.read_failure: BaseException | None = None
        self.write_failure: BaseException | None = None
        self.ensure_indexes_called = False

    def get_by_source(self, document_id: str, version: str, collection: Any = None, *, session: Any = None) -> Any:
        self.events.append("authority_read")
        self.read_sessions.append(session)
        if self.read_failure is not None:
            raise self.read_failure
        return self.evidence

    def create_or_replay(self, evidence: Any, collection: Any = None, *, session: Any = None) -> Any:
        self.events.append("authority_write")
        self.write_sessions.append(session)
        if self.write_failure is not None:
            raise self.write_failure
        self.evidence = evidence
        return evidence

    def ensure_indexes(self, *_args: Any, **_kwargs: Any) -> None:
        self.ensure_indexes_called = True
        raise AssertionError("service must not deploy indexes")


def _fields(*, document: Any | None = None, **changes: Any) -> dict[str, Any]:
    if document is None:
        document = corpus.get_institutional_charter_draft()
    values: dict[str, Any] = {
        "authority_evidence_id": "LEGAL-CORPUS-AUTH-R8I-001",
        "scope": LegalCorpusProvisioningAuthorityScope.PLATFORM,
        "operation": LegalCorpusProvisioningOperation.DRAFT_ADMISSION,
        "source_document_id": document.document_id,
        "source_agreement_type": document.agreement_type,
        "source_version": document.version,
        "source_status": document.status,
        "source_content_reference": document.content_reference,
        "source_sha3_512": document.sha3_512,
        "authority_source_id": LegalCorpusProvisioningAuthoritySource.DEPLOYMENT_OPERATOR,
        "authority_source_version": AUTHORITY_SOURCE_VERSION,
        "actor_representation": "deployment-job:r8i-certificate",
        "authorized_at": NOW,
        "idempotency_key": "r8i-idempotency-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(**values)
    return values


def _evidence(*, document: Any | None = None, **changes: Any) -> LegalCorpusProvisioningAuthorityEvidence:
    return LegalCorpusProvisioningAuthorityEvidence(**_fields(document=document, **changes))


def _service(document: Any = None, evidence: Any = None, events: list[str] | None = None) -> tuple[service_module.LegalCorpusProvisioningService, SpyDocumentRegistry, SpyAuthorityRegistry, list[str]]:
    ordered = events if events is not None else []
    documents = SpyDocumentRegistry(document, ordered)
    authorities = SpyAuthorityRegistry(evidence, ordered)
    instance = service_module.LegalCorpusProvisioningService()
    setattr(instance, "document_registry", documents)
    setattr(instance, "authority_registry", authorities)
    return instance, documents, authorities, ordered


def _error(call: Callable[[], Any]) -> service_module.LegalCorpusProvisioningServiceError:
    with pytest.raises(service_module.LegalCorpusProvisioningServiceError) as captured:
        call()
    return captured.value


def test_actual_api_is_narrow_and_result_contract_is_immutable() -> None:
    signature = inspect.signature(service_module.LegalCorpusProvisioningService.admit_draft)
    assert tuple(signature.parameters) == ("self", "authority_evidence", "session")
    assert service_module.LegalCorpusProvisioningResultState.PENDING_COMMIT.value == "PENDING_COMMIT"
    assert service_module.LegalCorpusProvisioningResultState.EXACT_REPLAY.value == "EXACT_REPLAY"
    assert not any(name in vars(service_module.LegalCorpusProvisioningService) for name in ("approve", "review", "accept", "sign", "commit"))


def test_missing_or_inactive_session_rejected_before_any_read_or_write() -> None:
    evidence = _evidence()
    instance, documents, authorities, events = _service(events=[])
    for supplied in (None, Session(False)):
        failure = _error(lambda supplied=supplied: instance.admit_draft(evidence, session=supplied))
        assert failure.code == "LEGAL_CORPUS_PROVISIONING_ACTIVE_TRANSACTION_REQUIRED"
    assert events == []
    assert documents.read_sessions == [] and authorities.read_sessions == []
    assert documents.write_sessions == [] and authorities.write_sessions == []


def test_only_r8d_authority_evidence_is_accepted() -> None:
    instance, _documents, _authorities, _events = _service()
    for invalid in (None, {}, corpus.get_institutional_charter_draft()):
        failure = _error(lambda invalid=invalid: instance.admit_draft(cast(Any, invalid), session=Session()))
        assert failure.code == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_INPUT_INVALID"


def test_canonical_source_and_authority_are_verified_before_mutation() -> None:
    evidence = _evidence()
    instance, documents, authorities, events = _service(events=[])
    result = instance.admit_draft(evidence, session=Session())
    assert result.document_id == "WILSY-OS-INSTITUTIONAL-CHARTER"
    assert result.document_version == "1.0.0-DRAFT"
    assert result.document_sha3_512 == corpus.get_institutional_charter_draft().sha3_512
    assert events == ["document_read", "authority_read", "document_write", "authority_write"]
    assert documents.write_sessions[0] is authorities.write_sessions[0] is documents.read_sessions[0] is authorities.read_sessions[0]


def test_all_eleven_platform_corpus_versions_stage_from_r8d_identity() -> None:
    """R8H resolves historical and reviewed-successor values without caller content."""
    for document in corpus.PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS:
        evidence = _evidence(document=document, authority_evidence_id=f"AUTH-{document.document_id}")
        instance, _documents, _authorities, _events = _service(events=[])
        result = instance.admit_draft(evidence, session=Session())
        assert result.document_id == document.document_id
        assert result.document_version == document.version
        assert result.document_sha3_512 == document.sha3_512


@pytest.mark.parametrize(
    "changes",
    [
        {"source_document_id": "OTHER-DOCUMENT"},
        {"source_agreement_type": LegalAgreementType.USER_TERMS},
        {"source_version": "1.0.1-DRAFT"},
        {"source_content_reference": "wilsy-os://legal/other"},
        {"source_sha3_512": "a" * 128},
    ],
)
def test_authority_mismatch_fails_before_both_writes(changes: dict[str, Any]) -> None:
    instance, documents, authorities, events = _service()
    failure = _error(lambda: instance.admit_draft(_evidence(**changes), session=Session()))
    assert failure.code == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_MISMATCH"
    assert events == []
    assert documents.write_sessions == [] and authorities.write_sessions == []


@pytest.mark.parametrize("status", [LegalDocumentStatus.APPROVED, LegalDocumentStatus.RETIRED])
def test_non_draft_canonical_source_is_rejected_before_reads_or_writes(monkeypatch: pytest.MonkeyPatch, status: LegalDocumentStatus) -> None:
    canonical = corpus.get_institutional_charter_draft()
    evidence = _evidence()
    monkeypatch.setattr(
        service_module.production_legal_corpus,
        "PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS",
        (replace(canonical, status=status), *service_module.production_legal_corpus.PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS[1:]),
    )
    instance, documents, authorities, events = _service()
    failure = _error(lambda: instance.admit_draft(evidence, session=Session()))
    assert failure.code == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_MISMATCH"
    assert events == []
    assert documents.write_sessions == [] and authorities.write_sessions == []


def test_both_absent_stages_document_then_authority_and_returns_pending_commit() -> None:
    evidence = _evidence()
    session = Session()
    instance, documents, authorities, events = _service(events=[])
    result = instance.admit_draft(evidence, session=session)
    assert result.state is service_module.LegalCorpusProvisioningResultState.PENDING_COMMIT
    assert result.authority_evidence_id == evidence.authority_evidence_id
    assert result.authority_evidence_fingerprint == evidence.evidence_fingerprint
    assert events == ["document_read", "authority_read", "document_write", "authority_write"]
    assert documents.write_sessions == [session] and authorities.write_sessions == [session]
    assert documents.document is corpus.get_institutional_charter_draft()
    assert not hasattr(result, "committed") and not hasattr(result, "durable")


def test_both_present_exact_returns_exact_replay_without_writes() -> None:
    evidence = _evidence()
    session = Session()
    instance, documents, authorities, events = _service(corpus.get_institutional_charter_draft(), evidence, [])
    result = instance.admit_draft(evidence, session=session)
    assert result.state is service_module.LegalCorpusProvisioningResultState.EXACT_REPLAY
    assert events == ["document_read", "authority_read"]
    assert documents.write_sessions == [] and authorities.write_sessions == []
    assert result.document_sha3_512 == evidence.source_sha3_512


def test_document_only_and_evidence_only_states_fail_without_backfill() -> None:
    evidence = _evidence()
    document = corpus.get_institutional_charter_draft()
    for document_value, evidence_value, expected in (
        (document, None, "LEGAL_CORPUS_PROVISIONING_PARTIAL_AUTHORITY_ABSENT"),
        (None, evidence, "LEGAL_CORPUS_PROVISIONING_PARTIAL_DOCUMENT_ABSENT"),
    ):
        instance, documents, authorities, events = _service(document_value, evidence_value, [])
        failure = _error(lambda instance=instance: instance.admit_draft(evidence, session=Session()))
        assert failure.code == expected
        assert events == ["document_read", "authority_read"]
        assert documents.write_sessions == [] and authorities.write_sessions == []


def test_divergent_document_and_authority_states_fail_without_writes() -> None:
    evidence = _evidence()
    divergent_document = replace(corpus.get_institutional_charter_draft(), title="Divergent title")
    instance, documents, authorities, events = _service(divergent_document, evidence, [])
    assert _error(lambda: instance.admit_draft(evidence, session=Session())).code == "LEGAL_CORPUS_PROVISIONING_DOCUMENT_DIVERGENCE"
    assert events == ["document_read", "authority_read"]
    assert documents.write_sessions == [] and authorities.write_sessions == []
    divergent_authority = _evidence(actor_representation="different-actor")
    instance, documents, authorities, events = _service(corpus.get_institutional_charter_draft(), divergent_authority, [])
    assert _error(lambda: instance.admit_draft(evidence, session=Session())).code == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DIVERGENCE"
    assert events == ["document_read", "authority_read"]
    assert documents.write_sessions == [] and authorities.write_sessions == []


def test_document_write_failure_stops_evidence_write_and_preserves_cause() -> None:
    cause = LegalDocumentRegistryError("DOCUMENT_CREATE_FAILED")
    instance, documents, authorities, events = _service(events=[])
    documents.write_failure = cause
    failure = _error(lambda: instance.admit_draft(_evidence(), session=Session()))
    assert failure.code == "LEGAL_CORPUS_PROVISIONING_DOCUMENT_WRITE_FAILED"
    assert failure.__cause__ is cause
    assert events == ["document_read", "authority_read", "document_write"]
    assert authorities.write_sessions == []


def test_authority_write_failure_propagates_without_compensation_or_commit() -> None:
    cause = LegalCorpusProvisioningAuthorityRegistryError("CREATE_FAILED")
    instance, documents, authorities, events = _service(events=[])
    authorities.write_failure = cause
    failure = _error(lambda: instance.admit_draft(_evidence(), session=Session()))
    assert failure.code == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_WRITE_FAILED"
    assert failure.__cause__ is cause
    assert events == ["document_read", "authority_read", "document_write", "authority_write"]
    assert not hasattr(documents, "delete")


def test_preflight_read_failures_are_bounded_and_do_not_write() -> None:
    document_failure = LegalDocumentRegistryError("READ_FAILED")
    instance, documents, authorities, events = _service(events=[])
    documents.read_failure = document_failure
    failure = _error(lambda: instance.admit_draft(_evidence(), session=Session()))
    assert failure.code == "LEGAL_CORPUS_PROVISIONING_PAIR_PREFLIGHT_FAILED"
    assert failure.__cause__ is document_failure
    assert events == ["document_read"]
    assert authorities.read_sessions == [] and documents.write_sessions == []
    authority_failure = LegalCorpusProvisioningAuthorityRegistryError("READ_FAILED")
    instance, documents, authorities, events = _service(corpus.get_institutional_charter_draft(), None, [])
    authorities.read_failure = authority_failure
    failure = _error(lambda: instance.admit_draft(_evidence(), session=Session()))
    assert failure.code == "LEGAL_CORPUS_PROVISIONING_PAIR_PREFLIGHT_FAILED"
    assert failure.__cause__ is authority_failure
    assert events == ["document_read", "authority_read"]
    assert documents.write_sessions == []


def test_transaction_and_index_lifecycle_are_not_owned_by_service() -> None:
    source = Path("tools/eos/legal_operations/service/legal_corpus_provisioning_service.py").read_text(encoding="utf-8")
    forbidden = ("MongoClient", "start_session", "start_transaction", "commit_transaction", "abort_transaction", "UnknownTransactionCommitResult", "time.sleep", "ensure_indexes")
    assert not any(token in source for token in forbidden)
    assert "LegalAcceptanceRegistry" not in source
    assert "tenant_id" not in source and "principal_id" not in source
    instance, documents, authorities, _events = _service()
    result = instance.admit_draft(_evidence(), session=Session())
    assert result.state is service_module.LegalCorpusProvisioningResultState.PENDING_COMMIT
    assert documents.ensure_indexes_called is False and authorities.ensure_indexes_called is False


def test_service_import_and_operation_have_no_live_persistence_surface() -> None:
    source = Path("tools/eos/legal_operations/service/legal_corpus_provisioning_service.py").read_text(encoding="utf-8")
    tree = __import__("ast").parse(source)
    imports = [node.module or "" for node in __import__("ast").walk(tree) if isinstance(node, __import__("ast").ImportFrom)]
    imports.extend(alias.name for node in __import__("ast").walk(tree) if isinstance(node, __import__("ast").Import) for alias in node.names)
    assert not any(token in module.casefold() for module in imports for token in ("pymongo", "http", "fastapi", "browser"))
    assert "resolve_platform_legal_corpus_draft" in source
    assert "LegalDocumentRegistry" in source and "LegalCorpusProvisioningAuthorityRegistry" in source


# ARTIFACT: test_legal_corpus_provisioning_service.py
# VERSION: v1.2.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-PROVISIONING-SERVICE-CERT
# AUTHORITY BOUNDARY: direct service certificate only; staged composition is not committed persistence
# TENANT POSTURE: PLATFORM corpus admission; no tenant/principal authority
# FAIL-CLOSED POSTURE: transaction, source, pair-state, divergence, and dependency failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
