# EOS Production Hosting — ECS Fargate Foundation

**Status:** Infrastructure definition only. No AWS resources have been created and no production task is running.  
**Target account/region:** AWS account `121014832643`, `af-south-1` (intended target; re-verify at change-set review).  
**Runtime:** Python Kennel EOS API, port `9095`, immutable GHCR image.  
**CloudFormation:** `infra/aws/eos-production-ecs-foundation.yaml`.

## Why ECS Fargate

The 2026-11-09 read-only inventory found no EKS clusters and no IAM OIDC providers in the AWS account. ECS Fargate provides an AWS-native task role without inventing a Kubernetes cluster or OIDC provider. This is an architecture selection for the new production target, not evidence that an existing live service has moved to ECS.

The earlier EKS-specific MFA template remains an unprovisioned alternative and must not be deployed alongside this ECS path. ECS is the selected target for this implementation.

## What the foundation stack creates

The template creates only:
- ECS cluster `wilsy-eos-production`.
- IAM task role `wilsy-eos-production-task-role`, assumed only by ECS tasks, with `kms:Encrypt` and `kms:Decrypt` against the dedicated key and the `GLOBAL_PRINCIPAL_TOTP` encryption-context condition.
- Separate ECS execution role for image pull, secret injection and CloudWatch logs. It has no KMS permissions.
- Dedicated symmetric production KMS key with annual rotation and alias `alias/wilsy/production/global-principal-mfa`; a separately existing key-administrator role is mandatory.
- CloudWatch log group with 90-day retention.
- Fargate task definition pinned to an immutable GHCR sha256 digest, with read-only root filesystem, non-root UID 10001, MongoDB URI secret injection, private GHCR registry credentials and KMS startup configuration.

It intentionally creates **no ECS service, running task, VPC, subnet, security group, NAT gateway, load balancer, certificate, DNS record, Atlas network access entry, Atlas database user, or secret value**. Registering a task definition does not launch it. There is no desired count to scale.

## Required existing inputs

Before a reviewed change set can be prepared, the infrastructure owner must verify:
1. Account identity is exactly the approved production account and region.
2. The separate key-administrator IAM role exists and its owner approves key administration.
3. GHCR package access is configured. The Secrets Manager secret referenced by `GhcrCredentialsSecretArn` must contain the ECS `repositoryCredentials` JSON for the private image package. Never put a token in a CloudFormation parameter or source file.
4. A production-only MongoDB URI secret exists in Secrets Manager. Its backing database, project, cluster, database user, role scope, backups and recovery posture must be independently certified. Do not point at local certification DB, test project, or infer production from the existing Free-tier `Wilsy/legalDocSystem` cluster.
5. The image reference is a verified published GHCR digest, not `latest` or a mutable tag.

Secret values are not read by this template. The ECS execution role can read only the two supplied secret ARNs. If either secret uses a customer-managed Secrets Manager KMS key, the execution role/key policy must separately be reviewed for decrypt access; this template does not grant it implicitly.

## Remaining production delivery work

The foundation does not provide ingress or networking. Before creating an ECS service:
- Select and document the VPC, private subnets, route tables, NAT or VPC endpoints, and outbound egress.
- Choose ingress (normally an HTTPS Application Load Balancer), approved DNS name and ACM certificate. The domain has not yet been evidenced as registered/controlled.
- Establish the Atlas private connectivity or fixed egress allow-list. Never use `0.0.0.0/0`.
- Verify the production Atlas project, cluster, dedicated least-privilege database user, backup policy and restore test.
- Define task security groups, health/readiness behavior, deployment circuit breaker, scaling, alarms, retention, incident response and rollback.
- Validate the exact published image digest and SBOM/provenance.
- Create a separate reviewed ECS service/ingress change set only after those decisions are proven.

## Production KMS verification sequence

After separately approved infrastructure provisioning and after the first controlled task launch:
1. Query ECS task metadata/control plane for the actual task ARN and task role.
2. Verify the effective STS identity from inside the task; it must be the dedicated production task role, never the execution role, administrator, developer, HR or local-development identity.
3. Verify the key ARN and region injected into the task match the CloudFormation outputs.
4. Run `python -m tools.eos.auth.global_principal_mfa_kms_probe` from the actual task environment using its ambient task role credentials.
5. Confirm EOS startup reports the KMS startup probe passed and global MFA runtime readiness is `READY`.
6. Confirm negative cases fail closed (wrong key, wrong region, missing task role, denied Encrypt/Decrypt).
7. Preserve CloudTrail evidence and the exact image digest/task definition revision.

A local probe, administrator CLI call, CloudFormation output, or successful task-definition registration is not a production workload probe. Do not activate login cutover or alter MFA factors as part of infrastructure provisioning.

## Explicit non-actions

This change is source-only. No AWS API mutation, CloudFormation change set creation/execution, task launch, service deployment, MongoDB mutation, DNS change, merge or production cutover is authorized by this repository change. Those actions require separate verification and approval.
