# WILSY OS — LEGAL EVIDENCE CAPACITY & ENTITLEMENT MAP

**Version:** v1.1.0-L10A2Q-LEGAL-EVIDENCE-CAPACITY-ENTITLEMENT-MAP
**Authority:** Wilsy OS Core Governance
**Certification / update date:** 2026-09-29
**Status:** ARCHITECTURAL CONTRACT — exact commercial-capacity values are delegated to the separately certified canonical commercial policy; provider-neutral binary storage and the AWS S3 adapter are certified capabilities, while production ingestion orchestration, capacity reservation, retention execution and Mongo/object-plane migration remain separately gated.

## 1. Purpose

This map defines the authority and composition model for Legal evidence upload,
storage, usage and capacity control.

It does not create pricing, subscription, entitlement, IAM, storage, payment,
Court, Court Online, AI, billing execution or settlement authority.

The governing sequence is:

`platform safety -> commercial catalogue -> tenant entitlement -> subscription/profile binding -> observed usage -> remaining capacity -> atomic capacity reservation -> IAM -> Legal admission -> binary-object persistence -> integrity verification -> canonical metadata commit -> usage/reservation commit -> authorized availability`

No downstream component may infer an upstream fact.

## 2. Existing certified authorities

WILSY OS already separates:

- tenant product catalogue identity;
- tenant product entitlement lifecycle;
- subscription and plan truth;
- VAS commercial catalogues;
- the certified Legal Evidence capacity-profile contract;
- the certified Legal Evidence commercial-capacity policy;
- WILSY AI commercial limits and reservation precedents;
- IAM permission and tenant-business-role eligibility;
- Legal evidence content identity;
- the provider-neutral Legal Evidence binary-storage port;
- the AWS S3 Legal Evidence binary-storage adapter;
- the existing Mongo Legal evidence registry.

These authorities are not interchangeable.

The current Mongo registry still persists `content_bytes` inline. It remains a
migration source for existing Legal evidence persistence and is not the target
binary-storage architecture.

The provider-neutral binary-storage port and S3 adapter are storage-capability
surfaces only. They do not become catalogue, subscription, entitlement, IAM,
Legal lifecycle, retention, Court, payment or settlement authorities.

Real-provider runtime certification proves the bounded adapter behavior that was
actually exercised. It does not by itself provision or certify the permanent
production Legal Evidence storage estate.

Legal Evidence capacity SHALL reuse existing catalogue, entitlement,
subscription, IAM and billing authority patterns rather than create duplicate
truth.

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

The closed profile vocabulary is:

- `STARTER`
- `GROWTH`
- `INSTITUTIONAL`
- `FOUNDER_ENTERPRISE`

`FOUNDER_ENTERPRISE` is an explicit concession/profile binding. It does not
mutate ordinary catalogue pricing and must not silently inherit authority from
a display name or browser value.

Exact numeric byte, ingress, version, OCR and AI-processing limits are NOT
owned by this architecture map.

The canonical exact values are delegated to the separately certified
`legal_evidence_capacity_commercial_policy.py` artifact. This map describes
authority relationships and capacity dimensions but SHALL NOT duplicate those
numbers and become a second commercial truth.

An AI document-processing allowance is a Legal Evidence capacity dimension
only. It does not grant WILSY AI VAS entitlement, model access, AI execution
authority or additional AI commercial rights.

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
3. require canonical Legal Evidence IAM permission;
4. require ACTIVE Legal Operations product entitlement;
5. resolve the exact canonical capacity profile from subscription/catalogue
   truth;
6. derive current remaining capacity from complete usage and outstanding
   reservation evidence;
7. reject before expensive processing when per-file, tenant-storage or monthly
   ingress capacity is unavailable;
8. atomically reserve required capacity for the exact tenant and ingestion
   intent before provider work begins;
9. stream bytes under a separate platform technical ceiling;
10. validate filename, extension, declared MIME and detected content signature;
11. quarantine / malware-scan where a certified security service exists;
12. independently calculate WILSY SHA3-512 content identity and exact byte
    length while streaming;
13. verify exact tenant + CaseMatter + ProcessDocument correlation;
14. complete binary-object persistence through the certified provider-neutral
    storage port;
15. verify provider object evidence against exact tenant intent, object version,
    byte length and canonical WILSY SHA3-512 evidence;
16. commit canonical immutable Legal Evidence metadata without duplicating the
    binary body into the Mongo control plane;
17. atomically consume or reconcile the reservation and persist corresponding
    immutable usage evidence;
18. expose the evidence only after canonical metadata commit and required
    security gates succeed;
19. expose resulting capacity and warning projections to authorized UI
    surfaces.

