# -*- coding: utf-8 -*-
"""
WILSY OS – FINANCIAL APPROVAL ACTOR AUTHORIZATION REGISTRY
VERSION: v1.1.0-BOUNDED-REQUIREMENT-KEYSET-PAGINATION

Immutable tenant-scoped authorization evidence bound to one policy evaluation, requirement, and VendorBill revision.
Actor capacity is asserted evidence, never authorization by itself. This registry has no approval aggregation,
VendorBill projection, release, execution, or settlement authority.
"""
from __future__ import annotations
import hashlib, json, re
import base64
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Optional, Sequence
from pymongo import ASCENDING, WriteConcern
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from ..domain.financial_approval_actor_authorization import FinancialApprovalActorAuthorization, FinancialApprovalActorAuthorizationDomainError
from ..domain.financial_approval_policy_evaluation import FinancialApprovalPolicyEvaluation, FinancialApprovalPolicySubjectType
from .financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry, _timestamp

COLLECTION = "financial_approval_actor_authorizations"
MAX_LIST_LIMIT = 250
WRITE_CONCERN = WriteConcern(w="majority", j=True, wtimeout=10_000)
READ_CONCERN = ReadConcern("majority")

class FinancialApprovalActorAuthorizationRegistryError(RuntimeError): pass
class FinancialApprovalActorAuthorizationPersistedRecordInvalidError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalActorAuthorizationNotFoundError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalAuthorizationEvaluationMismatchError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalAuthorizationRequirementNotFoundError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalAuthorizationCapacityMismatchError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalActorAuthorizationIdempotencyKeyReuseError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalActorAuthorizationCreateConflictError(FinancialApprovalActorAuthorizationRegistryError): pass
class FinancialApprovalActorAuthorizationCreateOutcome(StrEnum): CREATED="CREATED"; IDEMPOTENT_REPLAY="IDEMPOTENT_REPLAY"
@dataclass(frozen=True)
class FinancialApprovalActorAuthorizationCreateResult:
    outcome: FinancialApprovalActorAuthorizationCreateOutcome
    authorization: FinancialApprovalActorAuthorization

@dataclass(frozen=True)
class FinancialApprovalActorAuthorizationPage:
    items: tuple[FinancialApprovalActorAuthorization, ...]
    next_cursor: Optional[str]

def _collection(collection: Optional[Collection]=None) -> Collection:
    if collection is None:
        from ...kernel.db import get_database
        db=get_database()
        if db is None: raise FinancialApprovalActorAuthorizationRegistryError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_PERSISTENCE_UNAVAILABLE")
        collection=db[COLLECTION]
    return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)

def _required(doc: Mapping[str, Any], key: str) -> Any:
    if key not in doc: raise FinancialApprovalActorAuthorizationPersistedRecordInvalidError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_PERSISTED_RECORD_INVALID")
    return doc[key]

def _hydrate(doc: Mapping[str, Any]) -> FinancialApprovalActorAuthorization:
    try:
        key=_required(doc,"create_idempotency_key"); fp=_required(doc,"create_fingerprint")
        if not isinstance(key,str) or not key.strip() or key != key.strip() or len(key)>128 or not isinstance(fp,str) or re.fullmatch(r"[0-9a-f]{128}",fp) is None:
            raise ValueError("metadata")
        valid_until=_required(doc,"valid_until")
        return FinancialApprovalActorAuthorization(tenant_id=_required(doc,"tenant_id"),authorization_id=_required(doc,"authorization_id"),subject_type=FinancialApprovalPolicySubjectType(_required(doc,"subject_type")),subject_id=_required(doc,"subject_id"),subject_revision=_required(doc,"subject_revision"),evaluation_id=_required(doc,"evaluation_id"),approval_policy_reference=_required(doc,"approval_policy_reference"),approval_policy_version=_required(doc,"approval_policy_version"),requirement_id=_required(doc,"requirement_id"),actor_id=_required(doc,"actor_id"),actor_capacity=_required(doc,"actor_capacity"),authorization_source_reference=_required(doc,"authorization_source_reference"),authorization_basis_reference=_required(doc,"authorization_basis_reference"),authorized_at=_timestamp(_required(doc,"authorized_at")),valid_until=None if valid_until is None else _timestamp(valid_until),authorization_evidence_fingerprint=_required(doc,"authorization_evidence_fingerprint"),created_at=_timestamp(_required(doc,"created_at")))
    except Exception as error:
        if isinstance(error, FinancialApprovalActorAuthorizationPersistedRecordInvalidError): raise
        raise FinancialApprovalActorAuthorizationPersistedRecordInvalidError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_PERSISTED_RECORD_INVALID") from error

