# WILSY OS — LEGAL OPERATIONS COMPLETION CAPABILITY MATRIX

VERSION: v1.0.0-LEGAL-OPERATIONS-COMPLETION-MATRIX
AUTHORITY: Wilsy OS Core Governance
EPITOME: Repository-grounded completion map for the Legal Operations & Process
Service Plane, distinguishing current canonical truth, legacy/projection seams,
target sovereign architecture, and the migration order required to close the
vertical without collapsing legal, billing, payment, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/architecture/wilsy-legal-operations-capability-matrix.md
COLLABORATION / OWNERSHIP: Legal Operations owns process-service operational
truth; SaaS Billing owns invoice truth; Kennel EOS exclusively owns financial
execution; Settlement owns settlement allocation; Ledger owns accounting truth;
client, Storefront, providers, mobile and WILSY AI are projections/capabilities.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: v1.0.0 establishes the post-L7/C1 repository map, names concrete
canonical surfaces, records unresolved authority gaps, and freezes the completion
sequence before further Legal Operations mutation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Architecture evidence only. No customer data,
provider credentials, secrets, payment details, or production legal payloads.
TENANT BOUNDARY: Every target Legal Operations read/write remains exact-tenant
scoped; client, device, provider and header inputs never create tenant authority.
AUTHORITY BOUNDARY: This artifact maps ownership and migration only; it creates
no lifecycle, service, invoice, payment, settlement, IAM, or legal authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial
execution authority. Invoice issuance is not execution and execution is not
settlement.

---

## 1. Constitutional lifecycle

The Legal Operations lifecycle remains:

`INSTRUCTION != DOCUMENT REGISTERED != DOCUMENT RECEIVED != ALLOCATED TO DEPUTY != SERVICE ATTEMPTED != SERVICE COMPLETED != RETURN GENERATED != INVOICE GENERATED != PAYMENT EXECUTED != SETTLED`.

The custody lifecycle remains:

`DOCUMENT REGISTERED != DOCUMENT IN OFFICE != DOCUMENT WITH DEPUTY != DOCUMENT RETURNED TO CLIENT`.

Additional immutable separations:

- `ATTEMPT != SERVICE`.
- `SERVICE COMPLETED != RETURN GENERATED`.
- `RETURN GENERATED != TAX INVOICE`.
- `INVOICE GENERATED != PAYMENT EXECUTED`.
- `PAYMENT EXECUTED != SETTLED`.
- Courier, GPS, device, email, SMS and provider observations are evidence, not self-authenticating legal truth.
- WILSY AI observations and recommendations are not legal command authority.
- Client/browser state is a projection and never canonical lifecycle authority.

---

## 2. Repository-grounded current-state map

