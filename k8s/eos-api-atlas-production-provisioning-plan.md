# WILSY OS — Python EOS / MongoDB Atlas Production Provisioning Plan

**Version:** `v1.0.0-P0-C12F7C-EOS-ATLAS-PRODUCTION-PLAN`
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
**Version:** `v1.0.0-P0-C12F7C-EOS-ATLAS-PRODUCTION-PLAN`
**Mongo Strategy:** MongoDB Atlas
**HR Upload Policy:** 25 MiB / 26,214,400 bytes
**Secret Posture:** no production secret committed
**AWS Runtime Identity:** unresolved until cluster-specific proof
**Financial Execution Authority:** Kennel EOS exclusively
**End of artifact.**
