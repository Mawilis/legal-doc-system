"""TITLE: Accounts Payable Runtime Binding Registry.
VERSION: v1.0.4-M11E2C3-R4I-R1.
AUTHORITY: Durable AP binding history and explicit current head.
EPITOME: Separates immutable history from compare-and-swap currentness.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/accounts_payable_provider_policy_runtime_binding_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS AP runtime authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.4-M11E2C3-R4I-R1 validates explicit head integrity against exact immutable history.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every operation is tenant and family scoped.
AUTHORITY BOUNDARY: Binding persistence/currentness only; no selection.
"""
from datetime import datetime
from typing import Any
from ..domain.accounts_payable_provider_policy_runtime_binding import AccountsPayableProviderPolicyRuntimeBinding, AP_POLICY_FAMILY
class AccountsPayableProviderPolicyRuntimeBindingRegistryError(RuntimeError): pass
class AccountsPayableProviderPolicyRuntimeBindingRegistry:
    @staticmethod
    def ensure_indexes(collection:Any)->None: collection.create_index([('tenant_id',1),('family',1),('binding_revision',1)],unique=True,name='ap_binding_revision_unique')
    @staticmethod
    def _tx(session:Any)->Any:
        if session is None or getattr(session,'in_transaction',False) is not True: raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('ACTIVE_TRANSACTION_REQUIRED')
        return session
    @staticmethod
    def create(binding:AccountsPayableProviderPolicyRuntimeBinding, collection:Any, *, session:Any=None)->AccountsPayableProviderPolicyRuntimeBinding:
        tx=AccountsPayableProviderPolicyRuntimeBindingRegistry._tx(session); q={'tenant_id':binding.tenant_id,'family':AP_POLICY_FAMILY,'binding_revision':binding.binding_revision}; old=collection.find_one(q,session=tx)
        if old is not None:
            if old.get('binding_fingerprint')==binding.binding_fingerprint:return binding
            raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('BINDING_REVISION_CONFLICT')
        headq={'tenant_id':binding.tenant_id,'family':AP_POLICY_FAMILY,'_kind':'head'}; head=collection.find_one(headq,session=tx)
        if binding.binding_revision==1:
            if head is not None:raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('HEAD_ALREADY_EXISTS')
        elif head is None or head.get('binding_revision')!=binding.binding_revision-1 or head.get('binding_id')!=binding.previous_binding_id or head.get('binding_fingerprint')!=binding.previous_binding_fingerprint:raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('PREDECESSOR_INVALID')
        collection.insert_one({**binding.to_persisted(),'_kind':'binding'},session=tx)
        new_head={**headq,'binding_revision':binding.binding_revision,'binding_id':binding.binding_id,'binding_fingerprint':binding.binding_fingerprint}
        if binding.binding_revision == 1:
            collection.insert_one(new_head,session=tx)
        else:
            cas={**headq,'binding_revision':binding.binding_revision-1,'binding_id':binding.previous_binding_id,'binding_fingerprint':binding.previous_binding_fingerprint}
            result=collection.replace_one(cas,new_head,session=tx)
            if getattr(result,'matched_count',0) != 1:
                raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('PREDECESSOR_INVALID')
        return binding
    @staticmethod
    def get(tenant_id:str, collection:Any, *, revision:int, session:Any=None):
        row=collection.find_one({'tenant_id':tenant_id,'family':AP_POLICY_FAMILY,'binding_revision':revision,'_kind':'binding'},**({'session':session} if session is not None else {}))
        if row is None:return None
        body=dict(row);body.pop('_id',None);body.pop('_kind',None)
        for k in ('activated_at','created_at'):
            if isinstance(body.get(k),str):body[k]=datetime.fromisoformat(body[k])
        try:return AccountsPayableProviderPolicyRuntimeBinding(**body)
        except Exception as e:raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('BINDING_PERSISTED_RECORD_INVALID') from e
    @staticmethod
    def current(tenant_id:str, collection:Any, *, session:Any=None):
        q={'tenant_id':tenant_id,'family':AP_POLICY_FAMILY,'_kind':'head'}
        heads=list(collection.find(q,**({'session':session} if session is not None else {})))
        if len(heads)>1:
            raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('MULTIPLE_CURRENT_HEADS')
        if not heads:
            return None
        head=heads[0]
        required=('tenant_id','family','binding_id','binding_revision','binding_fingerprint')
        if any(key not in head for key in required) or head.get('tenant_id') != tenant_id or head.get('family') != AP_POLICY_FAMILY:
            raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('BINDING_PERSISTED_RECORD_INVALID')
        binding=AccountsPayableProviderPolicyRuntimeBindingRegistry.get(tenant_id,collection,revision=head['binding_revision'],session=session)
        if binding is None or (binding.tenant_id,binding.family,binding.binding_id,binding.binding_revision,binding.binding_fingerprint) != (head['tenant_id'],head['family'],head['binding_id'],head['binding_revision'],head['binding_fingerprint']):
            raise AccountsPayableProviderPolicyRuntimeBindingRegistryError('BINDING_PERSISTED_RECORD_INVALID')
        return binding
    @staticmethod
    def has_history(tenant_id:str, collection:Any, *, session:Any=None)->bool:
        """Return whether any AP binding history exists for this tenant."""
        AccountsPayableProviderPolicyRuntimeBindingRegistry._tx(session)
        row=collection.find_one({'tenant_id':tenant_id,'family':AP_POLICY_FAMILY,'_kind':'binding'},session=session)
        return row is not None
    @staticmethod
    def has_consumed_activation_authorization(tenant_id:str, authorization_id:str, authorization_fingerprint:str, collection:Any, *, session:Any=None)->bool:
        """Return existence-only proof that exact activation evidence was consumed by AP history."""
        AccountsPayableProviderPolicyRuntimeBindingRegistry._tx(session)
        row=collection.find_one({'tenant_id':tenant_id,'family':AP_POLICY_FAMILY,'_kind':'binding','activation_authorization_evidence_id':authorization_id,'activation_authorization_evidence_fingerprint':authorization_fingerprint},session=session)
        return row is not None
# ARTIFACT: accounts_payable_provider_policy_runtime_binding_registry.py
# VERSION: v1.0.4-M11E2C3-R4I-R1
# AUTHORITY BOUNDARY: AP binding history and explicit current head
# TENANT POSTURE: exact tenant/family scope
# FAIL-CLOSED POSTURE: stale predecessors and corrupt history reject
# END OF WILSY OS SOVEREIGN ARTIFACT
