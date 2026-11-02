# Sheriff Principal-to-Office Authority: Statutory Source and Enforcement Decision

- **Record:** WILSY-ADR-LEGAL-SHERIFF-OFFICE-AUTHORITY
- **Version:** 1.0.0
- **Date:** 2026-11-02
- **Status:** Engineering decision baseline; implementation not yet certified
- **Owner:** WILSY OS Legal Operations
- **Scope:** South African Sheriff and Deputy Sheriff identity, appointment, office and service-area authority
- **Repository baseline:** `main` at merge commit `0c1b30700aded8a7d3358a2192c860c01585b65a`

## 1. Decision

WILSY must not infer that a tenant-level `tenant_sheriff` role, a descriptive CX27 office scope, a provisioned `SheriffOffice` record, or a caller-supplied office identifier establishes that a principal is legally appointed to act for that office.

The canonical authority record must be grounded in the applicable external appointment/designation instrument and its effective scope. WILSY may preserve and verify the evidence, bind it to a verified natural-person/principal identity and a canonical office/district, and enforce its currentness. WILSY must not manufacture the appointment or replace the statutory appointing authority.

For South Africa, the source-of-authority model must distinguish at least:
1. Sheriff appointed by the Minister for a court under section 2 of the Sheriffs Act 90 of 1986, including any written area allocation under section 3.
2. Acting sheriff appointed under section 5, with its bounded term and scope.
3. Deputy sheriff appointed by a sheriff or acting sheriff under section 6, subject to Board approval and applicable conditions.
4. A person designated in writing by the Minister under section 6A, where applicable, with the specified court, period and conditions.

These are distinct legal capacities. They must not be collapsed into one generic `SHERIFF` business role or one tenant-wide office flag.

## 2. Verified statutory basis

The official Department of Justice copy of the Sheriffs Act describes the Minister's appointment power, office term/removal, acting-sheriff appointments, Deputy Sheriff appointment by a Sheriff/acting Sheriff with Board approval, and the written designation power. The Act also provides for allocation of areas within a court's jurisdiction.

- Department of Justice, **Sheriffs Act 90 of 1986** (official copy): https://www.justice.gov.za/legislation/acts/1986-090.pdf
- South African Government legislation record: https://www.gov.za/documents/sheriffs-act-10-mar-1986-0000
- South African Government, **Sheriffs FAQ**, including the explanation that a Sheriff is appointed for a magisterial district or an area within a district: https://www.justice.gov.za/faq/faq-sheriffs.html
- South African Board for Sheriffs, **Fidelity Fund**: https://sheriffs.org.za/fidelity-fund/ (annual Fidelity Fund Certificate issuance and Board administration).
- South African Board for Sheriffs, **Locate a Sheriff**: https://sheriffs.org.za/locate-a-sheriff/ (public directory; a directory listing is an observation source, not a substitute for the underlying appointment and current certificate evidence).
- Supreme Court of Appeal, *South African Board for Sheriffs v Thaka Frederick Seboka and Others* [2026] ZASCA 109: https://www3.saflii.org/za/cases/ZASCA/2026/109.html (section 5(1B) written Board confirmation issue).

Relevant provisions to encode and have South African legal counsel validate against the currently consolidated Act and regulations:
- **Section 2:** appointment of Sheriffs by the Minister for a lower or superior court; special appointment of another area's Sheriff in a vacancy scenario is a distinct written appointment.
- **Section 3:** the Sheriff performs functions within the court's area; the Minister may describe and allocate one or more areas within that jurisdiction and may alter the area.
- **Section 4:** tenure, resignation and removal.
- **Section 5:** acting Sheriff appointments, including bounded conditions and periods.
- **Section 6:** Sheriff/acting Sheriff may appoint one or more Deputy Sheriffs with Board approval and applicable conditions; Deputy acts subject to the appointing Sheriff's directions.
- **Section 6A:** written Ministerial designation of a Department official for a specified period, court and conditions in the stated vacancy circumstances; section 30 expressly does not apply to a section 6A designee.
- **Section 6B:** written Ministerial appointment of a Sheriff or acting Sheriff to perform specified non-service-of-process functions in another area, after Board consultation and on the Minister's conditions.
- **Sections 30–34:** a Sheriff or Deputy Sheriff may not perform functions unless the statutory fidelity-fund certificate and professional-indemnity requirements are met; an acting Sheriff has the alternative statutory contribution route. Certificates are time-bounded, and the Board may cancel them. Appointment currentness alone is therefore insufficient for operational currentness.

A 2026 Supreme Court of Appeal judgment, *South African Board for Sheriffs v Thaka Frederick Seboka and Others* [2026] ZASCA 109 (20 August 2026), discusses section 5(1B) and the required written Board confirmation concerning a fidelity-fund certificate before an acting-Sheriff appointment. It must be considered in the legal validation of the acting-Sheriff path: https://www3.saflii.org/za/cases/ZASCA/2026/109.html

