# TITLE: WILSY EOS Production Hosting — ECS Fargate Foundation
# VERSION: v1.0.2-EOS-PRODUCTION-ECS-FARGATE-FOUNDATION
# AUTHORITY: Wilsy OS Core Governance; operational architecture and deployment-boundary documentation.
# EPITOME: Records the selected but unprovisioned AWS ECS Fargate hosting foundation for the Python Kennel EOS API and its production MFA KMS workload identity.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/operations/eos-production-ecs-fargate-foundation.md
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Kennel EOS owns application, identity, tenant and business truth.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.2-EOS-PRODUCTION-ECS-FARGATE-FOUNDATION renders the status as ordinary
#   Markdown rather than a custom tag; the complete governance and whitespace
#   correction from v1.0.1 remains in force.
#   v1.0.1-EOS-PRODUCTION-ECS-FARGATE-FOUNDATION adds the sovereign artifact
#   contract, corrects the infrastructure status language, and records the
#   exact distinction between the source-defined target and an existing live
#   production host. It also removes trailing whitespace that failed PR diff
#   verification. No AWS resource or runtime behavior is changed.
#   v1.0.0 established the inactive ECS Fargate foundation runbook.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Read-only architecture and operational guidance; no secrets, credentials or production data.
# TENANT BOUNDARY: No tenant, principal, membership, session or database record is created or mutated by this artifact.
# AUTHORITY BOUNDARY: Documentation only; no provisioning, deployment, task activation or MFA factor/enforcement authority.
# FINANCIAL AUTHORITY BOUNDARY: Kennel EOS is the exclusive financial execution authority; this infrastructure has no financial execution authority.

## Status and intended target

**Status:** Infrastructure definition only.

The repository defines an intended AWS ECS Fargate production-hosting target in AWS account `121014832643`, region `af-south-1`. This is a source-code architecture decision, not evidence that an existing live production service is hosted in AWS or has moved to ECS.

The read-only AWS inventory performed on 2026-11-09 found no EKS clusters and no IAM OIDC providers in the inspected account. ECS, EC2, Lambda and CloudFormation inventories did not identify an existing EOS production runtime. Some provider inventories were unavailable or incomplete, and the discovery did not establish whether production is hosted outside AWS. The actual current production host therefore remains unverified.

The selected target runtime is the Python Kennel EOS API on port `9095`, packaged as an immutable GHCR image. The CloudFormation definition is:

`infra/aws/eos-production-ecs-foundation.yaml`

The earlier EKS-specific MFA template is not the selected path for this implementation and must not be provisioned alongside the ECS design without a new architecture decision.

## Connection and authority model

| Surface | Intended connection | Authority and boundary |
|---|---|---|
| EOS application | Immutable GHCR image built from the Python EOS container definition | Python Kennel EOS remains the sole application/API and business authority |
| ECS task identity | Dedicated `wilsy-eos-production-task-role` | Workload identity only; no administrator or local-development credentials |
| MFA cryptography | Dedicated production symmetric KMS key | Encrypt/Decrypt only for encryption context `purpose=GLOBAL_PRINCIPAL_TOTP` |
| ECS execution identity | Separate `wilsy-eos-production-execution-role` | Image pull, secret injection and CloudWatch logging; no MFA KMS data-plane permission |
| MongoDB | Existing Secrets Manager secret reference supplied as `MongoDbUriSecretArn` | Secret reference only; production Atlas project, cluster and database authority remain independently unverified |
| GHCR credentials | Existing Secrets Manager secret reference supplied as `GhcrCredentialsSecretArn` | Image-pull authentication only; secret value is not stored in this repository |
| Ingress and network | Not defined by this foundation | No public endpoint, network route or production traffic path is created |

## What the foundation stack defines

The CloudFormation template defines only:

- ECS cluster `wilsy-eos-production`.
- IAM task role `wilsy-eos-production-task-role`, assumed by ECS tasks and granted purpose-scoped KMS Encrypt/Decrypt against the dedicated production MFA key.
- Separate ECS execution role for image pull, secret injection and CloudWatch logs. It has no KMS Encrypt/Decrypt permissions.
- Dedicated symmetric production KMS key with annual rotation and alias `alias/wilsy/production/global-principal-mfa`. A separately existing key-administrator role is a mandatory input.
- CloudWatch log group with 90-day retention.
- Fargate task definition pinned to an immutable GHCR sha256 digest, configured for the Python EOS API on port `9095`, read-only root filesystem, non-root UID `10001`, MongoDB URI secret injection, private GHCR registry credentials and KMS startup configuration.

