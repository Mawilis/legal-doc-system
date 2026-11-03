"""WILSY OS certification tests for one-time membership-selection and MFA challenges.

TITLE: Membership Selection Challenge Unit Certification
VERSION: v1.0.1-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE-TESTS
AUTHORITY: Verifies challenge lifecycle boundaries; grants no runtime authority.
EPITOME: Exercises one-time challenge use, transaction requirements, exact
         EOS authority revalidation and credential/membership/capacity revision binding.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_membership_selection_challenge.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.0.1-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE-TESTS makes test doubles
    explicit to Pyright without changing runtime assertions.
    v1.0.0 adds adversarial unit coverage for selection and MFA challenge
    issuance, consumption, expiry, replay, stale revisions and transaction gates.
COMPLIANCE: Test artifact for POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Uses synthetic principals and fake persistence only;
    no production credentials, challenge secrets or tenant data are accessed.
TENANT BOUNDARY: Every selected membership and capacity is exact principal/tenant scoped.
AUTHORITY BOUNDARY: Tests challenge orchestration only; no role or permission is created.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, cast

from pymongo.collection import Collection as MongoCollection
from types import SimpleNamespace

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.membership_selection_challenge import (
    MFA_PURPOSE,
    SELECTION_PURPOSE,
    MembershipSelectionChallengeError,
    MembershipSelectionChallengeRejected,
    MembershipSelectionChallengeService,
)


class Transaction:
    """Minimal caller-owned transaction marker for service unit tests."""

    in_transaction = True


class ChallengeCollection:
    """In-memory Mongo collection double with atomic single-document consumption."""

    def __init__(self):
        self.documents = []
        self.indexes = []

    def create_index(self, keys, **options):
        """Record deterministic index declarations without changing test semantics."""
        self.indexes.append((keys, options))
        return options.get("name", "test-index")

    def insert_one(self, document, session=None):
        """Insert a copied challenge record and reject duplicate token digests."""
        if any(row["challenge_digest"] == document["challenge_digest"] for row in self.documents):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate challenge digest")
        self.documents.append(dict(document))
        return SimpleNamespace(inserted_id=len(self.documents))

    def find_one(self, query, session=None):
        """Read one exact unconsumed challenge without changing its state."""
        for row in self.documents:
            if any(row.get(key) != value for key, value in query.items() if key != "expires_at"):
                continue
            expiry = query.get("expires_at", {}).get("$gt")
            if expiry is not None and not row["expires_at"] > expiry:
                continue
            return dict(row)
        return None

    def find_one_and_update(self, query, update, return_document=None, session=None):
        """Atomically match purpose, digest, expiry and unused state."""
        for row in self.documents:
            if any(row.get(key) != value for key, value in query.items() if key != "expires_at"):
                continue
            expiry = query.get("expires_at", {}).get("$gt")
            if expiry is not None and not row["expires_at"] > expiry:
                continue
            row.update(update["$set"])
            return dict(row)
        return None


class PrincipalRepository:
    """Injectable global principal authority reader."""

    def __init__(self, status=PrincipalStatus.ACTIVE):
        self.status = status

    def get(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, status=self.status)


class CredentialRepository:
    """Injectable tenant-neutral credential revision reader."""

    def __init__(self, revision=4, mfa_enabled=True):
        self.revision = revision
        self.mfa_enabled = mfa_enabled

    def get_by_principal(self, principal_id, *, session=None):
        return SimpleNamespace(
            principal_id=principal_id,
            credential_revision=self.revision,
            mfa_enabled=self.mfa_enabled,
        )


class MembershipRepository:
    """Injectable exact principal/tenant membership reader."""

    def __init__(self, revision=8, status=TenantMembershipStatus.ACTIVE):
        self.revision = revision
        self.status = status

    def resolve(self, principal_id, tenant_id, *, session=None):
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            revision=self.revision,
            status=self.status,
        )


class BusinessRoleRepository:
    """Injectable exact principal/tenant/business-capacity reader."""

    def __init__(self, revision=11, status=TenantBusinessRoleStatus.ACTIVE):
        self.revision = revision
        self.status = status

    def resolve_business_role(self, principal_id, tenant_id, business_role, *, session=None):
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            business_role=business_role,
            revision=self.revision,
            status=self.status,
        )


def make_service(
    *,
    principal_status=PrincipalStatus.ACTIVE,
    credential_revision=4,
    mfa_enabled=True,
    membership_revision=8,
    membership_status=TenantMembershipStatus.ACTIVE,
    capacity_revision=11,
    capacity_status=TenantBusinessRoleStatus.ACTIVE,
):
    """Construct a challenge service with isolated, explicit authority doubles."""
    collection = ChallengeCollection()
    principal = PrincipalRepository(principal_status)
    credential = CredentialRepository(credential_revision, mfa_enabled)
    membership = MembershipRepository(membership_revision, membership_status)
    capacity = BusinessRoleRepository(capacity_revision, capacity_status)
    service = MembershipSelectionChallengeService(
        collection=cast(MongoCollection, collection),
        principal_repository=principal,
        credential_repository=credential,
        membership_repository=membership,
        business_role_repository=capacity,
        tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    )
    return service, collection, principal, credential, membership, capacity


def issue_selection(service, *, now=None):
    """Issue a deterministic-time selection capability for one synthetic principal."""
    return service.issue_membership_selection_challenge(
        principal_id="principal-1",
        credential_revision=4,
        session=Transaction(),
        now=now,
    )


def select_capacity(service, receipt, *, now=None):
    """Consume selection capability and select one explicit business capacity."""
    return service.select_membership_and_issue_mfa_challenge(
        selection_challenge_token=receipt.challenge_token,
        tenant_id="tenant-1",
        business_role="tenant_owner",
        session=Transaction(),
        now=now,
    )


def test_selection_challenge_persists_only_digest_and_is_tenant_neutral():
    service, collection, *_ = make_service()
    receipt = issue_selection(service)
    stored = collection.documents[0]
    assert receipt.challenge_token not in repr(stored)
    assert stored["challenge_digest"] != receipt.challenge_token
    assert stored["purpose"] == SELECTION_PURPOSE
    assert stored["principal_id"] == "principal-1"
    assert "tenant_id" not in stored
    assert "business_role" not in stored
    assert receipt.challenge_token not in repr(receipt)


def test_selection_issues_mfa_challenge_bound_to_exact_revisions_and_workspace():
    service, collection, *_ = make_service()
    selection = issue_selection(service)
    mfa = select_capacity(service, selection)
    stored = collection.documents[1]
    assert mfa.principal_id == "principal-1"
    assert mfa.tenant_id == "tenant-1"
    assert mfa.business_role == "tenant_owner"
    assert mfa.workspace_id == "EXECUTIVE_COMMAND_CENTRE"
    assert (mfa.credential_revision, mfa.membership_revision, mfa.capacity_revision) == (4, 8, 11)
    assert stored["purpose"] == MFA_PURPOSE
    assert stored["membership_revision"] == 8
    assert stored["capacity_revision"] == 11
    assert stored["workspace_id"] == "EXECUTIVE_COMMAND_CENTRE"
    assert mfa.challenge_token not in repr(stored)


def test_mfa_challenge_consumption_revalidates_and_returns_current_selection():
    service, *_ = make_service()
    selection = issue_selection(service)
    mfa = select_capacity(service, selection)
    selected = service.consume_mfa_challenge_after_factor_verification(
        mfa_challenge_token=mfa.challenge_token,
        session=Transaction(),
    )
    assert selected.principal_id == "principal-1"
    assert selected.tenant_id == "tenant-1"
    assert selected.business_role == "tenant_owner"
    assert selected.workspace_id == "EXECUTIVE_COMMAND_CENTRE"
    assert selected.credential_revision == 4
    assert selected.membership_revision == 8
    assert selected.capacity_revision == 11


def test_selection_challenge_context_is_read_only_and_revision_bound():
    service, collection, *_ = make_service()
    receipt = issue_selection(service)
    context = service.get_selection_challenge_context(
        selection_challenge_token=receipt.challenge_token,
        session=Transaction(),
    )
    assert context.principal_id == "principal-1"
    assert context.credential_revision == 4
    assert collection.documents[0]["consumed_at"] is None


def test_mfa_factor_context_is_read_only_and_principal_bound():
    service, collection, *_ = make_service()
    mfa = select_capacity(service, issue_selection(service))
    context = service.get_mfa_challenge_factor_context(
        mfa_challenge_token=mfa.challenge_token,
        session=Transaction(),
    )
    assert context.principal_id == "principal-1"
    assert context.credential_revision == 4
    assert collection.documents[1]["consumed_at"] is None


def test_selection_challenge_is_single_use():
    service, *_ = make_service()
    selection = issue_selection(service)
    select_capacity(service, selection)
    with pytest.raises(MembershipSelectionChallengeRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
        select_capacity(service, selection)


def test_mfa_challenge_is_single_use():
    service, *_ = make_service()
    mfa = select_capacity(service, issue_selection(service))
    service.consume_mfa_challenge_after_factor_verification(
        mfa_challenge_token=mfa.challenge_token,
        session=Transaction(),
    )
    with pytest.raises(MembershipSelectionChallengeRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
        service.consume_mfa_challenge_after_factor_verification(
            mfa_challenge_token=mfa.challenge_token,
            session=Transaction(),
        )


def test_selection_challenge_expiry_is_enforced():
    service, *_ = make_service()
    issued_at = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
    selection = issue_selection(service, now=issued_at)
    with pytest.raises(MembershipSelectionChallengeRejected, match="INVALID_EXPIRED_OR_CONSUMED"):
        select_capacity(service, selection, now=issued_at + timedelta(minutes=6))


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"principal_status": PrincipalStatus.SUSPENDED}, "PRINCIPAL_NOT_ACTIVE"),
        ({"credential_revision": 5}, "CREDENTIAL_REVISION_STALE"),
        ({"membership_status": TenantMembershipStatus.SUSPENDED}, "MEMBERSHIP_INACTIVE_OR_MISMATCHED"),
        ({"capacity_status": TenantBusinessRoleStatus.REVOKED}, "CAPACITY_INACTIVE_OR_MISMATCHED"),
        ({"membership_revision": 9}, "SELECTED_AUTHORITY_STALE"),
        ({"capacity_revision": 12}, "SELECTED_AUTHORITY_STALE"),
    ],
)
def test_stale_or_inactive_authority_rejects_selected_capacity(overrides, reason):
    service, *_ = make_service()
    selection = issue_selection(service)
    mfa = select_capacity(service, selection)
    if "principal_status" in overrides:
        cast(Any, service)._principals.status = overrides["principal_status"]
    if "credential_revision" in overrides:
        cast(Any, service)._credentials.revision = overrides["credential_revision"]
    if "membership_status" in overrides:
        cast(Any, service)._memberships.status = overrides["membership_status"]
    if "capacity_status" in overrides:
        cast(Any, service)._business_roles.status = overrides["capacity_status"]
    if "membership_revision" in overrides:
        cast(Any, service)._memberships.revision = overrides["membership_revision"]
    if "capacity_revision" in overrides:
        cast(Any, service)._business_roles.revision = overrides["capacity_revision"]
    with pytest.raises(MembershipSelectionChallengeRejected, match=reason):
        service.consume_mfa_challenge_after_factor_verification(
            mfa_challenge_token=mfa.challenge_token,
            session=Transaction(),
        )


def test_inactive_principal_cannot_issue_selection_challenge():
    service, *_ = make_service(principal_status=PrincipalStatus.SUSPENDED)
    with pytest.raises(MembershipSelectionChallengeRejected, match="PRINCIPAL_NOT_ACTIVE"):
        issue_selection(service)


def test_unenrolled_mfa_cannot_issue_a_selected_membership_challenge():
    service, *_ = make_service(mfa_enabled=False)
    with pytest.raises(MembershipSelectionChallengeRejected, match="MFA_ENROLLMENT_REQUIRED"):
        select_capacity(service, issue_selection(service))


def test_challenge_transition_requires_caller_owned_active_transaction():
    service, *_ = make_service()
    with pytest.raises(MembershipSelectionChallengeError, match="TRANSACTION_REQUIRED"):
        service.issue_membership_selection_challenge(
            principal_id="principal-1",
            credential_revision=4,
            session=SimpleNamespace(in_transaction=False),
        )


def test_index_contract_has_unique_digest_and_expiry_ttl():
    service, collection, *_ = make_service()
    service.ensure_indexes(cast(MongoCollection, collection))
    assert collection.indexes[0][1]["unique"] is True
    assert collection.indexes[0][1]["name"] == "eos_authentication_challenge_digest_unique"
    assert collection.indexes[1][1]["expireAfterSeconds"] == 0


# ARTIFACT: test_membership_selection_challenge.py
# VERSION: v1.0.1-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE-TESTS
# AUTHORITY BOUNDARY: challenge lifecycle certification only
# TENANT POSTURE: synthetic exact principal/tenant scope
# FAIL-CLOSED POSTURE: replay, expiry, stale revisions and inactive authority are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
