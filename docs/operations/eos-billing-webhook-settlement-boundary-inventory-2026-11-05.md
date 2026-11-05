# EOS billing and payment-settlement boundary inventory

**Date:** 2026-11-05  
**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Scope:** Platform invoice settlement, PayShap provider events, canonical subscription correlation, transaction and replay controls.

## Certified baseline

The billing/webhook workflow now runs on roadmap-branch pushes and pull requests. Its current certification set includes:

- Billing registry and commercial receivable policy unit tests.
- PayShap execution-webhook contract and host-runtime unit tests.
- Authenticated settlement-observation ingestion and settlement-evidence bridge unit tests.
- Commercial invoice-settlement orchestration unit tests.
- Real-replica-set billing, subscription registry, financial-truth firewall, financial-execution reconciliation, PayShap evidence, PayShap host reconciliation, and commercial settlement projection tests.
- HTTP-level PayShap execution webhook test: bad HMAC signature is rejected; valid event is accepted; exact replay is idempotent and does not duplicate execution evidence/truth.

Latest completed baseline before the expanded unit gate: commit `deb09946229b816a6cec358603d1ec9957d593f8`, workflow run [41986006382](https://github.com/Mawilis/legal-doc-system/actions/runs/41986006382), with 28/28 unit tests and 97/97 replica-set integration tests passing. The expanded unit gate is running on commit `1d0f92a3e8d6b6eb62637ceffec1025714e5b541`; do not treat it as passed until its run is complete.

## Verified authority path

1. The mounted PayShap endpoint is `POST /providers/payshap/webhook`.
2. Its signed payload is persisted as tenant-scoped provider evidence. The host resolves exactly one PayShap execution attempt for the signed tenant and command.
3. An `EXECUTED` event is correlated into canonical execution observation/fact/truth through Kennel EOS. The caller-owned Mongo transaction encloses the provider evidence, observation, attempt CAS, execution fact, and truth.
4. The endpoint does not invoke settlement ingestion or invoice-paid projection. Provider execution is not settlement.
5. A separate internal settlement pipeline already exists: authenticated settlement observation -> platform settlement evidence -> commercial settlement projection. It requires an active caller transaction, correlates settlement evidence to durable executed truth, and the commercial projection validates tenant, invoice, release authorization, currency, amount, and invoice evidence fingerprint before a compare-and-set marks the platform invoice paid.
6. Subscription lifecycle authority remains in `SubscriptionRegistry`; settlement evidence must not directly suspend, terminate, resume, or otherwise mutate a subscription.

## Gaps to close before production billing enforcement

### 1. Settlement transport ingress is not yet certified

The mounted PayShap webhook is execution-only. `PayShapStatus` deliberately has no `SETTLED` or `PAID` status; unknown or `PAID` values remain non-settlement evidence. The authenticated settlement-observation and evidence-bridge modules are internal orchestration contracts, not a separately certified provider settlement HTTP ingress.

Do not silently reinterpret an execution webhook as settlement. Implement a separate authenticated settlement-ingress adapter only after its provider payload/signature contract is confirmed. It must correlate to one existing executed truth and reject ambiguous or partial platform settlement.

### 2. Subscription-linked invoice correlation is missing in the commercial projection

The commercial settlement projection preserves `subscription_id` in its invoice compare-and-set predicate, preventing concurrent mutation of that field. It does not currently load the corresponding canonical `subscriptions` record through `SubscriptionRegistry`. Existing commercial settlement projection fixtures do not seed or assert a linked subscription.

Before marking a subscription-linked platform invoice paid, the projection must verify that the invoice's tenant/subscription identity resolves to one valid canonical subscription record using the same caller-owned session. Missing, corrupt, or cross-tenant subscription linkage must fail closed. This is a read/consistency check, not subscription lifecycle mutation.

### 3. Audit and recovery evidence

The execution webhook tests prove transaction rollback for host evidence, observation, attempt CAS, and execution truth. Settlement tests prove caller-session-bound evidence and invoice projection. The next integration certificate must prove one transaction encloses settlement observation, platform settlement evidence, invoice paid CAS, commercial projection, and audit/outbox evidence, including abort and retry after an interrupted attempt.

### 4. Lifecycle governance

Dunning stages such as suspension review and termination review remain review signals only. Any actual suspension or termination must be a separately authorized `SubscriptionRegistry` lifecycle command with independent approval and audit evidence. No webhook worker may become lifecycle authority.

## Eight-day execution sequence

1. Close canonical subscription-to-invoice correlation in the settlement projection and certify missing, corrupt, and cross-tenant subscription references.
2. Define and validate the provider settlement event contract; implement a separate signed settlement ingress without broadening the execution webhook.
3. Compose settlement ingress, execution-truth correlation, settlement evidence, invoice CAS, projection, and audit/outbox under one caller-owned transaction.
4. Certify exact replay, divergent replay, signature rejection, duplicate delivery, partial settlement, wrong amount/currency/destination, wrong tenant, missing execution truth, concurrent writers, transaction abort, and retry recovery on a real replica set.
5. Verify the authorized `SubscriptionRegistry` lifecycle path independently; do not automate suspension or termination from webhook/dunning state.
6. Run the full latest-commit CI gate and review the complete billing/webhook authority graph before any release decision.

## Release boundary

This inventory is engineering certification, not production activation. No production provider credentials, payment enforcement, subscription suspension/termination, PR merge, or deployment is authorized by these tests.
