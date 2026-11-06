# EOS Dunning Worker — Transaction and Execution Contract

**Status:** DESIGN / NOT IMPLEMENTED  
**Production mutation authorized:** No  
**Canonical API owner today:** `tools/eos/api/billing_router.py`  
**Current scheduler owner today:** `tools/eos/api/server.py`  
**Review boundary:** Legal/product policy, billing authority, subscription lifecycle, and platform operations

## 1. Current source facts

1. The API process arms an in-process asyncio scheduler for daily 00:15 Africa/Johannesburg. `WILSY_DUNNING_SCHEDULER_ENABLED` defaults false in production mode and true outside production unless explicitly overridden.
2. The scheduler calls `evaluate_all_tenant_dunning_lifecycles()`; that function scans `platform_invoices` and calls the API evaluator once per tenant. It shares the API's kernel Mongo client and database. There is no separate dunning worker process or independent MongoDB identity proven in the repository.
3. The evaluator reads `billing_dunning_policies`, `platform_invoices`, and `billing_dunning_states`; it writes state with `update_one(..., upsert=True)`, subscription projection with `subscriptions.update_many`, then appends to `billing_audit_events`. These writes do not share a Mongo session/transaction. Telemetry is emitted inline after these writes.
4. `collections_day` is normalized, persisted and exposed in the policy DTO, but `_dunning_state_for_days` does not use it. The current ordered states are ACTIVE, WARNING, CRITICAL, SUSPENDED_READONLY and TERMINATED. No COLLECTIONS state/action exists in the current evaluator.
5. The evaluator processes each invoice separately. Multiple overdue invoices for one subscription can cause multiple intermediate state transitions in one pass. The final monotonic state may converge to the highest ordinal, but emitted transition/audit history depends on invoice cursor order.
6. `SubscriptionRegistry` has a tenant + subscription unique index and its own revision-checked replacement mechanism. The current dunning evaluator bypasses that registry and updates subscription documents directly with `update_many`.
7. Repository search found the current Python writer for `suspension_state` / `dunning_state` in the billing evaluator, but no other Python reader in the reviewed source. This does not prove that external/legacy consumers do not read those fields.
8. No canonical registry/index owner was found for `billing_dunning_states` or `billing_dunning_policies`. The billing router writes `billing_audit_events`, a shared collection with multiple event families and no dunning-specific idempotency contract.

## 2. Required policy decision — hard gate

No implementation may assign semantics to `collections_day` by inference.

The policy owner must determine whether day 21 means:
- a distinct COLLECTIONS access state;
- an external referral/collection workflow event while access remains unchanged;
- an escalation/notification threshold with no access-state transition; or
- a retired compatibility field that must be explicitly deprecated.

The decision must specify the responsible authority, permitted action, required evidence, notification obligations, reversal/cure behavior, and whether it changes tenant service access. Until approved, the worker must not silently ignore or reinterpret this field as if policy were complete.

## 3. Proposed worker boundary

The future dunning worker is a separate process, not a task inside the public API server.

- Dedicated non-production and production runtime identities; no Atlas administrator role.
- Dedicated worker connection configuration/secret reference, separate from API, migration and provisioner credentials.
- No index creation, collection creation, KMS administration, secret administration, or broad database administration.
- Read only the canonical invoice, subscription and policy evidence needed for evaluation.
- Write only the dunning lease, state, transition-event and explicitly approved service-access projection collections.
- No provider payment execution, refund, invoice settlement, paid-state mutation or commercial entitlement authority.
- Worker deployment and credential source must be independently verified before any activation. No such identity is currently proven.

The API route may submit or inspect an evaluation request, but it must not share scheduler ownership with the worker. Exactly one governed worker schedule should be active per environment.

## 4. Deterministic evaluation contract

Before opening a transaction, the worker may discover candidate tenant/subscription pairs using bounded indexed reads. Candidate discovery grants no mutation authority.

For each tenant + subscription pair:

