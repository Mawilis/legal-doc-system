"""WILSY OS immutable Legal Matter Workflow Transition registry.

TITLE: Legal Matter Workflow Transition Registry
VERSION: v1.0.0-G7G-P0B-DURABLE-TRANSITION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist immutable tenant/matter/workflow progression evidence and derive
         currentness from instance start plus the complete durable transition chain.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_matter_workflow_transition_registry.py
COLLABORATION / OWNERSHIP: Transition and currentness domains own semantics; this
                            registry owns durability, replay, ordered history,
                            lineage validation, and derivation composition only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0B establishes append-only transition history, exact replay,
           strict tenant/matter/instance correlation, and no mutable current pointer.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Every persistence predicate starts with tenant_id.
TENANT BOUNDARY: Foreign-tenant absence never discloses durable existence.
AUTHORITY BOUNDARY: Persistence does not authorize transitions, IAM, assignment,
                    supervision, work generation, or legal-event truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Caller owns the active transaction and whole retry.
FAIL-CLOSED DECLARATION: Invalid input, divergence, corrupt/forked/gapped history,
                         correlation drift, race and outage reject.
"""
from __future__ import annotations
from collections.abc import Mapping
import hmac
from typing import Any,Final,NoReturn,cast
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError,PyMongoError
from tools.eos.legal_operations.domain.legal_matter_workflow_currentness import LegalMatterWorkflowCurrentness
from tools.eos.legal_operations.domain.legal_matter_workflow_instance import LegalMatterWorkflowInstance
from tools.eos.legal_operations.domain.legal_matter_workflow_transition import LegalMatterWorkflowTransition,LegalMatterWorkflowTransitionError

VERSION:Final[str]="v1.0.0-G7G-P0B-DURABLE-TRANSITION-REGISTRY"
COLLECTION_NAME:Final[str]="legal_matter_workflow_transitions"
IDENTITY_INDEX_NAME:Final[str]="legal_matter_workflow_transition_identity_unique"
FINGERPRINT_INDEX_NAME:Final[str]="legal_matter_workflow_transition_fingerprint_unique"
SEQUENCE_INDEX_NAME:Final[str]="legal_matter_workflow_transition_sequence_unique"
MATTER_HISTORY_INDEX_NAME:Final[str]="legal_matter_workflow_transition_matter_history"

class LegalMatterWorkflowTransitionRegistryError(RuntimeError):
    """Base stable registry error."""
    def __init__(self,code:str)->None:self.code=code;super().__init__(code)
class LegalMatterWorkflowTransitionRegistryInputError(LegalMatterWorkflowTransitionRegistryError):"""Invalid input."""
class LegalMatterWorkflowTransitionRegistryTransactionRequiredError(LegalMatterWorkflowTransitionRegistryError):"""Active transaction absent."""
class LegalMatterWorkflowTransitionRegistryConflictError(LegalMatterWorkflowTransitionRegistryError):"""Replay or lineage conflict."""
class LegalMatterWorkflowTransitionRegistryNotFoundError(LegalMatterWorkflowTransitionRegistryError):"""Transition absent."""
class LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError(LegalMatterWorkflowTransitionRegistryError):"""Durable history invalid."""
class LegalMatterWorkflowTransitionRegistryRetryTransactionError(LegalMatterWorkflowTransitionRegistryError):"""Whole retry required."""
class LegalMatterWorkflowTransitionRegistryPersistenceError(LegalMatterWorkflowTransitionRegistryError):"""Mongo failure."""

def _raise(kind:type[LegalMatterWorkflowTransitionRegistryError],code:str,cause:BaseException|None=None)->NoReturn:
    error=kind(code)
    if cause is None:raise error
    raise error from cause

def _tx(session:object)->object:
    marker=getattr(session,"in_transaction",None) if session is not None else None
    try:active=marker() if callable(marker) else marker
    except (AttributeError,TypeError) as error:_raise(LegalMatterWorkflowTransitionRegistryTransactionRequiredError,"G7G_P0B_ACTIVE_TRANSACTION_REQUIRED",error)
    if active is not True:_raise(LegalMatterWorkflowTransitionRegistryTransactionRequiredError,"G7G_P0B_ACTIVE_TRANSACTION_REQUIRED")
    return session

def _text(name:str,value:object)->str:
    if not isinstance(value,str) or not value or value!=value.strip() or len(value)>320:_raise(LegalMatterWorkflowTransitionRegistryInputError,f"G7G_P0B_{name.upper()}_INVALID")
    return value
