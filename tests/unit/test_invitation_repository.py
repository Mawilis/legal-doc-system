"""Unit certificate for the invitation authority and repository."""
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
from datetime import datetime, timedelta, timezone
import hashlib
import pytest
from pymongo.errors import DuplicateKeyError
from tools.eos.auth.invitation import InvitationAuthority, InvitationStatus, canonicalize_invitation_datetime
from tools.eos.auth.invitation_repository import (
    InvitationAlreadyConsumedError, InvitationAlreadyExistsError,
    InvitationConcurrentModificationError, InvitationExpiredError,
    InvitationNotFoundError, InvitationRepository, InvitationRevokedError,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
DIGEST = hashlib.sha3_512(b"synthetic-capability").hexdigest()

class FakeCollection:
    def __init__(self): self.rows = {}
    def insert_one(self, doc, session=None):
        if doc["invitation_id"] in self.rows or any(r["capability_digest"] == doc["capability_digest"] for r in self.rows.values()): raise DuplicateKeyError("duplicate")
        self.rows[doc["invitation_id"]] = dict(doc)
    def find_one(self, query, session=None):
        row = self.rows.get(query.get("invitation_id")); return dict(row) if row else None
    def find_one_and_update(self, query, update, return_document=None, session=None):
        row = self.rows.get(query.get("invitation_id"))
        if not row or any(row.get(k) != v for k, v in query.items() if k != "expires_at"): return None
        if row["expires_at"] <= query["expires_at"]["$gt"]: return None
        row.update(update["$set"]); return dict(row)
    def create_index(self, *args, **kwargs): return "idx"

def authority(**overrides):
    values = dict(invitation_id="inv-1", tenant_id="tenant-1", recipient_principal_id="recipient-1", inviter_principal_id="inviter-1", authorization_role_id="AUDITOR", capability_digest=DIGEST, status=InvitationStatus.ACTIVE, expires_at=NOW + timedelta(hours=1), revision=0, created_at=NOW)
    values.update(overrides); return InvitationAuthority(**values)  # type: ignore

def test_insert_get_and_immutability():
    c = FakeCollection(); value = authority(); assert InvitationRepository.insert(value, c) == value; assert InvitationRepository.get("inv-1", c) == value
    with pytest.raises(Exception): value.status = InvitationStatus.REVOKED

def test_duplicate_and_missing():
    c = FakeCollection(); InvitationRepository.insert(authority(), c)
    with pytest.raises(InvitationAlreadyExistsError): InvitationRepository.insert(authority(invitation_id="inv-2"), c)
    with pytest.raises(InvitationNotFoundError): InvitationRepository.get("missing", c)

def test_consume_cas_and_replay():
    c = FakeCollection(); InvitationRepository.insert(authority(), c)
    consumed = InvitationRepository.consume("inv-1", DIGEST, 0, NOW + timedelta(minutes=1), c)
    assert consumed.status is InvitationStatus.CONSUMED and consumed.revision == 1 and consumed.consumed_at == NOW + timedelta(minutes=1)
    with pytest.raises(InvitationAlreadyConsumedError): InvitationRepository.consume("inv-1", DIGEST, 1, NOW + timedelta(minutes=2), c)

def test_consume_failures_do_not_leak_digest():
    c = FakeCollection(); InvitationRepository.insert(authority(), c)
    with pytest.raises(InvitationConcurrentModificationError) as exc: InvitationRepository.consume("inv-1", "0" * 128, 0, NOW + timedelta(minutes=1), c)
    assert DIGEST not in str(exc.value)
    with pytest.raises(InvitationExpiredError): InvitationRepository.consume("inv-1", DIGEST, 0, NOW + timedelta(hours=2), c)
    c.rows["inv-1"]["status"] = InvitationStatus.REVOKED.value
    with pytest.raises(InvitationRevokedError): InvitationRepository.consume("inv-1", DIGEST, 0, NOW + timedelta(minutes=1), c)

def test_domain_invariants_and_index_hook():
    with pytest.raises(ValueError): authority(capability_digest="ABC")
    with pytest.raises(ValueError): authority(expires_at=NOW)
    InvitationRepository.ensure_indexes(FakeCollection())

def test_naive_bson_datetimes_hydrate_as_utc_and_reject_malformed():
    c = FakeCollection(); value = authority(); InvitationRepository.insert(value, c)
    row = c.rows["inv-1"]
    row.update(expires_at=value.expires_at.replace(tzinfo=None), created_at=NOW.replace(tzinfo=None))
    hydrated = InvitationRepository.get("inv-1", c)
    assert hydrated.created_at == NOW and hydrated.expires_at == value.expires_at
    row["created_at"] = "not-a-date"
    from tools.eos.auth.invitation_repository import InvitationPersistedRecordInvalidError
    with pytest.raises(InvitationPersistedRecordInvalidError): InvitationRepository.get("inv-1", c)

def test_domain_time_is_bson_millisecond_canonical_and_idempotent():
    value = authority(created_at=NOW.replace(microsecond=123456), expires_at=NOW.replace(microsecond=999999))
    assert value.created_at.microsecond == 123000 and value.expires_at.microsecond == 999000
    assert canonicalize_invitation_datetime(canonicalize_invitation_datetime(NOW.replace(microsecond=456789))) == canonicalize_invitation_datetime(NOW.replace(microsecond=456789))
    with pytest.raises(ValueError): authority(created_at=NOW.replace(tzinfo=None))

def test_sub_millisecond_only_lifetime_is_rejected():
    with pytest.raises(ValueError): authority(created_at=NOW.replace(microsecond=100), expires_at=NOW.replace(microsecond=900))
