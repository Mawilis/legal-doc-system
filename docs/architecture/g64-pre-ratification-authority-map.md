# G64 Pre-Ratification Authority Map and Adversarial Readiness Matrix

**Status: ENGINEERING MAP ONLY — NOT RATIFICATION, NOT AUTHORIZATION, NOT A CERTIFICATION OF LIVE WALL ENFORCEMENT**
**Scope:** G63 readiness, G77 canonical-source denial boundary, G79 disclosure coordinator, canonical IAM/eligibility, and current tests.
**Tracking:** [Issue #250](https://github.com/Mawilis/legal-doc-system/issues/250)
**Contract:** `docs/architecture/wilsy-practitioner-confidentiality-institutional-authority-contract.md`

This map records repository-observed controls and gaps. It does not assign institutional decision rights, select a future policy, or turn documentary evidence into permission. Source references must be rechecked against the exact commit under certification.

## 1. Authority chain as implemented

`Authenticated TenantAuthorizationContext` → exact tenant/principal and active caller-owned transaction → G77 current IAM / matter binding / work assignment / conflict disposition / confidentiality review / current wall policy and history checks → unconditional `G77_INSTITUTIONAL_AUTHORITY_UNRATIFIED` denial → G63 non-authorizing readiness backstop → G72 content-admission guard → G79 coordinator → content reader (currently unreachable through the canonical path).

| Layer | Repository evidence | Implemented and tested | Limit / certification status |
|---|---|---|---|
| Canonical tenant IAM | `tools/eos/auth/tenant_authorization.py`; `tools/eos/auth/tenant_authority_policy.py` | G77 requires a canonical `TenantAuthorizationDecision` with authorized state; eligibility policy distinguishes business-role eligibility from permission possession | Eligibility is not reviewer authorization; institutional reviewer permission and issuer ownership are not ratified |
| Matter binding and assignment | G77 source resolver contracts and `tests/unit/test_legal_work_ethical_wall_enforcement.py` | Exact tenant/matter/principal binding, active binding and matching assignment are checked | Binding/assignment are relationship/work evidence, not content permission |
| Conflict and review | G77 current conflict and confidentiality-review source checks | Canonical types, scope, conflict fingerprint relationship and review/policy fingerprint relationship are validated | A favorable conflict or review record cannot independently grant access; independent reviewer authority remains unassigned |
| Wall policy/history | `tools/eos/legal_operations/domain/legal_work_ethical_wall_policy.py`; G77 current/history reads | Current pointer must equal final history entry; tenant/matter/policy scope and revocation are checked; restricted state denies | Policy records and fingerprints are documentary evidence; no independently certified live enforcement/membership/acknowledgement source |
| G63 readiness | `tools/eos/legal_operations/domain/legal_work_confidentiality_policy_readiness.py`; `tests/unit/test_legal_work_confidentiality_policy_readiness.py` | All D01–D10 remain unresolved; no caller override; immutable projection; access/reviewer/wall-claim permissions are always false | It is a fixed readiness guard, not a ratification parser or an operational authorization engine |
| G79 disclosure seam | `tools/eos/legal_operations/service/legal_practitioner_disclosure_coordinator.py`; `tests/unit/test_legal_practitioner_disclosure_coordinator.py` | Authenticated context, tenant consistency and transaction are checked; G77 denial and G63/G72 backstops stop before content reader | Coordinator is denial-only; no HTTP route is enabled; no content release is certified |
| Institutional decision record | G62 contract and G64 template | Template requires issuer authority, independent verification, scope, dates, fingerprints, revocation and D01–D10 dispositions | No attributable, independently verified institutional record is present in repository evidence; template is not a decision |

## 2. D01–D10 decision-to-source map

All ten decisions remain **UNRESOLVED / DENY**. “Existing evidence” below is evidence that code or a test exists, not evidence of institutional approval.

| Decision | Existing source/control | Existing test evidence | Concrete unresolved gap / exit evidence |
|---|---|---|---|
| D01 Reviewer eligibility and grant authority | Canonical IAM decision and tenant business-role eligibility policy; G77 consumes current IAM | G77 rejects boolean/noncanonical IAM and denied IAM; G63 denies reviewer authorization | Institution must name the authorized reviewer role/issuer and exact permission-operation binding. Verify active permission possession, revocation and matter scope independently |
| D02 Reviewer/target and reviewer/admin separation | Review record has reviewer identity; wall revision has administrator identity | Scope and review validity checks exist; no source evidence found that fully certifies all prohibited identity combinations | Ratify prohibited identity combinations and source of enforcement; test reviewer=target, reviewer=administrator, shared delegation, and conflicting principals |
| D03 Independent `NO_WALL_REQUIRED` authority | Review domain records wall requirement; G77 requires canonical review and wall evidence | Review/policy mismatch denies; G63 remains non-authorizing | No independently authorized decision source is certified. Test requester-selected/no-wall booleans and unverified reviewer assertions remain denied |
| D04 Authoritative policy and membership | G77 reads current wall policy and full policy history inside caller-owned transaction | Current-pointer/history mismatch and foreign policy scope are rejected | A policy model is not a live membership/enforcement system. Identify and independently certify canonical membership source, ownership, revision semantics and availability behavior |
| D05 Acknowledgement and effective enforcement | Review carries wall-satisfaction evidence references; policy has documentary ratification fingerprints | Recorded approval still ends in unconditional institutional-authority denial | A fingerprint is not acknowledgement provenance or proof the control blocks reads. Require revision-bound acknowledgements and independent runtime enforcement tests |
| D06 Emergency denial/revocation | G77 rejects revoked policy/ratification and explicit restrictions | Revocation and restriction checks exist in G77; breadth of emergency authority is not established | Ratify who may invoke emergency deny/revoke, scope, audit source, propagation bound and incident owner; test stale positive history after revocation |
| D07 Maximum approval duration/re-review | Review has `expires_at`; policy has effective time bounds; G77 evaluates at a supplied aware UTC time | Current review and policy time checks exist | Institution must set maximum lifetime/re-review cadence. Test exact expiry boundary, stale evaluation time, expired review and expired policy |
| D08 Explicit-deny precedence | G77 validates IAM, binding, assignment, conflict, review, policy history and explicit restriction in sequence | Denied IAM stops later reads; explicit restriction and unratified approval deny | Need a documented, ratified ordering across all canonical sources and adversarial combination tests proving stale positives never override any current deny |
| D09 Point-of-read revalidation / transaction | G77 requires active caller-owned transaction; G79 runs checks before reader | Inactive transaction and source denial stop before content read | No operational read path is enabled, so end-to-end concurrent-revocation behavior is not certified. Test same transaction/scope and simulated revocation between admission and read before any future enablement |
| D10 Independent policy approval, rollout and rollback | Contract/template require independent approver, rollout/rollback owners and gates | G63 and G77 keep access/wall claims disabled; PR checks are software gates only | No attributable institutional approval or accountable owner record exists. Require independently verified ratification plus staged rollout, monitoring and tested rollback evidence |

## 3. Denial-path certification inventory

### Observed coverage in the current G77 certificate
- Inactive or missing caller-owned transaction.
- Noncanonical/boolean IAM and denied IAM short-circuiting later source reads.
- Revoked binding and missing assignment.
- Noncanonical conflict evidence and review matter-scope mismatch.
- Explicit restriction and review/current-policy fingerprint mismatch.
- Favorable documentary records still produce `G77_INSTITUTIONAL_AUTHORITY_UNRATIFIED`.
- No G77 positive access/content-delivery API; both exported safety constants remain false.

### Observed coverage in the current G63 certificate
- All ten decision identifiers remain unresolved and stable.
- Operational access, reviewer authorization and wall-enforcement claim are false.
- Caller override keywords are rejected; readiness result is immutable and deterministic.

### Observed coverage in the current G79 certificate
- Missing authenticated context, inactive transaction and authenticated tenant mismatch deny before the content reader.
- G77 denial, G63 backstop and G72 admission denial each prevent reader invocation.
- Caller-supplied approval flags do not release content.

### Adversarial cases that must be individually certified before any future enablement
1. Expired review and expired wall policy, including exact expiry instant and stale evaluation time.
2. Revoked policy/ratification and emergency revocation with a stale positive review/history record.
3. Contradictory policy history, stale current pointer, and positive history followed by current deny.
4. Cross-tenant and cross-matter IAM, binding, assignment, conflict, review, wall current record, and history.
5. Reviewer equals practitioner/target; reviewer equals wall administrator; self-approved `NO_WALL_REQUIRED`.
6. Source timeout/unavailability and malformed or inconsistent records at each source boundary.
7. Point-of-read revalidation and simulated concurrent revocation; exact transaction/session identity and unchanged tenant/matter/content scope.
8. In every coordinator denial, assert content reader call count remains zero and no content bytes are returned.

This list is a gap register, not a claim those tests have already passed. Existing passing tests must not be weakened. Any new test is only certified after execution against the exact branch head.

## 4. Bounded competitor scan (reference patterns, not authority)

The current official iManage Security Policy Manager material describes policy-based allow/deny, automatic policy updates on staffing changes, recorded acknowledgements, and scheduled reviews ([iManage Security Policy Manager](https://imanage.com/imanage-products/security-governance/security-policy-manager/); [iManage policy guidance](https://docs.imanage.com/cloud/irm-dcrm-help/en-US/Best_Practices_-_Ethical_Walls_and_Security_Policies.html)). NetDocuments describes user/document/workspace-level restrictions and reporting ([NetDocuments Ethical Walls](https://www.netdocuments.com/solutions/ethical-walls/)). These public descriptions support treating effective enforcement, change propagation, acknowledgement evidence and auditability as separate concerns. They do not prove WILSY has equivalent controls, and no vendor policy is imported as WILSY institutional policy.

## 5. Exit gates and evidence ledger

Before a positive authorization path may even be considered:
- [ ] Attributable institutional decision record supplied with immutable locator and exact contract version/fingerprint.
- [ ] Ratifier identity and delegated authority independently verified by a separate verifier.
- [ ] Each D01–D10 disposition complete, scoped, internally consistent, effective, unexpired and revocable.
- [ ] Canonical IAM issuer/permission/operation and current membership/enforcement sources identified and independently verified.
- [ ] D02 separation-of-duties controls and D03 independent `NO_WALL_REQUIRED` decision source certified.
- [ ] Adversarial tests above implemented and run on exact branch head; failures fixed without weakening assertions.
- [ ] G63/G77/G79 positive path reviewed as a separate governed delivery only after the authority/source prerequisites are met.
- [ ] Independent certification records transaction/scope isolation, explicit-deny precedence, point-of-read revalidation, and actual content-layer enforcement.
- [ ] Production route remains disabled until every gate passes and rollout/rollback owners are attributable.

**Release boundary:** G63 stays `INSTITUTIONAL_APPROVAL_MISSING`; G77 stays denial-only; G79 stays unmounted; no positive content disclosure or ethical-wall enforcement claim is permitted by this map.

**END OF G64 PRE-RATIFICATION AUTHORITY MAP**