def _tenant(value:object)->str:
    tenant=_text("tenant_id",value)
    if tenant.casefold() in {"default","global","global_root","root","master","*"}:_raise(LegalMatterWorkflowTransitionRegistryInputError,"G7G_P0B_TENANT_REQUIRED")
    return tenant
def _hydrate(raw:Mapping[str,object])->LegalMatterWorkflowTransition:
    row=dict(raw);row.pop("_id",None)
    try:value=LegalMatterWorkflowTransition.from_dict(row)
    except (LegalMatterWorkflowTransitionError,TypeError,ValueError,KeyError) as error:_raise(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,"G7G_P0B_PERSISTED_RECORD_INVALID",error)
    if value.to_dict()!=row:_raise(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,"G7G_P0B_RECORD_CORRELATION_INVALID")
    return value
def _mongo(error:PyMongoError)->NoReturn:
    try:transient=error.has_error_label("TransientTransactionError")
    except Exception:transient=False
    if transient:_raise(LegalMatterWorkflowTransitionRegistryRetryTransactionError,"G7G_P0B_WHOLE_TRANSACTION_RETRY_REQUIRED",error)
    _raise(LegalMatterWorkflowTransitionRegistryPersistenceError,"G7G_P0B_PERSISTENCE_FAILURE",error)

def _validate(values:tuple[LegalMatterWorkflowTransition,...])->tuple[LegalMatterWorkflowTransition,...]:
    ordered=tuple(sorted(values,key=lambda value:(value.sequence_number,value.transition_id)))
    for index,value in enumerate(ordered):
        if index==0:
            if value.sequence_number!=1 or value.previous_transition_fingerprint is not None:_raise(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,"G7G_P0B_HISTORY_ROOT_INVALID")
            continue
        previous=ordered[index-1]
        if value.sequence_number!=previous.sequence_number+1 or value.previous_transition_fingerprint!=previous.fingerprint or value.source_stage_definition_id!=previous.target_stage_definition_id or value.transitioned_at<previous.transitioned_at:_raise(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,"G7G_P0B_HISTORY_LINEAGE_INVALID")
        if value.tenant_id!=ordered[0].tenant_id or value.workflow_instance_id!=ordered[0].workflow_instance_id or value.case_matter_id!=ordered[0].case_matter_id:_raise(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,"G7G_P0B_HISTORY_SCOPE_INVALID")
    return ordered

