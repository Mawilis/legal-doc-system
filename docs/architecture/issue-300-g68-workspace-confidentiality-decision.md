# Issue #300: G68 populated-workspace confidentiality decision

**Status:** Institutional authority unresolved; populated workspace remains deny-only
**Prepared:** 2026-11-02
**Authority:** Decision brief only. This document creates no reviewer role, confidentiality clearance, ethical-wall policy, or content permission.

## Decision required

Before a positive populated Legal Operations workspace response can be enabled, the institution must identify and independently verify who owns confidentiality policy, who may issue and revoke a review decision, who may determine that a wall is not required, what sources prove current membership and enforcement, what approval duration/re-review rules apply, and who owns emergency denial, rollout and rollback.

Engineering has not selected those decision-makers or policies. Until a separately attributable and verifiable decision resolves the relevant G64/D01–D10 authority gaps, G68 remains a final deny gate for populated workspace disclosure. The route must return the bounded `503 LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE` and must not read or return workspace lifecycle content.

## Canonical workspace admission and confidentiality flow

The inspected route is `GET /api/legal-operations/workspace` in `tools/eos/api/legal_operations_router.py`.

1. The four independently composed D15 authorities are instruction-read, allocation-read, attempt-read and return-read. `_workspace_context` requires a common authenticated principal, tenant and published legal-practice role. None is replaced by browser claims or a single broad role.
2. Inside the existing read-only caller-owned snapshot, `resolve_legal_commercial_context` composes canonical D22B5 Legal product availability and one canonical ACTIVE subscription containing the Legal feature. Commercial absence denies with 403; commercial authority corruption/unavailability denies with a distinct non-disclosing 503.
3. Even after all four D15 checks and valid ACTIVE D22B5/subscription evidence, G68 returns its authority-unavailable 503 before `list_entity_read_models` or other workspace lifecycle reads.
4. The transaction wrapper then closes the read-only snapshot. No populated workspace row or content locator is returned on the deny path.

The required conjunction is:

```text
authenticated exact tenant/principal
+ all four D15 read decisions
+ canonical D22B5 Legal product availability
+ canonical ACTIVE Legal subscription
+ independently ratified G68 confidentiality decision and current enforcement
= eligible to evaluate a future disclosure decision
```

It does **not** mean commercial entitlement grants confidentiality permission. A future positive response also requires an independently ratified policy and live point-of-read decision; the conjunction above alone is insufficient.

## Repository-observed evidence

- `tools/eos/api/legal_operations_router.py` v1.18.0 retains the four D15 dependencies, same-snapshot commercial reads, and unconditional G68 denial before lifecycle reads.
- `docs/architecture/wilsy-practitioner-confidentiality-institutional-authority-contract.md` defines the G62/G64 ratification boundary and states that its safety defaults are not institutional approvals.
- `docs/architecture/g64-pre-ratification-authority-map.md` records G77's unconditional `G77_INSTITUTIONAL_AUTHORITY_UNRATIFIED` denial, G63 non-authorizing readiness guard, G72 content-admission guard, and G79 denial-only coordinator. Its D01–D10 decisions remain UNRESOLVED / DENY.
- `tests/unit/test_legal_practice_workspace_confidentiality_boundary.py` proves populated records remain denied before lifecycle reads.
- `tests/integration/test_legal_operations_practice_workspace_http.py` proves all four D15 dependencies remain independent and that product evidence does not bypass the G68 503.
- `tests/integration/test_legal_operations_practice_workspace_real_mongo.py` proves real tenant-scoped snapshot behavior, commercial conjunction/currentness and that populated/foreign/corrupt workspace records stay undisclosed without confidentiality clearance.

These tests prove the current deny boundary, not legal ratification, a positive content release, or production runtime readiness.

## Human governance decisions required

Role names below describe the accountable authority needed; they do not claim that a person currently holds the role. Identity, institutional appointment and decision scope must be independently verified under the institution's existing governance process.

| Decision | Required accountable role | Approval record must establish | Current state |
|---|---|---|---|
| Institutional confidentiality-policy owner and reviewer eligibility/grant authority | Institutional Governance Authority with Legal Governance | Exact institution/tenant/matter scope, issuer role, permission-operation binding, separation of duties and independent authentication | UNRESOLVED / DENY |
| Who may determine `NO_WALL_REQUIRED`, impose/revise a wall, and maintain authoritative policy membership | Legal Governance Authority and designated policy owner | Canonical policy source, membership ownership, revision/history rules, effective scope and conflict-of-interest controls | UNRESOLVED / DENY |
| Review lifecycle, maximum approval duration and mandatory re-review cadence | Legal Governance Authority | Start/expiry boundaries, re-review events, staffing/matter changes, stale-state and appeal handling | UNRESOLVED / DENY |
| Emergency deny, restriction, revocation and incident authority | Security Operations incident owner with Legal Governance | Authorized principals, scope, propagation time, audit source, escalation, monitoring and stale-positive invalidation | UNRESOLVED / DENY |
| Acknowledgement and effective enforcement | Privacy/Security Control Owner plus independent reviewer | Revision-bound acknowledgement provenance and evidence that the restriction is enforced before each content read | UNRESOLVED / DENY |
| Decision precedence, point-of-read revalidation and transaction policy | Legal Governance with Security Architecture | Exact order of IAM, matter binding, assignment, conflict, review, policy/history, revocation, expiry and explicit deny; transaction and race semantics | UNRESOLVED / DENY |
| Rollout, monitoring, independent review and rollback | Core Governance and Security Operations | Staged rollout thresholds, on-call owner, alerts, audit review and tested rollback plan | UNRESOLVED / DENY |

