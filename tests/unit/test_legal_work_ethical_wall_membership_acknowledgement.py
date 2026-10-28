"""TITLE: WILSY OS G65 Membership/Acknowledgement Adversarial Certificate.
VERSION: v1.0.0-G65-CANONICAL-EVIDENCE-ADVERSARIAL-CERT
AUTHORITY: Negative and shape-validation tests only.
EPITOME: Certify strict transaction, scope, ambiguity, expiry, revocation and revision-bound acknowledgement behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_ethical_wall_membership_acknowledgement.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-28.
CHANGELOG: 2026-10-28 v1.0.0 adds focused G65 adversarial source tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tests never authorize content access.
TENANT BOUNDARY: Exact tenant/matter/principal/policy/revision required.
AUTHORITY BOUNDARY: Evidence projection is not institutional ratification.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

from tools.eos.legal_operations.service import legal_work_ethical_wall_membership_acknowledgement as source

NOW = datetime(2026, 10, 28, tzinfo=timezone.utc)


class Session:
    def in_transaction(self) -> bool:
        return True


class Cursor:
    def __init__(self, rows: tuple[dict[str, object], ...]) -> None:
        self.rows = rows

    def limit(self, count: int) -> "Cursor":
        return Cursor(self.rows[:count])


class Collection:
    def __init__(self, rows: tuple[dict[str, object], ...]) -> None:
        self.rows = rows
        self.queries: list[dict[str, object]] = []
        self.sessions: list[object] = []

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.queries.append(query)
        self.sessions.append(session)
        return Cursor(tuple(row for row in self.rows if all(row.get(k) == v for k, v in query.items())))


def seal(document: dict[str, object]) -> dict[str, object]:
    result = dict(document)
    payload = {key: value for key, value in result.items() if key not in {"fingerprint", "_id"}}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                         default=lambda value: value.isoformat() if type(value) is datetime else str(value)).encode()
    result["fingerprint"] = hashlib.sha256(encoded).hexdigest()
    return result


def membership(**changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "tenant_id": "tenant-a", "case_matter_id": "matter-a",
        "practitioner_principal_id": "practitioner-a", "membership_id": "member-a",
        "revision": 1, "status": "ACTIVE", "effective_at": NOW - timedelta(days=1),
        "expires_at": NOW + timedelta(days=1), "revoked_at": None,
        "issuer_id": "institution-issuer", "issuer_evidence_reference": "evidence-member-a",
        "fingerprint": "",
    }
    row.update(changes)
    return seal(row)


def acknowledgement(**changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "tenant_id": "tenant-a", "case_matter_id": "matter-a",
        "practitioner_principal_id": "practitioner-a", "policy_id": "wall-a",
        "policy_revision_fingerprint": "policy-fingerprint-a", "acknowledgement_id": "ack-a",
        "revision": 1, "status": "ACTIVE", "acknowledged_at": NOW - timedelta(hours=1),
        "expires_at": NOW + timedelta(days=1), "revoked_at": None,
        "issuer_id": "institution-issuer", "issuer_evidence_reference": "evidence-ack-a",
        "fingerprint": "",
    }
    row.update(changes)
    return seal(row)


def build(member_rows: tuple[dict[str, object], ...] | None = None,
          ack_rows: tuple[dict[str, object], ...] | None = None) -> tuple[source.CanonicalWallMembershipAcknowledgementSource, Collection, Collection]:
    members = Collection(member_rows if member_rows is not None else (membership(),))
    acknowledgements = Collection(ack_rows if ack_rows is not None else (acknowledgement(),))
    return source.CanonicalWallMembershipAcknowledgementSource(
        membership_collection=members, acknowledgement_collection=acknowledgements,
    ), members, acknowledgements


def test_current_membership_and_exact_revision_acknowledgement_are_projected() -> None:
    resolver, members, acknowledgements = build()
    session = Session()
    current = resolver.resolve_membership(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=session,
    )
    ack = resolver.resolve_acknowledgement(
        tenant_id="tenant-a", case_matter_id="matter-a", practitioner_principal_id="practitioner-a",
        policy_id="wall-a", policy_revision_fingerprint="policy-fingerprint-a",
        evaluation_time=NOW, session=session,
    )
    assert current.membership_id == "member-a"
    assert ack.acknowledgement_id == "ack-a"
    assert members.sessions == [session]
    assert acknowledgements.sessions == [session]
    assert current.fingerprint and ack.fingerprint
    assert source.SOURCE_VERIFIED_CLEARANCE is False
    assert source.OPERATIONAL_ACCESS_ENABLED is False


@pytest.mark.parametrize("session", [None, object()])
def test_inactive_transaction_fails_closed(session: object) -> None:
    resolver, _, _ = build()
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match="G65_TRANSACTION_REQUIRED"):
        resolver.resolve_membership(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=session,
        )


def test_cross_tenant_and_wrong_policy_revision_never_match() -> None:
    resolver, _, _ = build()
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match="MISSING_OR_AMBIGUOUS"):
        resolver.resolve_membership(
            tenant_id="tenant-b", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=Session(),
        )
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match="MISSING_OR_AMBIGUOUS"):
        resolver.resolve_acknowledgement(
            tenant_id="tenant-a", case_matter_id="matter-a", practitioner_principal_id="practitioner-a",
            policy_id="wall-a", policy_revision_fingerprint="older-revision",
            evaluation_time=NOW, session=Session(),
        )


def test_duplicate_evidence_is_ambiguous_and_denied() -> None:
    resolver, _, _ = build(member_rows=(membership(), membership(membership_id="member-b")))
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match="MISSING_OR_AMBIGUOUS"):
        resolver.resolve_membership(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=Session(),
        )


@pytest.mark.parametrize("changes,code", [
    ({"expires_at": NOW}, "G65_MEMBERSHIP_EXPIRED"),
    ({"revoked_at": NOW - timedelta(seconds=1)}, "G65_MEMBERSHIP_REVOKED"),
    ({"effective_at": NOW + timedelta(seconds=1)}, "G65_NOT_YET_EFFECTIVE"),
    ({"status": "REVOKED"}, "G65_EVIDENCE_MISSING_OR_AMBIGUOUS"),
])
def test_membership_expiry_revocation_and_inactive_state_deny(changes: dict[str, object], code: str) -> None:
    resolver, _, _ = build(member_rows=(membership(**changes),))
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match=code):
        resolver.resolve_membership(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=Session(),
        )


def test_tampered_fingerprint_denies() -> None:
    row = membership()
    row["membership_id"] = "tampered"
    resolver, _, _ = build(member_rows=(row,))
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match="G65_FINGERPRINT_INVALID"):
        resolver.resolve_membership(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=Session(),
        )


def test_acknowledgement_revocation_and_expiry_deny() -> None:
    for changes, code in [
        ({"revoked_at": NOW - timedelta(seconds=1)}, "G65_ACKNOWLEDGEMENT_REVOKED"),
        ({"expires_at": NOW}, "G65_ACKNOWLEDGEMENT_EXPIRED"),
    ]:
        resolver, _, _ = build(ack_rows=(acknowledgement(**changes),))
        with pytest.raises(source.CanonicalWallEvidenceUnavailable, match=code):
            resolver.resolve_acknowledgement(
                tenant_id="tenant-a", case_matter_id="matter-a", practitioner_principal_id="practitioner-a",
                policy_id="wall-a", policy_revision_fingerprint="policy-fingerprint-a",
                evaluation_time=NOW, session=Session(),
            )


def test_source_outage_is_content_free_denial() -> None:
    class BrokenCollection:
        def find(self, query: dict[str, object], *, session: object) -> Cursor:
            raise RuntimeError("private database detail")

    resolver = source.CanonicalWallMembershipAcknowledgementSource(
        membership_collection=BrokenCollection(), acknowledgement_collection=BrokenCollection(),
    )
    with pytest.raises(source.CanonicalWallEvidenceUnavailable, match="G65_MEMBERSHIP_SOURCE_UNAVAILABLE") as error:
        resolver.resolve_membership(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", evaluation_time=NOW, session=Session(),
        )
    assert "private database detail" not in str(error.value)


# ARTIFACT: test_legal_work_ethical_wall_membership_acknowledgement.py
# VERSION: v1.0.0-G65-CANONICAL-EVIDENCE-ADVERSARIAL-CERT
# AUTHORITY BOUNDARY: denial and source-shape certification only
# TENANT POSTURE: cross-scope evidence rejected
# FAIL-CLOSED POSTURE: ambiguous, absent, malformed, expired or revoked denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
