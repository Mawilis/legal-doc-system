"""TITLE: WILSY P9 Practitioner Access Evidence History Reader Tests.
VERSION: v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
AUTHORITY: Immutable evidence reading only; no policy issuance.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_practitioner_matter_access_history_reader.py
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
    Freeze exact-scope, active-transaction, fail-closed history reads.
TENANT BOUNDARY: Exact tenant/matter/practitioner predicates.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from datetime import datetime, timezone
from importlib import import_module

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision as Decision,
    LegalPractitionerMatterAccessEvidence as Evidence,
)

MODULE = (
    "tools.eos.legal_operations.registry."
    "legal_practitioner_matter_access_history_reader"
)


def _api():
    return import_module(MODULE)


def _evidence():
    return _p47_create(
        access_evidence_id="policy-1",
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="principal-1",
        revision=1,
        decision=Decision.ALLOW,
        effective_from=datetime(2026, 10, 19, tzinfo=timezone.utc),
        effective_until=None,
        issued_by_principal_id="issuer-1",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=None,
    )


class Session:
    in_transaction = True


class Collection:
    def __init__(self, documents=(), error=None):
        self.documents = list(documents)
        self.error = error
        self.calls = []

    def find(self, predicate, *, session):
        self.calls.append((predicate, session))
        if self.error is not None:
            raise self.error
        return iter(self.documents)


def _read(collection, session=None, **changes):
    kwargs = dict(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="principal-1",
        collection=collection,
        session=Session() if session is None else session,
    )
    kwargs.update(changes)
    return _api().read_practitioner_matter_access_history(**kwargs)


def test_empty_history_is_not_authority():
    assert _read(Collection()) == ()


def test_exact_history_is_hydrated():
    value = _evidence()
    assert _read(Collection((_p47_encode(value),))) == (value,)


def test_mongo_id_metadata_is_not_policy_evidence():
    value = _evidence()
    assert _read(Collection(({**_p47_encode(value), "_id": "opaque"},))) == (value,)


def test_query_is_exactly_tenant_matter_practitioner():
    collection = Collection()
    session = Session()
    _read(collection, session=session)
    assert collection.calls == [(
        {
            "tenant_id": "tenant-1",
            "case_matter_id": "matter-1",
            "practitioner_principal_id": "principal-1",
        },
        session,
    )]


def test_missing_transaction_fails_before_find():
    collection = Collection()
    with pytest.raises(ValueError):
        _read(collection, session=object())
    assert collection.calls == []


def test_explicit_inactive_transaction_fails():
    class Inactive:
        in_transaction = False
    with pytest.raises(ValueError):
        _read(Collection(), session=Inactive())


def test_pseudo_tenant_fails():
    with pytest.raises(ValueError):
        _read(Collection(), tenant_id="global")


def test_cross_tenant_document_fails_closed():
    value = _p47_encode(_evidence())
    value["tenant_id"] = "tenant-other"
    with pytest.raises(ValueError):
        _read(Collection((value,)))


def test_missing_persisted_fingerprint_fails_closed():
    value = _p47_encode(_evidence())
    value["fingerprint"] = ""
    with pytest.raises(ValueError):
        _read(Collection((value,)))


def test_unrecognized_metadata_fails_closed():
    value = _p47_encode(_evidence())
    value["self_authorized"] = True
    with pytest.raises(ValueError):
        _read(Collection((value,)))


def test_persistence_failure_fails_closed():
    with pytest.raises(ValueError):
        _read(Collection(error=RuntimeError("storage unavailable")))


def test_overlong_history_fails_closed():
    value = _p47_encode(_evidence())
    with pytest.raises(ValueError):
        _read(Collection([value] * 129))


def test_replay_deduplicated_without_mutation():
    value = _evidence()
    assert _read(Collection((_p47_encode(value), _p47_encode(value)))) == (value,)


def test_no_policy_issuance_or_access_execution():
    module = _api()
    for name in (
        "grant_matter_access",
        "issue_matter_access",
        "revoke_matter_access",
        "authorize_matter_access",
        "persist_policy",
        "execute_reassignment",
    ):
        assert not hasattr(module, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_history_reader.py
# VERSION: v1.0.0-P9-R99-PRACTITIONER-ACCESS-HISTORY-READER
# AUTHORITY: READ-ONLY EVIDENCE
# END OF WILSY OS SOVEREIGN ARTIFACT

from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    create_practitioner_matter_access as _p47_create,
    encode_practitioner_matter_access as _p47_encode,
    decode_practitioner_matter_access as _p47_decode,
)
