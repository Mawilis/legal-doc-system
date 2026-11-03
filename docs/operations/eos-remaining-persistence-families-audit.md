# EOS Remaining Persistence Families — Source Audit Tranche

**Repository:** `Mawilis/legal-doc-system`  
**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Status:** source-level inventory of the inspected repositories and composition excerpts; incomplete API-wide operation matrix  
**Production posture:** NO-GO for credential, role, or network changes

This tranche records literal collection names and source-observed operations where they were verified. It deliberately leaves unresolved collection names and route reachability explicit rather than guessing.

## 1. System Services case registry — unresolved exact repository mapping

The earlier server composition inventory identified startup index creation for `system_service_cases` and `system_service_case_events`. The current source retrieval in this tranche did not resolve the registry implementation path or its complete CRUD methods. Therefore this document does **not** assign application actions or propose a role for either collection.

Required follow-up: locate the case-registry module and event registry from the current branch's imports, resolve exact index keys/options, trace the case router/service to repository methods, and determine whether event writes are append-only. Keep case and event collections distinct in the role design. Do not infer write permissions from their names.

## 2. Privileged authorization and workload evidence

The following literal collections were verified from repository constants or declarations:

| Collection | Source owner | Operations observed | Design note |
|---|---|---|---|
| `tenant_authorization_decision_evidence` | `tenant_authorization_decision_evidence_registry.py` | `find_one` by tenant/decision identity and idempotency key; `insert_one` | Caller-owned transaction; tenant-scoped durable decision evidence |
| `privileged_factor_verification_currentness` | `privileged_factor_verification_currentness_registry.py` | `find_one`; `insert_one`; `update_one` | Currentness lifecycle; not interchangeable with historical evidence |
| `privileged_workload_trust_currentness` | `privileged_workload_trust_currentness_registry.py` | `find_one`; `insert_one`; `update_one` | Workload trust currentness |
| `internal_service_replay_nonces` | `internal_service_replay_registry.py` | `insert_one` with unique replay identity | TTL expiry index; replay reservation is an atomic write |
| `internal_service_workload_credential_authority_history` | `internal_service_workload_credential_registry.py` | `find_one`; `insert_one` | Immutable credential lifecycle history; no raw HMAC secrets |
| `internal_service_workload_credential_authority_current` | same | `find_one`; `insert_one`; CAS `replace_one` | One current pointer per service/key |
| `privileged_noninteractive_security_proofs` | `privileged_noninteractive_security_proof_registry.py` | `find_one`; `find`; `insert_one` | Append/replay proof evidence; exact collection name is from server's imported constant? See caveat below |
| `privileged_security_assurance_evidence` | `privileged_security_assurance_evidence_registry.py` | `find_one`; `insert_one` | Historical assurance evidence |
| `authorization_role_revocation_evidence` | `authorization_role_revocation_evidence_registry.py` | `find_one`; `insert_one` | Immutable revocation evidence |

**Collection-name caveat:** the exact strings for the noninteractive proof, assurance evidence, and role-revocation registries should be read from their `COLLECTION` declarations on the target revision before a provisioning manifest is emitted. The symbolic names above are descriptive and are not a substitute for resolving those declarations.

The internal-service workload credential registry has two explicit collections. Its index contract is five indexes across history and current pointer: unique service/key/credential-revision/lifecycle-revision; unique authority fingerprint; service/key timeline; unique service/key current pointer; and principal/scope lookup. This is a distinct authority family and must not be mixed into tenant-facing API grants without route/worker reachability proof.

## 3. Legal Storefront public intent

The server imports `LEGAL_STOREFRONT_PUBLIC_INTENT_COLLECTION` from `tools.eos.legal_operations.registry.legal_storefront_public_intent_registry` and invokes its index bootstrap after primary database connection. The public intent router is mounted at `/api/legal-storefront/public-intents`.

The registry implements `find_one` replay/identity lookups and `insert_one` for immutable create-or-replay. Its index installer creates deterministic indexes. A separate public-intent rate-limit collection is also bootstrapped in the server composition; its exact collection literal and operation set must be resolved from its registry before role generation.

This is an anonymous ingress surface, but anonymous HTTP access does not mean anonymous database credentials. Requests are still mediated by the EOS application runtime.

## 4. Practitioner/matter binding and conflict-disposition evidence

Verified literal collection names:

| Collection | Source | Operations observed | Index contract |
|---|---|---|---|
| `legal_practitioner_matter_access_evidence` | `legal_practitioner_matter_access_registry.py` | tenant-scoped `find_one`; `insert_one` append; replay/scope reads | Unique tenant/access-evidence identity; unique tenant/matter/practitioner/revision; unique tenant/fingerprint |
| `legal_practitioner_matter_bindings` | `legal_practitioner_matter_binding_registry.py` | bounded `find` history read; `insert_one` append; current-binding resolution | Unique tenant/binding/status snapshot; unique tenant/fingerprint; unique active tenant/matter/practitioner partial index |
| `legal_client_matter_conflict_dispositions` | `legal_client_matter_conflict_disposition_registry.py` | tenant-scoped `find` bounded history; `insert_one` immutable evidence | Multiple tenant-scoped identity, fingerprint, idempotency, review-lineage and history indexes |

