# Sheriff Office Appointment Authority — Connection Matrix

VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-AUTHORITY-CONNECTION-MATRIX
AUTHORITY: WILSY OS Legal Operations engineering record
CERTIFICATION DATE: 2026-11-02
REPOSITORY: `Mawilis/legal-doc-system`
BRANCH: `feat/sheriff-office-scoped-operations-20261102`

## 1. Change boundary

This feature prevents a tenant-level `tenant_sheriff` business role or `SHERIFF`
authorization assignment from being treated as statutory appointment or
universal access to every Sheriff office in a tenant.

A location-evidence read is permitted only when the authenticated Sheriff
principal has a current, independently verified appointment for the exact
canonical SheriffOffice attached to the allocation receipt. The appointment
record also carries the exact office/court/area scope, the Fidelity Fund
Certificate jurisdiction and validity, and current professional indemnity
insurance as a separate WILSY operational-evidence condition.

WILSY records a tenant administrator's attestation that external source
instruments were inspected. WILSY does not issue appointments, issue Fidelity
Fund Certificates, or independently authenticate external issuers/documents.

## 2. Authority and dependency matrix

| Source / component | Owned fact | Required use | Explicit non-authority |
|---|---|---|---|
| `PrincipalAuthorityRepository` | Principal active/inactive status | Target Sheriff and verifier must be active | No tenant membership or business role |
| `TenantMembershipRepository` | Principal's active tenant membership | Target and verifier must be active members of the exact tenant | No office appointment |
| `TenantBusinessRoleRepository` | Current tenant business role | Target = `tenant_sheriff`; verifier = `tenant_admin` | Role label is not appointment |
| `RoleAssignmentRepository` | Current authorization role assignment | Target = `SHERIFF`; verifier = `ENTERPRISE_ADMIN` | Static role grant alone is not possession or legal appointment |
| P1 lifecycle registry | Canonical `District` and `SheriffOffice` current values and fingerprints | Resolve office and parent District in the same transaction | Directory record does not issue appointment |
| Sheriff appointment registry | Immutable appointment revisions and currentness | Tenant/principal/office scoped history, overlap rejection, replay and currentness | Does not issue or authenticate external instruments |
| Appointment orchestrator | Same-transaction IAM + P1 + appointment composition | Re-checks target and verifier, derives District and jurisdiction, controls revision lineage | Does not grant IAM or start/commit transactions |
| Command router | Authenticated tenant-admin command | Derives tenant/verifier/time, bootstraps indexes before transaction, owns transaction | Request body cannot supply authority |
| Sheriff read router | Current attempt, allocation receipt and location evidence | Matches receipt office to current appointment, canonical P1 fingerprints, jurisdiction, FFC and insurance | No tenant-wide office enumeration or fallback |
| Client Legal Operations service | Strict transport and response projection | Sends evidence facts only; validates appointment response and location projection V2 | Presentation never authorizes |
| Focused CI workflow | Reproducible certification | Python unit + real replica-set + Pyright + client Vitest + diff/worktree checks | Not a production deployment |

## 3. Write path

1. Authenticated tenant admin calls `POST /legal-operations/sheriff/appointments`.
2. `RequireTenantAuthorization` requires the dedicated
   `legal_operations:sheriff_appointment:write` permission and
   `legal_sheriff_appointment_write` operation.
3. Static permission possession is granted only to `ENTERPRISE_ADMIN`;
   business-role eligibility is limited to `tenant_admin`.
4. The command router creates the appointment registry indexes before opening
   the transaction; DDL is never attempted inside the transaction.
5. One API-owned transaction re-resolves active target Sheriff and verifier
   principal, membership, business role and authorization role.
6. The orchestrator resolves the exact canonical SheriffOffice and parent
   District from P1. District identity, jurisdiction and fingerprints are
   server-derived; the request cannot supply them.
7. The orchestrator derives the certificate jurisdiction from the canonical
   District and requires it to be part of the immutable appointment evidence.
8. The registry enforces immutable revisions, exact replay, predecessor
   continuity, overlap rejection and caller-owned transaction semantics.
