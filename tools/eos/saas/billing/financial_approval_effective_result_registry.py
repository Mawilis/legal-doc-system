"""Immutable tenant-scoped persistence for canonical financial approval results."""
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional, Sequence
from pymongo import ASCENDING, WriteConcern
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from ...kernel.db import get_database
from ..domain.financial_approval_effective_result import FinancialApprovalEffectiveResult, FinancialApprovalEffectiveResultDomainError
from .financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry

COLLECTION="financial_approval_effective_results"; MAX_LIST_LIMIT=250; WRITE_CONCERN=WriteConcern(w="majority",j=True,wtimeout=10000); READ_CONCERN=ReadConcern("majority")
class FinancialApprovalEffectiveResultRegistryError(RuntimeError): pass
class FinancialApprovalEffectiveResultPersistedRecordInvalidError(FinancialApprovalEffectiveResultRegistryError): pass
class FinancialApprovalEffectiveResultNotFoundError(FinancialApprovalEffectiveResultRegistryError): pass
class FinancialApprovalEffectiveResultIdempotencyKeyReuseError(FinancialApprovalEffectiveResultRegistryError): pass
class FinancialApprovalEffectiveResultCreateConflictError(FinancialApprovalEffectiveResultRegistryError): pass
class FinancialApprovalEffectiveResultCreateOutcome(StrEnum): CREATED="CREATED"; IDEMPOTENT_REPLAY="IDEMPOTENT_REPLAY"
@dataclass(frozen=True)
class FinancialApprovalEffectiveResultCreateResult:
 outcome: FinancialApprovalEffectiveResultCreateOutcome
 result: FinancialApprovalEffectiveResult

def _collection(collection: Optional[Collection]=None)->Collection:
 if collection is not None: return collection.with_options(write_concern=WRITE_CONCERN,read_concern=READ_CONCERN)
 db=get_database()
 if db is None: raise FinancialApprovalEffectiveResultRegistryError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_PERSISTENCE_UNAVAILABLE")
 return db[COLLECTION].with_options(write_concern=WRITE_CONCERN,read_concern=READ_CONCERN)
