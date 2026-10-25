# WILSY OS — Python EOS / MongoDB Atlas Production Provisioning Plan

**Version:** `v1.1.0-L10A2R-C4D7-RECONCILIATION-RUNTIME-INPUTS`
**Authority:** Wilsy OS Core Governance
**Date:** 2026-10-06
**Artifact:** `k8s/eos-api-atlas-production-provisioning-plan.md`

## Purpose

This artifact freezes the production provisioning sequence for the certified
Python EOS runtime after explicit production authority selected:

- MongoDB provider strategy: **MongoDB Atlas**
- HR document maximum upload size: **25 MiB**
- Exact upload ceiling: **26,214,400 bytes**

This plan contains no credentials, connection strings, private keys, database
passwords, AWS static credentials, Kubernetes secrets, or fabricated cloud
identifiers.

## Certified Runtime Inputs

The certified EOS Kubernetes workload consumes:

- `WILSY_ENV=production`
- `WILSY_HR_DOCUMENT_S3_BUCKET=wilsy-hr-documents-af-south-1-4a5acd714dc2`
- `WILSY_HR_DOCUMENT_S3_REGION=af-south-1`
- `WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES=26214400`
- optional `WILSY_HR_DOCUMENT_S3_KMS_KEY_ID`
- required secret `MONGODB_URI`

The EOS image remains bound by immutable digest in
`k8s/eos-api-production.yaml`.

## MongoDB Atlas Production Authority

A dedicated production Atlas target must be explicitly provisioned or selected
before `MONGODB_URI` may be created.

The following must be evidence-derived from Atlas and must not be invented:

1. Atlas organization identity.
2. Atlas project identity.
3. Production cluster name.
4. Atlas provider and region.
5. Production database-user identity.
6. Network connectivity policy from the eventual EOS Kubernetes runtime.
7. TLS-capable production connection string.
8. Canonical database name encoded by the approved production URI.

Repository-local, CI, synthetic, and test MongoDB URIs are forbidden as
production authority.

Existing GitHub secret names are Atlas control-plane evidence only:

- `MONGODB_ATLAS_PROJECT_ID`
- `MONGODB_ATLAS_PUBLIC_KEY`
- `MONGODB_ATLAS_PRIVATE_KEY`

`TEST_MONGODB_URI` is explicitly forbidden for production EOS.

## Atlas Runtime Database User

The production EOS database principal must be dedicated to runtime use.

It must not reuse:

- Atlas control-plane API credentials;
- developer credentials;
- test database credentials;
- local MongoDB credentials.

Its permissions must be bounded to the database and collections required by
canonical Python EOS runtime authority.

No database credential may be committed to Git.

## MongoDB Secret Binding

After the production Atlas target and runtime database user are proven, the
approved TLS production connection string must be injected as:

- Kubernetes Secret: `wilsy-eos-runtime-secrets`
- key: `mongodb-uri`
- process variable: `MONGODB_URI`

The actual URI must never appear in this repository.

## Governed Legal-Evidence Reconciliation Runtime Inputs

The Python EOS production deployment now declares these additional required
keys in the existing `wilsy-eos-runtime-secrets` Kubernetes Secret:

| Secret key | Process variable | Purpose |
| --- | --- | --- |
| `internal-auth-service-id` | `WILSY_INTERNAL_AUTH_SERVICE_ID` | Exact registered internal caller identity |
| `internal-auth-audience` | `WILSY_INTERNAL_AUTH_AUDIENCE` | Signed workload audience accepted by EOS |
| `internal-auth-key-id` | `WILSY_INTERNAL_AUTH_KEY_ID` | Active signed-workload key identifier |
| `internal-auth-secret` | `WILSY_INTERNAL_AUTH_SECRET` | Secret used by the existing signed-workload protocol |
| `legal-evidence-reconciliation-audit-mongodb-uri` | `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI` | Separate MongoDB audit deployment URI |

The production Kubernetes readiness probe now targets
`/api/legal-operations/evidence-provider/reconciliation/health`, not the
generic root-health endpoint. The pod becomes ready only when startup has
injected the canonical composition, the distinct audit client is retained, and
the platform decision-audit indexes have been verified. A missing or invalid
configuration keeps the pod unready; it is not represented as a healthy
reconciliation runtime.

These key names are deployment contracts, not populated credentials. Do not
create placeholder or synthetic production values. The internal service ID,
audience, key ID, and secret must be provisioned from the actual approved caller
and existing internal-service trust authority. **A repository search found the generic signing helper but no callsite that
invokes this reconciliation route; no actual caller is certified here. No
caller-side signature change is made in this Python/EOS work. The registered
service ID must not be guessed or populated until the real caller is approved.**

The exact mounted endpoint is:

`POST /api/legal-operations/evidence-provider/reconciliation`

The caller must sign the actual origin-form path including `/api`, the HTTP
method, exact body bytes, body SHA3-512 digest, timestamp, nonce, service ID,
audience, key ID, correlation ID, and signature using the existing
`X-Wilsy-*` contract. The UTF-8 JSON body schema is exactly
`{"idempotency_key":"<caller-generated-stable-operation-key>"}`; duplicate
JSON properties and additional fields are rejected. Retries must use a fresh
signed nonce while preserving the same operation idempotency key and exact
operation body. Correlation ID is not an idempotency key.

Before enabling the endpoint, identify and certify the actual caller, verify
that it signs the exact path above, and run adversarial HTTP tests for bad
signatures, replayed nonce, changed body/key conflict, scope/permission denial,
audit outage, and transaction abort. Until the secret values come from that
approved caller and deployment, the reconciliation composition intentionally
remains unavailable and the route returns a bounded 503.

