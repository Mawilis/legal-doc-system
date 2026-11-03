# EOS dunning worker transaction redesign — engineering contract

**Source:** `tools/eos/api/billing_router.py`, especially `_dunning_state_for_days`, `evaluate_tenant_dunning_lifecycle` and `evaluate_all_tenant_dunning_lifecycles`.  
**Status:** design contract only; no scheduler extraction or billing behavior change in this commit.  
**Production mutation:** none.

## 1. Verified current behavior and risks

The current evaluator:
1. Reads a tenant's policy from `billing_dunning_policies`.
2. Reads platform invoices whose tenant key is `tenant_id` or legacy `tenantId`.
3. Skips paid/void/cancelled invoices and invoices without valid due date, subscription ID or invoice ID.
4. Computes overdue days using UTC date.
5. Reads `billing_dunning_states` by tenant and subscription.
6. If the proposed state advances, writes the dunning state with `update_one(upsert=True)`.
7. Updates all matching subscription projections with `update_many`.
8. Inserts a `billing_audit_events` row.
9. Emits telemetry.
10. The daily scheduler enumerates tenant IDs using two `distinct` calls and evaluates tenants sequentially.

The three database writes do not share a Mongo session. A process crash or database error can therefore leave state, subscription posture and audit evidence inconsistent. Concurrent API and scheduler evaluation can race. The current state write is not a revision-guarded compare-and-set. The subscription projection update is broad across matching subscription aliases and has no expected-old-state predicate.

**Additional policy defect to resolve explicitly:** `collections_day` is validated and persisted in the policy but `_dunning_state_for_days` never reads it. The current state ordering contains ACTIVE, WARNING, CRITICAL, SUSPENDED_READONLY and TERMINATED; it has no COLLECTIONS state. Do not silently invent a state or discard the configured threshold. Product/legal policy owners must decide whether this is a named state, an event-only milestone, or a deprecated field before worker migration.

The current transition proof hash includes the evaluation timestamp, so it is not by itself a stable idempotency identity across retries.

## 2. Target architecture

Separate three independently deployable responsibilities:

- **Billing API:** authenticated policy read/update and explicitly approved manual evaluation command. No scheduler loop. The API may request an evaluation command but must not bypass the same transactional service.
- **Dunning worker:** scheduled tenant discovery and evaluation. Separate workload identity, queue/lease authority and narrow billing collections only.
- **Index provisioner:** owns all index DDL. Neither API nor worker creates indexes during startup.

Kennel remains the authority for financial execution and settlement. Dunning changes platform service posture only; it must not initiate payment, refund, collection execution or settlement.

## 3. Transactional transition contract

One transition for one tenant/subscription is one Mongo transaction. All participating operations receive the same active session:

1. Read the current policy and its revision.
2. Read the eligible platform invoice facts and derive a deterministic evaluation candidate.
3. Read current dunning state and its revision.
4. Confirm candidate is a permitted monotonic transition under the approved policy revision.
5. Insert or acquire a durable evaluation claim/lease with a unique key scoped to tenant, subscription and evaluation identity.
6. Compare-and-set `billing_dunning_states` using tenant, subscription, expected revision/current state and expected policy revision; increment revision.
7. Update exactly the intended subscription document(s), not an unconstrained tenant-wide match. Require expected prior projection state or revision and verify matched/modified count.
8. Insert exactly one immutable `billing_audit_events` record under a unique transition/idempotency key.
9. Mark the evaluation claim complete in the same transaction.
10. Commit; emit telemetry only after confirmed commit, with a durable outbox if telemetry delivery must be guaranteed.

No external provider call or non-transactional side effect belongs inside the Mongo transaction.

### Stable idempotency

Derive an evaluation identity from stable facts, for example:
- tenant ID;
- subscription ID;
- source invoice ID(s) and their relevant revision/fingerprint;
- policy revision/fingerprint;
- prior dunning state revision;
- target state.

Do not include wall-clock evaluation time in the idempotency key. Store evaluated/occurred time as evidence metadata, not as the sole replay identity.

Enforce a unique audit/idempotency key. Exact replay returns the original committed result. Divergent replay under the same key returns a conflict and requires reconciliation.

### Concurrency and lease semantics