class LegalMatterWorkflowTransitionRegistry:
    """Append-only transition durability and derived-currentness facade."""
    def __init__(self,collection:Any)->None:
        """Bind one collection without lifecycle authority."""
        if collection is None:_raise(LegalMatterWorkflowTransitionRegistryInputError,"G7G_P0B_COLLECTION_REQUIRED")
        self._collection=collection
    def ensure_indexes(self)->None:
        """Create tenant-first unique history indexes without TTL."""
        indexes=(
            ([("tenant_id",ASCENDING),("transition_id",ASCENDING)],True,IDENTITY_INDEX_NAME),
            ([("tenant_id",ASCENDING),("fingerprint",ASCENDING)],True,FINGERPRINT_INDEX_NAME),
            ([("tenant_id",ASCENDING),("workflow_instance_id",ASCENDING),("sequence_number",ASCENDING)],True,SEQUENCE_INDEX_NAME),
            ([("tenant_id",ASCENDING),("case_matter_id",ASCENDING),("workflow_instance_id",ASCENDING),("sequence_number",ASCENDING)],False,MATTER_HISTORY_INDEX_NAME),
        )
        try:
            for keys,unique,name in indexes:self._collection.create_index(keys,unique=unique,name=name)
        except AttributeError as error:_raise(LegalMatterWorkflowTransitionRegistryInputError,"G7G_P0B_COLLECTION_INTERFACE_INVALID",error)
        except PyMongoError as error:_mongo(error)
    def create_or_replay(self,value:LegalMatterWorkflowTransition,*,session:object)->LegalMatterWorkflowTransition:
        """Persist one next transition or return exact replay."""
        if type(value) is not LegalMatterWorkflowTransition:_raise(LegalMatterWorkflowTransitionRegistryInputError,"G7G_P0B_TRANSITION_REQUIRED")
        tx=_tx(session)
        try:
            raw=self._collection.find_one({"tenant_id":value.tenant_id,"transition_id":value.transition_id},session=tx)
            if raw is not None:
                persisted=_hydrate(cast(Mapping[str,object],raw))
                if hmac.compare_digest(persisted.fingerprint,value.fingerprint) and persisted==value:return persisted
                _raise(LegalMatterWorkflowTransitionRegistryConflictError,"G7G_P0B_DIVERGENT_REPLAY")
            history=self.list_history(value.tenant_id,value.workflow_instance_id,session=tx)
            if not history:coherent=value.sequence_number==1 and value.previous_transition_fingerprint is None
            else:
                previous=history[-1]
                coherent=value.sequence_number==previous.sequence_number+1 and value.previous_transition_fingerprint==previous.fingerprint and value.source_stage_definition_id==previous.target_stage_definition_id and value.case_matter_id==previous.case_matter_id and value.transitioned_at>=previous.transitioned_at
            if not coherent:_raise(LegalMatterWorkflowTransitionRegistryConflictError,"G7G_P0B_LINEAGE_CONFLICT")
            self._collection.insert_one(value.to_dict(),session=tx)
        except DuplicateKeyError as error:_raise(LegalMatterWorkflowTransitionRegistryRetryTransactionError,"G7G_P0B_DUPLICATE_RACE_RETRY_TRANSACTION",error)
        except LegalMatterWorkflowTransitionRegistryError:raise
        except PyMongoError as error:_mongo(error)
        return value
    def list_history(self,tenant_id:str,workflow_instance_id:str,*,session:object)->tuple[LegalMatterWorkflowTransition,...]:
        """Return complete validated transition history for one instance."""
        tenant=_tenant(tenant_id);instance=_text("workflow_instance_id",workflow_instance_id);tx=_tx(session)
        try:rows=tuple(self._collection.find({"tenant_id":tenant,"workflow_instance_id":instance},session=tx).sort([("sequence_number",ASCENDING),("transition_id",ASCENDING)]))
        except PyMongoError as error:_mongo(error)
        values=tuple(_hydrate(cast(Mapping[str,object],row)) for row in rows)
        if any(v.tenant_id!=tenant or v.workflow_instance_id!=instance for v in values):_raise(LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError,"G7G_P0B_PERSISTED_SCOPE_MISMATCH")
        return _validate(values)
    def derive_currentness(self,currentness_id:str,workflow_instance:LegalMatterWorkflowInstance,*,session:object)->LegalMatterWorkflowCurrentness:
        """Derive current stage from instance start and complete durable history."""
        if type(workflow_instance) is not LegalMatterWorkflowInstance:_raise(LegalMatterWorkflowTransitionRegistryInputError,"G7G_P0B_INSTANCE_REQUIRED")
        history=self.list_history(workflow_instance.tenant_id,workflow_instance.workflow_instance_id,session=session)
        return LegalMatterWorkflowCurrentness.derive(currentness_id=_text("currentness_id",currentness_id),workflow_instance=workflow_instance,transitions=history)

def ensure_indexes(collection:Any)->None:
    """Create governed indexes on one explicit collection."""
    LegalMatterWorkflowTransitionRegistry(collection).ensure_indexes()
__all__=["VERSION","COLLECTION_NAME","IDENTITY_INDEX_NAME","FINGERPRINT_INDEX_NAME","SEQUENCE_INDEX_NAME","MATTER_HISTORY_INDEX_NAME","LegalMatterWorkflowTransitionRegistry","LegalMatterWorkflowTransitionRegistryError","LegalMatterWorkflowTransitionRegistryInputError","LegalMatterWorkflowTransitionRegistryTransactionRequiredError","LegalMatterWorkflowTransitionRegistryConflictError","LegalMatterWorkflowTransitionRegistryNotFoundError","LegalMatterWorkflowTransitionRegistryPersistedRecordInvalidError","LegalMatterWorkflowTransitionRegistryRetryTransactionError","LegalMatterWorkflowTransitionRegistryPersistenceError","ensure_indexes"]
# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_matter_workflow_transition_registry.py
# VERSION: v1.0.0-G7G-P0B-DURABLE-TRANSITION-REGISTRY
# AUTHORITY BOUNDARY: immutable transition durability and currentness derivation only
# TENANT POSTURE: exact tenant/matter/workflow-instance correlation
# FAIL-CLOSED POSTURE: invalid input, divergence, corrupt lineage, race, and outage reject
# MUTABLE CURRENT POINTER / TTL / UPDATE / DELETE AUTHORITY: NONE
# IAM / WORK / ASSIGNMENT / SUPERVISION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
