"""Immutable Mongo registry for committed VendorBill command identities."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
from pymongo import ASCENDING, ReturnDocument, WriteConcern
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from ...kernel.db import get_database
from ..domain.vendor_bill_command import VendorBillCommand, VendorBillCommandDomainError

COLLECTION = "vendor_bill_commands"; WC = WriteConcern(w="majority", j=True, wtimeout=10000); RC = ReadConcern("majority")
VERSION = "v1.0.1-VENDORBILL-COMMAND-LEDGER-REGISTRY"
class VendorBillCommandRegistryError(RuntimeError): pass
class VendorBillCommandNotFoundError(VendorBillCommandRegistryError): pass
class VendorBillCommandPersistedRecordInvalidError(VendorBillCommandRegistryError): pass
class VendorBillCommandIdempotencyReuseConflictError(VendorBillCommandRegistryError): pass
class VendorBillCommandSequenceConflictError(VendorBillCommandRegistryError): pass
class VendorBillCommandCreateOutcome(StrEnum): CREATED="CREATED"; IDEMPOTENT_REPLAY="IDEMPOTENT_REPLAY"
@dataclass(frozen=True)
class VendorBillCommandCreateResult:
    outcome: VendorBillCommandCreateOutcome; command: VendorBillCommand
def _c(collection: Optional[Collection]) -> Collection:
    if collection is not None: return collection.with_options(write_concern=WC, read_concern=RC)
    db=get_database()
    if db is None: raise VendorBillCommandRegistryError("VENDOR_BILL_COMMAND_PERSISTENCE_UNAVAILABLE")
    return db[COLLECTION].with_options(write_concern=WC, read_concern=RC)
def _hydrate(doc: dict) -> VendorBillCommand:
    try: return VendorBillCommand.from_persistence_dict({k:v for k,v in doc.items() if k != "_id"})
    except Exception as error: raise VendorBillCommandPersistedRecordInvalidError("VENDOR_BILL_COMMAND_PERSISTED_RECORD_INVALID") from error
class VendorBillCommandRegistry:
    @staticmethod
    def ensure_indexes(collection: Optional[Collection]=None) -> None:
        c=_c(collection); c.create_index([("tenant_id",ASCENDING),("payable_id",ASCENDING),("idempotency_key",ASCENDING)],unique=True,name="tenant_payable_command_idempotency_unique"); c.create_index([("tenant_id",ASCENDING),("payable_id",ASCENDING),("command_sequence",ASCENDING)],unique=True,name="tenant_payable_command_sequence_unique")
    @staticmethod
    def create_command(command: VendorBillCommand, collection: Optional[Collection]=None, *, session: Optional[ClientSession]=None) -> VendorBillCommandCreateResult:
        if not isinstance(command, VendorBillCommand): raise VendorBillCommandDomainError("command must be a VendorBillCommand")
        c=_c(collection); document=command.to_persistence_dict()
        try: c.insert_one(document, session=session); return VendorBillCommandCreateResult(VendorBillCommandCreateOutcome.CREATED, command)
        except DuplicateKeyError as error:
            existing=c.find_one({"tenant_id":command.tenant_id,"payable_id":command.payable_id,"idempotency_key":command.idempotency_key}, session=session)
            if existing is None:
                sequence_existing = c.find_one({"tenant_id":command.tenant_id,"payable_id":command.payable_id,"command_sequence":command.command_sequence}, session=session)
                if sequence_existing is not None: raise VendorBillCommandSequenceConflictError("VENDOR_BILL_COMMAND_SEQUENCE_CONFLICT") from error
                raise VendorBillCommandRegistryError("VENDOR_BILL_COMMAND_CREATE_CONFLICT") from error
            persisted=_hydrate(existing)
            if persisted.command_type is command.command_type and persisted.command_fingerprint == command.command_fingerprint: return VendorBillCommandCreateResult(VendorBillCommandCreateOutcome.IDEMPOTENT_REPLAY,persisted)
            raise VendorBillCommandIdempotencyReuseConflictError("VENDOR_BILL_COMMAND_IDEMPOTENCY_REUSE_CONFLICT") from error
    @staticmethod
    def get_by_idempotency_key(tenant_id:str,payable_id:str,idempotency_key:str,collection:Optional[Collection]=None,*,session:Optional[ClientSession]=None)->VendorBillCommand:
        doc=_c(collection).find_one({"tenant_id":tenant_id.strip(),"payable_id":payable_id.strip(),"idempotency_key":idempotency_key.strip()},session=session)
        if doc is None: raise VendorBillCommandNotFoundError("VENDOR_BILL_COMMAND_NOT_FOUND")
        return _hydrate(doc)
    @staticmethod
    def get_by_sequence(tenant_id:str,payable_id:str,sequence:int,collection:Optional[Collection]=None,*,session:Optional[ClientSession]=None)->VendorBillCommand:
        doc=_c(collection).find_one({"tenant_id":tenant_id.strip(),"payable_id":payable_id.strip(),"command_sequence":sequence},session=session)
        if doc is None: raise VendorBillCommandNotFoundError("VENDOR_BILL_COMMAND_NOT_FOUND")
        return _hydrate(doc)