9. The verifier must be a different principal from the target Sheriff.

## 4. Read path

1. The Sheriff authenticates with current tenant Sheriff IAM.
2. The API resolves the exact current ServiceAttempt and P4 allocation receipt.
3. The office identifier is taken from the allocation receipt, not the browser.
4. The appointment registry returns the principal's current appointments; the
   read path selects only the exact office on that receipt.
5. The current canonical SheriffOffice and District are reloaded from P1.
6. The allocation receipt's office/District identifiers and source fingerprints
   must match current P1. The appointment District and certificate jurisdiction
   must also match the canonical District.
7. The appointment, Fidelity Fund Certificate and professional indemnity
   insurance must all be current at the same snapshot time.
8. A missing, expired, corrupt or different-office appointment denies the read.
   Multiple current appointments for different offices are allowed; no
   tenant-wide single-office assumption or fallback exists.
9. Every successful evidence read records a metadata-only access event.

## 5. Data and security invariants

- Tenant, verifier principal, verification timestamp, District, certificate
  jurisdiction, revision and predecessor are server-derived.
- The command body contains only opaque target identifiers, external source
  references/fingerprints, effective dates and optimistic concurrency tokens.
- A replay is returned only when all source facts, target, office and verifier
  match the existing immutable revision.
- A successor requires the exact current revision and predecessor fingerprint.
- The target Sheriff cannot verify their own appointment.
- Currentness requires appointment validity, FFC validity and PI insurance
  validity; the PI condition is a WILSY operational control, not a statement
  that the Sheriffs Act itself prescribes this platform requirement.
- Location evidence remains one-shot/attempt-bound; this feature adds no
  continuous tracking.
- No retention period, legal-hold policy or deletion authority is inferred.
- No production MongoDB, production customer data or production legal payload
  was used by the certification workflow.

## 6. Certification evidence

Focused feature-branch certification at commit
`5d2213608ccd848fc5bf9be341427b7d79b73847` completed:

- Python appointment evidence suite: **64 passed**.
- Client Legal Operations transport suite: **62 passed**.
- Pyright: **0 errors, 0 warnings, 0 informations**.
- Real MongoDB: isolated writable replica set; commit, exact replay, abort,
  active IAM, P1 lineage, multiple offices, overlap and foreign-office denial.
- Client CI: strict command whitelist, response binding and V2 location read.
- Repository integrity and diff checks are included in the dedicated workflow.

The architecture/documentation commits that follow this certification do not
change the certified runtime code. The full repository PR workflows remain
separate release gates and must pass before merge.

## 7. Explicit remaining launch gaps

1. Tenant-admin appointment evidence-entry UI is not yet mounted in the product.
2. Source-document upload/retention and cryptographic hash derivation are not
   connected to this command. The administrator supplies references and
   fingerprints after external inspection.
3. Ministerial, Board and insurer issuer authenticity is not independently
   verified by WILSY; the verifier attestation is recorded, not treated as
   cryptographic proof of issuer origin.
4. Full Sheriff/deputy dashboard parity, native camera/GPS integrity and
   offline evidence synchronization remain separate work.
5. Broader legal lifecycle end-to-end certification, retention governance,
   operational incident controls and production pilot are not certified here.

## 8. Release decision

This is a backend authority and office-isolation slice, not a claim that the
entire Legal Operations product is launch-complete. Merge is conditional on
all required PR workflows, code scanning and review gates passing. Production
deployment additionally requires the remaining launch gaps to be accepted or
closed by the relevant product, legal and security owners.

---

ARTIFACT: 2026-11-02-sheriff-office-appointment-authority-connection-matrix.md
VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-AUTHORITY-CONNECTION-MATRIX
AUTHORITY BOUNDARY: engineering dependency map only; no runtime authority
TENANT POSTURE: exact-tenant authority and evidence reads/writes
FAIL-CLOSED POSTURE: absent source proof, office scope, current certificate, current indemnity or verified IAM denies
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
END OF WILSY OS SOVEREIGN ARTIFACT