| Capability | Current repository surface | Classification | Current evidence / boundary |
|---|---|---|---|
| Lifecycle domain | `tools/eos/legal_operations/domain/legal_operations_lifecycle.py` | CANONICAL | Immutable tenant-scoped `LegalInstruction`, `CaseMatter`, `ProcessDocument`, `District`, `SheriffOffice`, `Deputy`, custody, attempt, execution and return contracts. |
| Lifecycle persistence | `tools/eos/legal_operations/registry/legal_operations_lifecycle_registry.py` | CANONICAL | Immutable P1 snapshot persistence and strict hydration; caller owns transaction. No generic current pointer exists. |
| Assignment authority | `process_service_assignment_authority.py` | CANONICAL | Requires accepted instruction and received document before allocation. |
| Allocation | `process_service_allocation_orchestrator.py` + allocation registry | CANONICAL | P4 allocation, custody progression and dedicated current-pointer/CAS evidence. |
| Attempt authority | `process_service_attempt_authority.py` + registry | CANONICAL | Durable allocation-to-attempt authority handoff. |
| Attempt lifecycle | attempt orchestrator + transition/outcome authorities/registries | CANONICAL | Initial attempt, attempted transition, terminal service/non-service outcome and execution factory evidence. |
| Mobile/offline field evidence | field-evidence authority, registry, orchestrator and projection | CANONICAL / PROJECTION | Mobile observations are journal evidence only and cannot create service or financial truth. |
| Return of service | return authority, registry and orchestrator | CANONICAL | Return derives only from certified service execution. |
| Tariff assessment | tariff authority + registry | CANONICAL | Versioned tariff assessment evidence; no quotation/invoice/payment authority. |
| Billing eligibility | billing-eligibility authority + registry | CANONICAL | Completed/return-backed eligibility only; no invoice/payment/settlement authority. |
| Client billing authority | `tools/eos/saas/billing/process_service_client_billing_authority.py` | CANONICAL COMMERCIAL BRIDGE | Legal evidence is converted into bounded billing authority without moving money. |
| Invoice handoff / issuance | process-service invoice handoff, issuance and registry | CANONICAL BILLING | Billing owns invoice truth; Legal Operations does not. |
| Legal read HTTP | `tools/eos/api/legal_operations_router.py` | EMERGING CANONICAL | Authenticated tenant-scoped reads for instruction, attempt, execution and return. Current-snapshot selection is not durably explicit. |
| Legal command HTTP | `tools/eos/api/legal_operations_command_router.py` | EMERGING CANONICAL | Allocation, attempt, attempt transition/outcome and return commands exist. No instruction-registration/document-receipt command was found. |
| Billing read HTTP | `legal_operations_billing_read_router.py` | EMERGING CANONICAL | Tariff, billing-eligibility and invoice projections. |
| Legal IAM | `tools/eos/auth/permission_namespace.py`, `roles.py` | CANONICAL CONTROL | Legal read/write permissions exist, including `legal_operations:instruction:write`; no production instruction-write route currently consumes that capability. |
| WILSY AI legal read tools | legal AI gateway/read adapter/tool registry | PROJECTION / INTELLIGENCE | Seven read-only canonical Legal Operations tools; no command authority. |
| WILSY AI legal advisory | `legal_operations_advisory_adapter.py` | PROJECTION / INTELLIGENCE | Deterministic review-only next-best-action advisory bound to canonical evidence. |
| Intelligence Dock client | `client/src/components/intelligence/WilsyOSIntelligenceDock.jsx` | CLIENT PROJECTION | Legal-services/advisory UI exists; no legal mutation authority. |
| Sheriff/process-service client | `client/src/components/industry/LegalDashboard.jsx` | LEGACY / MIGRATION SOURCE | Rich sheriff-office requirements are represented, but no canonical Legal Operations API consumption was found in this component. |
| General legal client | `client/src/components/legal/LegalDashboard.jsx`, `client/src/services/legalService.js` | LEGACY / OVERLAPPING | Contract/compliance/risk/IP/policy dashboard targets legacy `/legal/*` resources and browser-supplied tenant headers; it is not the process-service canonical client. |
| Node sheriff controller/routes | `server/controllers/sheriffController.js`, `server/routes/sheriffRoutes.js` | LEGACY / REQUIRES FORENSICS | Exists outside Python EOS sovereign process-service authorities; must not become duplicate lifecycle truth. |
| Courier integration | no production Legal Operations implementation found | UNKNOWN / GAP | Constitution names courier as external evidence/capability; no canonical adapter/evidence path was found. |
| Notifications | no production Legal Operations notification implementation found | UNKNOWN / GAP | Return-ready/invoice/custody notifications remain unwired. |
| Storefront Legal Operations | no Legal Operations Storefront implementation found | UNKNOWN / GAP | Storefront is required as a public projection only; it must not own instruction/billing truth. |
| Search/indexing | no canonical case/client/process-service search authority found | UNKNOWN / GAP | Current constitution requires case/client search; query/index ownership remains to be created or mapped. |
| Files/uploads | no canonical Legal Operations file/evidence attachment authority mapped in this campaign | UNKNOWN / GAP | Uploaded process documents and annexures need explicit provenance and tenant-safe file authority. |
| District/office/deputy provisioning | no production constructors/writers found outside P1 domain/registry | GAP | Allocation consumes these canonical identities, but no production provisioning command/authority was found. |
| Instruction registration | P1 domain + P2 persistence exist; no production constructor/orchestrator found | GAP | Tests seed `LegalInstruction` directly; runtime ingress is absent. |
| Case/matter registration | P1 domain + P2 persistence exist; no production constructor/orchestrator found | GAP | Runtime case/matter ingress is absent. |
| Process-document registration | P1 domain + P2 persistence exist; no production constructor/orchestrator found | GAP | Runtime document ingress is absent. |
| Document receipt / office custody | P1 transition and custody contracts exist; no production receipt orchestrator found | GAP | P3/P4 require `RECEIVED` plus `RECEIVED_IN_OFFICE`, but runtime creation path is absent. |
| Client projection policy | L7A explicitly denies `tenant_legal_client` | INTENTIONAL FAIL-CLOSED GAP | Client-facing bounded projection policy must be authored before clients can read internal lifecycle views. |
| Current lifecycle projection | P2 stores history; L7A resolves one row by entity identity | REQUIRES HARDENING | Multi-snapshot entities can have more than one durable row; a current-snapshot authority/projection must be explicit and deterministic. |
| Kennel EOS payment execution | `tools/eos/kennel` | CANONICAL FINANCIAL EXECUTION | Legal Operations and Billing may hand off evidence but cannot execute funds. |
| Settlement allocation | settlement plane | CANONICAL FINANCIAL EVIDENCE | Payment execution must not be treated as settlement. |
| Ledger/accounting | accounting/ledger plane | CANONICAL ACCOUNTING | Legal invoice/service evidence cannot manufacture postings. |
| Tenant/identity | canonical auth/tenant repositories and RequireTenantAuthorization | CANONICAL CONTROL | X-Tenant-ID is scope input only and becomes usable only through current durable authorization. |
| Subscription/entitlement | SaaS entitlement and WILSY AI entitlement surfaces | CANONICAL / EMERGING CANONICAL | Entitlements gate capability; they do not create legal lifecycle facts. |
| CI/governance | root `AGENTS.md`, workflows, direct/HTTP/real-Mongo certificates | CANONICAL CONTROL PLANE | No unexecuted test or unavailable local infrastructure may be represented as passing evidence. |