A failed, expired or aborted ingestion SHALL release or reconcile its
reservation under separately certified rules. Unknown reservation state SHALL
fail closed.

Provider-object success alone is not Legal Evidence commitment. Mongo metadata
success without verified binary-object evidence is not binary-persistence
success.

No step may manufacture a later Legal lifecycle state.

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

## 7A. Usage and reservation accounting semantics

Usage observations and capacity reservations are separate evidence classes.

Capacity policy SHALL define, through separately certified artifacts, the
accounting treatment of at least:

- durable active object bytes;
- retained historical object-version bytes;
- monthly ingress bytes;
- outstanding reserved bytes;
- incomplete multipart/provider-session bytes;
- quarantined object bytes;
- failed or aborted ingestion;
- archived bytes;
- objects pending physical deletion;
- objects retained under legal hold or retention rules.

A reservation SHALL be tenant scoped, bounded, time constrained and correlated
to one exact ingestion intent.

Outstanding reservations SHALL consume admission capacity so concurrent
ingestions cannot spend the same remaining capacity twice.

Reservation creation is not usage consumption.

Reservation consumption is not payment, billing, settlement or plan mutation.

Release, expiry, reconciliation and consumption require durable,
concurrency-safe certification before production ingestion is enabled.

## 8. Security controls

Commercial entitlement and security admission are independent.

A tenant with available capacity still SHALL NOT be permitted to ingest
unsupported or unsafe content.

The production upload path must ultimately certify:

- allow-listed content types;
- extension / MIME / magic-byte correlation;
- filename/path traversal rejection;
- bounded streaming;
- decompression/archive-bomb protection if archive formats are enabled;
- malware/quarantine integration before ordinary availability;
- content fingerprint verification;
- immutable tenant/document binding;
- audit/observability;
- rate limiting;
- denial behavior that does not leak confidential matter existence.

## 9. Storage architecture rule

Legal Evidence capacity SHALL NOT be designed around MongoDB single-document
size.

WILSY Legal Evidence uses two architectural planes.

### Mongo control plane

The Mongo control plane owns canonical transactional metadata and WILSY
business evidence, including where separately certified:

- exact tenant / matter / document correlation;
- canonical Legal Evidence identity;
- provider-neutral object evidence references;
- reservation and usage evidence;
- immutable admission and reconciliation evidence;
- Legal workflow correlation;
- retention and legal-hold authority evidence;
- audit and observability correlation.

Mongo SHALL NOT persist the large binary body merely to make metadata
transactional.

### Binary object plane

The binary object plane owns provider execution of durable binary storage.

A provider adapter may create multipart sessions, upload chunks, complete an
object, inspect provider evidence and abort provider work.

The binary object plane SHALL NOT become canonical:

- tenant truth;
- Legal lifecycle truth;
- catalogue or subscription truth;
- commercial-capacity truth;
- IAM truth;
- retention or legal-hold truth;
- Court or Court Online truth;
- payment, execution or settlement truth.

The content persistence architecture must preserve:

- tenant isolation;
- immutable content identity;
- exact replay;
- corruption detection;
- exact provider object-version correlation;
- canonical WILSY SHA3-512 identity;
- atomic metadata/content visibility or a separately certified equivalent
  commit protocol;
- abort/retry safety;
- reconciliation of provider success with metadata failure;
- reconciliation of canonical metadata uncertainty;
- no raw-byte duplication into oversized BSON metadata documents.

### Two-plane commit protocol

The target progression is:

`capacity reservation`
`-> binary write session`
`-> provider object evidence`
`-> canonical integrity verification`
`-> canonical metadata commit`
`-> usage/reservation commit`
`-> authorized availability`

No earlier state implies a later state.

`S3 COMPLETE != LEGAL EVIDENCE COMMITTED`

`PROVIDER OBJECT EXISTS != AUTHORIZED AVAILABILITY`

`MONGO METADATA EXISTS != PROVIDER OBJECT VERIFIED`

The existing L10A2 registry still writes `content_bytes` into Mongo and remains
a migration source, not the target architecture.

Authenticated production multipart/streaming ingestion SHALL remain blocked
until canonical metadata/object-plane orchestration replaces the inline-byte
production write path.

### Canonical integrity versus provider integrity

WILSY SHA3-512 remains the canonical Legal Evidence content identity.

Provider ETag, checksum, version identifier, metadata or other provider
integrity evidence MAY strengthen transport/storage verification but SHALL NOT
replace canonical WILSY SHA3-512 identity.

`PROVIDER CHECKSUM != CANONICAL WILSY SHA3-512 IDENTITY`

### Orphan and reconciliation rule