This is an engineering source map, not legal advice or a substitute for checking the latest amendments, regulations, appointment notices, fidelity-fund status and instrument-specific conditions before production use.

## 3. Current repository evidence and gap

The following existing components were inspected on `main`:

| Existing component | Current responsibility | What it does not establish |
|---|---|---|
| `tools/eos/legal_operations/domain/legal_operations_lifecycle.py` — `District`, `SheriffOffice`, `Deputy` | Immutable tenant-scoped directory identities and parent relationships | Appointment of a natural person as Sheriff, acting Sheriff or Deputy Sheriff |
| `tools/eos/legal_operations/orchestration/process_service_directory_provisioning_orchestrator.py` | Constructs/provisions canonical District, SheriffOffice and Deputy records | Who is legally appointed to hold an office |
| `tools/eos/auth/tenant_authority_policy.py` | Business-role eligibility, including Sheriff process-service operations | Appointment, court jurisdiction, area allocation or institutional office authority |
| `tools/eos/auth/tenant_authorization.py` | Conjunctive principal, membership, business-role and granting-role IAM authorization | A statutory appointment or current office-specific authority |
| `tools/eos/legal_operations/domain/legal_principal_operating_role_binding.py` and its registry | Immutable effective-dated descriptive principal-to-operating-role occupancy | IAM, workforce authority, professional status, regulatory appointment or execution authority |
| `tools/eos/legal_operations/domain/legal_operating_role_scope_binding.py` and its registry | Descriptive office/practice/business-unit/jurisdiction scope metadata | Record-access, matter, route, workflow, assignment or supervision authority |
| `tools/eos/api/legal_operations_router.py` — `GET /legal-operations/operational-queues` | Sheriff-only, own-tenant operational queue projection | Office-level restriction; it currently delegates tenant scope to the lifecycle queue projection |
| R62/R63/R64 practitioner professional-standing evidence and regulatory source-verification components | Existing immutable source-observation, issuer classification, FFC validity and freshness patterns for Legal Practice Council evidence | Their canonical issuer map and subject model are LPC-specific; they do not establish South African Sheriff appointment, SABFS certificate status or Sheriff-office scope |
| Deputy principal binding and personal active-work route | Binds authenticated Deputy principal to canonical Deputy and SheriffOffice evidence | Sheriff principal-to-office appointment |

The repository already has a disciplined R62/R63/R64 pattern for observing and verifying Legal Practice Council professional-standing and FFC records. Its source allowlist is explicitly LPC-only. Reuse its integrity, freshness, issuer-trust and no-self-attestation patterns, but do not reuse its LPC issuer constants, subject model or claim that the South African Board for Sheriffs is already integrated. No authenticated SABFS API/trust-root integration was established in this discovery.

The key current risk is the difference between **tenant IAM admission** and **statutory office authority**. The existing Sheriff queue permission is intentionally own-tenant and Sheriff-role-only, but it is not office-specific. In a tenant representing multiple Sheriff offices, it cannot safely be treated as proof that the caller may see every office's work.

The CX27 scope metadata must not be repurposed as the missing authority. Its own domain contract expressly says that organizational scope descriptions never grant record access.

## 4. Required canonical authority model

Implement a separate, append-only, effective-dated **Sheriff Office Appointment Binding** authority. It must be a distinct domain from CX27 role occupancy and descriptive scope.

Minimum semantic fields (final names/types to be frozen only after repository discovery and legal review):

- exact `tenant_id`;
- stable binding identifier and monotonic revision;
- verified authenticated `principal_id` and separately verified natural-person identity reference;
- canonical `sheriff_office_id`, `district_id`, court identifier and allocated service-area reference(s);
- legal capacity enum: `SHERIFF`, `ACTING_SHERIFF`, `DEPUTY_SHERIFF`, or `SECTION_6A_DESIGNEE`;
- statutory provision and appointment/designation instrument type;
- issuing/appointing authority and instrument reference;
- cryptographic fingerprint of the original source instrument and its provenance/verification record;
- for Deputy Sheriffs, appointing Sheriff/acting Sheriff identity and Board approval evidence;
- effective-from and effective-until times, with explicit revocation/supersession lineage;
- conditions/limitations that affect court, matter, area, time or function;
- source verification actor, verification time and verification method;
- immutable fingerprint over the complete semantic record.

An opaque source reference and a caller-supplied hash are not, by themselves, proof that an instrument is authentic. The ingestion/verification boundary must establish the source document's provenance, integrity, identity match, issuing authority and current status. If any cannot be established, no active binding is created.

