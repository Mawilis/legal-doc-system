"""TITLE: Accounts Payable Provider Policy Registry.
VERSION: v1.0.0-M11E2C2.
AUTHORITY: Durable immutable AP eligibility evidence.
EPITOME: Tenant-scoped replay-safe AP policy persistence.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/accounts_payable_provider_policy_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS AP registry.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes strict hydration and replay protection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every key and lookup includes tenant identity.
AUTHORITY BOUNDARY: Persistence only; never currentness or selection.
"""
from datetime import datetime
from typing import Any
from ..domain.accounts_payable_provider_policy import AccountsPayableProviderPolicy, AccountsPayableProviderPolicyError, AP_POLICY_FAMILY

class AccountsPayableProviderPolicyRegistryError(RuntimeError):
    """Raised for persistence, replay, or hydration failures."""

class AccountsPayableProviderPolicyRegistry:
    """Caller-transaction-owned immutable AP policy registry."""
    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        collection.create_index([('tenant_id', 1), ('policy_id', 1), ('policy_revision', 1)], unique=True, name='accounts_payable_provider_policy_revision_unique')

    @staticmethod
    def create(policy: AccountsPayableProviderPolicy, collection: Any, *, session: Any = None) -> AccountsPayableProviderPolicy:
        query = {'tenant_id': policy.tenant_id, 'policy_id': policy.policy_id, 'policy_revision': policy.policy_revision}
        kwargs = {'session': session} if session is not None else {}
        try:
            existing = collection.find_one(query, **kwargs)
            if existing is not None:
                if dict(existing).get('policy_fingerprint') == policy.policy_fingerprint:
                    return AccountsPayableProviderPolicyRegistry.get(policy.tenant_id, policy.policy_id, collection, revision=policy.policy_revision, session=session)
                raise AccountsPayableProviderPolicyRegistryError('POLICY_REVISION_CONFLICT')
            collection.insert_one(policy.to_persisted(), **kwargs)
            return policy
        except AccountsPayableProviderPolicyRegistryError:
            raise
        except Exception as error:
            raise AccountsPayableProviderPolicyRegistryError('POLICY_PERSISTENCE_FAILED') from error

    @staticmethod
    def get(tenant_id: str, policy_id: str, collection: Any, *, revision: int, session: Any = None) -> AccountsPayableProviderPolicy:
        kwargs = {'session': session} if session is not None else {}
        try:
            row = collection.find_one({'tenant_id': tenant_id, 'policy_id': policy_id, 'policy_revision': revision}, **kwargs)
            if row is None:
                raise AccountsPayableProviderPolicyRegistryError('POLICY_NOT_FOUND')
            body = dict(row); body.pop('_id', None)
            if body.get('family') != AP_POLICY_FAMILY:
                raise AccountsPayableProviderPolicyRegistryError('POLICY_FAMILY_INVALID')
            body.pop('family', None)
            body['eligible_provider_names'] = tuple(body['eligible_provider_names'])
            body['created_at'] = datetime.fromisoformat(body['created_at'])
            return AccountsPayableProviderPolicy(**body)
        except AccountsPayableProviderPolicyRegistryError:
            raise
        except (KeyError, TypeError, ValueError, AccountsPayableProviderPolicyError) as error:
            raise AccountsPayableProviderPolicyRegistryError('POLICY_PERSISTED_RECORD_INVALID') from error
        except Exception as error:
            raise AccountsPayableProviderPolicyRegistryError('POLICY_LOOKUP_FAILED') from error

# ARTIFACT: accounts_payable_provider_policy_registry.py
# VERSION: v1.0.0-M11E2C2
# AUTHORITY BOUNDARY: durable AP policy evidence only
# TENANT POSTURE: exact tenant/policy/revision lookup
# FAIL-CLOSED POSTURE: corrupt records and divergent replay reject
# END OF WILSY OS SOVEREIGN ARTIFACT