---

## 3. Connection matrix

| Producer / authority | Consumer | Contract carried | Forbidden inference |
|---|---|---|---|
| Tenant/IAM | Legal HTTP command/read routers | current principal + membership + role + exact tenant permission | Header/JWT claim alone is not tenant authority. |
| P1 lifecycle | P2 registry | immutable lifecycle snapshot + SHA3-512 fingerprint | Persistence cannot invent transitions. |
| P2 instruction/document/directory evidence | P3 assignment | exact accepted/received/current source evidence | Registration is not receipt; receipt is not assignment. |
| P3 assignment | P4 allocation | assignment decision + canonical P1 source facts | Assignment does not create an attempt. |
| P4 allocation | P5 attempt authority | allocation receipt/current evidence | Allocation does not prove an attempted service. |
| P5 field evidence | P5 transition/outcome | validated observation/evidence fingerprint | GPS/photo/device observation is not service completion. |
| P5 terminal attempt | ServiceExecution factory | exact terminal evidence | Attempted does not equal served. |
| ServiceExecution | ReturnOfService factory | certified outcome + chronology | Service does not imply a generated return. |
| Return + tariff | Billing eligibility | legal/commercial evidence | Return/tariff do not create invoice truth. |
| Billing eligibility | Client billing / invoice issuance | exact bounded authority | Eligibility does not execute payment. |
| Invoice | Kennel EOS | payable/receivable execution request via approved financial boundary | Invoice is not execution or settlement. |
| Canonical reads | WILSY AI | allowlisted transient projection + invocation evidence | AI result/recommendation is not command authority. |
| Canonical reads | Client dashboards | bounded projection | Client state cannot become durable truth. |
| Courier/mobile/providers | Legal evidence adapters | provider observation + provenance | Provider status is not legal completion. |
| Legal lifecycle | Notifications | event trigger/projection | Notification delivery cannot mutate lifecycle. |
| Storefront | Tenant genesis / Legal intake | public intent only | Storefront form submission is not accepted instruction truth. |

---

## 4. Critical gaps that block a complete Legal Operations vertical

### G0 — Current-state projection authority
P2 intentionally stores immutable history and does not expose a generic current
pointer. L7A currently locates a row by tenant/entity type/entity identity before
hydrating by evidence identity. Multi-snapshot entities therefore require an
explicit current-state projection rule or durable current authority. Arbitrary
row selection is not acceptable sovereign truth.

### G1 — Directory provisioning
`District`, `SheriffOffice`, and `Deputy` are canonical P1 values consumed by
assignment/allocation, but no production provisioning authority or command path
was found. Test seeding is not runtime architecture.