It intentionally defines no ECS service, running task, VPC, subnet, security group, NAT gateway, load balancer, certificate, DNS record, Atlas network access entry, Atlas database user or secret value. Registering a task definition does not launch it. No desired count or service scheduler is created.

## Required existing inputs and proof

Before a reviewed infrastructure change set can be prepared, the infrastructure owner must verify:

1. The AWS caller identity, account and region match the separately approved production target.
2. The separate key-administrator IAM role exists and its owner has approved key administration.
3. GHCR package access is configured. The Secrets Manager secret referenced by `GhcrCredentialsSecretArn` contains the ECS `repositoryCredentials` JSON for the private image package. A token must never be placed in a CloudFormation parameter or source file.
4. A production-only MongoDB URI secret exists in Secrets Manager. Its backing database, project, cluster, database user, role scope, backups and recovery posture must be independently certified. Do not point at the local certification database or infer production authority from the existing Free-tier `Wilsy/legalDocSystem` cluster.
5. The image reference is a verified published GHCR digest, not `latest` or another mutable tag.
6. The exact runtime image is built from the canonical Python EOS container definition and has a verified provenance/SBOM appropriate to the release process.

Secret values are not read by this template. The ECS execution role can read only the two supplied secret ARNs. If either secret uses a customer-managed Secrets Manager KMS key, its decrypt permissions and key policy require a separate review; this template does not grant them implicitly.

## Remaining production delivery work

The foundation does not provide ingress or networking. Before defining an ECS service, the platform design must establish and independently review:

- VPC, private subnets, route tables, NAT or VPC endpoints, and outbound egress.
- Ingress, normally an HTTPS Application Load Balancer, approved DNS name and ACM certificate. Domain registration and control have not been evidenced.
- Atlas private connectivity or a fixed egress allow-list. Never use `0.0.0.0/0`.
- Production Atlas project, cluster, dedicated least-privilege database user, backup policy and restore test.
- Task security groups, health/readiness behavior, deployment circuit breaker, scaling, alarms, log retention, incident response and rollback.
- Exact published image digest and its provenance.
- A separately reviewed ECS service/ingress change set after those decisions and dependencies are proven.

These items are not silently supplied by the current foundation and must not be invented from example manifests or local-development configuration.

## Production KMS verification sequence

Only after separately approved infrastructure provisioning and a separately approved controlled task launch:

1. Obtain the actual ECS task ARN and registered task-definition revision from the AWS control plane.
2. Verify the effective STS identity from inside the task. It must be the dedicated production task role, never the execution role, administrator, developer, HR or local-development identity.
3. Verify the KMS key ARN and region injected into the task match the approved CloudFormation outputs.
4. Run `python -m tools.eos.auth.global_principal_mfa_kms_probe` from the actual task environment using its ambient task-role credentials.
5. Confirm EOS startup reports the KMS startup probe passed and global MFA runtime readiness is `READY`.
6. Confirm negative cases fail closed, including wrong key, wrong region, missing task role and denied Encrypt/Decrypt.
7. Preserve CloudTrail evidence, exact image digest and task-definition revision.

A local probe, administrator CLI call, CloudFormation output or successful task-definition registration is not a production workload probe. Do not activate login cutover or alter MFA factors as part of infrastructure provisioning.

## Explicit non-actions and approval boundary

This repository change is source-only. No AWS API mutation, CloudFormation change-set creation or execution, task launch, service deployment, MongoDB mutation, DNS change, merge or production cutover is authorized by this artifact. Those actions require separate verification and explicit approval.

# ARTIFACT: docs/operations/eos-production-ecs-fargate-foundation.md
# VERSION: v1.0.2-EOS-PRODUCTION-ECS-FARGATE-FOUNDATION
# AUTHORITY BOUNDARY: Operational documentation only; no infrastructure or runtime activation.
# TENANT POSTURE: No tenant, identity, session or database records are created or mutated.
# FAIL-CLOSED POSTURE: Unverified hosting, network, database, image and identity dependencies remain explicit blockers.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