### Audit target provisioning and identity proof

1. Select the approved audit MongoDB deployment and a dedicated runtime database
   principal. Do not reuse the business Mongo URI or credentials unless a
   separately governed design explicitly approves it.
2. Populate the Secret key
   `legal-evidence-reconciliation-audit-mongodb-uri` with the exact approved
   TLS URI, and use that same secret key/value for the deployment-only
   `tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_audit_provisioner`
   invocation.
3. Supply the canonical business `MONGODB_URI` and the audit URI to the
   provisioner. It rejects a matching host/database target, provisions the
   two required unique platform decision-evidence indexes, and verifies them.
4. The EOS startup runtime independently reads the same named audit URI
   variable, creates and pings its own retained client, checks it is distinct
   from the business client, and the composition verifies the provisioned audit
   index shape read-only. Never substitute the business database, a CI URI, or
   an implicit default database.
5. Capture the provisioner's success output and runtime startup logs without
   printing either URI. Both now emit the same credential-free
   `AUDIT_TARGET_FINGERPRINT` derived from the parsed host list or SRV FQDN,
   database, and replica-set identity (never username, password, or query credentials). Compare that
   fingerprint and database name across both records. Do not claim production
   audit-target certification until the fingerprints match and both index
   verification observations exist.

The provisioner is a deployment-only command and must never be invoked from a
request handler. The production Kubernetes manifest references these keys but
does not create the Secret or assert that a production caller, cluster, or
audit deployment already exists.

## HR Upload Policy

Production authority explicitly approved:

`WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES=26214400`

Equivalent policy: **25 MiB**.

This value is deployment policy and is not derived from repository test
fixtures.

The runtime ConfigMap contract is:

- ConfigMap: `wilsy-eos-runtime`
- key: `hr-document-max-upload-bytes`
- approved value: `26214400`

## HR S3 Runtime Authority

The certified HR S3 adapter requires exactly:

- `s3:PutObject`
- `s3:GetObject`
- `s3:AbortMultipartUpload`

Runtime authority does not require:

- `s3:ListBucket`
- `s3:ListMultipartUploadParts`
- bucket administration
- IAM administration

The bucket provisioner role is not a runtime workload role.

Static AWS access keys are forbidden in EOS deployment.

## Encryption

S3-managed AES256 remains the certified default.

`WILSY_HR_DOCUMENT_S3_KMS_KEY_ID` remains optional.

KMS permissions must not be introduced unless a specific production KMS key is
separately selected and certified.

## Kubernetes Workload Identity

The dedicated Kubernetes ServiceAccount is `wilsy-eos-api`.

No AWS role annotation is currently authorized because the concrete production
Kubernetes provider/cluster identity mechanism has not yet been proven.

When the deployment cluster is established, only the provider-supported
workload identity mechanism may be bound to this ServiceAccount.

Operator and bucket-provisioner profiles must not be reused as runtime
identities.

## Network Exposure

The certified EOS service remains:

- type: `ClusterIP`
- port: `9095`

No public LoadBalancer, Ingress, external hostname, or internet exposure is
authorized by this plan.

## Provisioning Sequence

1. Resolve Atlas control-plane authority without exposing credential values.
2. Select or provision the dedicated production Atlas project/cluster.
3. Establish production network connectivity between EOS runtime and Atlas.
4. Create a dedicated production EOS MongoDB database principal.
5. Obtain the TLS production `MONGODB_URI` without committing it.
6. Create Kubernetes Secret `wilsy-eos-runtime-secrets` with key `mongodb-uri`.
7. Create ConfigMap `wilsy-eos-runtime` with
   `hr-document-max-upload-bytes=26214400`.
8. Leave KMS unset unless independently authorized.
9. Resolve the concrete Kubernetes provider/cluster.
10. Bind dedicated runtime workload identity with only certified S3 actions.
11. Deploy the immutable EOS image digest already frozen in
    `k8s/eos-api-production.yaml`.
12. Run authenticated live HR document upload/read certification.
13. Certify Mongo durability, S3 multipart execution, tenant isolation,
    persisted-sensitivity authorization, and restart durability.
14. Only after those runtime certificates pass may HR production deployment be
    represented as operational.

## Prohibited Substitutions

Never promote the following into production authority:

- `TEST_MONGODB_URI`
- localhost MongoDB
- synthetic CI MongoDB
- repository `.env` MongoDB rescue
- Atlas API keys as runtime Mongo credentials
- `1024` test upload fixtures
- mutable container tag `latest`
- static AWS access keys
- bucket-provisioner role as EOS runtime identity
- predictive/Node Kubernetes workload as Python EOS deployment
- guessed Atlas cluster identifiers
- guessed Kubernetes provider identity
- guessed KMS key

## Completion Boundary

This plan does **not** claim:

- an Atlas production cluster exists;
- a production `MONGODB_URI` exists;
- a Kubernetes production cluster exists;
- AWS workload identity exists;
- the EOS workload is deployed;
- S3 writes have run from the deployed workload;
- authenticated HR HTTP runtime certification has run.

Those claims require separate runtime evidence.

---

### WILSY OS Sovereign Artifact Seal

**Artifact:** `k8s/eos-api-atlas-production-provisioning-plan.md`
**Version:** `v1.1.0-L10A2R-C4D7-RECONCILIATION-RUNTIME-INPUTS`
**Mongo Strategy:** MongoDB Atlas
**HR Upload Policy:** 25 MiB / 26,214,400 bytes
**Secret Posture:** no production secret committed
**AWS Runtime Identity:** unresolved until cluster-specific proof
**Financial Execution Authority:** Kennel EOS exclusively
**End of artifact.**
