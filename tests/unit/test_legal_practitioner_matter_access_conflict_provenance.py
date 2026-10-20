"""WILSY P9-R105-P4C-R2B conflict provenance RED certificate."""
from pathlib import Path
import runpy
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.service import (
    legal_practitioner_matter_access_conflict_provenance as provenance,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)["_make"]


class Session:
    in_transaction = True


def call(**changes):
    args = dict(
        evidence=MAKE(),
        matter_fingerprint="a" * 128,
        client_party_id="client-1",
        subject_identity_fingerprint="b" * 128,
        evaluation_time=MAKE().effective_from,
        disposition_collection=object(),
        session=Session(),
    )
    args.update(changes)
    return provenance.verify_current_conflict_provenance(**args)


def test_missing_transaction_denies_before_read(monkeypatch):
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context",
        lambda **kw: pytest.fail("DATABASE_ACCESSED"),
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call(session=None)


def test_inactive_transaction_denies(monkeypatch):
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context",
        lambda **kw: pytest.fail("DATABASE_ACCESSED"),
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call(session=SimpleNamespace(in_transaction=False))


def test_missing_history_denies(monkeypatch):
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context", lambda **kw: ()
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call()


def test_registry_outage_denies(monkeypatch):
    def unavailable(**kw):
        raise RuntimeError("unavailable")
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context", unavailable
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call()


def test_invalid_evidence_denies_before_read(monkeypatch):
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context",
        lambda **kw: pytest.fail("DATABASE_ACCESSED"),
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call(evidence=object())


@pytest.mark.parametrize("state", [
    "NO_DISPOSITION", "ENGAGEMENT_PROHIBITED",
    "ENGAGEMENT_UNRESOLVED", "AMBIGUOUS", "CORRUPT_BLOCKED",
])
def test_nonpermitted_currentness_denies(monkeypatch, state):
    item = MAKE()
    from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
        LegalClientMatterConflictDispositionCurrentnessState as State,
    )
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context",
        lambda **kw: (object(),),
    )
    monkeypatch.setattr(
        provenance, "project_legal_client_matter_conflict_disposition_currentness",
        lambda **kw: SimpleNamespace(state=State(state)),
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call(evidence=item)


def test_forged_positive_without_source_denies(monkeypatch):
    item = MAKE()
    from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
        LegalClientMatterConflictDispositionCurrentnessState as State,
    )
    monkeypatch.setattr(
        provenance, "list_dispositions_for_context",
        lambda **kw: (object(),),
    )
    monkeypatch.setattr(
        provenance, "project_legal_client_matter_conflict_disposition_currentness",
        lambda **kw: SimpleNamespace(
            state=State.ENGAGEMENT_PERMITTED,
            tenant_id=item.tenant_id,
            case_matter_id=item.case_matter_id,
            matter_fingerprint="a" * 128,
            client_party_id="client-1",
            subject_identity_fingerprint="b" * 128,
            evaluation_time=item.effective_from,
            corruption_evidence_fingerprints=(),
            decisive_disposition_fingerprints=(item.source_evidence_fingerprint,),
        ),
    )
    with pytest.raises(provenance.PractitionerMatterAccessConflictProvenanceDenied):
        call(evidence=item)


def test_no_issuance_or_access_mutation_interface():
    for name in ("issue", "append_evidence", "grant_access", "reassign"):
        assert not hasattr(provenance, name)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_conflict_provenance.py
# VERSION: v1.0.0-P9-R105-P4C-R2B-RED


# P9-R105-P4C-R2D: genuine immutable source objects and real pure projector.
from datetime import timedelta as _timedelta
import runpy as _runpy

_CANONICAL = _runpy.run_path(
    str(ROOT / "tests/unit/test_legal_client_matter_conflict_disposition.py")
)
_BUNDLE = _CANONICAL["bundle"]


def _canonical_provenance_case(monkeypatch, **changes):
    disposition = _BUNDLE()[0]
    evidence = MAKE(
        tenant_id=disposition.tenant_id,
        case_matter_id=disposition.case_matter_id,
        source_evidence_fingerprint=disposition.fingerprint,
    )
    history = changes.pop("history", (disposition,))
    captured = []

    def reader(**kwargs):
        captured.append(kwargs)
        return history

    monkeypatch.setattr(
        provenance, "list_dispositions_for_context", reader
    )
    args = dict(
        evidence=evidence,
        matter_fingerprint=disposition.matter_fingerprint,
        client_party_id=disposition.client_party_id,
        subject_identity_fingerprint=disposition.subject_identity_fingerprint,
        evaluation_time=disposition.effective_from,
        disposition_collection=object(),
        session=Session(),
    )
    args.update(changes)
    return disposition, args, captured


def test_real_canonical_permitted_history_satisfies_conflict_provenance(
    monkeypatch,
):
    disposition, args, captured = _canonical_provenance_case(monkeypatch)
    assert disposition.disposition.value == "ENGAGEMENT_PERMITTED"
    assert disposition.review_outcome.value == "NO_CONFLICT_IDENTIFIED"
    assert provenance.verify_current_conflict_provenance(**args) is None
    assert len(captured) == 1
    query = captured[0]
    assert query["tenant_id"] == disposition.tenant_id
    assert query["case_matter_id"] == disposition.case_matter_id
    assert query["matter_fingerprint"] == disposition.matter_fingerprint
    assert query["client_party_id"] == disposition.client_party_id
    assert query["subject_identity_fingerprint"] == (
        disposition.subject_identity_fingerprint
    )
    assert query["session"] is args["session"]


def test_real_canonical_permitted_history_wrong_fingerprint_denied(
    monkeypatch,
):
    disposition, args, _ = _canonical_provenance_case(monkeypatch)
    args["evidence"] = MAKE(
        tenant_id=disposition.tenant_id,
        case_matter_id=disposition.case_matter_id,
        source_evidence_fingerprint="f" * 128
        if disposition.fingerprint != "f" * 128 else "e" * 128,
    )
    with pytest.raises(
        provenance.PractitionerMatterAccessConflictProvenanceDenied
    ):
        provenance.verify_current_conflict_provenance(**args)


def test_real_canonical_future_only_history_denied(monkeypatch):
    _, args, _ = _canonical_provenance_case(monkeypatch)
    args["evaluation_time"] -= _timedelta(microseconds=1)
    with pytest.raises(
        provenance.PractitionerMatterAccessConflictProvenanceDenied
    ):
        provenance.verify_current_conflict_provenance(**args)


def test_real_canonical_history_wrong_scope_denied(monkeypatch):
    _, args, _ = _canonical_provenance_case(monkeypatch)
    args["evidence"] = MAKE(
        tenant_id="other-tenant",
        case_matter_id="other-matter",
    )
    with pytest.raises(
        provenance.PractitionerMatterAccessConflictProvenanceDenied
    ):
        provenance.verify_current_conflict_provenance(**args)


def test_real_canonical_history_wrong_subject_denied(monkeypatch):
    _, args, _ = _canonical_provenance_case(monkeypatch)
    old = args["subject_identity_fingerprint"]
    args["subject_identity_fingerprint"] = (
        "d" * 128 if old != "d" * 128 else "c" * 128
    )
    with pytest.raises(
        provenance.PractitionerMatterAccessConflictProvenanceDenied
    ):
        provenance.verify_current_conflict_provenance(**args)

# END OF WILSY OS SOVEREIGN ARTIFACT