## 5. Issuance and lifecycle rules

1. No tenant-level Sheriff, tenant admin, Deputy, client, or generic operator may self-assert a statutory appointment.
2. A section 2 Sheriff appointment requires the appointment instrument issued by the competent Ministerial authority, plus court/office and area scope.
3. An acting Sheriff binding must carry its section 5 appointment instrument, reason/capacity, scope and bounded term. Expiry must automatically remove current authority from reads.
4. A Deputy Sheriff binding requires evidence of appointment by the relevant Sheriff/acting Sheriff and Board approval, plus the exact appointing office and conditions. A Deputy principal binding is not a Deputy Sheriff appointment.
5. A section 6A designation must be represented separately, with the written designation, named court, period and conditions. It must not be promoted to a general Sheriff appointment.
6. Revocation, resignation, removal, expiry, replacement, change of area and appointment correction are append-only events. They must not rewrite history.
7. Conflicting or overlapping current appointments that cannot be resolved from the source instruments fail closed.
8. Multi-office or multi-court authority is allowed only where the source instruments independently support it. It must not be inferred from tenant membership or a UI selection.
9. A role/office binding never grants unrelated IAM permissions. Existing IAM checks remain conjunctive and independent.
10. The legal office appointment record is evidence of institutional capacity; operation-specific permission, matter scope, conflict restrictions and lifecycle conditions remain separate gates.

## 6. Read-path enforcement

Before enabling office-scoped Sheriff queue reads:

- Resolve authenticated principal and exact tenant only from current canonical IAM context.
- Within the same read snapshot, load the current, verified appointment binding(s) for that principal and tenant.
- Resolve the exact canonical SheriffOffice and court/service-area scope from P1 directory facts.
- For functions governed by sections 30–34, resolve current Fidelity Fund Certificate status and professional-indemnity insurance evidence (or the applicable acting-Sheriff contribution route); section 6A designees follow their express statutory exception.
- Intersect appointment scope with the requested server-derived queue scope; do not accept an office ID as an authority selector from the caller.
- Filter all three queue classes (office receipt, Deputy assignment, active attempts) by the same authorized office set and verify each returned lifecycle record's tenant, office and district lineage.
- If there is no current appointment, invalid/expired/revoked evidence, unknown office, multiple ambiguous appointments, missing office lineage, or multi-office tenant with no exact appointment scope, deny before disclosing queue rows.
- Preserve existing tenant and principal IAM checks; appointment evidence supplements them and never replaces them.
- Audit access decisions with pseudonymous identifiers and the binding fingerprint; do not log legal instrument contents or raw identity documents.
- Use one caller-owned snapshot transaction for appointment, office and lifecycle reads. No fallback to tenant-wide queue access is permitted.

## 7. Required certification matrix

### Unit and contract tests
- each statutory capacity and required source-instrument fields;
- wrong issuing authority, missing instrument, missing source fingerprint and invalid provenance;
- subject/principal mismatch;
- court, district, office and allocated-area mismatch;
- expired, future-dated, revoked, removed, resigned and superseded appointments;
- acting Sheriff and section 6A/6B scope/period constraints;
- expired/cancelled Fidelity Fund Certificate, missing insurance evidence, acting-Sheriff section 5(1B) Board confirmation, and the section 6A section-30 exception;
- Deputy appointment without Board approval;
- cross-tenant, cross-office and caller-substitution denial;
- multiple valid appointments only where each is explicitly evidenced;
- overlapping conflicting appointments fail closed;
- replay and same-key/different-payload conflict behavior;
- no authorization, IAM grant, lifecycle mutation or financial methods on the domain/registry.

### Real-Mongo replica-set tests
- UUID-isolated disposable database only;
- exact tenant-first query predicates and same active transaction propagation;
- unique indexes and immutable append-only history;
- concurrent issue/revoke/expiry and current-read races;
- exact replay, conflict, corruption, lineage and transaction abort behavior;
- no production database, no port 27027 defaults, no external provider calls.

### HTTP and client parity
- existing `/operational-queues` remains denied for a Sheriff without a current office binding;
- tenant-wide legacy queue is not reachable as a fallback;
- office A principal cannot see office B records, including mixed-office batches;
- authorized multi-office principal sees only offices listed in verified instruments;
- client cannot supply/override principal, tenant, office, court or scope;
- UI presents the verified appointment status and scope but cannot create legal authority;
- audit, telemetry and Intelligence Dock observe denials without exposing sensitive instrument data.

## 8. Connection and blast-radius matrix

