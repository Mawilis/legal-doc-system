"""TITLE: WILSY OS G65 Canonical Membership/Acknowledgement Real-Mongo Certificate.
VERSION: v1.0.0-G65-REAL-MONGO-CERT
AUTHORITY: Disposable transactional source-read evidence only.
EPITOME: Certify actual MongoDB replica-set transaction reads, exact scope, revision binding, fingerprint integrity, expiry and revocation denial for G65.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_work_ethical_wall_membership_acknowledgement_real_mongo.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-28.
CHANGELOG: 2026-10-28 v1.0.0 adds disposable real-Mongo G65 source certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Unique disposable database; no production URI; no content access.
TENANT BOUNDARY: Exact tenant/matter/principal/policy/revision predicates.
AUTHORITY BOUNDARY: Source-read evidence only; no institutional ratification or access grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import json
import os
import uuid
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.service.legal_work_ethical_wall_membership_acknowledgement import (
    CanonicalWallEvidenceUnavailable,
    CanonicalWallMembershipAcknowledgementSource,
)

URI = os.environ["WILSY_G65_REAL_MONGO_URI"]
NOW = datetime(2026, 10, 28, 18, 0, tzinfo=UTC)


def _fingerprint(document: dict[str, object]) -> str:
    payload = {
        key: value for key, value in document.items()
        if key not in {"_id", "fingerprint"}
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=lambda value: value.astimezone(UTC).isoformat()
        if type(value) is datetime else str(value),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _membership(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "tenant_id": "tenant-g65-a",
        "case_matter_id": "matter-g65-a",
        "practitioner_principal_id": "practitioner-g65-a",
        "membership_id": "membership-g65-a",
        "revision": 1,
        "status": "ACTIVE",
        "effective_at": NOW - timedelta(days=1),
        "expires_at": NOW + timedelta(days=1),
        "revoked_at": None,
        "issuer_id": "institution-issuer-g65",
        "issuer_evidence_reference": "membership-evidence-g65-a",
        "fingerprint": "",
    }
    value.update(changes)
    value["fingerprint"] = _fingerprint(value)
    return value


def _acknowledgement(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "tenant_id": "tenant-g65-a",
        "case_matter_id": "matter-g65-a",
        "practitioner_principal_id": "practitioner-g65-a",
        "policy_id": "wall-g65-a",
        "policy_revision_fingerprint": "policy-revision-g65-a",
        "acknowledgement_id": "acknowledgement-g65-a",
        "revision": 1,
        "status": "ACTIVE",
        "acknowledged_at": NOW - timedelta(hours=1),
        "expires_at": NOW + timedelta(days=1),
        "revoked_at": None,
        "issuer_id": "institution-issuer-g65",
        "issuer_evidence_reference": "acknowledgement-evidence-g65-a",
        "fingerprint": "",
    }
    value.update(changes)
    value["fingerprint"] = _fingerprint(value)
    return value


@pytest.fixture()
def context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI, serverSelectionTimeoutMS=5_000, tz_aware=True, tzinfo=UTC,
    )
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True and hello.get("setName")
    database = client["wilsy_g65_" + uuid.uuid4().hex]
    memberships = database["ethical_wall_memberships"]
    acknowledgements = database["ethical_wall_acknowledgements"]
    source = CanonicalWallMembershipAcknowledgementSource(
        membership_collection=memberships,
        acknowledgement_collection=acknowledgements,
    )
    try:
        yield client, database, memberships, acknowledgements, source
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_mongo_transaction_reads_exact_current_membership_and_ack(context: Any) -> None:
    client, _, memberships, acknowledgements, source = context
    memberships.insert_one(_membership())
    acknowledgements.insert_one(_acknowledgement())
    with client.start_session() as session:
        with session.start_transaction():
            membership = source.resolve_membership(
                tenant_id="tenant-g65-a", case_matter_id="matter-g65-a",
                practitioner_principal_id="practitioner-g65-a",
                evaluation_time=NOW, session=session,
            )
            acknowledgement = source.resolve_acknowledgement(
                tenant_id="tenant-g65-a", case_matter_id="matter-g65-a",
                practitioner_principal_id="practitioner-g65-a", policy_id="wall-g65-a",
                policy_revision_fingerprint="policy-revision-g65-a",
                evaluation_time=NOW, session=session,
            )
            assert membership.membership_id == "membership-g65-a"
            assert acknowledgement.acknowledgement_id == "acknowledgement-g65-a"
            assert membership.tenant_id == acknowledgement.tenant_id
            assert membership.case_matter_id == acknowledgement.case_matter_id
            assert membership.practitioner_principal_id == acknowledgement.practitioner_principal_id


@pytest.mark.parametrize(
    "tenant_id,case_matter_id,principal_id,policy_fingerprint",
    [
        ("tenant-g65-foreign", "matter-g65-a", "practitioner-g65-a", "policy-revision-g65-a"),
        ("tenant-g65-a", "matter-g65-foreign", "practitioner-g65-a", "policy-revision-g65-a"),
        ("tenant-g65-a", "matter-g65-a", "practitioner-g65-foreign", "policy-revision-g65-a"),
        ("tenant-g65-a", "matter-g65-a", "practitioner-g65-a", "prior-policy-revision"),
    ],
)
def test_real_mongo_foreign_scope_or_prior_revision_denies(
    context: Any, tenant_id: str, case_matter_id: str, principal_id: str,
    policy_fingerprint: str,
) -> None:
    client, _, memberships, acknowledgements, source = context
    memberships.insert_one(_membership())
    acknowledgements.insert_one(_acknowledgement())
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(CanonicalWallEvidenceUnavailable):
                if policy_fingerprint == "prior-policy-revision":
                    source.resolve_acknowledgement(
                        tenant_id=tenant_id, case_matter_id=case_matter_id,
                        practitioner_principal_id=principal_id, policy_id="wall-g65-a",
                        policy_revision_fingerprint=policy_fingerprint,
                        evaluation_time=NOW, session=session,
                    )
                else:
                    source.resolve_membership(
                        tenant_id=tenant_id, case_matter_id=case_matter_id,
                        practitioner_principal_id=principal_id,
                        evaluation_time=NOW, session=session,
                    )


@pytest.mark.parametrize(
    "changes,expected_code",
    [
        ({"expires_at": NOW}, "G65_MEMBERSHIP_EXPIRED"),
        ({"revoked_at": NOW - timedelta(seconds=1)}, "G65_MEMBERSHIP_REVOKED"),
    ],
)
def test_real_mongo_expired_or_revoked_membership_denies(
    context: Any, changes: dict[str, object], expected_code: str,
) -> None:
    client, _, memberships, _, source = context
    memberships.insert_one(_membership(**changes))
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(CanonicalWallEvidenceUnavailable, match=expected_code):
                source.resolve_membership(
                    tenant_id="tenant-g65-a", case_matter_id="matter-g65-a",
                    practitioner_principal_id="practitioner-g65-a",
                    evaluation_time=NOW, session=session,
                )


def test_real_mongo_duplicate_active_memberships_deny(context: Any) -> None:
    client, _, memberships, _, source = context
    memberships.insert_one(_membership())
    memberships.insert_one(_membership(membership_id="membership-g65-duplicate", revision=2))
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(CanonicalWallEvidenceUnavailable, match="MISSING_OR_AMBIGUOUS"):
                source.resolve_membership(
                    tenant_id="tenant-g65-a", case_matter_id="matter-g65-a",
                    practitioner_principal_id="practitioner-g65-a",
                    evaluation_time=NOW, session=session,
                )


# ARTIFACT: test_legal_work_ethical_wall_membership_acknowledgement_real_mongo.py
# VERSION: v1.0.0-G65-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical source-read certification only; no access grant
# TENANT POSTURE: exact tenant/matter/principal/policy/revision predicates
# FAIL-CLOSED POSTURE: absent, duplicate, foreign, expired or revoked evidence denies
# FINANCIAL EXECUTION AUTHORITY: None
# END OF WILSY OS SOVEREIGN ARTIFACT
