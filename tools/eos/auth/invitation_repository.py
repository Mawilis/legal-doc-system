"""TITLE: WILSY OS Invitation Authority Repository.
VERSION: v1.0.0-WILSY-F1C2B-A1
AUTHORITY: Durable invitation persistence, reads, and consume CAS.
PURPOSE: Persist immutable invitation provenance with caller sessions.
EPITOME: One-operation expiry-aware replay-safe consumption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/invitation_repository.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
SECURITY / PRIVACY POSTURE: Digest-only capability; no secret leakage.
TENANT BOUNDARY: Invitation records carry explicit tenant and recipient identity.
AUTHORITY BOUNDARY: Persistence only; no admission authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller-owned Mongo sessions are forwarded unchanged.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes session-aware invitation repository and CAS.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
from typing import Mapping, Optional, cast
from pymongo import ASCENDING, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from .invitation import InvitationAuthority, InvitationStatus, canonicalize_invitation_datetime

VERSION = "v1.0.0-WILSY-F1C2B-A1"; COLLECTION = "invitations"
class InvitationRepositoryError(RuntimeError): pass
class InvitationAlreadyExistsError(InvitationRepositoryError): pass
class InvitationNotFoundError(InvitationRepositoryError): pass
class InvitationAlreadyConsumedError(InvitationRepositoryError): pass
class InvitationConcurrentModificationError(InvitationRepositoryError): pass
class InvitationRevokedError(InvitationRepositoryError): pass
class InvitationExpiredError(InvitationRepositoryError): pass
class InvitationPersistedRecordInvalidError(InvitationRepositoryError): pass

def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None: return collection
    from tools.eos.kernel.db import get_database
    db = get_database()
    if db is None: raise InvitationRepositoryError("INVITATION_PERSISTENCE_UNAVAILABLE")
    return db[COLLECTION]
def _document(v: InvitationAuthority) -> dict[str, object]:
    return {"invitation_id":v.invitation_id,"tenant_id":v.tenant_id,"recipient_principal_id":v.recipient_principal_id,"recipient_email":v.recipient_email,"inviter_principal_id":v.inviter_principal_id,"authorization_role_id":v.authorization_role_id,"capability_digest":v.capability_digest,"status":v.status.value,"expires_at":v.expires_at,"revision":v.revision,"created_at":v.created_at,"consumed_at":v.consumed_at}
def _hydrate(d: Mapping[str, object]) -> InvitationAuthority:
    def utc(value: object, *, nullable: bool = False) -> datetime | None:
        if value is None and nullable: return None
        if not isinstance(value, datetime): raise TypeError("persisted datetime invalid")
        if value.tzinfo is None or value.utcoffset() is None: return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    try: return InvitationAuthority(cast(str,d["invitation_id"]),cast(str,d["tenant_id"]),cast(str,d["recipient_principal_id"]),cast(str,d["recipient_email"]),cast(str,d["inviter_principal_id"]),cast(str,d["authorization_role_id"]),cast(str,d["capability_digest"]),InvitationStatus(cast(str,d["status"])),cast(datetime,utc(d["expires_at"])),cast(int,d["revision"]),cast(datetime,utc(d["created_at"])),cast(datetime | None,utc(d.get("consumed_at"), nullable=True)))
    except (KeyError, TypeError, ValueError, AttributeError) as e: raise InvitationPersistedRecordInvalidError("INVITATION_PERSISTED_RECORD_INVALID") from e
class InvitationRepository:
    @staticmethod
    def ensure_indexes(collection: Optional[Collection]=None) -> None:
        c=_target(collection); c.create_index([('invitation_id',ASCENDING)],unique=True,name='invitation_id_unique'); c.create_index([('capability_digest',ASCENDING)],unique=True,name='invitation_capability_digest_unique')
    @staticmethod
    def insert(value: InvitationAuthority, collection: Optional[Collection]=None, *, session: Optional[ClientSession]=None) -> InvitationAuthority:
        if not isinstance(value,InvitationAuthority): raise InvitationRepositoryError("INVITATION_INSERT_INVALID")
        try: _target(collection).insert_one(_document(value),session=session); return value
        except DuplicateKeyError as e: raise InvitationAlreadyExistsError("INVITATION_ALREADY_EXISTS") from e
        except PyMongoError as e: raise InvitationRepositoryError("PERSISTENCE_FAILURE") from e
    @staticmethod
    def get(invitation_id: str, collection: Optional[Collection]=None, *, session: Optional[ClientSession]=None) -> InvitationAuthority:
        if not isinstance(invitation_id,str) or not invitation_id.strip(): raise InvitationNotFoundError("INVITATION_NOT_FOUND")
        try: row=_target(collection).find_one({'invitation_id':invitation_id},session=session)
        except PyMongoError as e: raise InvitationRepositoryError("PERSISTENCE_FAILURE") from e
        if row is None: raise InvitationNotFoundError("INVITATION_NOT_FOUND")
        return _hydrate(row)
    @staticmethod
    def consume(invitation_id: str, capability_digest: str, expected_revision: int, consumed_at: datetime, collection: Optional[Collection]=None, *, session: Optional[ClientSession]=None) -> InvitationAuthority:
        if not isinstance(expected_revision,int) or isinstance(expected_revision,bool) or expected_revision<0: raise InvitationConcurrentModificationError("INVITATION_CONCURRENT_MODIFICATION")
        try: consumed_at = canonicalize_invitation_datetime(consumed_at)
        except ValueError as exc: raise InvitationRepositoryError("PERSISTENCE_FAILURE") from exc
        c=_target(collection)
        try:
            row=c.find_one_and_update({'invitation_id':invitation_id,'capability_digest':capability_digest,'status':InvitationStatus.ACTIVE.value,'revision':expected_revision,'expires_at':{'$gt':consumed_at}}, {'$set':{'status':InvitationStatus.CONSUMED.value,'revision':expected_revision+1,'consumed_at':consumed_at}}, return_document=ReturnDocument.AFTER, session=session)
        except PyMongoError as e: raise InvitationRepositoryError("PERSISTENCE_FAILURE") from e
        if row is not None: return _hydrate(row)
        try: current=c.find_one({'invitation_id':invitation_id},session=session)
        except PyMongoError as e: raise InvitationRepositoryError("PERSISTENCE_FAILURE") from e
        if current is None: raise InvitationNotFoundError("INVITATION_NOT_FOUND")
        if current.get('status') == InvitationStatus.CONSUMED.value: raise InvitationAlreadyConsumedError("INVITATION_ALREADY_CONSUMED")
        if current.get('status') == InvitationStatus.REVOKED.value: raise InvitationRevokedError("INVITATION_REVOKED")
        if current.get('expires_at') <= consumed_at: raise InvitationExpiredError("INVITATION_EXPIRED")
        raise InvitationConcurrentModificationError("INVITATION_CONCURRENT_MODIFICATION")

__all__=['COLLECTION','InvitationRepository','InvitationRepositoryError','InvitationAlreadyExistsError','InvitationNotFoundError','InvitationAlreadyConsumedError','InvitationConcurrentModificationError','InvitationRevokedError','InvitationExpiredError','InvitationPersistedRecordInvalidError']
# ARTIFACT: invitation_repository.py
# VERSION: v1.0.0-WILSY-F1C2B-A1
# AUTHORITY BOUNDARY: invitation persistence and consume CAS only
# TENANT POSTURE: explicit durable provenance
# FAIL-CLOSED POSTURE: duplicate, malformed, stale, expired, revoked, and persistence failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