A decision is effective for engineering only when it is attributable, independently authenticated, scoped to the exact contract version and policy, has effective/review/expiry dates, and includes source references/fingerprints plus revocation/supersession semantics. A Git approval, job title, role label, successful HTTP test, commercial entitlement, or fingerprint alone is not that record.

## Engineering work allowed after ratification

After the authority record is approved and independently verified, engineering must separately certify:

- canonical reviewer IAM, issuer and operation/permission binding;
- reviewer/subject/admin separation and conflict-of-interest checks;
- canonical wall membership and policy history, exact tenant/matter binding, revocation and supersession;
- review source authority, explicit `NO_WALL_REQUIRED` authority, expiry and re-review;
- revision-bound acknowledgement and point-of-read enforcement;
- same active caller-owned transaction across every admission source and content read, with deterministic concurrent revocation tests;
- G63/G77/G79 behavior, route composition, content-reader call ordering, audit evidence, telemetry, privacy/records handling and rollback;
- adversarial unit, HTTP and disposable real-Mongo tests, then authenticated browser and production-like runtime evidence.

The current implementation has no positive workspace-content branch. This contract does not authorize adding one. Any positive-path initiative must first reopen the full caller/dependency/blast-radius map and preserve D15 IAM and D22B5 commercial checks as independent conjuncts.

## Relationship and blast-radius map

| Dimension | Current relationship |
|---|---|
| Direct imports / exports | This Markdown decision is not imported at runtime. The route consumes `resolve_legal_commercial_context`, `_workspace_context`, D15 dependencies and read-model services. |
| Routes / HTTP surface | `GET /api/legal-operations/workspace`; current G68 result is one non-disclosing 503. |
| Models / collections | D22B5 product history/current and canonical subscription collections are read in the snapshot; workspace lifecycle repositories are not reached after the G68 denial. |
| Metrics / telemetry | No G68 positive-disclosure metric or route telemetry change is authorized here. Any future metric must distinguish denied/unavailable without tenant or matter PII. |
| Shared crypto | Decision/policy fingerprints can prove exact content integrity; they do not prove ratifier identity or institutional authority. No key or root is selected in this record. |
| Config / environment | No deployment flag or environment variable may disable the G68 denial. D15 and D22B5 remain server-owned canonical sources. |
| UI / hooks | Client surfaces may render the bounded denial only; no browser/client route may synthesize clearance or show hidden workspace rows. |
| Latency / transaction chain | Current order: D15 admission → read-only snapshot → D22B5/subscription conjunction → G68 denial → close transaction → bounded response. A future path must decide and enforce confidentiality before lifecycle content reads. |
| Blast radius | This document changes no runtime. A positive path would affect the workspace router, canonical IAM/policy/clearance sources, lifecycle history, registries/indexes, startup wiring, audit/metrics, client surfaces, browser tests and operational rollout. |

## Post-decision action table

| | Action | File / surface | Why (blast radius) | Priority | Done? |
|---|---|---|---|---|---|
| 1 | Independently identify and authenticate the institutional ratifier and policy owner | G64/G62 decision record | No engineering artifact can assign institutional disclosure authority | P0 | [ ] |
| 2 | Ratify every applicable D01–D10 decision with exact scope and currentness rules | `docs/architecture/g64-institutional-ratification-decision-record-template.md` and signed decision locator | Existing G63/G77/G79 deny because authority and ownership decisions remain unresolved | P0 | [ ] |
| 3 | Verify canonical IAM issuer, policy membership/enforcement and independent acknowledgement source | EOS IAM, G77 source adapters and content-read boundary | A policy record alone cannot prove a current actor may disclose specific matter content | P0 | [ ] |
| 4 | Implement only the ratified positive path with current-source reads, explicit deny precedence and point-of-read enforcement | `tools/eos/api/legal_operations_router.py` and governed G77/G79 services | Prevents early disclosure, stale clearance, cross-matter access and transaction races | P0 | [ ] |
| 5 | Certify server, real-Mongo, browser and production-like runtime evidence; preserve rollback and monitoring | G68-specific workflow and operational runbook | Unit tests alone cannot establish deployed disclosure control or revocation behavior | P0 | [ ] |

## Certification seal

**Artifact:** `issue-300-g68-workspace-confidentiality-decision.md`
**Version:** `v1.0.0-ISSUE-300-G68-CONFIDENTIALITY-DECISION`
**Authority boundary:** Decision proposal only; no G68 permission granted
**Tenant posture:** Exact tenant/matter confidentiality remains deny-only pending ratification
**Fail-closed posture:** Commercial evidence alone never discloses confidential workspace content
**Financial execution authority:** Kennel EOS exclusively
**End of Wilsy OS sovereign artifact**
