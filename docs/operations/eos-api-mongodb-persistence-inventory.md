# EOS API MongoDB Persistence Inventory — Source-Level Baseline

**Status:** preliminary source-composition inventory; not a deployed-runtime CRUD certification  
**Repository revision reviewed:** `eos/tenant-discovery-iam-dashboard-roadmap` at `c1d22f6ea5807ab10229017c397980031ed24020`  
**Primary source:** `tools/eos/api/server.py`, `tools/eos/kernel/db.py`

## Purpose and safety boundary

This inventory advances the runtime-role design without assuming which Atlas project or cluster is production. It describes the checked-in FastAPI composition root and startup persistence bootstrap. It does not prove that this revision, image digest, or any particular database is running in production. No database credentials, users, roles, network rules, or deployments were changed.

The exact deployed host, image digest, secret-manager object reference/version, and Atlas cluster binding remain unverified. Do not use this document as authority to rotate credentials or grant a role.

## Connection authority

The EOS kernel resolves `MONGODB_URI` as its sole MongoDB URI authority. It constructs a PyMongo `MongoClient`, pings the server, and selects the database embedded in the URI. The canonical API lifecycle calls `connect_db()` at startup and `disconnect_db()` at shutdown. Production mode is recognized from either `WILSY_ENV` or `ENV` with value `production` or `prod`; repository dotenv loading is disabled in that mode.

The URI value itself must never be copied into tickets, logs, CI output, or this inventory. For host/database matching, use a controlled, non-reversible fingerprint produced inside the secret-owning runtime or approved deployment tooling. Do not expose username, password, query parameters, or full connection strings.

## Collections explicitly referenced by API composition

The following names are visible as direct collection references in the server composition/startup code. Constant-backed names must be resolved from their defining modules before a final policy is generated.

| Collection / constant source | Composition-time purpose | Preliminary implication |
|---|---|---|
| `system_service_cases` | System Services case registry index bootstrap | Startup index DDL; request CRUD must be traced in case registry/router |
| `system_service_case_events` | System Services case event index bootstrap | Startup index DDL; event append/read paths require tracing |
| `PRINCIPAL_CREDENTIAL_COLLECTION` | Global principal credential repository indexes | Auth read/write paths require exact repository audit |
| `MEMBERSHIP_SELECTION_CHALLENGE_COLLECTION` | One-time membership/MFA challenge indexes | Challenge issue/consume/read operations |
| `GLOBAL_PRINCIPAL_SESSION_COLLECTION` | Global session indexes | Session create/read/revoke operations |
| `GLOBAL_PRINCIPAL_REFRESH_COLLECTION` | Refresh token indexes | Refresh create/rotate/revoke operations |
| `GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION` | TOTP factor indexes and verifier | Factor read/update operations |
| `GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION` | MFA enrollment challenge indexes | Enrollment challenge create/consume/update |
| `PRINCIPAL_AUTH_RATE_LIMIT_COLLECTION` | Durable authentication rate-limit indexes | Rate-limit read/upsert/update operations |
| `wilsy_sovereign_telemetry` | Unique sparse `trace_id` index | Startup index DDL; ingestion CRUD must be traced |
| `TENANT_AUTHORIZATION_DECISION_EVIDENCE_COLLECTION` | Authorization decision evidence indexes | Append/read evidence paths |
| `AUTHORIZATION_ROLE_REVOCATION_EVIDENCE_COLLECTION` | Role revocation evidence indexes | Append/read evidence paths |
| `PRIVILEGED_FACTOR_CURRENTNESS_COLLECTION` | Privileged factor currentness indexes | Read/write currentness paths |
| `INTERNAL_SERVICE_REPLAY_COLLECTION` | Internal-service replay indexes | Replay lookup/insert/update paths |
| `INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_COLLECTION` | Workload credential indexes | Credential lookup/rotation/revocation paths |
| `INTERNAL_SERVICE_WORKLOAD_CREDENTIAL_POINTER_COLLECTION` | Workload credential pointer indexes | Pointer lookup/update paths |
| `PRIVILEGED_WORKLOAD_TRUST_CURRENTNESS_COLLECTION` | Workload trust currentness indexes | Read/write currentness paths |
| `PRIVILEGED_NONINTERACTIVE_SECURITY_PROOF_COLLECTION` | Noninteractive security proof indexes | Proof lookup/append/consume paths |
| `PRIVILEGED_SECURITY_ASSURANCE_EVIDENCE_COLLECTION` | Security assurance evidence indexes | Evidence append/read paths |
| `DEPUTY_PRINCIPAL_BINDING_COLLECTION` | Deputy-principal binding indexes | Binding read/write paths |
| `LOCATION_PERMISSION_COLLECTION` | Process-service location permission indexes | Permission read/write/revoke paths |
| `LOCATION_OBSERVATION_COLLECTION` | Process-service location observation indexes | Observation append/read paths |
| `LOCATION_REVOCATION_COLLECTION` | Process-service location revocation indexes | Revocation append/read paths |
| `LOCATION_ACCESS_AUDIT_COLLECTION` | Process-service location audit indexes | Audit append/read paths |
| `LEGAL_STOREFRONT_PUBLIC_INTENT_COLLECTION` | Public intent indexes | Public intent create/read/update lifecycle |
| `LEGAL_STOREFRONT_PUBLIC_INTENT_RATE_LIMIT_COLLECTION` | Public intent rate-limit indexes | Rate-limit read/upsert/update paths |
| `legal_practitioner_matter_access_evidence` | Practitioner-matter access evidence indexes | Access evidence append/read paths |
| `p12c_binding_registry.COLLECTION_NAME` | Practitioner-matter binding indexes | Binding read/write paths |
| `p12c_disposition_registry.COLLECTION` | Client-matter conflict disposition indexes | Disposition read/write paths |
| `C1C_ORCHESTRATION_COLLECTION` | Conditional AI orchestration root indexes | Only when reasoning provider is configured |
| `wilsy_ai_legal_tool_invocations` | AI tool invocation evidence create/replay | Conditional accounting transaction write/read |
| `ENTITLEMENT_COLLECTION` | AI entitlement lookup | Conditional accounting transaction read |
| `OBSERVATION_COLLECTION` | AI usage capacity and observation | Conditional accounting transaction read/write |

