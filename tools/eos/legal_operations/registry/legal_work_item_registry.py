"""WILSY OS immutable Legal Work Item registry.

TITLE: Legal Work Item Registry
VERSION: v1.0.0-G7G-P0D-DURABLE-WORK-ITEM-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and query immutable exact-tenant Legal work-item evidence for
         future daily queues without creating assignment or completion authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_work_item_registry.py
COLLABORATION / OWNERSHIP: LegalWorkItem owns lifecycle semantics; this registry
                            owns exact replay, strict hydration and read access.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0D establishes append-only tenant-first durability and
           matter/status/due-time/source query indexes without TTL.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Every operational predicate starts with tenant_id.
TENANT BOUNDARY: Foreign-tenant absence reveals no durable existence.
AUTHORITY BOUNDARY: Work presence is not IAM, assignment, supervision, review,
                    completion permission, or workflow-transition authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Caller owns the active Mongo transaction and retry.
FAIL-CLOSED DECLARATION: Invalid input, transaction absence, divergent replay,
                         corruption, collision, race and outage reject.
"""
from __future__ import annotations
from collections.abc import Mapping
import hmac
from typing import Any, Final, NoReturn, cast
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from tools.eos.legal_operations.domain.legal_work_item import LegalWorkItem, LegalWorkItemError, LegalWorkItemStatus

VERSION: Final[str]="v1.0.0-G7G-P0D-DURABLE-WORK-ITEM-REGISTRY"
COLLECTION_NAME: Final[str]="legal_work_items"
IDENTITY_INDEX_NAME: Final[str]="legal_work_item_identity_unique"
FINGERPRINT_INDEX_NAME: Final[str]="legal_work_item_fingerprint_unique"
MATTER_INDEX_NAME: Final[str]="legal_work_item_matter_queue"
STATUS_INDEX_NAME: Final[str]="legal_work_item_status_queue"
SOURCE_INDEX_NAME: Final[str]="legal_work_item_source_lookup"

class LegalWorkItemRegistryError(RuntimeError):
    """Base stable registry error."""
    def __init__(self,code:str)->None: self.code=code; super().__init__(code)
class LegalWorkItemRegistryInputError(LegalWorkItemRegistryError): """Invalid caller input."""
class LegalWorkItemRegistryTransactionRequiredError(LegalWorkItemRegistryError): """Active transaction absent."""
class LegalWorkItemRegistryConflictError(LegalWorkItemRegistryError): """Immutable replay conflict."""
class LegalWorkItemRegistryNotFoundError(LegalWorkItemRegistryError): """Exact tenant item absent."""
class LegalWorkItemRegistryPersistedRecordInvalidError(LegalWorkItemRegistryError): """Durable row corrupt."""
class LegalWorkItemRegistryRetryTransactionError(LegalWorkItemRegistryError): """Whole transaction retry required."""
class LegalWorkItemRegistryPersistenceError(LegalWorkItemRegistryError): """Mongo failure."""

def _raise(kind:type[LegalWorkItemRegistryError],code:str,cause:BaseException|None=None)->NoReturn:
    error=kind(code)
    if cause is None: raise error
    raise error from cause

def _tx(session:object)->object:
    marker=getattr(session,"in_transaction",None) if session is not None else None
    try: active=marker() if callable(marker) else marker
    except (AttributeError,TypeError) as error: _raise(LegalWorkItemRegistryTransactionRequiredError,"G7G_P0D_ACTIVE_TRANSACTION_REQUIRED",error)
    if active is not True: _raise(LegalWorkItemRegistryTransactionRequiredError,"G7G_P0D_ACTIVE_TRANSACTION_REQUIRED")
    return session

def _text(name:str,value:object)->str:
    if not isinstance(value,str) or not value or value!=value.strip() or len(value)>320:
        _raise(LegalWorkItemRegistryInputError,f"G7G_P0D_{name.upper()}_INVALID")
    return value