def _fingerprint(auth: FinancialApprovalActorAuthorization, key: str) -> str:
    return hashlib.sha3_512(json.dumps({**auth.to_dict(), "idempotency_key": key}, sort_keys=True, separators=(",",":"), ensure_ascii=True).encode()).hexdigest()

class FinancialApprovalActorAuthorizationRegistry:
    @staticmethod
    def ensure_indexes(collection: Optional[Collection]=None) -> None:
        c=_collection(collection)
        c.create_index([("tenant_id",ASCENDING),("authorization_id",ASCENDING)],unique=True,name="tenant_actor_authorization_identity_unique")
        c.create_index([("tenant_id",ASCENDING),("evaluation_id",ASCENDING),("requirement_id",ASCENDING)],name="tenant_evaluation_requirement")
        c.create_index([("tenant_id",ASCENDING),("subject_type",ASCENDING),("subject_id",ASCENDING),("subject_revision",ASCENDING)],name="tenant_subject_revision")
        c.create_index([("tenant_id",ASCENDING),("actor_id",ASCENDING),("evaluation_id",ASCENDING)],name="tenant_actor_evaluation")
        c.create_index([("tenant_id",ASCENDING),("evaluation_id",ASCENDING),("requirement_id",ASCENDING),("actor_capacity",ASCENDING)],name="tenant_evaluation_requirement_capacity")
        c.create_index([("tenant_id",ASCENDING),("created_at",ASCENDING)],name="tenant_created_at")

    @staticmethod
    def create(authorization: FinancialApprovalActorAuthorization, idempotency_key: str, collection: Optional[Collection]=None) -> FinancialApprovalActorAuthorizationCreateResult:
        if not isinstance(authorization,FinancialApprovalActorAuthorization): raise FinancialApprovalActorAuthorizationDomainError("authorization must be FinancialApprovalActorAuthorization")
        if not isinstance(idempotency_key,str) or not idempotency_key.strip() or len(idempotency_key.strip())>128: raise FinancialApprovalActorAuthorizationDomainError("idempotency_key must be a non-empty string of at most 128 characters")
        key=idempotency_key.strip(); c=_collection(collection); eval_doc=FinancialApprovalPolicyEvaluationRegistry.get(authorization.tenant_id,authorization.evaluation_id,c.database["financial_approval_policy_evaluations"])
        if any((authorization.tenant_id,authorization.subject_type.value,authorization.subject_id,authorization.subject_revision,authorization.approval_policy_reference,authorization.approval_policy_version)!=(eval_doc.tenant_id,eval_doc.subject_type.value,eval_doc.subject_id,eval_doc.subject_revision,eval_doc.approval_policy_reference,eval_doc.approval_policy_version) for _ in [0]): raise FinancialApprovalAuthorizationEvaluationMismatchError("FINANCIAL_APPROVAL_AUTHORIZATION_EVALUATION_MISMATCH")
        if not eval_doc.approval_required: raise FinancialApprovalActorAuthorizationRegistryError("FINANCIAL_APPROVAL_AUTHORIZATION_SUBJECT_INELIGIBLE")
        requirement=next((r for r in eval_doc.approval_requirements if r.requirement_id==authorization.requirement_id),None)
        if requirement is None: raise FinancialApprovalAuthorizationRequirementNotFoundError("FINANCIAL_APPROVAL_AUTHORIZATION_REQUIREMENT_NOT_FOUND")
        if requirement.actor_capacity!=authorization.actor_capacity: raise FinancialApprovalAuthorizationCapacityMismatchError("FINANCIAL_APPROVAL_AUTHORIZATION_CAPACITY_MISMATCH")
        document={**authorization.to_dict(),"create_idempotency_key":key}; document["create_fingerprint"]=_fingerprint(authorization,key)
        try: c.insert_one(document)
        except DuplicateKeyError as error:
            existing=c.find_one({"tenant_id":authorization.tenant_id,"authorization_id":authorization.authorization_id})
            if existing is None: raise FinancialApprovalActorAuthorizationCreateConflictError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_CREATE_CONFLICT") from error
            persisted=_hydrate(existing)
            if existing.get("create_idempotency_key")==key and existing.get("create_fingerprint")==document["create_fingerprint"]: return FinancialApprovalActorAuthorizationCreateResult(FinancialApprovalActorAuthorizationCreateOutcome.IDEMPOTENT_REPLAY,persisted)
            if existing.get("create_idempotency_key")==key: raise FinancialApprovalActorAuthorizationIdempotencyKeyReuseError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND") from error
            raise FinancialApprovalActorAuthorizationCreateConflictError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_CREATE_CONFLICT") from error
        except PyMongoError as error: raise FinancialApprovalActorAuthorizationRegistryError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_CREATE_FAILED") from error
        return FinancialApprovalActorAuthorizationCreateResult(FinancialApprovalActorAuthorizationCreateOutcome.CREATED,authorization)

    @staticmethod
    def get(tenant_id:str, authorization_id:str, collection:Optional[Collection]=None)->FinancialApprovalActorAuthorization:
        if not isinstance(tenant_id,str) or not tenant_id.strip() or not isinstance(authorization_id,str) or not authorization_id.strip(): raise FinancialApprovalActorAuthorizationDomainError("tenant_id and authorization_id are required strings")
        doc=_collection(collection).find_one({"tenant_id":tenant_id.strip(),"authorization_id":authorization_id.strip()})
        if doc is None: raise FinancialApprovalActorAuthorizationNotFoundError("FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_NOT_FOUND")
        return _hydrate(doc)

    @staticmethod
    def list_for_requirement(tenant_id:str,evaluation_id:str,requirement_id:str,limit:int=100,collection:Optional[Collection]=None,*,session:Optional[ClientSession]=None)->Sequence[FinancialApprovalActorAuthorization]:
        if not all(isinstance(v,str) and v.strip() for v in (tenant_id,evaluation_id,requirement_id)): raise FinancialApprovalActorAuthorizationDomainError("tenant_id, evaluation_id, and requirement_id are required strings")
        if not isinstance(limit,int) or isinstance(limit,bool) or limit<1 or limit>MAX_LIST_LIMIT: raise FinancialApprovalActorAuthorizationDomainError(f"limit must be an integer from 1 to {MAX_LIST_LIMIT}")
        rows=_collection(collection).find({"tenant_id":tenant_id.strip(),"evaluation_id":evaluation_id.strip(),"requirement_id":requirement_id.strip()},session=session).sort([("created_at",ASCENDING),("authorization_id",ASCENDING)]).limit(limit)
        return tuple(_hydrate(row) for row in rows)

    @staticmethod
    def list_for_requirement_page(tenant_id:str,evaluation_id:str,requirement_id:str,page_size:int=MAX_LIST_LIMIT,cursor:Optional[str]=None,collection:Optional[Collection]=None,*,session:Optional[ClientSession]=None)->FinancialApprovalActorAuthorizationPage:
        if not all(isinstance(v,str) and v.strip() for v in (tenant_id,evaluation_id,requirement_id)): raise FinancialApprovalActorAuthorizationDomainError("tenant_id, evaluation_id, and requirement_id are required strings")
        if not isinstance(page_size,int) or isinstance(page_size,bool) or page_size<1 or page_size>MAX_LIST_LIMIT: raise FinancialApprovalActorAuthorizationDomainError(f"page_size must be an integer from 1 to {MAX_LIST_LIMIT}")
        predicate: dict[str,Any] = {"tenant_id":tenant_id.strip(),"evaluation_id":evaluation_id.strip(),"requirement_id":requirement_id.strip()}
        if cursor is not None:
            try:
                if not isinstance(cursor,str) or not cursor.strip() or len(cursor)>512: raise ValueError("cursor")
                payload=json.loads(base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8"))
                if not isinstance(payload,dict) or set(payload)!={"created_at","authorization_id"} or not isinstance(payload["created_at"],str) or not isinstance(payload["authorization_id"],str) or not payload["authorization_id"].strip(): raise ValueError("cursor")
                _timestamp(payload["created_at"])
                predicate["$or"]=[{"created_at":{"$gt":payload["created_at"]}},{"created_at":payload["created_at"],"authorization_id":{"$gt":payload["authorization_id"]}}]
            except Exception as error: raise FinancialApprovalActorAuthorizationDomainError("cursor is invalid") from error
        rows=list(_collection(collection).find(predicate,session=session).sort([("created_at",ASCENDING),("authorization_id",ASCENDING)]).limit(page_size+1))
        items=tuple(_hydrate(row) for row in rows[:page_size]); next_cursor=None
        if len(rows)>page_size:
            last=items[-1]; next_cursor=base64.urlsafe_b64encode(json.dumps({"created_at":last.created_at.isoformat(),"authorization_id":last.authorization_id},separators=(",",":")).encode()).decode()
        return FinancialApprovalActorAuthorizationPage(items,next_cursor)