**Important:** the constants above are not assumed to equal their symbolic names. Resolve each constant to its literal collection name and trace its repository implementation before producing Atlas custom-role statements. This table is a bootstrap reference list, not a complete inventory of every collection used by every mounted router.

## Additional database authority

The Legal Evidence provider read-only reconciliation runtime is composed separately after the primary database connects. Its builder receives the primary database and returns a distinct audit client. The composition root verifies that its business client is the same primary client and closes the audit client on mismatch. The builder must be inspected to establish the separate audit URI source, target, and exact read/write operations. Do not merge this audit connection into the primary EOS runtime role by assumption.

## Startup DDL finding

The API startup path directly calls multiple `ensure_indexes()` methods and at least one direct `create_index()` on `wilsy_sovereign_telemetry`. Therefore, the current API startup contract includes index-creation authority on the collections listed above (and possibly additional collections hidden inside ensure-index implementations).

This is a material least-privilege design issue. Preferred target: move index DDL to a separately governed deployment/provisioning job, certify the complete index manifest, and remove index creation from the application runtime. Until that migration is implemented and tested, a runtime role that cannot create indexes may cause startup to fail or leave readiness flags false. Do not simply grant broad database-wide index privileges as a workaround.

## Mounted API surface

The composition root mounts kernel, tenant, authentication/global-principal authentication, billing, employee, subscription/plan, System Services, telemetry, HR documents, Legal Operations, Legal Evidence upload/reconciliation, Legal Client Acceptance, Legal Matter Deadline, Legal Operating Model, Legal Storefront public intent, tenant branding, legal practitioner-matter binding, AI gateway/reasoning/advisory/services, and authority-bridge routers.

A mounted router is not proof that all its operations are enabled in a given deployment. Optional providers and deployment configuration gate some paths. The deployed route inventory must be captured from the exact production image/configuration after the host is identified.

## Required next certification work

1. Resolve every collection constant to its literal name.
2. Trace each mounted router -> service -> repository -> PyMongo operation, including bulk writes, transactions, change streams, GridFS, and index creation.
3. Separate API runtime, worker/scheduler, reconciliation audit, migration/index-provisioning, operator, and CI/test identities.
4. Produce a collection/action matrix from code, then validate it against the deployed image and observed command telemetry in a controlled window.
5. Move startup DDL to a separately authenticated provisioning step, or document and test the exact minimum startup permissions if migration is not yet possible.
6. Only after the live host, secret reference, and Atlas cluster are fingerprint-matched, create a custom role in a non-production project and certify representative API journeys, denied out-of-scope operations, rollback, and restore.

## Current decision

**NO-GO for production role creation, user replacement, credential rotation, or allow-list changes.** The deployed host/secret/cluster chain and complete operation matrix are not yet proven.
