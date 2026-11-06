# EOS route, Legal Evidence, practitioner and AI persistence audit — tranche 5

**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Source revision:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Status:** partial source-level route closure; not a final runtime role contract  
**Production changes:** none

## 1. Legal Evidence upload route -> orchestrator -> registry closure

Mounted route:
- `POST /api/legal-evidence/documents/{document_id}`
- Router: `tools/eos/api/legal_evidence_upload_router.py`
- Orchestrator: `tools/eos/legal_operations/service/legal_evidence_upload_orchestrator.py`
- Binary provider adapter: `tools/eos/legal_operations/service/legal_evidence_s3_storage_adapter.py`

The orchestrator composes six durable registries and calls their `ensure_indexes()` methods during construction. These are runtime-path DDL calls and must be removed only after an independently governed provisioner has installed the complete source-matched manifest and runtime performs read-only verification.

| Collection | Registry | Observed Mongo operations | Indexes |
|---|---|---|---|
| `legal_evidence_capacity_admission_fences` | `legal_evidence_capacity_admission_fence_registry.py` | `find_one`, `insert_one`, `find_one_and_update` | Unique tenant fence |
| `legal_evidence_capacity_reservations` | `legal_evidence_capacity_reservation_registry.py` | `find_one`, `find`, `insert_one`, `find_one_and_update` | Five tenant-scoped indexes |
| `legal_evidence_binary_write_intents` | `legal_evidence_binary_write_intent_registry.py` | `find_one`, `insert_one` | Unique tenant ingestion and fingerprint; document chronology |
| `legal_evidence_object_metadata` | `legal_evidence_object_metadata_registry.py` | `find_one`, `find`, `insert_one` | Content reference unique; matter/document chronology; fingerprint and provider-object lookups |
| `legal_evidence_usage_observations` | `legal_evidence_usage_observation_registry.py` | `find_one`, `find`, `insert_one` | Unique tenant observation/idempotency; occurred and document history |
| `legal_evidence_commit_uncertainties` | `legal_evidence_commit_uncertainty_registry.py` | `find_one`, `find`, `insert_one` | Unique uncertainty, ingestion and provider-object identities; detected chronology |

All six registries use caller-owned transactions for operational work. The registry methods do not own transaction lifecycle. Several use majority+journal durability and strict immutable replay semantics. The reservation expiry field is an application-level epoch-microseconds lookup; it is **not** a Mongo TTL index. Commit uncertainty, metadata and usage observations are retained evidence, not TTL-cleanup candidates.

The orchestrator additionally composes:
- `legal_operations_lifecycle_registry.COLLECTION`;
- literal `subscriptions`;
- `tenant_product_entitlement_registry.HISTORY_COLLECTION`;
- `tenant_product_entitlement_registry.CURRENT_COLLECTION`.

Those are dependencies of the upload composition but their complete operation/index authority is not reclassified here; they remain in their canonical lifecycle, billing and entitlement families.

## 2. S3 storage is a separate cloud permission plane

The upload router requires:
- `WILSY_LEGAL_EVIDENCE_S3_BUCKET`;
- `WILSY_LEGAL_EVIDENCE_S3_REGION` (default `af-south-1`);
- optional `WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID`;
- an injected AWS SDK client using the ambient AWS credential chain.

Source-observed SDK calls in the storage adapter:
- `CreateMultipartUpload`
- `UploadPart`
- `CompleteMultipartUpload`
- `HeadObject`
- `ListMultipartUploads`
- `ListObjectVersions`
- `AbortMultipartUpload`

No `DeleteObject` call was found in this adapter. Do not grant object deletion merely because this is a storage workflow. Exact bucket, object prefix, KMS key ARN, AWS workload principal, multipart cleanup lifecycle and required ListBucket/ListBucketMultipartUploads resource scoping still need verification before a policy is drafted. S3 is not MongoDB and must be modelled as a separate permission contract.

## 3. Practitioner/matter binding route closure

Mounted route:
- Router: `tools/eos/api/legal_practitioner_matter_binding_router.py`
- Prefix: `/api/legal-operations/practitioner-bindings`
- Commands: POST grant at the prefix root; POST revocation at `/revocations`.