| Surface | Required connection | Blast radius | Change policy |
|---|---|---|---|
| Legal statutory source | Appointment/area instrument, Board approval and currentness evidence | Legal validity and office jurisdiction | External evidence verification; no inference |
| Identity and IAM | Principal, ACTIVE membership, current business and authorization role | Authentication and tenant access | Preserve existing conjunctive IAM |
| P1 directory | District, SheriffOffice, Deputy | Service lifecycle lineage | Read-only from authority projection |
| New appointment domain/registry | Append-only issue/revoke/currentness | Institutional office authority | Separate canonical authority |
| Sheriff queue API | Appointment + office filter + lifecycle queue | Confidential cross-office disclosure | Fail closed; no tenant-wide fallback |
| Deputy binding | Deputy identity vs Deputy Sheriff appointment | Personal field-work authority | Keep concepts distinct |
| Client dashboard | Scope-aware projection | UI disclosure and user expectations | Projection only |
| Audit/telemetry | Decision and evidence fingerprints | Accountability and privacy | Metadata only |
| Mongo/transactions | One snapshot and immutable writes | Race, replay and tenant isolation | Caller-owned transaction; disposable replica-set tests |
| Legal review | Statutory capacity, instrument, conditions and currentness | Unauthorized legal acts | Required before production certification |

## 9. Release gates

This capability is **not production-ready** until all of the following are true:

- South African legal counsel has validated the current consolidated Act (including sections 6A, 6B and 30–34), regulations, relevant appointment forms/notices, 2026 SCA judgment implications, and the accepted evidence-verification process.
- A trusted source for Ministerial appointments, area allocations, Board approvals, Fidelity Fund Certificates, insurance evidence and revocations has been identified and operationally connected. The SABFS public directory and Fidelity Fund information page are useful source references, but a public directory observation or tenant upload alone is not automatically an authenticated trust root.
- The appointment domain, registry, lifecycle command, revocation/currentness projection and office-scoped read enforcement are implemented.
- All unit, type, real-Mongo, HTTP, security and replay tests pass in isolated CI.
- Independent security review confirms no caller-controlled office selection, tenant-wide fallback, cross-office leakage or self-appointment path.
- Client and operational dashboards display the distinction between tenant IAM role, statutory capacity, appointment currentness and office scope.
- A controlled pilot verifies real appointment instruments and revocation handling before broad release.

## 10. Implementation status and next engineering slices

### Merged first slice

The first pure-domain source-evidence slice has now been merged to `main` in PR #284:

- Primary artifact: `tools/eos/legal_operations/domain/sheriff_appointment_source_evidence.py`
- Unit certificate: `tests/unit/test_sheriff_appointment_source_evidence.py`
- Dedicated workflow: `.github/workflows/sheriff-appointment-source-evidence.yml`
- Domain version: `v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE`
- Merge commit: `dae3d3dbd9265232976f81ecc0ad62ffe2a3107e`
- Verification: 20 unit tests passed; Python compilation, pinned Pyright, patch whitespace, repository integrity, Deputy device provenance, image publication, security audit, and the retained R2A/R2B real-Mongo gates all passed on the PR head.

The domain stores typed statutory source observations and required special-path Board references. It is deliberately non-authorizing: it does not authenticate the issuer, prove a current appointment, establish Fidelity Fund Certificate or insurance currentness, grant IAM, or authorize office/queue access.

### Next slices, in order

1. **Sheriff appointment evidence registry:** caller-owned transaction, immutable append-only history, tenant-first unique indexes, exact replay, fork/conflict/corruption rejection, and isolated real-Mongo certification.
2. **Source verification/currentness:** separate Ministerial appointment/area-allocation and SABFS Board/FFC source evidence, trust-root or independently governed human verification, currentness, revocation, and expiry. Do not reuse LPC trust roots.
3. **Identity binding:** verified natural-person-to-WILSY-principal correlation, with no self-attestation or tenant-admin self-appointment.
4. **Office-scoped Sheriff queue enforcement:** same-snapshot appointment, current certificate/insurance, office, court/area and lifecycle reads; no tenant-wide fallback.
5. **HTTP, client, audit and independent legal/security certification:** cross-office adversarial tests, currentness/revocation races, real-Mongo replay, and controlled pilot.

Do not change the current Sheriff queue to trust CX27 office references. Until the complete appointment, source-currentness and read-enforcement path is certified, multi-office Sheriff queue access must remain restricted/denied rather than silently treated as tenant-wide.

## 11. Explicit unresolved inputs

- Trusted institutional source/API or verified instrument workflow for appointment, area allocation, Board approval and revocation.
- Identity-proofing mechanism linking the natural person named in the instrument to the authenticated WILSY principal.
- Legal review of the exact instrument fields, accepted electronic copies, verification standard and update cadence.
- Whether a pilot customer has one Sheriff office or multiple offices, and the authoritative office identifiers to reconcile.

These are evidence and legal-governance dependencies, not permission to invent defaults.
