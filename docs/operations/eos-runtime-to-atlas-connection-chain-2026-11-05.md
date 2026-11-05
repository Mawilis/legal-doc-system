# EOS runtime-to-Atlas connection chain — 2026-11-05

**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Release boundary:** development and CI only; no production credential rotation, network-policy change, merge or deployment.

## Canonical runtime owner

`tools/eos/kernel/db.py` is the sole application-runtime Mongo connection authority:

- `connect_db()` reads the configured `MONGODB_URI`, selects the database encoded by the URI, and constructs the process-owned `MongoClient`.
- `get_client()` and `get_database()` expose that same connected client/database pair.
- `disconnect_db()` closes the process-owned client; application modules do not create their own Mongo clients or select a second database.
- Production has no localhost fallback. Non-production dotenv loading is separate from production configuration.

The API server starts and stops that kernel-owned connection. Runtime readiness remains fail-closed when the URI, database or required indexes are unavailable.

## Billing consumers corrected or guarded

1. **PlanRegistry** now resolves `plans` lazily through `get_database()`. It no longer constructs an independent client, reads a second URI, or falls back to localhost.
2. **SubscriptionRegistry** now resolves `subscriptions` lazily through `get_database()` under the same rules. Subscription lifecycle authority remains in this registry.
3. **OrderNumberService** no longer selects a hard-coded `wilsy` database from an arbitrary client. Construction requires the exact kernel database and matching kernel client. Its singleton refuses to survive a kernel database/client rebind.
4. **FinancialApprovalAggregator** rejects a caller-supplied client/database pair unless both point to the same Mongo client.
5. **Platform financial execution-request issuance** rejects a supplied client that does not own the supplied database.
6. **Platform release-authorization issuance** already resolves the kernel client/database pair and enforces the same-client invariant.
7. The billing router's compatibility `db`/`client` aliases remain unset in production; runtime consumers resolve the kernel database/client.

New unit certificates cover the Plan/Subscription collection proxies, order-number database binding, and mixed-client rejection in financial approval aggregation. The billing workflow runs these tests.

## Deliberate boundary requiring separate review

The legal evidence provider has a separately injected, server-owned audit evidence registry/client contract. It is not silently folded into the billing application's kernel database: its independent audit transaction is a separate evidence boundary and must be reviewed against the approved audit-storage topology, credential owner and deployment contract before any connection consolidation. No new audit client or credential is created by this change.

## Remaining runtime-to-Atlas certification

- Verify the exact production Atlas cluster/database target from the deployed EOS runtime configuration; do not infer it from local environment names.
- Verify the production runtime identity has only the required database/collection privileges and no `atlasAdmin`.
- Verify test and production identities are distinct, with restricted Atlas network access and rotation ownership.
- Prove the API server, kernel registries, billing routes, order numbering and financial workflows all resolve the same intended runtime client/database in a production-like environment.
- Record the exact Atlas cluster, database name, user role, network allowlist and secret owner in the deployment contract before any credential change.

## Explicitly unchanged

No production database credential, Atlas user, network allowlist, deployment, billing enforcement, subscription lifecycle action, PR merge or provider activation was changed.