1. Acquire a lease with a unique tenant/subscription identity, owner token, expiry and monotonically increasing fencing revision.
2. Read a deterministic snapshot of every relevant platform invoice for that subscription, including status, due date, invoice identity and canonical tenant/subscription correlation.
3. Exclude paid, void, cancelled and not-yet-due invoices. Reject malformed/missing identity or ambiguous subscription correlation rather than widening the query.
4. Aggregate all eligible overdue invoices before deriving one target state. Do not emit one transition per invoice.
5. Select the triggering invoice deterministically (greatest overdue duration, then stable invoice identity tie-break); persist the selected evidence set/fingerprint so a retry cannot silently choose a different invoice.
6. Read the tenant policy with an explicit policy revision and fingerprint. A policy change invalidates the snapshot and requires a fresh evaluation.
7. Read the current dunning state and revision. State is monotonic unless an explicitly governed cure/reinstatement contract authorizes a reverse transition.
8. Revalidate lease owner/fencing revision, invoice status and due-date facts, policy revision, subscription identity/revision, and dunning-state revision inside the transaction.
9. Perform the state transition with compare-and-set on the expected revision. No blind upsert after the canonical state exists.
10. Update only the dedicated dunning/access-posture projection through its own expected-revision predicate. Do not use broad `update_many` against subscriptions.
11. Append exactly one immutable transition event with the same transaction and deterministic idempotency identity.
12. Commit. Emit telemetry only after confirmed commit.

If the deployment has not yet established which external/legacy consumers enforce read-only or terminated access, the new projection must not be treated as an enforcement boundary. Consumer discovery and migration are prerequisites to activation.

## 5. Proposed persistence contract and index candidates

These are **proposed contracts**, not source-declared indexes and not yet approved for the canonical manifest.

| Collection | Required identity / concurrency contract | Candidate index |
|---|---|---|
| `billing_dunning_evaluation_leases` | One lease per tenant + subscription; owner token, expiry, fencing revision | Unique `tenant_id, subscription_id`; lease-expiry lookup on `lease_expires_at` |
| `billing_dunning_states` | One current state per tenant + subscription; integer revision; policy revision; source snapshot fingerprint | Unique `tenant_id, subscription_id`; optional state timeline only if a query requires it |
| `billing_dunning_transition_events` | Append-only event; deterministic idempotency key; exact snapshot/policy/state revision references | Unique `tenant_id, idempotency_key`; unique `tenant_id, transition_id`; tenant/subscription/time history |
| `billing_dunning_access_postures` | Dedicated consumer projection; one current posture per tenant + subscription; CAS revision | Unique `tenant_id, subscription_id`; tenant/posture lookup |

The worker must not add these indexes itself. A separate provisioner must own them after source contract approval, duplicate-data preflight, and exact option validation.

### Deterministic transition identity

The idempotency identity must derive from stable business inputs, not evaluation time. Candidate fields:

`tenant_id + subscription_id + selected_invoice_id + target_state + policy_revision + source_snapshot_fingerprint`

The implementation must use a canonical, versioned serialization and cryptographic digest. Re-running the same snapshot must resolve to the same transition identity. A changed invoice, policy revision or target state must not be mistaken for replay.

## 6. Transaction and unknown-commit handling

- One caller-owned Mongo session/transaction covers state CAS, access-posture CAS and immutable transition event append.
- Lease acquisition may precede the transaction, but the transaction must revalidate the fencing token and lease ownership before any state write.
- On transient transaction error, abort and retry the entire evaluation from fresh reads, bounded by an explicit retry budget.
- On unknown commit result, resolve using a fresh primary read of the exact deterministic transition idempotency key and matching fingerprints. Never blindly repeat a non-idempotent write.
- Duplicate-key races inside an active transaction require whole-transaction abort and fresh retry; they must not be swallowed as a successful replay inside an aborted transaction.
- A stale lease holder must be unable to commit after a newer fencing revision has been issued.

## 7. Required replica-set certification

The implementation is not eligible for worker activation until a disposable writable replica-set suite proves:

1. two concurrent workers evaluating the same tenant/subscription;
2. lease expiry and stale-holder fencing;
3. deterministic aggregation across multiple overdue invoices in different cursor orders;
4. paid/void/cancelled invoice race during evaluation;
5. invoice due-date correction during evaluation;
6. policy revision change during evaluation;
7. subscription identity/revision mismatch;
8. stale dunning-state revision;
9. exactly one transition event under simultaneous duplicate evaluation;
10. unknown commit resolution by exact idempotency key;
11. abort after each individual transactional write leaves no partial state/projection/event;
12. telemetry is absent before commit and emitted only after confirmed commit;
13. dry-run performs no writes, lease acquisition or telemetry side effects;
14. a stale lease holder cannot mutate state after fencing;
15. all cross-tenant negative predicates are rejected;
16. all worker database privileges outside the explicit read/write collection set are denied.

The current evaluator does not satisfy this contract. No worker extraction or production activation is authorized by this document.