These repositories require caller-owned active transactions. Their records are documentary evidence, not IAM grants, content authorization, ethical-wall waivers, or legal currentness decisions. The access and binding collections must remain distinct. Do not add destructive delete permissions where the source exposes append-only evidence.

The server imports the access, binding and conflict-disposition registries and installs their indexes during canonical startup. This is another concrete reason to separate provisioning/index DDL from the request-serving identity.

## 5. AI orchestration, invocation, entitlement and usage

Verified literal collections:

| Collection | Source | Operations observed | Design note |
|---|---|---|---|
| `wilsy_ai_tool_orchestrations` | `ai_tool_orchestration_registry.py` | `find_one`, `insert_one`, revision-guarded `replace_one` | C1C orchestration state; startup index bootstrap is conditional on reasoning provider/database/client |
| `wilsy_ai_legal_tool_invocations` | `legal_ai_tool_invocation_registry.py` | tenant-scoped `find_one`, `insert_one` create-or-replay | Durable invocation evidence; transaction supplied by caller |
| `wilsy_ai_entitlements` | `wilsy_ai_entitlement_registry.py` | `find_one`, `insert_one`, revision-guarded `update_one` | Tenant/module entitlement authority; not a general IAM role |
| `wilsy_ai_usage_observations` | `wilsy_ai_usage_observation_registry.py` | tenant-scoped `find_one`, bounded `find`, `insert_one` append/replay | Append-only source-evidenced usage; no billing/financial execution authority |

The entitlement registry defines unique tenant/entitlement, tenant/module, and tenant/idempotency indexes. The usage-observation registry defines unique tenant/observation, unique tenant/idempotency, and tenant/time plus tenant/entitlement/module/time lookup indexes.

The AI invocation accounting callback composes entitlement lookup, usage capacity derivation, invocation evidence persistence and usage observation persistence within a caller-owned session. AI orchestration index installation is conditional on the reasoning provider being configured; therefore the deployed configuration determines whether that collection is part of the live API runtime contract. AI billing/entitlement and usage routes also compose these registries separately. Do not assume all AI routes share one static collection set.

## 6. Separate Legal Evidence reconciliation audit connection

This is a distinct MongoDB connection, not merely another collection in the primary EOS database.

Verified runtime configuration:
- Audit URI environment variable name: `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI`.
- Optional role ARN environment variable: `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AWS_ROLE_ARN`.
- Allowed ambient credential methods in the runtime source include `assume-role-with-web-identity` and `container-role`.
- Runtime parser derives a credential-free deployment identity from SRV FQDN or direct hosts and replica-set metadata.
- `mongo_deployment_fingerprint(uri)` fingerprints deployment identity without database name or credentials.
- `audit_target_fingerprint(uri)` includes deployment identity and database name, still without credentials.
- `require_distinct_mongo_deployments(business_uri, audit_uri)` rejects identical business and audit deployment identities.
- Production composition requires the audit database's client to be distinct from the business database client.
- The production composition has a dedicated `PlatformAuthorizationDecisionEvidenceIndexProvisioner`; it explicitly describes deployment-only index provisioning with a distinct audit client.
- Runtime composition verifies provisioned audit indexes read-only; it does not provision them during request composition.

This establishes a strong architectural separation, but not the live deployed audit secret object, actual AWS role, runtime credential method, audit database, Atlas project/cluster, or effective permissions. Those must be proven from deployment metadata without retrieving secret values.

**Identity implication:** the audit workload requires a separate runtime identity and separately governed index-provisioning identity. Do not give the primary EOS API credential write access to the audit database merely because the composition root passes both databases into a builder.

## 7. Route reachability and remaining audit gaps

The source composition confirms mounts for global auth, tenant/auth, System Services, authorization revocation, Legal Storefront, practitioner/matter binding, AI gateway/reasoning/legal services/advisory, telemetry, Legal Evidence upload and Legal Evidence read-only reconciliation. A mounted router does not prove every route is enabled in a given deployment.

Outstanding work before the matrix is complete:

1. Resolve the System Services case/event registry module and exact literal collection names, methods and indexes.
2. Resolve exact `COLLECTION` strings for every privileged evidence registry and the public-intent rate-limit registry.
3. Resolve the legacy MFA factor source collection and migration-only access.
4. Trace every mounted router -> dependency -> service -> repository, including helper functions that open their own sessions or call `get_database()`.
5. Inventory background tasks, schedulers, reconciliation workers, CLI/operator tools and migration entrypoints independently from the API.
6. Complete the Legal Evidence audit-side collection/action matrix and identify the audit database's separate secret reference and workload identity.
7. Capture the exact deployed image digest, runtime configuration and route/provider gates; compare those to this source revision.
8. Validate the candidate role in non-production with positive API journeys and negative tests for out-of-scope database/collection operations.
9. Extract startup index definitions into a versioned manifest and separately authenticated, idempotent provisioning job. The application runtime should not create indexes.

## Decision

This tranche resolves additional source families but is not a complete collection/action matrix. **NO-GO** remains for production runtime-role creation, user replacement, credential rotation, or Atlas network changes. The live EOS host, secret-manager reference, Atlas project/cluster binding, and effective workload identity remain unproven. No production secret values, database data, users, roles, access lists, cloud roles, or deployments were changed.