### G2 — Intake registration
No production orchestrator/command was found that constructs and persists the
initial `CaseMatter`, `LegalInstruction`, `ProcessDocument`, and first
`DocumentCustodyEvent.REGISTERED` evidence under one governed transaction.

### G3 — Acceptance and receipt
No runtime authority was found for the distinct transitions:
- instruction REGISTERED -> ACCEPTED;
- document REGISTERED -> RECEIVED;
- custody REGISTERED -> RECEIVED_IN_OFFICE.

These transitions must remain separate from allocation and require concurrency-
safe current-state evidence.

### G4 — Client parity
The active sheriff/process-service dashboard is not wired to the canonical
Python Legal Operations APIs. The general legal dashboard is a separate legacy
legal-management surface. Canonical backend truth therefore lacks an end-user
process-service projection.

### G5 — Client-facing projection policy
`tenant_legal_client` is intentionally denied by L7A. A separate bounded
client/law-firm visibility policy is required rather than exposing internal
sheriff-office projections.

### G6 — Courier, notifications and files
Courier, return-ready notifications, invoice notifications, document uploads
and annexure/file provenance are constitutionally required but not yet mapped
to certified production adapters.

### G7 — Storefront/legal acquisition
The Storefront has no mapped Legal Operations acquisition/intake projection.
Public submission must remain intent until canonical tenant/identity and Legal
Operations admission gates succeed.

### G8 — Search and operational queues
Case/client search, office receipt queue, deputy queue, urgent/same-day queue,
return queue and billing-readiness queue need canonical read models derived
from owned truth rather than client-local filtering.

### G9 — End-to-end observation
Existing unit, HTTP and real-Mongo certificates cover many backend slices, but
the whole path from authenticated intake -> receipt -> allocation -> attempt ->
field evidence -> outcome -> return -> billing eligibility -> invoice projection
-> Kennel handoff is not yet represented as one closed, zero-skip campaign.

---

## 5. Target sovereign architecture

### 5.1 Canonical write path

`authenticated tenant authority`
-> `Legal Operations intake command`
-> `case/matter + instruction + process-document registration evidence`
-> `instruction acceptance authority`
-> `document receipt/custody authority`
-> `assignment authority`
-> `allocation current/CAS`
-> `attempt authority`
-> `offline/mobile evidence journal`
-> `attempt transition/outcome`
-> `ServiceExecution`
-> `ReturnOfService`
-> `TariffAssessment`
-> `BillingEligibility`
-> `ClientInvoice issuance`
-> `Kennel EOS execution request/evidence`
-> `settlement allocation`
-> `ledger/accounting projection`.

Each arrow is a separately evidenced authority boundary.

### 5.2 Canonical read path

Canonical registries
-> deterministic current/history projection
-> authenticated role-specific API
-> sheriff/deputy/law-firm/client dashboards
-> Intelligence Dock/WILSY AI read tools
-> observability/analytics.

No consumer may select an arbitrary historical row and call it current truth.

### 5.3 External evidence path

Mobile device / courier / mapping / email / SMS / file store
-> adapter
-> normalized observation/evidence
-> canonical authority validates whether the evidence permits a lifecycle
transition.

Provider success never directly writes legal completion, payment or settlement.

---

## 6. Completion sequence

The remaining campaign MUST execute in this order unless a later forensic gate
proves the dependency graph different.

| Gate | Primary objective | Why it precedes the next gate |
|---|---|---|
| L8-0 | Current-state projection authority and divergence detection | Reads, AI and future clients must never surface arbitrary historical truth. |
| L8-1 | District / SheriffOffice / Deputy provisioning authority | Assignment/allocation require canonical directory identities. |
| L8-2 | Case / instruction / document registration orchestration | Establishes the runtime beginning of the lifecycle. |
| L8-3 | Instruction acceptance + document receipt/custody orchestration | Produces the exact P3 prerequisites without collapsing states. |
| L8-4 | Intake/directory authenticated command API | Makes canonical authorities reachable without browser-owned truth. |
| L8-5 | Read models: current/history, queues and search | Gives operational consumers deterministic projections. |
| L8-6 | Sheriff/deputy client migration | Wires the active Legal dashboard to canonical APIs and removes client-local truth. |
| L8-7 | Law-firm/client bounded projection policy | Exposes only authorized client-visible evidence. |
| L8-8 | Files, courier and notification adapters | Adds external capability as evidence/projection only. |
| L8-9 | Storefront legal-intake projection | Connects public intent to authenticated tenant/legal admission without becoming authority. |
| L8-10 | Intelligence/observability expansion | Adds queue analytics, SLA signals and advisory provenance from canonical reads. |
| L8-11 | Whole-path real-Mongo + HTTP + client certification | Proves the complete vertical with no skipped launch-critical gates. |
| L8-12 | Legacy cleanup | Retires/quarantines Node sheriff and overlapping client legal paths only after replacement proof. |

