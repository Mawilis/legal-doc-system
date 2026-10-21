"""TITLE: WILSY P9 Practitioner Access Evidence Evaluation Service Tests.
VERSION: v1.1.0-R59-P47-CODEC-EVALUATION-TESTS
AUTHORITY: Test-first, read-only documentary evaluation.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_practitioner_matter_access_evaluation_service.py
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.1.0-R59-P47-CODEC-EVALUATION-TESTS
    Freeze end-to-end read/projection and fail-closed boundaries.
    2026-10-21 v1.1.0-R59-P47-CODEC-EVALUATION-TESTS
    Migrate fixtures to canonical P47 service-owned codec;
    preserve all documentary assertions and denial cases.
TENANT BOUNDARY: Exact tenant/matter/practitioner.
AUTHORITY BOUNDARY: No IAM admission, issuer authority or matter access.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from datetime import datetime, timedelta, timezone
from importlib import import_module

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision as Decision,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    create_practitioner_matter_access,
    encode_practitioner_matter_access,
)

MODULE = (
    "tools.eos.legal_operations.service."
    "legal_practitioner_matter_access_evaluation_service"
)
AT = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class Collection:
    def __init__(self, docs):
        self.docs = docs
        self.calls = []

    def find(self, predicate, *, session):
        self.calls.append((predicate, session))
        return iter(self.docs)


def _evidence(eid="policy-1", decision=Decision.ALLOW, until=None):
    return create_practitioner_matter_access(
        access_evidence_id=eid,
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        revision=1,
        decision=decision,
        effective_from=AT - timedelta(hours=1),
        effective_until=until,
        issued_by_principal_id="issuer-1",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=None,
    )


def _evaluate(docs, **changes):
    collection = Collection(docs)
    kwargs = dict(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        evaluation_time=AT,
        collection=collection,
        session=Session(),
    )
    kwargs.update(changes)
    result = import_module(MODULE).evaluate_practitioner_matter_access_evidence(
        **kwargs
    )
    return result, collection


def test_empty_history_fails_closed():
    result, _ = _evaluate(())
    assert result.state.value == "NO_APPLICABLE_EVIDENCE"
    assert result.permits_access is False


def test_single_allow_is_documentary_only():
    result, _ = _evaluate((encode_practitioner_matter_access(_evidence()),))
    assert result.state.value == "ALLOW_UNVERIFIED"
    assert result.permits_access is False


def test_explicit_deny_blocks_allow():
    result, _ = _evaluate((
        encode_practitioner_matter_access(_evidence()),
        encode_practitioner_matter_access(_evidence("policy-2", Decision.DENY)),
    ))
    assert result.state.value == "DENY_BLOCKED"


def test_expired_allow_is_not_current():
    result, _ = _evaluate((encode_practitioner_matter_access(_evidence(until=AT)),))
    assert result.state.value == "NO_APPLICABLE_EVIDENCE"


def test_reader_receives_exact_scoped_predicate():
    result, collection = _evaluate(())
    assert result.permits_access is False
    assert collection.calls[0][0] == {
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "practitioner-1",
    }


def test_missing_transaction_rejected():
    with pytest.raises(ValueError):
        _evaluate((), session=object())


def test_invalid_persisted_fingerprint_rejected():
    doc = encode_practitioner_matter_access(_evidence())
    doc["fingerprint"] = ""
    with pytest.raises(ValueError):
        _evaluate((doc,))


def test_cross_tenant_document_rejected():
    doc = encode_practitioner_matter_access(_evidence())
    doc["tenant_id"] = "tenant-other"
    with pytest.raises(ValueError):
        _evaluate((doc,))


def test_no_access_grant_or_issuance_interface():
    module = import_module(MODULE)
    for name in (
        "grant_matter_access", "issue_matter_access",
        "authorize_matter_access", "persist_policy",
        "execute_reassignment", "override_ethical_wall",
    ):
        assert not hasattr(module, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_evaluation_service.py
# VERSION: v1.1.0-R59-P47-CODEC-EVALUATION-TESTS
# AUTHORITY: READ-ONLY DOCUMENTARY EVALUATION
# END OF WILSY OS SOVEREIGN ARTIFACT
