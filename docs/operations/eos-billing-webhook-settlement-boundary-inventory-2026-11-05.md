# EOS billing and payment-settlement boundary inventory

**Date:** 2026-11-05  
**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Scope:** Platform invoice settlement, PayShap provider events, canonical subscription correlation, transaction and replay controls.  
**Status:** Atomic settlement composition and real-replica-set coverage are implemented; latest-head certification is pending. Provider settlement transport remains intentionally unimplemented pending a verified provider contract.

## 1. Verified authority path

1. The mounted PayShap endpoint is `POST /providers/payshap/webhook`.
2. Its signed payload is persisted as tenant-scoped provider evidence. The host resolves exactly one PayShap execution attempt for the signed tenant and command.
3. An `EXECUTED` event is correlated into canonical execution observation/fact/truth through Kennel EOS. The caller-owned Mongo transaction encloses provider evidence, observation, attempt CAS, execution fact and truth.
4. The execution webhook does not invoke settlement ingestion or invoice-paid projection. Provider execution is not settlement.
5. The separate atomic settlement composer performs authenticated settlement observation, durable platform settlement evidence, canonical commercial projection, immutable audit evidence and pending outbox intent under one caller-owned MongoDB transaction.
6. The commercial projection validates tenant, invoice, release authorization, currency, amount, execution truth and invoice evidence fingerprint before compare-and-set marking the invoice paid.
7. For a subscription-linked invoice, the projection reads the canonical `SubscriptionRegistry` record using the same caller-owned session. Missing, invalid, corrupt or cross-tenant subscription linkage fails closed. This is a consistency read only; it does not mutate subscription lifecycle.
8. Subscription lifecycle authority remains exclusively in `SubscriptionRegistry`. Settlement and dunning evidence cannot suspend, terminate or resume a subscription.

## 2. Atomic settlement composition and existing evidence

`tools/eos/saas/billing/atomic_platform_settlement.py` composes:

- authenticated transport evidence and durable execution-truth correlation;
- settlement observation persistence;
- bridge to full platform settlement evidence (partial platform settlement is rejected);
- subscription-aware commercial invoice projection and invoice paid CAS;
- immutable `PLATFORM_INVOICE_SETTLED` audit evidence;
- a separately mutable `PENDING` outbox delivery intent.

The caller owns the transaction. No nested transaction is started. Every persistence operation receives the same session. Audit and outbox identity is tenant-scoped and deterministic. Exact replay is accepted; divergent evidence fails closed. Outbox delivery-state changes do not rewrite immutable audit evidence.

The real-replica-set suite `tests/integration/test_platform_billing_commercial_settlement_projection_real_mongo.py` already contains:

- RM01: canonical full settlement;
- RM01b/RM01c/RM01d: linked subscription preservation, cross-tenant subscription-link denial and missing canonical subscription denial;
- RM07: one-transaction commit across observation, platform evidence, invoice projection, audit and outbox;
- RM08: forced transaction abort rolls back every stage, followed by successful whole-operation retry;
- RM09: duplicate delivery preserves one durable settlement and the existing outbox delivery state;
- RM10: divergent settlement replay is rejected without duplicating evidence;
- RM11: concurrent identical delivery with bounded whole-transaction retry converges to one observation, evidence, invoice projection, audit event and outbox intent.

RM11 is newly added and requires the current exact-head real-replica-set run before it is considered certified. Earlier workflow evidence does not certify the new test.

## 3. Remaining gaps before production billing enforcement

### 3.1 Provider settlement transport ingress

The mounted PayShap webhook remains execution-only. `PayShapStatus` deliberately has no `SETTLED` or `PAID` status; unknown or `PAID` values remain non-settlement evidence.

The authenticated settlement-observation and evidence-bridge modules are internal orchestration contracts, not a certified provider settlement HTTP ingress. A separate signed settlement adapter must not be invented until the provider's actual settlement payload, signature verification, event identity, retry and reconciliation contract is confirmed. It must correlate to one existing executed truth and reject ambiguous, partial, wrong-destination, wrong-amount, wrong-currency and cross-tenant evidence.

### 3.2 Unknown commit and transient conflict certification

The suite proves explicit transaction abort and subsequent recovery, exact duplicate replay, divergent replay and now concurrent duplicate convergence with bounded caller retries. It does not yet inject a real MongoDB `UnknownTransactionCommitResult` during commit acknowledgement. Add a controlled replica-set failpoint test where supported, or a transaction-runner contract test proving that the caller retries the entire deterministic operation after an unknown commit result and reads back the committed event graph before reporting completion.

### 3.3 Outbox delivery ownership

Outbox claim, lease fencing, retry and acknowledgement primitives have their own real-replica-set tests. They do not authorize activating a dispatcher. Delivery remains disabled until an operational owner, delivery policy, secrets, retry/dead-letter policy, alerting and incident handling are explicitly approved.

### 3.4 Lifecycle governance

Dunning stages such as suspension review and termination review remain review signals only. Any actual suspension or termination must be a separately authorized `SubscriptionRegistry` lifecycle command with independent approval and audit evidence. No webhook or outbox worker may become lifecycle authority.

## 4. Next execution sequence

1. Run and review the latest-head billing/webhook certification, including RM01b/c/d and RM07–RM11 against the real replica set.
2. Add controlled unknown-commit acknowledgement recovery evidence without weakening caller-owned transaction boundaries.
3. Obtain and verify the provider's signed settlement-event contract; only then implement a separate settlement ingress.
4. Extend authenticated route-level certification for settlement ingress once its provider contract exists.
5. Keep outbox dispatch disabled until its operational owners and delivery policy are established.
6. Verify the authorized `SubscriptionRegistry` lifecycle path independently; do not automate suspension or termination from webhook/dunning state.
7. Run the full latest-commit CI gate and review the complete billing/webhook authority graph before any release decision.

## 5. Release boundary

This is engineering certification, not production activation. No production provider credentials, payment enforcement, subscription suspension/termination, PR merge or deployment is authorized. Electrum onboarding and sandbox completion remain separately gated on provider feedback.