---

## 7. Mandatory certification matrix

Every production gate must state which evidence actually ran.

| Evidence class | Minimum requirement |
|---|---|
| Static | syntax/compile plus bounded type/static analysis |
| Direct | adversarial unit certificate for authority, replay, corruption, tenant and transaction boundaries |
| Persistence | real Mongo when durable truth or concurrency is changed |
| HTTP | mounted API proof for authentication, tenant isolation and bounded error semantics |
| Concurrency | deterministic conflict/CAS proof where a current pointer or transition race exists |
| Client | browser/component/API transport proof without client-owned authority |
| Observation | telemetry/Intelligence projections bound to committed canonical evidence |
| Financial boundary | explicit proof that no Legal Operations component manufactures execution or settlement |

Skipped infrastructure is `NOT CERTIFIED`, never PASS.

---

## 8. Cleanup constraints

The following may not be deleted merely because a canonical replacement is
planned:

- `server/controllers/sheriffController.js`;
- `server/routes/sheriffRoutes.js`;
- `client/src/components/industry/LegalDashboard.jsx`;
- `client/src/components/legal/LegalDashboard.jsx`;
- `client/src/services/legalService.js`.

They remain migration/forensic surfaces until callers, routes, tests, user
journeys and rollback paths prove replacement. Cleaning occurs only at L8-12.

---

## 9. Completion definition

Legal Operations is complete only when all of the following are simultaneously
true:

1. A real authenticated tenant can create the beginning of the process-service
   lifecycle without direct database seeding.
2. Registration, receipt, allocation, attempt, service, return, invoice,
   payment execution and settlement remain distinct authorities.
3. District/office/deputy authority is durable and tenant scoped.
4. Current-state reads are deterministic and corruption/divergence fails closed.
5. Sheriff/deputy and law-firm/client surfaces consume canonical APIs.
6. Mobile/offline, courier, files and notifications are adapters/evidence only.
7. Storefront intake is public intent, not legal truth.
8. WILSY AI and Intelligence Dock observe/recommend only from canonical evidence.
9. Billing owns invoice truth and Kennel EOS exclusively owns financial execution.
10. Whole-path certification passes static, direct, HTTP, real-Mongo,
    concurrency and client gates with no launch-critical skips.
11. Legacy duplicate paths are either retired or explicitly quarantined.
12. Main, operating branch and local checkout reconverge after protected merge.

---

## 10. Immediate next bounded gate

**L8-0 — Legal Operations Current-State Projection Authority**

Primary objective: remove arbitrary lifecycle-history row selection from
canonical Legal Operations reads before creating new runtime intake paths.

Required discovery before mutation:

- P2 immutable history/index semantics;
- all L7A callers;
- WILSY AI read-adapter callers;
- direct HTTP and real-Mongo certificates;
- history divergence/corruption behavior;
- whether a durable generic current pointer already exists elsewhere.

No production file beyond the single frozen primary artifact may be modified in
one certified delivery.

---

# SOVEREIGN ARTIFACT SEAL

ARTIFACT: wilsy-legal-operations-capability-matrix.md
VERSION: v1.0.0-LEGAL-OPERATIONS-COMPLETION-MATRIX
AUTHORITY BOUNDARY: architecture discovery/map only; no runtime authority
TENANT POSTURE: all target capabilities remain exact-tenant scoped
FAIL-CLOSED POSTURE: unknown ownership, ambiguous current truth and unexecuted
certification remain blockers rather than inferred success
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
END OF WILSY OS SOVEREIGN ARTIFACT