def _fingerprint(body: dict[str,Any], key: str)->str:
 return hashlib.sha3_512(json.dumps({"operation":"CREATE_EFFECTIVE_RESULT","idempotency_key":key,"body":body},sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def _hydrate(doc: dict[str,Any])->FinancialApprovalEffectiveResult:
 try:
  body={k:v for k,v in doc.items() if k not in {"_id","create_idempotency_key","create_command_fingerprint"}}
  result=FinancialApprovalEffectiveResult.from_persistence_dict(body)
  fp=doc.get("create_command_fingerprint"); key=doc.get("create_idempotency_key")
  if not isinstance(key,str) or not key.strip() or not isinstance(fp,str) or re.fullmatch(r"[0-9a-f]{128}",fp) is None or fp != _fingerprint(body,key): raise ValueError("metadata")
  return result
 except Exception as error: raise FinancialApprovalEffectiveResultPersistedRecordInvalidError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_PERSISTED_RECORD_INVALID") from error
class FinancialApprovalEffectiveResultRegistry:
 @staticmethod
 def ensure_indexes(collection: Optional[Collection]=None)->None:
  c=_collection(collection); c.create_index([("tenant_id",ASCENDING),("result_id",ASCENDING)],unique=True,name="tenant_effective_result_identity_unique"); c.create_index([("tenant_id",ASCENDING),("create_idempotency_key",ASCENDING)],unique=True,name="tenant_effective_result_idempotency_unique"); c.create_index([("tenant_id",ASCENDING),("evaluation_id",ASCENDING),("created_at",ASCENDING),("result_id",ASCENDING)],name="tenant_effective_result_evaluation_order"); c.create_index([("tenant_id",ASCENDING),("subject_type",ASCENDING),("subject_id",ASCENDING),("subject_revision",ASCENDING)],name="tenant_effective_result_subject"); c.create_index([("tenant_id",ASCENDING),("evaluation_id",ASCENDING),("source_evidence_fingerprint",ASCENDING)],name="tenant_effective_result_source")
 @staticmethod
 def create(result: FinancialApprovalEffectiveResult,idempotency_key: str,collection: Optional[Collection]=None,*,session: Optional[ClientSession]=None)->FinancialApprovalEffectiveResultCreateResult:
  if not isinstance(result,FinancialApprovalEffectiveResult) or not isinstance(idempotency_key,str) or not idempotency_key.strip() or len(idempotency_key.strip())>128: raise FinancialApprovalEffectiveResultRegistryError("invalid create command")
  key=idempotency_key.strip(); c=_collection(collection); evaluation=FinancialApprovalPolicyEvaluationRegistry.get(result.tenant_id,result.evaluation_id,c.database["financial_approval_policy_evaluations"],session=session)
  if (evaluation.tenant_id,evaluation.subject_type.value,evaluation.subject_id,evaluation.subject_revision,evaluation.approval_policy_reference,evaluation.approval_policy_version)!=(result.tenant_id,result.subject_type.value,result.subject_id,result.subject_revision,result.approval_policy_reference,result.approval_policy_version): raise FinancialApprovalEffectiveResultRegistryError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_EVALUATION_MISMATCH")
  body=result.to_persistence_dict(); document={**body,"create_idempotency_key":key,"create_command_fingerprint":_fingerprint(body,key)}
  try: c.insert_one(document,session=session)
  except DuplicateKeyError as error:
   existing=c.find_one({"tenant_id":result.tenant_id,"result_id":result.result_id},session=session) or c.find_one({"tenant_id":result.tenant_id,"create_idempotency_key":key},session=session)
   if existing is None: raise FinancialApprovalEffectiveResultCreateConflictError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_CREATE_CONFLICT") from error
   persisted=_hydrate(existing)
   if existing.get("create_idempotency_key")==key and existing.get("create_command_fingerprint")==document["create_command_fingerprint"]: return FinancialApprovalEffectiveResultCreateResult(FinancialApprovalEffectiveResultCreateOutcome.IDEMPOTENT_REPLAY,persisted)
   if existing.get("create_idempotency_key")==key: raise FinancialApprovalEffectiveResultIdempotencyKeyReuseError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_IDEMPOTENCY_KEY_REUSED") from error
   raise FinancialApprovalEffectiveResultCreateConflictError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_CREATE_CONFLICT") from error
  except PyMongoError as error: raise FinancialApprovalEffectiveResultRegistryError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_CREATE_FAILED") from error
  return FinancialApprovalEffectiveResultCreateResult(FinancialApprovalEffectiveResultCreateOutcome.CREATED,result)
 @staticmethod
 def get(tenant_id:str,result_id:str,collection:Optional[Collection]=None,*,session:Optional[ClientSession]=None)->FinancialApprovalEffectiveResult:
  doc=_collection(collection).find_one({"tenant_id":tenant_id.strip(),"result_id":result_id.strip()},session=session)
  if doc is None: raise FinancialApprovalEffectiveResultNotFoundError("FINANCIAL_APPROVAL_EFFECTIVE_RESULT_NOT_FOUND")
  return _hydrate(doc)
 @staticmethod
 def list_for_evaluation(tenant_id:str,evaluation_id:str,limit:int=MAX_LIST_LIMIT,collection:Optional[Collection]=None,*,session:Optional[ClientSession]=None)->tuple[FinancialApprovalEffectiveResult,...]:
  if not isinstance(limit,int) or isinstance(limit,bool) or limit<1 or limit>MAX_LIST_LIMIT: raise FinancialApprovalEffectiveResultRegistryError("limit is invalid")
  rows=_collection(collection).find({"tenant_id":tenant_id.strip(),"evaluation_id":evaluation_id.strip()},session=session).sort([("created_at",ASCENDING),("result_id",ASCENDING)]).limit(limit)
  return tuple(_hydrate(row) for row in rows)
