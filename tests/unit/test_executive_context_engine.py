"""WILSY OS direct certificate for the executive evidence context boundary.

TITLE: WILSY Executive Context Evidence Certificate
VERSION: v1.0.3-WILSY-EXECUTIVE-CONTEXT-CERT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS sovereign truth
EPITOME: Direct unit proof that authority plus verified evidence yields context, while no evidence yields no fact.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_executive_context_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.3 closes final independent adversarial positive-contract coverage for explicit source_version None/v2 preservation and direct/engine aware assembled_at preservation; frozen production v1.0.1 remained unchanged.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY: Receipt references are opaque provenance only; tests confer no authority.
TENANT BOUNDARY: KernelBootstrapRequest is the sole authority envelope; mixed scopes fail closed.
AUTHORITY BOUNDARY: No authentication, authorization, execution, persistence, retrieval, or model authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial execution authority.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from hashlib import sha3_512
from typing import Any

import pytest

from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.executive.intelligence.executive_context_engine import (
    VERSION,
    ExecutiveContext,
    ExecutiveContextEngine,
    ExecutiveContextError,
    ExecutiveEvidence,
    executive_context_engine,
)

TEST_VERSION = "v1.0.3-WILSY-EXECUTIVE-CONTEXT-CERT"
UTC = timezone.utc
RETRIEVED = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)
ASSEMBLED = datetime(2026, 9, 1, 8, 1, tzinfo=UTC)


def request() -> KernelBootstrapRequest:
    return KernelBootstrapRequest("tenant-a", "principal-a", "request-a", "corr-a")


def evidence(**overrides: object) -> ExecutiveEvidence:
    values: dict[str, Any] = {
        "evidence_id": "evidence-a", "tenant_id": "tenant-a", "principal_id": "principal-a",
        "request_id": "request-a", "source_id": "source-a", "source_type": "document",
        "source_locator": "repo://document/a", "citation_locator": "page:1", "content": "explicit fact",
        "content_sha3_512": sha3_512(b"explicit fact").hexdigest(), "authorization_receipt_ref": "receipt-a",
        "retrieved_at": RETRIEVED, "source_version": None,
    }
    values.update(overrides)
    return ExecutiveEvidence(**values)


def test_version_and_valid_evidence_contract() -> None:
    item = evidence(source_version="v2")
    none_version = evidence(source_version=None)
    assert TEST_VERSION == "v1.0.3-WILSY-EXECUTIVE-CONTEXT-CERT"
    assert VERSION == "v1.0.1-WILSY-EXECUTIVE-CONTEXT-EVIDENCE"
    assert item.source_version == "v2"
    assert none_version.source_version is None
    assert item.content == "explicit fact"
    with pytest.raises(FrozenInstanceError):
        item.content = "changed"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        item.extra = 1  # type: ignore[attr-defined]


@pytest.mark.parametrize("field", ["evidence_id", "tenant_id", "principal_id", "request_id", "source_id", "source_type", "source_locator", "citation_locator", "content", "authorization_receipt_ref"])
@pytest.mark.parametrize("value", ["", "   "])
def test_required_strings_reject_blank(field: str, value: str) -> None:
    with pytest.raises(ExecutiveContextError, match=f"^INVALID_EVIDENCE_FIELD:{field}$"):
        evidence(**{field: value})


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_checksum_rejects_with_checksum_code(value: str) -> None:
    with pytest.raises(ExecutiveContextError, match="^INVALID_CHECKSUM$"):
        evidence(content_sha3_512=value)


@pytest.mark.parametrize("field", ["evidence_id", "tenant_id", "principal_id", "request_id", "source_id", "authorization_receipt_ref"])
@pytest.mark.parametrize("value", ["unknown", "NONE", " null ", "Tenant-Default"])
def test_identity_sentinels_reject(field: str, value: str) -> None:
    with pytest.raises(ExecutiveContextError, match=f"^INVALID_EVIDENCE_FIELD:{field}$"):
        evidence(**{field: value})


@pytest.mark.parametrize("digest", ["a" * 127, "g" * 128, " " + sha3_512(b"explicit fact").hexdigest(), sha3_512(b"explicit fact").hexdigest() + " ", sha3_512(b"other").hexdigest(), 7, b"x", True, object()])
def test_checksum_fails_closed(digest: object) -> None:
    with pytest.raises(ExecutiveContextError, match="^INVALID_CHECKSUM$"):
        evidence(content_sha3_512=digest)


def test_checksum_uppercase_and_tamper() -> None:
    assert evidence(content_sha3_512=sha3_512(b"explicit fact").hexdigest().upper())
    with pytest.raises(ExecutiveContextError):
        evidence(content="tampered")


def test_optional_source_version_blank_rejected() -> None:
    with pytest.raises(ExecutiveContextError, match="^INVALID_EVIDENCE_FIELD:source_version$"):
        evidence(source_version="")
    with pytest.raises(ExecutiveContextError, match="^INVALID_EVIDENCE_FIELD:source_version$"):
        evidence(source_version="  ")


@pytest.mark.parametrize("value", [datetime(2026, 1, 1), "2026-01-01"])
def test_retrieved_at_must_be_aware_datetime(value: object) -> None:
    with pytest.raises(ExecutiveContextError, match="^INVALID_RETRIEVED_AT$"):
        evidence(retrieved_at=value)


def test_direct_context_boundary_and_properties() -> None:
    item = evidence()
    context = ExecutiveContext(request(), (item,), ASSEMBLED)
    assert context.evidence == (item,)
    assert context.assembled_at == ASSEMBLED
    assert (context.tenant_id, context.principal_id, context.request_id, context.correlation_id, context.evidence_count) == ("tenant-a", "principal-a", "request-a", "corr-a", 1)
    with pytest.raises(FrozenInstanceError):
        context.evidence = ()  # type: ignore[misc]
    with pytest.raises(AttributeError):
        context.extra = 1  # type: ignore[attr-defined]


def test_direct_context_rejects_non_tuple_and_scope_failures() -> None:
    item = evidence()
    for bad, code in [([item], "INVALID_EVIDENCE_TYPE"), ((x for x in [item]), "INVALID_EVIDENCE_TYPE"), ({item}, "INVALID_EVIDENCE_TYPE"), ((object(),), "INVALID_EVIDENCE_TYPE"), ((evidence(tenant_id="tenant-b"),), "TENANT_MISMATCH")]:
        with pytest.raises(ExecutiveContextError, match=f"^{code}$"):
            ExecutiveContext(request(), bad, ASSEMBLED)  # type: ignore[arg-type]
    with pytest.raises(ExecutiveContextError):
        ExecutiveContext(object(), (), ASSEMBLED)  # type: ignore[arg-type]
    with pytest.raises(ExecutiveContextError, match="^INVALID_ASSEMBLED_AT$"):
        ExecutiveContext(request(), (), datetime(2026, 1, 1))
    with pytest.raises(ExecutiveContextError, match="^INVALID_REQUEST_TYPE$"):
        ExecutiveContext(object(), (), ASSEMBLED)  # type: ignore[arg-type]
    with pytest.raises(ExecutiveContextError, match="^INVALID_ASSEMBLED_AT$"):
        ExecutiveContext(request(), (), "bad")  # type: ignore[arg-type]


def test_empty_context_is_factual_empty() -> None:
    context = executive_context_engine.assemble_context(request(), [], assembled_at=ASSEMBLED)
    assert context.evidence == ()
    assert context.evidence_count == 0
    assert (context.tenant_id, context.principal_id, context.request_id) == ("tenant-a", "principal-a", "request-a")
    assert context.assembled_at == ASSEMBLED
    assert not any(hasattr(context, name) for name in ("get_or_create_context", "update_domain_state", "export_context_state"))


def test_errors_do_not_leak_evidence_content() -> None:
    secret = "distinctive-secret-evidence"
    bad = evidence(tenant_id="tenant-b", content=secret, content_sha3_512=sha3_512(secret.encode()).hexdigest())
    with pytest.raises(ExecutiveContextError) as caught:
        executive_context_engine.assemble_context(request(), [bad])
    assert secret not in str(caught.value)


def test_engine_snapshots_lists_and_consumes_generator_once() -> None:
    item = evidence()
    supplied = [item]
    context = executive_context_engine.assemble_context(request(), supplied, assembled_at=ASSEMBLED)
    supplied.clear()
    assert context.evidence == (item,)
    assert context.assembled_at == ASSEMBLED
    count = 0
    def stream():
        nonlocal count
        count += 1
        yield item
    assert executive_context_engine.assemble_context(request(), stream(), assembled_at=ASSEMBLED).evidence_count == 1
    assert count == 1


@pytest.mark.parametrize("bad", [None, 7])
def test_engine_rejects_non_iterable(bad: object) -> None:
    with pytest.raises(ExecutiveContextError, match="^INVALID_EVIDENCE_TYPE$"):
        executive_context_engine.assemble_context(request(), bad)  # type: ignore[arg-type]


def test_engine_scope_duplicate_and_timestamp_fail_closed() -> None:
    item = evidence()
    cases = [(evidence(evidence_id="tenant-b-evidence", tenant_id="tenant-b"), "TENANT_MISMATCH"), (evidence(evidence_id="principal-b-evidence", principal_id="principal-b"), "PRINCIPAL_MISMATCH"), (evidence(evidence_id="request-b-evidence", request_id="request-b"), "REQUEST_MISMATCH"), (evidence(evidence_id="evidence-a", tenant_id="tenant-a", principal_id="principal-a", request_id="request-a", source_id="source-b", content="other", content_sha3_512=sha3_512(b"other").hexdigest()), "DUPLICATE_EVIDENCE_ID")]
    for bad, code in cases:
        with pytest.raises(ExecutiveContextError, match=f"^{code}$"):
            executive_context_engine.assemble_context(request(), [item, bad], assembled_at=ASSEMBLED)
    with pytest.raises(ExecutiveContextError, match="^INVALID_ASSEMBLED_AT$"):
        executive_context_engine.assemble_context(request(), [], assembled_at=datetime(2026, 1, 1))
    with pytest.raises(ExecutiveContextError, match="^INVALID_REQUEST_TYPE$"):
        executive_context_engine.assemble_context(object(), [], assembled_at=ASSEMBLED)  # type: ignore[arg-type]


def test_engine_invalid_element_code() -> None:
    with pytest.raises(ExecutiveContextError, match="^INVALID_EVIDENCE_TYPE$"):
        executive_context_engine.assemble_context(request(), [object()])  # type: ignore[list-item]


def test_engine_state_isolation_and_legacy_surface() -> None:
    engine = ExecutiveContextEngine()
    item_a = evidence()
    item_b = evidence(evidence_id="evidence-b", source_id="source-b", content="other", content_sha3_512=sha3_512(b"other").hexdigest())
    list_a, list_b = [item_a], [item_b]
    context_a = engine.assemble_context(request(), list_a, assembled_at=ASSEMBLED)
    context_b = engine.assemble_context(request(), list_b, assembled_at=ASSEMBLED)
    list_a.clear(); list_a.append(item_b); list_b.clear()
    assert context_a.evidence == (item_a,)
    assert context_b.evidence == (item_b,)
    for operation in ("get_or_create_context", "update_domain_state", "export_context_state"):
        assert not hasattr(engine, operation)
        assert not hasattr(executive_context_engine, operation)
    assert isinstance(executive_context_engine, ExecutiveContextEngine)


def test_engine_defaults_to_aware_utc_and_is_stateless() -> None:
    first = executive_context_engine.assemble_context(request(), [])
    second = executive_context_engine.assemble_context(request(), [])
    assert first.evidence_count == second.evidence_count == 0
    assert first.assembled_at.tzinfo is not None and first.assembled_at.utcoffset() is not None
    assert not hasattr(executive_context_engine, "_active_contexts")


# ARTIFACT: test_executive_context_engine.py
# VERSION: v1.0.3-WILSY-EXECUTIVE-CONTEXT-CERT
# AUTHORITY BOUNDARY: direct evidence-context certification only; no authority grant.
# TENANT POSTURE: KernelBootstrapRequest-bound and mixed-scope fail closed.
# FAIL-CLOSED POSTURE: malformed evidence and context are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
