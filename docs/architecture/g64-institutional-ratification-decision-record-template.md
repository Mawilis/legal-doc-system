# G64 Institutional Ratification Decision Record — Template Only

**Status: TEMPLATE — NOT A DECISION, NOT RATIFICATION, NOT AUTHORIZATION**

This document is an evidence-capture instrument for the institutionally authorized decision-maker. It intentionally contains no preselected decisions, ratifier identity, effective dates, IAM grants, or operational permissions. Completing a form or merging this template does not itself establish the authority of its signer.

Canonical contract: `docs/architecture/wilsy-practitioner-confidentiality-institutional-authority-contract.md`  
Readiness guard: `tools/eos/legal_operations/domain/legal_work_confidentiality_policy_readiness.py`  
Tracking issue: https://github.com/Mawilis/legal-doc-system/issues/250

## 1. Decision authority and provenance

- **Institution / legal entity in scope:** [REQUIRED — exact registered/approved identifier]
- **Ratifier full identity:** [REQUIRED — independently verifiable identity]
- **Authority source:** [REQUIRED — authoritative governance instrument / delegation reference and immutable locator or fingerprint]
- **Evidence verifier:** [REQUIRED — independent verifier identity and authority]
- **Decision timestamp (UTC):** [REQUIRED]
- **Effective-from timestamp (UTC):** [REQUIRED]
- **Expiry / mandatory review timestamp (UTC):** [REQUIRED]
- **Contract version and SHA3-512 fingerprint:** [REQUIRED]
- **Decision-record identifier and immutable source locator:** [REQUIRED]
- **Supporting evidence references/fingerprints:** [REQUIRED]
- **Revocation / supersession process and accountable owner:** [REQUIRED]
- **Independent witness or second approver, where required:** [REQUIRED or documented basis for not applicable]

Do not infer authority from repository ownership, GitHub permissions, a job title, a commit, a test result, or a self-asserted boolean. If the ratifier's authority cannot be independently verified, every decision remains unresolved and deny-only.

## 2. Decision semantics

For each decision below, select exactly one disposition in the signed institutional record: `APPROVE`, `REJECT`, or `DEFER`. A blank, ambiguous, contradictory, expired, unverifiable, or out-of-scope entry is unresolved and defaults to `DENY`. `APPROVE` records a policy decision only; it does not by itself prove that the runtime implements or enforces the decision.

Every decision must specify:
- exact disposition and rationale;
- exact institutional, tenant, matter, principal/role and operation scope as applicable;
- responsible source/system and source owner;
- evidence references with integrity fingerprints;
- effective/expiry/review times and revocation/supersession rule;
- decision-maker and required independent approver attestations;
- implementation acceptance criteria and independent verification owner.

## 3. D01–D10 register

### D01 — Reviewer eligibility and granting authorization role
- Disposition: [REQUIRED]
- Eligible reviewer principals/roles and exclusions: [REQUIRED]
- Authoritative IAM issuer, permission, and exact operation binding: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D02 — Reviewer/target and reviewer/administrator separation of duties
- Disposition: [REQUIRED]
- Prohibited identity combinations and how they are checked: [REQUIRED]
- Independent enforcement source and evidence: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D03 — Independent authority for NO_WALL_REQUIRED
- Disposition: [REQUIRED]
- Authorized decision role and independent policy basis: [REQUIRED]
- Prohibition on self-review and requester-selected disposition: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D04 — Authoritative wall policy and membership source
- Disposition: [REQUIRED]
- Canonical policy, membership, and versioned source identifiers: [REQUIRED]
- Source ownership, integrity, consistency and failure behavior: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D05 — Acknowledgement provenance and effective enforcement
- Disposition: [REQUIRED]
- Required acknowledgement actors, exact policy revision, timestamps and proof: [REQUIRED]
- Runtime enforcement owner and independently testable evidence: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D06 — Emergency denial, revocation and incident authority
- Disposition: [REQUIRED]
- Authorized emergency actors and narrow permitted operations: [REQUIRED]
- Immediate deny/revoke mechanism, audit trail and incident owner: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D07 — Maximum approval duration and re-review cadence
- Disposition: [REQUIRED]
- Maximum validity duration and review schedule: [REQUIRED]
- Expiry behavior, renewal authority and stale-state handling: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D08 — Explicit-deny precedence
- Disposition: [REQUIRED]
- Ordering across conflict, review, wall, membership, expiry, revocation and contradictory sources: [REQUIRED]
- Proof that stale positive history cannot override a current deny: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D09 — Point-of-read revalidation and transaction boundaries
- Disposition: [REQUIRED]
- Required revalidation immediately before content read: [REQUIRED]
- Canonical caller-owned transaction/session and exact scope binding: [REQUIRED]
- Failure, timeout, source-unavailable and concurrent-revocation behavior: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

### D10 — Independent policy approval, rollout and rollback ownership
- Disposition: [REQUIRED]
- Independent policy approver and evidence of authority: [REQUIRED]
- Named accountable rollout and rollback owners: [REQUIRED]
- Release gates, monitoring, rollback trigger and tested rollback procedure: [REQUIRED]
- Evidence / scope / dates / revocation: [REQUIRED]

## 4. Required independent verification

The verifier must record each result as `VERIFIED`, `FAILED`, or `UNRESOLVED`, with evidence references. No self-verification by the decision-maker where separation of duties applies.

| Gate | Result | Evidence reference / fingerprint | Verifier and timestamp |
|---|---|---|---|
| Ratifier identity and authority | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Scope and contract-version match | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Integrity, provenance and immutable record | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Effective time, expiry, revocation and supersession | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| D01–D10 completeness and consistency | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Canonical IAM and operation mapping | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Wall/membership/acknowledgement runtime enforcement | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Deny precedence, tenant/matter isolation, point-of-read revalidation | [REQUIRED] | [REQUIRED] | [REQUIRED] |
| Focused adversarial tests and production certification | [REQUIRED] | [REQUIRED] | [REQUIRED] |

## 5. Release guard — mandatory

Until institutional authority is independently verified and the implementation gates above pass:

- G63 remains `INSTITUTIONAL_APPROVAL_MISSING`.
- All unresolved decisions remain `DENY`.
- No reviewer authorization, positive practitioner content disclosure, or ethical-wall enforcement claim may be enabled.
- No HTTP route or production access path may be activated.
- A signed record is evidence to verify, not a substitute for canonical IAM, runtime enforcement, or tests.

## 6. Signatures / attestations

- **Ratifier signature / verifiable signing reference:** [REQUIRED]
- **Ratifier signed timestamp (UTC):** [REQUIRED]
- **Independent verifier signature / verifiable signing reference:** [REQUIRED]
- **Verifier timestamp (UTC):** [REQUIRED]
- **Institutional immutable record locator:** [REQUIRED]
- **Revocation/supersession contact or system of record:** [REQUIRED]

**This template must not be represented as completed, approved, ratified, or production-authorizing until an actual attributable institutional decision record has been supplied and independently verified.**