def _tenant(value:object)->str:
    tenant=_text("tenant_id",value)
    if tenant.casefold() in {"default","global","global_root","root","master","*"}:
        _raise(LegalWorkItemRegistryInputError,"G7G_P0D_TENANT_REQUIRED")
    return tenant

def _hydrate(raw:Mapping[str,object])->LegalWorkItem:
    row=dict(raw); row.pop("_id",None)
    try: value=LegalWorkItem.from_dict(row)
    except (LegalWorkItemError,TypeError,ValueError,KeyError) as error:
        _raise(LegalWorkItemRegistryPersistedRecordInvalidError,"G7G_P0D_PERSISTED_RECORD_INVALID",error)
    if value.to_dict()!=row: _raise(LegalWorkItemRegistryPersistedRecordInvalidError,"G7G_P0D_RECORD_CORRELATION_INVALID")
    return value

def _mongo(error:PyMongoError)->NoReturn:
    try: transient=error.has_error_label("TransientTransactionError")
    except Exception: transient=False
    if transient: _raise(LegalWorkItemRegistryRetryTransactionError,"G7G_P0D_WHOLE_TRANSACTION_RETRY_REQUIRED",error)
    _raise(LegalWorkItemRegistryPersistenceError,"G7G_P0D_PERSISTENCE_FAILURE",error)

class LegalWorkItemRegistry:
    """Append-only exact-tenant work-item durability and queue-read facade."""
    def __init__(self,collection:Any)->None:
        """Bind one explicit collection without lifecycle authority."""
        if collection is None: _raise(LegalWorkItemRegistryInputError,"G7G_P0D_COLLECTION_REQUIRED")
        self._collection=collection

    def ensure_indexes(self)->None:
        """Create domain-supported tenant-first non-TTL access indexes."""
        indexes=(
            ([("tenant_id",ASCENDING),("work_item_id",ASCENDING)],True,IDENTITY_INDEX_NAME),
            ([("tenant_id",ASCENDING),("fingerprint",ASCENDING)],True,FINGERPRINT_INDEX_NAME),
            ([("tenant_id",ASCENDING),("case_matter_id",ASCENDING),("created_at",ASCENDING),("work_item_id",ASCENDING)],False,MATTER_INDEX_NAME),
            ([("tenant_id",ASCENDING),("status",ASCENDING),("due_at",ASCENDING),("created_at",ASCENDING),("work_item_id",ASCENDING)],False,STATUS_INDEX_NAME),
            ([("tenant_id",ASCENDING),("source_kind",ASCENDING),("source_reference",ASCENDING)],False,SOURCE_INDEX_NAME),
        )
        try:
            for keys,unique,name in indexes: self._collection.create_index(keys,unique=unique,name=name)
        except AttributeError as error: _raise(LegalWorkItemRegistryInputError,"G7G_P0D_COLLECTION_INTERFACE_INVALID",error)
        except PyMongoError as error: _mongo(error)

    def create_or_replay(self,value:LegalWorkItem,*,session:object)->LegalWorkItem:
        """Insert immutable work evidence or return exact durable replay."""
        if type(value) is not LegalWorkItem: _raise(LegalWorkItemRegistryInputError,"G7G_P0D_WORK_ITEM_REQUIRED")
        tx=_tx(session)
        try:
            raw=self._collection.find_one({"tenant_id":value.tenant_id,"work_item_id":value.work_item_id},session=tx)
            if raw is not None:
                persisted=_hydrate(cast(Mapping[str,object],raw))
                if hmac.compare_digest(persisted.fingerprint,value.fingerprint) and persisted==value: return persisted
                _raise(LegalWorkItemRegistryConflictError,"G7G_P0D_DIVERGENT_REPLAY")
            collision=self._collection.find_one({"tenant_id":value.tenant_id,"fingerprint":value.fingerprint},session=tx)
            if collision is not None: _raise(LegalWorkItemRegistryConflictError,"G7G_P0D_FINGERPRINT_COLLISION")
            self._collection.insert_one(value.to_dict(),session=tx)
        except DuplicateKeyError as error: _raise(LegalWorkItemRegistryRetryTransactionError,"G7G_P0D_DUPLICATE_RACE_RETRY_TRANSACTION",error)
        except LegalWorkItemRegistryError: raise
        except PyMongoError as error: _mongo(error)
        return value

    def get_by_id(self,tenant_id:str,work_item_id:str,*,session:object)->LegalWorkItem:
        """Read one exact tenant-scoped immutable work item."""
        tenant=_tenant(tenant_id); identity=_text("work_item_id",work_item_id); tx=_tx(session)
        try: raw=self._collection.find_one({"tenant_id":tenant,"work_item_id":identity},session=tx)
        except PyMongoError as error: _mongo(error)
        if raw is None: _raise(LegalWorkItemRegistryNotFoundError,"G7G_P0D_WORK_ITEM_NOT_FOUND")
        value=_hydrate(cast(Mapping[str,object],raw))
        if value.tenant_id!=tenant or value.work_item_id!=identity: _raise(LegalWorkItemRegistryPersistedRecordInvalidError,"G7G_P0D_PERSISTED_SCOPE_MISMATCH")
        return value

    def _list(self,query:dict[str,object],sort:list[tuple[str,int]],*,session:object)->tuple[LegalWorkItem,...]:
        tx=_tx(session)
        try: rows=tuple(self._collection.find(query,session=tx).sort(sort))
        except PyMongoError as error: _mongo(error)
        values=tuple(_hydrate(cast(Mapping[str,object],row)) for row in rows)
        tenant=query["tenant_id"]
        if any(value.tenant_id!=tenant for value in values): _raise(LegalWorkItemRegistryPersistedRecordInvalidError,"G7G_P0D_PERSISTED_SCOPE_MISMATCH")
        return values

    def list_matter(self,tenant_id:str,case_matter_id:str,*,session:object)->tuple[LegalWorkItem,...]:
        """List deterministic immutable work evidence for one matter."""
        return self._list({"tenant_id":_tenant(tenant_id),"case_matter_id":_text("case_matter_id",case_matter_id)},[("created_at",ASCENDING),("work_item_id",ASCENDING)],session=session)

    def list_status(self,tenant_id:str,status:LegalWorkItemStatus|str,*,session:object)->tuple[LegalWorkItem,...]:
        """List one tenant queue posture without granting action authority."""
        try: normalized=LegalWorkItemStatus(status).value
        except (TypeError,ValueError) as error: _raise(LegalWorkItemRegistryInputError,"G7G_P0D_STATUS_INVALID",error)
        return self._list({"tenant_id":_tenant(tenant_id),"status":normalized},[("due_at",ASCENDING),("created_at",ASCENDING),("work_item_id",ASCENDING)],session=session)

