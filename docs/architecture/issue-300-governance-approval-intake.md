# Issue #300 — Independent governance approval intake

**Status:** INTAKE TEMPLATE ONLY — NO APPROVALS GRANTED OR RECORDED  
**Authority:** This template is not an appointment, legal opinion, key ceremony, trust-root enrollment, or authorization to activate ownership issuance or recovery.  
**Applies to:** Tenant genesis, ownership transfer, governed recovery, issuer trust roots and production composition.

## 1. Submission rules

- Complete one decision record for each authority below. Do not combine issuer, trust-root/key custody, and recovery into one undifferentiated approval.
- The decision-maker's identity and decision-making capacity must be independently verifiable. Attach or reference the institutional instrument/delegation that grants the decision-maker authority for this exact subject.
- Record immutable decision identifiers and fingerprints. Preserve the signed original and verification result in the organization's approved records system; the repository stores references and fingerprints only.
- Use an approved controlled evidence channel. **Never commit private keys, credentials, identity documents, confidential board packs, or unredacted personal information.**
- A GitHub issue comment, code review, deployment setting, repository ownership, test fixture, or statement by an engineer is not a governance approval.
- Approval must be current, scoped, non-self-approved, revocable, and independently verifiable. Missing, ambiguous, expired, disputed, unverifiable, or conflicting evidence means DENY.

## 2. Common decision record

Copy this section for every decision.

| Field | Required value |
|---|---|
| Decision reference | Immutable institutional decision / resolution ID |
| Decision fingerprint | SHA-256 or stronger digest of the signed canonical decision artifact |
| Issuing institution/body | Full legal name and jurisdiction |
| Decision-maker(s) | Verified subject references; do not place identity documents here |
| Capacity and delegation | Office/capacity plus reference/fingerprint of instrument authorizing this decision |
| Decision scope | Exact operation, jurisdiction, entity types, system boundary and limitations |
| Effective from / until | UTC timestamps; no open-ended validity unless expressly justified and approved |
| Review date | Mandatory reassessment date |
| Signature format | Exact signed-artifact format and algorithm |
| Verification method | Independent verification procedure, trust anchor and verifier identity/version |
| Verification evidence | Immutable reference and fingerprint for the verification result |
| Conflicts / recusals | Declared conflicts and recorded recusals |
| Revocation | Authority, notification channel, effective-time semantics and emergency suspension process |
| Records custodian | Approved custodian and retention schedule reference |

## 3. Required separate decisions

### A. Legal scope and evidence sufficiency — UNRESOLVED / DENY

**Accountable authority:** Authorized Legal Counsel / Legal Governance decision-maker.

The decision must specify:
- supported jurisdictions and legal-entity forms;
- legally relevant meaning of ownership, control and authority to represent;
- acceptable independent entity-identity sources and their precedence;
- acceptable ownership/control evidence, mandate instruments and source freshness;
- distinction between beneficial ownership, registered office, directors/members, signing mandate and authority to bind the entity;
- revocation, dispute, mismatch, deceased/incapacitated representative and unavailable-source handling;
- jurisdiction-specific privacy, retention and lawful-processing constraints.

Decision reference/fingerprint: **NOT PROVIDED**  
Authorized approver and delegation evidence: **NOT PROVIDED**  
Status: **UNRESOLVED / DENY**

### B. Independent issuer appointment — UNRESOLVED / DENY

**Accountable authority:** Institutional Governance Authority, advised by Legal Counsel.

The decision must name the issuer institution and exact authorized issuer identity; qualification/accreditation basis; permitted jurisdiction/entity/operation scope; independence and conflicts controls; issuance, verification, currentness and revocation duties; audit obligations; dispute escalation; and separation of duties. The issuer cannot appoint or approve itself as its own trust root.

Decision reference/fingerprint: **NOT PROVIDED**  
Issuer identity / qualification evidence: **NOT PROVIDED**  
Status: **UNRESOLVED / DENY**

### C. Trust-root ownership and key custody — UNRESOLVED / DENY

**Accountable authority:** Security Authority / Key Custodian with independent governance approver(s).