Multipart sessions and completed provider objects can outlive a failed caller,
network operation or metadata transaction.

Production orchestration therefore requires separately certified:

- bounded write-session lifetime;
- deterministic abort semantics;
- idempotent completion handling;
- orphan discovery;
- provider-object versus metadata reconciliation;
- reservation reconciliation;
- retry safety;
- incomplete multipart cleanup;
- observability and alerting.

Provider-native lifecycle cleanup is defense in depth only. It SHALL NOT replace
WILSY reconciliation evidence.

## 9A. Retention, legal hold and physical deletion

A commercial profile field such as `legal_hold_available` expresses capability
availability only.

It does not prove that a legal hold is active for a tenant, matter, document or
object version.

Canonical retention and legal-hold authority must be represented by separately
certified WILSY evidence. A storage provider may enforce that authority through
provider capabilities but does not become canonical legal-hold authority.

The deletion chain is:

`deletion requested`
`!= retention satisfied`
`!= legal hold cleared`
`!= deletion authorized`
`!= provider deletion executed`
`!= deletion reconciled`

Capacity exhaustion SHALL never imply deletion authorization.

Physical deletion SHALL fail closed when retention, hold, object-version or
reconciliation truth is incomplete.

## 9B. Production storage policy dimensions

Before permanent production Legal Evidence storage is provisioned, WILSY SHALL
separately certify the applicable policy for:

- geographic region / data residency;
- provider account and environment isolation;
- bucket/container ownership;
- public-access prohibition;
- encryption and encryption-key class;
- object versioning;
- archive/lifecycle behavior;
- incomplete multipart cleanup;
- backup / replication / disaster recovery;
- retention enforcement;
- legal-hold enforcement;
- provider event/audit evidence;
- permanent deletion and version cleanup;
- storage economics and capacity-pack behavior.

No browser value, caller-selected bucket, arbitrary provider region or
unverified provider configuration may become canonical policy truth.

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
Founder-class Legal Evidence capacity by explicit concession evidence.

The `FOUNDER_ENTERPRISE` Legal Evidence capacity profile does not alter, infer
or replace base-plan pricing authority.

Founder base-plan price remains owned by canonical PlanRegistry / subscription
truth. Capacity expansion SHALL NOT silently make the Founder base plan
billable.

Separately governed VAS, including WILSY AI and Enterprise Branding, remain
independent unless separately conceded by their own canonical authority.

Zero or concessionary price does not mutate the ordinary commercial catalogue.

## 12. Required certification sequence

The implementation sequence is:

1. **L10A2Q** — architecture / authority map.
2. **L10A2Q-P1** — immutable Legal Evidence capacity contract and canonical
   commercial policy.
3. **L10A2Q-P2** — tenant subscription/profile resolver.
4. **L10A2Q-P3** — immutable Legal Evidence usage observation.
5. **L10A2Q-P4** — remaining-capacity derivation.
6. **L10A2Q-P5** — atomic tenant-scoped capacity reservation, expiry,
   concurrency and reconciliation.
7. **L10A2R** — provider-neutral binary-storage seam, provider adapter and
   canonical Mongo-control-plane/object-plane migration.
8. **L10A2R-RETENTION** — retention, legal-hold, lifecycle, orphan and physical
   deletion authority/enforcement reconciliation.
9. **L10A2R-SECURITY** — malware/quarantine, content admission, rate limiting,
   object-integrity and observability gates.
10. **L10A3D** — authenticated streaming/multipart HTTP ingestion after the
    inline Mongo byte path is no longer the production write path.
11. Client projection / capacity warnings / upgrade opportunity.
12. Authenticated browser, concurrency and negative-boundary certification.
13. Production storage provisioning / residency / encryption / DR certificate.

Already certified lower-layer storage capability does not permit later roadmap
gates to be skipped.

Each step must preserve the governing WILSY OS authority boundaries and
`NO EVIDENCE = NO FACT`.

---

**ARTIFACT:** wilsy-legal-evidence-capacity-and-entitlement-map.md
**VERSION:** v1.1.0-L10A2Q-LEGAL-EVIDENCE-CAPACITY-ENTITLEMENT-MAP
**AUTHORITY BOUNDARY:** architecture/ownership contract only; no commercial, entitlement, IAM, storage or financial authority
**TENANT POSTURE:** exact tenant scope must be supplied by canonical upstream evidence
**FAIL-CLOSED POSTURE:** unknown/missing catalogue, entitlement, subscription, usage or capacity truth blocks admission
**FINANCIAL EXECUTION AUTHORITY:** Kennel EOS exclusively
**END OF WILSY OS SOVEREIGN ARTIFACT**