def ensure_indexes(collection:Any)->None:
    """Create governed indexes on one explicit collection."""
    LegalWorkItemRegistry(collection).ensure_indexes()

__all__=["VERSION","COLLECTION_NAME","IDENTITY_INDEX_NAME","FINGERPRINT_INDEX_NAME","MATTER_INDEX_NAME","STATUS_INDEX_NAME","SOURCE_INDEX_NAME","LegalWorkItemRegistry","LegalWorkItemRegistryError","LegalWorkItemRegistryInputError","LegalWorkItemRegistryTransactionRequiredError","LegalWorkItemRegistryConflictError","LegalWorkItemRegistryNotFoundError","LegalWorkItemRegistryPersistedRecordInvalidError","LegalWorkItemRegistryRetryTransactionError","LegalWorkItemRegistryPersistenceError","ensure_indexes"]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_work_item_registry.py
# VERSION: v1.0.0-G7G-P0D-DURABLE-WORK-ITEM-REGISTRY
# AUTHORITY BOUNDARY: immutable durability and read projection only
# TENANT POSTURE: exact tenant-first writes, replay, reads, and queue queries
# FAIL-CLOSED POSTURE: invalid input, transaction absence, conflict, corruption, race, and outage reject
# MUTABLE CURRENT POINTER / TTL / UPDATE / DELETE AUTHORITY: NONE
# IAM / ASSIGNMENT / SUPERVISION / COMPLETION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