The decision must identify:
- trust-root owner and exact purpose scope (issuer versus recovery);
- independently verified key custodian(s), approver quorum and separation of duties;
- public-key algorithm, key identifier, public-key fingerprint and revision;
- independently witnessed key-generation/ceremony evidence;
- validity window, rotation, supersession and revocation publication;
- compromise response, emergency disable, recovery and audit procedure;
- custody provider/security boundary and evidence that private keys remain outside application storage and source control.

Only public verification material and opaque references/fingerprints may enter the repository. **Private key material must never be submitted here.**

Decision reference/fingerprint: **NOT PROVIDED**  
Public-key fingerprint / ceremony evidence: **NOT PROVIDED**  
Custodian and independent approver evidence: **NOT PROVIDED**  
Status: **UNRESOLVED / DENY**

### D. Evidence contract and privacy/records approval — UNRESOLVED / DENY

**Accountable authority:** Legal Governance plus Privacy / Records Governance and Security review.

The decision must approve the exact typed evidence contract, source hierarchy, cross-binding rules, currentness/revocation checks, data minimization, access controls, retention schedule, legal holds, deletion restrictions, audit history and lawful-processing basis. Raw documents and identity attributes must not be copied into ownership registries.

Decision reference/fingerprint: **NOT PROVIDED**  
Approved schema/version and review evidence: **NOT PROVIDED**  
Status: **UNRESOLVED / DENY**

### E. Independent recovery authority — UNRESOLVED / DENY

**Accountable authority:** Separate Independent Recovery Governance Authority and Legal Counsel.

The decision must appoint a recovery adjudicator institution distinct from the issuer and tenant administration; define dual-control quorum and conflicts/recusals; specify admissible court, estate, incapacity or other instruments as applicable; define notice, objection, contest window, appeal, emergency restrictions and audit; and bind every decision to one exact tenant, legal entity, case, successor and validity window. Recovery must not be a support override or ordinary tenant-admin capability.

Decision reference/fingerprint: **NOT PROVIDED**  
Recovery authority / delegation evidence: **NOT PROVIDED**  
Dual-control and appeal policy reference: **NOT PROVIDED**  
Status: **UNRESOLVED / DENY**

### F. Production composition and operational authorization — UNRESOLVED / DENY

**Accountable authority:** Core Governance and Security Operations.

After A–E are approved and independently verified, authorize the exact production adapter versions, deployment boundary, secret/key references, monitoring, on-call owner, incident response, emergency disable, rollback and tabletop exercise. Production composition must reject missing, stale, mismatched, revoked or unavailable dependencies. No environment variable or feature flag may bypass the verifier.

Decision reference/fingerprint: **NOT PROVIDED**  
Operational owner / runbook / tabletop evidence: **NOT PROVIDED**  
Status: **UNRESOLVED / DENY**

## 4. Engineering acceptance gate

Engineering may implement a production adapter only after the applicable signed decisions and authority proofs above are available through the approved controlled channel and can be verified independently. Acceptance requires:

1. Verify signer identity, institutional capacity and delegation independently of the proposed issuer.
2. Verify signed decision integrity, scope, effective period, quorum, conflicts and revocation status.
3. Verify trust-root public key fingerprint, purpose, revision, validity and revocation from the approved custody source.
4. Bind issuer evidence to exact legal entity, jurisdiction, principal identity, mandate, operation and tenant; reject all cross-scope substitutions.
5. Keep issuer, key custody, and recovery as distinct adapters and authority domains.
6. Keep private keys outside application databases, logs, repository contents and test fixtures.
7. Make missing dependencies, verifier errors, network uncertainty, stale caches, key compromise and ambiguous evidence fail closed.
8. Certify unit, adversarial, type, real replica-set Mongo transaction, replay, revocation, rotation, outage and production-composition behavior on one exact commit.
9. Preserve the existing denial code and prove that no bootstrap, transfer, recovery, IAM, tenant-admin, support or deployment path bypasses the canonical verifier.

**Current production decision:** DENY.  
**Required behavior until every applicable gate is satisfied:** `OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE`.  
**This intake template does not change runtime behavior.**
