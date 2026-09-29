# WILSY OS — LEGAL EVIDENCE CAPACITY & ENTITLEMENT MAP

**Version:** v1.0.0-L10A2Q-LEGAL-EVIDENCE-CAPACITY-ENTITLEMENT-MAP
**Authority:** Wilsy OS Core Governance
**Certification / update date:** 2026-09-29
**Status:** ARCHITECTURAL CONTRACT — numeric commercial limits deliberately unresolved until separately certified.

## 1. Purpose

This map defines the authority and composition model for Legal evidence upload,
storage, usage and capacity control.

It does not create pricing, subscription, entitlement, IAM, storage, payment,
Court, Court Online, AI, billing execution or settlement authority.

The governing sequence is:

`platform safety -> commercial catalogue -> tenant entitlement -> subscription/profile binding -> observed usage -> remaining capacity -> IAM -> Legal admission -> persistence`

No downstream component may infer an upstream fact.

## 2. Existing certified authorities

WILSY OS already separates:

- tenant product catalogue identity;
- tenant product entitlement lifecycle;
- subscription and plan truth;
- VAS commercial catalogues;
- WILSY AI commercial limits;
- WILSY AI observed usage and remaining-capacity projection;
- IAM permission and tenant-business-role eligibility;
- Legal evidence content identity and persistence.

Legal evidence capacity SHALL reuse these authority patterns rather than create
a second subscription, catalogue, entitlement or billing authority.

## 3. Legal evidence commercial capacity profile

One immutable Legal evidence capacity profile SHALL be able to express:

- `single_file_max_bytes`
- `tenant_storage_limit_bytes`
- `monthly_ingress_limit_bytes`
- `max_document_versions`
- `ocr_page_allowance`
- `ai_document_processing_allowance`
- `retention_class`
- `legal_hold_available`
- `bulk_ingest_available`
- `api_ingest_available`
- `external_client_upload_available`

Future expansion MAY add separately certified metrics such as archival capacity,
export bandwidth, eDiscovery workspace capacity, disaster-recovery class,
encryption-key class, or geographic-storage class.

Unknown fields and unknown profile identities SHALL fail closed.

## 4. Commercial profiles

The initial closed profile vocabulary is:

- `STARTER`
- `GROWTH`
- `INSTITUTIONAL`
- `FOUNDER_ENTERPRISE`

`FOUNDER_ENTERPRISE` is an explicit concession/profile binding. It does not
mutate ordinary catalogue pricing and must not silently inherit authority from
a display name or browser value.

Numeric byte, ingress, version, OCR and AI limits are intentionally NOT fixed
by this architecture map. They require a separate commercial-policy
certificate backed by storage economics and production capacity evidence.

## 5. Authority ownership

### Commercial catalogue authority

Owns immutable capacity-profile definitions and their deterministic evidence
fingerprints.

It does not prove that any tenant owns a profile.

### Tenant product entitlement authority

Owns whether one exact tenant has an ACTIVE Legal Operations product
entitlement.

ACTIVE product entitlement does not prove IAM, upload authority, storage
capacity, payment, or subscription status by itself.

### Subscription / plan authority

Owns the canonical commercial evidence from which the applicable Legal
evidence capacity profile is resolved.

Legal Operations must not inspect arbitrary display names or caller-provided
plan strings.

### Usage evidence authority

Owns immutable tenant-scoped observations of consumed evidence resources.

At minimum future usage evidence should distinguish:

- durable stored bytes;
- monthly ingress bytes;
- evidence-content/version count;
- OCR pages consumed;
- AI document-processing units consumed.

Usage observation is evidence only and does not itself grant or deny access.

### Capacity projection authority

Consumes:

- exact ACTIVE entitlement evidence;
- exact commercial capacity policy;
- complete required usage evidence;
- explicit evaluation time.

Produces immutable remaining-capacity evidence.

Capacity projection has no pricing, payment, IAM or Legal lifecycle authority.

### IAM authority

Determines whether the authenticated principal may execute
`legal_operations:evidence:write` for the exact tenant.

Commercial entitlement never grants IAM permission.

### Legal Operations authority

Consumes the approved capacity result and IAM context.

Legal Operations owns:

- exact tenant binding;
- exact CaseMatter / ProcessDocument binding;
- evidence-content identity;
- Legal workflow correlation.

Legal Operations does not own plan prices, subscription lifecycle, payment,
financial execution or settlement.

## 6. Admission sequence

Evidence ingestion SHALL proceed fail closed in this order:

1. authenticate principal;
2. derive exact tenant context;
3. require canonical Legal evidence IAM permission;
4. require ACTIVE Legal Operations product entitlement;
5. resolve exact canonical capacity profile from subscription/catalogue truth;
6. derive current remaining capacity from complete usage evidence;
7. reject before expensive processing when per-file, tenant-storage or monthly
   ingress capacity is unavailable;