Dependencies:
- `legal_operations_lifecycle_registry.COLLECTION`;
- `legal_practitioner_matter_access_evidence` (router-injected collection; registry itself does not declare a collection constant);
- `legal_practitioner_matter_bindings`;
- `legal_client_matter_conflict_dispositions`;
- current IAM membership/role-assignment repositories and provisioning service.

Observed persistence:
- Access evidence: exact tenant-scoped `find_one`, append-only `insert_one`; no update/delete.
- Binding evidence: bounded `find` history and `insert_one`; indexes include unique tenant/binding/status snapshot, tenant/fingerprint, and active tenant/matter/practitioner scope via partial filter.
- Conflict dispositions: tenant-scoped `find` and append-only `insert_one`; eight indexes cover identity, fingerprint, idempotency, review lineage and bounded history dimensions.

The HTTP router owns session/transaction lifecycle; registry access requires caller-owned active transaction. This is not a generic user-to-matter write permission. The provisioning service checks current IAM, matter, policy and conflict-disposition evidence before grant/revoke. The index manifest records these collections and exact source index definitions.

## 4. AI route persistence — separate compositions

### 4.1 Tenant reasoning command

Mounted `POST /api/.../reasoning` route in `wilsy_ai_reasoning_router.py` composes:
- `wilsy_ai_entitlements`;
- `wilsy_ai_usage_admissions`;
- `wilsy_ai_model_invocations`;
- `wilsy_ai_usage_observations`.

The router owns HTTP validation and transaction lifecycle. Admission, invocation and usage registries use the caller session; AI model invocation evidence is immutable. Source-observed operations include exact `find_one`, `insert_one`, admission `update_one` CAS transitions and bounded `find` for held admissions/usage. Indexes are tenant-scoped and recorded in `infra/mongodb/eos-index-manifest-v1.json`.

### 4.2 Legal services and legal gateway

`wilsy_ai_legal_services_router.py` uses entitlement and usage-observation collections and delegates policy/tool membership/evidence composition to the C1C orchestrator. `wilsy_ai_legal_gateway_router.py` has its own legal-resource admission and post-read evidence composition. Do not assume the reasoning route's four-collection action set fully describes these routes; complete C1C and gateway transitive registry closure remains a separate task.

## 5. Index manifest extension

Updated `infra/mongodb/eos-index-manifest-v1.json` in commit `05b7c87af79cafa0073c97124990f97a92867fd2`.

It now includes verified source index declarations for the six upload registries, three practitioner/matter registries and AI model invocation, in addition to the previously inventoried entries. It remains `INVENTORY_INCOMPLETE` and explicitly non-executable. This is a source inventory, not an authorization to apply indexes.

## 6. Remaining gaps and no-go conditions

- Complete Legal Evidence reconciliation upload/capacity/usage/cleanup and all lifecycle/entitlement dependencies end-to-end.
- Resolve every remaining router's transitive repository closure, including both duplicated mounts of certain routers, webhooks, HR, payroll, employee, owner/commercial and tenant APIs.
- Identify all scheduler/worker/CLI processes and deployed runtime principals; source presence is not proof of deployment.
- Verify actual S3 bucket, prefix, KMS key, AWS account and workload identity.
- Move every API-path `ensure_indexes()` / `create_index()` call to the governed provisioner only after exact index parity and non-production tests.
- Add read-only runtime index verification and readiness failure when a required index is absent or divergent.
- Validate the candidate Mongo role and S3 policy with positive and negative integration tests against an explicitly fingerprinted non-production environment.

**NO-GO:** no production role, database credential, S3 policy, KMS key, network allowlist, deployment or data has been changed. No production target has been selected.


### 4.3 Server-owned legal AI orchestration and tool evidence

The server composition root also constructs the server-owned C1C tool registry and mounts the legal gateway/services/advisory routes. Two further durable collections are confirmed:
- `wilsy_ai_tool_orchestrations` — `find_one`, `insert_one`, `replace_one`; unique `tenant_id, orchestration_id` index.
- `wilsy_ai_legal_tool_invocations` — `find_one`, `insert_one`; unique tenant/invocation identity and tenant/fingerprint indexes.

Their exact source index declarations have been added to the versioned manifest in commit `fe19610ba79d2b7da45977900a48a7c05e73e70e`. The gateway and advisory route transitive dependencies still need complete call-graph closure; these two collections do not exhaust that work.