A unique claim key prevents duplicate work for the same candidate. If leases are used:
- claim owner is a random worker execution identity, not tenant input;
- lease expiry and heartbeat are server time;
- acquisition is atomic and revision-guarded;
- a live lease cannot be stolen;
- expired lease takeover increments a fencing token;
- every subsequent state/audit write includes the fencing token;
- completion and lease release occur in the same transaction as the state/projection/audit writes.

The state CAS remains mandatory even with a lease. A lease is not a substitute for database concurrency control.

### Transaction retry and unknown commit

- Retry the entire transaction only for MongoDB transient transaction errors, with bounded attempts and jitter.
- Use the driver's commit retry behavior for `UnknownTransactionCommitResult`; do not rerun business writes blindly.
- If commit remains uncertain, reconcile in a fresh session using the deterministic evaluation/idempotency key and unique audit record.
- Never report success merely because the state document exists; verify the complete state + projection + audit tuple.
- A partial tuple is a consistency incident and must fail closed for further state advancement until reconciled.

## 4. Required collection and index inventory

Existing collections:
- `platform_invoices`: tenant discovery and eligible invoice read.
- `billing_dunning_policies`: tenant policy read; policy update command write.
- `billing_dunning_states`: state read and transactional revision CAS.
- `subscriptions`: exact subscription projection update.
- `billing_audit_events`: append-only immutable transition evidence.

Proposed new collection (not yet implemented):
- `billing_dunning_evaluation_claims`: deterministic candidate claim/lease, fencing token, completion status and replay evidence.

Candidate index requirements (must be source-reviewed and tested before adding to manifest):
- dunning state unique `tenant_id, subscription_id`;
- audit unique `tenant_id, idempotency_key` or equivalent stable transition identity;
- claim unique `tenant_id, subscription_id, evaluation_key`;
- claim lease scan index on status/lease expiry with tenant ordering;
- source invoice query indexes for tenant alias + due date/status/subscription, after legacy alias strategy is resolved;
- exact subscription projection index matching canonical subscription identity and tenant.

Do not create these indexes from this design note. Existing collection duplicates and legacy alias coverage require preflight.

## 5. Required tests before worker extraction

Replica-set integration tests must cover:
1. Happy path commits state, exact subscription projection and one audit record together.
2. Failure after state CAS aborts all writes.
3. Failure after subscription update aborts state and audit.
4. Duplicate worker execution produces one transition/audit.
5. Two workers racing same candidate: one wins CAS; the other returns exact replay or stale conflict.
6. Expired lease takeover increments fencing token; stale worker cannot commit.
7. Policy revision changes during evaluation; stale candidate aborts/recomputes.
8. Subscription projection mismatch or multiple unexpected matches aborts transaction.
9. Unknown commit result is reconciled by stable idempotency key without duplicate audit.
10. Dry-run performs no writes.
11. Paid/void/cancelled invoices do not transition.
12. Legacy tenant aliases cannot cause cross-tenant selection.
13. Collections-day policy behavior matches an approved product/legal decision.
14. Telemetry failure after commit does not roll back or falsely repeat financial/service-state mutation.

## 6. Runtime role boundary

**Dunning worker candidate:** read invoices and policy; claim/evaluate state; update dunning state; update narrowly matched subscription projection; append audit evidence; update claim; emit telemetry via an outbox/approved channel. No index DDL, no broad database admin, no identity/MFA/session mutation, no legal document access, no payment execution, no settlement, no object storage.

**Billing API candidate:** only operations reachable from mounted billing routes and manual dunning command. Policy writes and audit evidence are separate from scheduler authority. Do not assume the worker's broad tenant-discovery read or claim write is required by the API.

**Provisioner:** separate identity owns collection/index DDL only. It is not the API or worker.

## 7. Extraction gate

Do not enable a separate worker until:
- collections and exact index specs are reviewed;
- collections-day policy is resolved;
- transaction service is implemented;
- replica-set failure/race/unknown-commit tests pass;
- scheduler is disabled in API composition;
- worker has its own deployment identity and secret reference;
- non-production target is fingerprint-verified;
- candidate worker role passes positive and negative command tests.

No code path, index, database user, role or production schedule was changed by this design document.
