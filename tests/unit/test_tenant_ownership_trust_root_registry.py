"""Unit tests for governed ownership trust-root enrollment."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.auth.tenant_ownership_trust_root_registry import (
    GovernedTrustRootRegistry,
    TrustRootEnrollmentRequest,
    TrustRootError,
    VerifiedTrustRootEnrollment,
)


class Session:
    def in_transaction(self) -> bool:
        return True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def create_index(self, *args: Any, **kwargs: Any) -> None:
        return None

    def find_one(self, query: dict[str, Any], **kwargs: Any) -> dict[str, Any] | None:
        rows = [row for row in self.rows if all(row.get(k) == v for k, v in query.items() if not isinstance(v, dict))]
        if "valid_from" in query:
            rows = [row for row in rows if row["valid_from"] <= query["valid_from"]["$lte"] and row["valid_until"] > query["valid_until"]["$gt"]]
        return max(rows, key=lambda row: row.get("revision", 0), default=None)

    def insert_one(self, document: dict[str, Any], **kwargs: Any) -> None:
        self.rows.append(dict(document))


class Database:
    def __init__(self) -> None:
        self.collections: dict[str, Collection] = {}

    def __getitem__(self, name: str) -> Collection:
        return self.collections.setdefault(name, Collection())


class Verifier:
    def verify(self, request: TrustRootEnrollmentRequest) -> VerifiedTrustRootEnrollment:
        return VerifiedTrustRootEnrollment(
            request=request, verified_at=datetime.now(timezone.utc),
            governance_verifier_id="governance-verifier",
            governance_verifier_version="1.0",
            governance_proof_fingerprint="proof-fingerprint",
        )


def request(**changes: Any) -> TrustRootEnrollmentRequest:
    now = datetime(2026, 11, 2, tzinfo=timezone.utc)
    values: dict[str, Any] = {
        "trust_root_reference": "root-1", "fingerprint": "sha3-root",
        "jurisdiction": "ZA", "authority_scope": "TENANT_OWNERSHIP_ISSUER",
        "issuer_identity": "independent-issuer", "key_id": "key-1", "key_revision": 1,
        "valid_from": now, "valid_until": now + timedelta(days=365),
        "governance_decision_reference": "decision-1",
        "governance_decision_fingerprint": "decision-fp",
        "approver_subjects": ("governor-a", "governor-b"), "required_approvals": 2,
    }
    values.update(changes)
    return TrustRootEnrollmentRequest(**values)


def test_enrollment_requires_caller_owned_transaction() -> None:
    registry = GovernedTrustRootRegistry(Database(), Verifier())
    with pytest.raises(Exception, match="ACTIVE_TRANSACTION_REQUIRED"):
        registry.enroll(request(), session=None)


def test_enrollment_requires_independent_governance_quorum() -> None:
    registry = GovernedTrustRootRegistry(Database(), Verifier())
    with pytest.raises(TrustRootError, match="INDEPENDENT_GOVERNANCE_QUORUM_REQUIRED"):
        registry.enroll(request(required_approvals=1), session=Session())


def test_issuer_cannot_approve_own_trust_root() -> None:
    registry = GovernedTrustRootRegistry(Database(), Verifier())
    with pytest.raises(TrustRootError, match="ISSUER_CANNOT_APPROVE_OWN_TRUST_ROOT"):
        registry.enroll(
            request(approver_subjects=("independent-issuer", "governor-b")),
            session=Session(),
        )


def test_only_governance_verifier_result_can_be_enrolled() -> None:
    class Deny:
        def verify(self, request: TrustRootEnrollmentRequest) -> object:
            return object()

    registry = GovernedTrustRootRegistry(Database(), Deny())  # type: ignore[arg-type]
    with pytest.raises(TrustRootError, match="GOVERNANCE_VERIFICATION_RESULT_INVALID"):
        registry.enroll(request(), session=Session())


def test_valid_governed_enrollment_is_persisted_and_current() -> None:
    database = Database()
    registry = GovernedTrustRootRegistry(database, Verifier())
    record = registry.enroll(request(), session=Session())
    assert record.revision == 1
    assert record.approver_subjects == ("governor-a", "governor-b")
    current = registry.current(
        "root-1", at=record.enrolled_at + timedelta(days=1), session=Session()
    )
    assert current == record
    assert len(database["tenant_ownership_trust_root_events"].rows) == 1


def test_wrong_scope_and_duplicate_approvers_are_denied() -> None:
    registry = GovernedTrustRootRegistry(Database(), Verifier())
    with pytest.raises(TrustRootError, match="TRUST_ROOT_SCOPE_INVALID"):
        registry.enroll(request(authority_scope="TENANT_ADMIN"), session=Session())
    with pytest.raises(TrustRootError, match="INDEPENDENT_GOVERNANCE_APPROVALS_INSUFFICIENT"):
        registry.enroll(
            request(approver_subjects=("governor-a", "governor-a")),
            session=Session(),
        )