8. stream bytes under a separate platform technical ceiling;
9. validate filename, extension, declared MIME and detected content signature;
10. quarantine / malware-scan where the certified security service exists;
11. calculate SHA3-512 content identity;
12. verify exact tenant + CaseMatter + ProcessDocument correlation;
13. persist immutable content and metadata;
14. persist immutable usage observation;
15. expose resulting capacity / warning projection to authorized UI surfaces.

No step may manufacture a later legal lifecycle state.

`UPLOADED != REGISTERED != RECEIVED != ALLOCATED != SERVED != RETURNED != FILED != COURT ACCEPTED`

## 7. Capacity exhaustion

Capacity exhaustion SHALL block new ingestion.

It SHALL NOT:

- delete existing Legal evidence;
- mutate existing immutable content;
- weaken evidence integrity;
- bypass retention;
- bypass legal hold;
- create payment success;
- create an upgrade automatically;
- grant a larger plan;
- silently borrow another tenant's capacity.

Recommended presentation states are:

- `NORMAL`
- `NEAR_LIMIT`
- `CRITICAL`
- `EXHAUSTED`

The threshold policy belongs to capacity presentation/policy, not Legal
evidence persistence.

## 8. Security controls

Commercial entitlement and security admission are independent.

A tenant with available capacity still SHALL NOT be permitted to ingest
unsupported or unsafe content.

The production upload path must ultimately certify:

- allow-listed content types;
- extension / MIME / magic-byte correlation;
- filename/path traversal rejection;
- bounded streaming;
- decompression/archive-bomb protection if archive formats are ever enabled;
- malware/quarantine integration before ordinary availability;
- content fingerprint verification;
- immutable tenant/document binding;
- audit/observability;
- rate limiting;
- denial behavior that does not leak confidential matter existence.

## 9. Storage architecture rule

Legal evidence capacity SHALL NOT be designed around MongoDB single-document
size.

The content persistence layer must support the largest certified commercial
single-file profile while preserving:

- tenant isolation;
- immutable content identity;
- exact replay;
- corruption detection;
- atomic metadata/content visibility or a separately certified equivalent
  commit protocol;
- abort/retry safety;
- no raw-byte duplication into oversized BSON metadata documents.

The existing L10A2 raw-byte-in-one-document persistence therefore requires
repair before the multipart API may be certified.

## 10. Product differentiation rule

WILSY OS SHALL not differentiate plans by storage alone.

Legal evidence commercial differentiation may include:

- storage capacity;
- single-file size;
- monthly ingress;
- document version capacity;
- OCR allowance;
- AI document-processing allowance;
- bulk discovery ingest;
- external-client evidence intake;
- API ingest;
- retention class;
- legal hold;
- audit history depth;
- eDiscovery/export capability;
- disaster-recovery class.

Optional evidence-capacity packs may later increase capacity without requiring
a full base-plan migration, but such packs require their own commercial and
entitlement authority.

## 11. Founder posture

Founder Enterprise may receive Enterprise-class or separately certified
Founder-class Legal evidence capacity by explicit concession evidence.

Zero or concessionary price does not mutate the ordinary commercial catalogue.

## 12. Required certification sequence

The implementation sequence is:

1. **L10A2Q** — architecture / authority map.
2. **L10A2Q-P1** — immutable Legal evidence capacity commercial policy.
3. **L10A2Q-P2** — tenant subscription/profile resolver.
4. **L10A2Q-P3** — immutable Legal evidence usage observation.
5. **L10A2Q-P4** — remaining-capacity derivation.
6. **L10A2R** — repair evidence binary persistence for the certified maximum.
7. **L10A3D** — authenticated streaming/multipart HTTP ingestion.
8. Client projection / capacity warnings / upgrade opportunity.
9. Authenticated browser and negative-boundary certification.

Each step must preserve the governing WILSY OS authority boundaries and
`NO EVIDENCE = NO FACT`.

---

**ARTIFACT:** wilsy-legal-evidence-capacity-and-entitlement-map.md
**VERSION:** v1.0.0-L10A2Q-LEGAL-EVIDENCE-CAPACITY-ENTITLEMENT-MAP
**AUTHORITY BOUNDARY:** architecture/ownership contract only; no commercial, entitlement, IAM, storage or financial authority
**TENANT POSTURE:** exact tenant scope must be supplied by canonical upstream evidence
**FAIL-CLOSED POSTURE:** unknown/missing catalogue, entitlement, subscription, usage or capacity truth blocks admission
**FINANCIAL EXECUTION AUTHORITY:** Kennel EOS exclusively
**END OF WILSY OS SOVEREIGN ARTIFACT**
