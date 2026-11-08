# TITLE: WILSY EOS Global Principal MFA — AWS KMS Operations and Hosting Binding
# VERSION: v1.0.3-EOS-GLOBAL-PRINCIPAL-MFA-KMS-OPERATIONS
# AUTHORITY: Wilsy OS Core Governance; cryptographic infrastructure operations guidance.
# EPITOME: Define the canonical Python EOS MFA KMS contract, distinguish local-development and selected ECS production identities, and preserve fail-closed provisioning and runtime certification gates.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/infra/aws/README-global-principal-mfa-kms.md
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS owns MFA factor, identity, session and tenant truth.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.3-EOS-GLOBAL-PRINCIPAL-MFA-KMS-OPERATIONS records the exact
#   published Python EOS Dockerfile, ephemeral task-volume boundary and
#   liveness-versus-readiness distinction for the ECS target.
#   v1.0.2-EOS-GLOBAL-PRINCIPAL-MFA-KMS-OPERATIONS aligns this guide with the
#   selected ECS Fargate production target, removes contradictory EKS production
#   deployment instructions, records AWS inventory limitations, and preserves
#   the separate already-certified local-development path.
#   v1.0.1 selected ECS Fargate as the intended production hosting architecture.
#   v1.0.0 documented the original EKS/IRSA proposal and local-development path.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: No credentials, TOTP material, secret values or plaintext factor secrets belong in source, logs or configuration files.
# TENANT BOUNDARY: KMS encryption context binds each envelope to the principal and credential revision; this guide creates no tenant or identity records.
# AUTHORITY BOUNDARY: KMS protects MFA secrets only; IAM workload identity is supplied by the hosting platform and never inferred from local administrator credentials.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.

## Current status and target selection

**Local development:** The dedicated local-development KMS stack and assumed-role runtime path have been provisioned and locally certified. The canonical launcher is `scripts/start-eos-local-mfa.sh`.

**Production:** AWS ECS Fargate in account `121014832643`, region `af-south-1`, is the selected target architecture for new production hosting. The source foundation is `infra/aws/eos-production-ecs-foundation.yaml`. It is not provisioned, no ECS service or task is running, and the actual existing production host has not been proven to be AWS. The 2026-11-09 read-only AWS inventory found no known EKS or ECS production cluster, Lambda runtime or production CloudFormation stack in the inspected account. Some provider inventory calls were unavailable or incomplete; an external hosting provider has not been ruled out.

The production ECS foundation is a source definition only. Its dedicated production key and task role do not exist until a separately approved CloudFormation provisioning action is reviewed and executed. The repository change does not authorize provisioning, task launch, service deployment, DNS, database mutation, merge or MFA factor/enforcement changes.

## Canonical Python EOS KMS contract

The canonical adapter is `tools/eos/auth/global_principal_mfa_kms_envelope.py`.

Configure the application with:

- `WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS`
- `WILSY_GLOBAL_MFA_KMS_KEY_ID` set to a full customer-managed KMS key ARN.
- `WILSY_GLOBAL_MFA_KMS_REGION` set to the key's AWS region.
- Optional `WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS` for a separately governed key-rotation migration window.
- Ambient short-lived AWS credentials supplied by the hosting platform's workload identity.

The adapter requires a full key ARN and an explicit matching region. It does not use static AWS credentials or a local-key fallback. Encryption context binds ciphertext to:

- `purpose=GLOBAL_PRINCIPAL_TOTP`
- `principal_id=<principal>`
- `credential_revision=<revision>`

At startup, `validate_access()` performs a synthetic encrypt/decrypt round trip. A configured but inaccessible or incorrectly scoped KMS provider fails closed; it must not silently downgrade to another encryption mechanism.

## Connection and authority matrix

| Surface | Canonical connection | Authority boundary |
|---|---|---|
| MFA envelope | Python EOS KMS envelope adapter | Cryptographic protection only; not factor, enrollment or session authority |
| Local AWS identity | Dedicated local assumed role | Local development only; never production |
| Production AWS identity | Dedicated ECS task role from the actual ECS task metadata credential chain | Production workload identity only; never the ECS execution or administrator role |
| Production KMS | Dedicated production key and alias | Encrypt/Decrypt only, constrained by `GLOBAL_PRINCIPAL_TOTP` purpose |
| ECS execution role | Image pull, secret injection and CloudWatch logging | No application KMS data-plane permission |
| MFA persistence | Existing Python EOS factor repository in the canonical `wilsy` database | Stores encrypted envelope and factor metadata; no duplicate MFA collection |
| Audit | Existing EOS audit authorities | This KMS guide does not create or certify an independent audit database |

The adapter's full encryption context also binds principal and credential revision. The production key policy restricts the workload role's KMS use to the MFA purpose. These controls are complementary: the KMS key policy restricts workload purpose, while the adapter enforces principal/revision binding.

## Local-development KMS path

The local-development CloudFormation template is:

`infra/aws/global-principal-mfa-kms-local-development.yaml`

The local stack name used by the canonical launcher is `wilsy-eos-global-principal-mfa-local-dev-v3`. It creates a dedicated symmetric key, alias `alias/wilsy/local-development/global-principal-mfa`, and role `wilsy-eos-global-mfa-local-development`.

The local role trusts the exact configured developer IAM user and has only KMS Encrypt/Decrypt use for `purpose=GLOBAL_PRINCIPAL_TOTP`. Key administration is separately assigned to the designated key administrator. The role is not a production identity and must never be attached to an ECS task or used for production factor encryption.

The dedicated local AWS CLI profile is `wilsy-eos-mfa-local`. The launcher reads the non-secret key ARN from the local stack, clears static AWS credential environment variables, selects the assumed-role profile, verifies the effective account/role identity, runs the canonical synthetic KMS probe, and only then starts Python EOS:

```bash
bash scripts/start-eos-local-mfa.sh
```

The probe is:

`python -m tools.eos.auth.global_principal_mfa_kms_probe`

It verifies the expected local account and assumed role and performs a real synthetic KMS encrypt/decrypt round trip. It emits only sanitized success markers or the exception class. Local certification proves the local-development role/key path only; it does not certify production identity, hosting, database or ingress.

## Selected production ECS path

The production foundation template is:

`infra/aws/eos-production-ecs-foundation.yaml`

It defines:

1. ECS cluster `wilsy-eos-production`.
2. Dedicated task role `wilsy-eos-production-task-role`, assumed by ECS tasks and granted direct KMS Encrypt/Decrypt in the production key policy only for `purpose=GLOBAL_PRINCIPAL_TOTP`.
3. Separate execution role `wilsy-eos-production-execution-role` for private GHCR image pull, Secrets Manager secret injection and CloudWatch logging. It has no KMS Encrypt/Decrypt permissions.
4. Dedicated symmetric production MFA KMS key and alias `alias/wilsy/production/global-principal-mfa`, with automatic rotation.
5. CloudWatch log group `/wilsy/eos/production/api` with 90-day retention.
6. Fargate task definition pinned to a full immutable GHCR sha256 digest, running the Python EOS API on port `9095`.

The template creates no ECS service, running task, VPC, subnet, security group, NAT gateway, load balancer, certificate, DNS record, Atlas network access entry, database user or secret value. It is not a production deployment.

The separate existing key-administrator role, private GHCR credential secret and production-only MongoDB URI secret are required inputs. Secret values must never be committed or supplied as plaintext CloudFormation parameters. The production Atlas target, dedicated database user, network path, backups and restore evidence remain independent blockers. Networking, HTTPS ingress, DNS, Atlas connectivity, service activation and actual task launch require separately reviewed infrastructure work and approval.

### Production provisioning gates

Before preparing a production change set, independently verify:

- Actual hosting target and approved AWS account/region.
- Approved key-administrator role ARN and its administrative scope.
- Production-only MongoDB secret ARN and its underlying Atlas project, cluster, database and principal.
- GHCR credential secret ARN and access to the exact private package.
- Published immutable image digest, provenance and software bill of materials.
- VPC/subnet/egress/ingress design and Atlas connectivity plan.
- Security groups, health/readiness endpoint, alarms, retention, rollback and incident response.

A resource name, source manifest, CloudFormation template, local KMS probe or administrator CLI identity is not proof of an actual production workload.

### Production workload KMS certification gates

Only after separately approved provisioning and controlled task launch:

1. Identify the actual ECS task ARN, task-definition revision and configured task role.
2. From inside the task, verify the effective STS identity is exactly the dedicated production task role. The ECS execution role is not the application identity.
3. Verify the injected full key ARN and region against the approved stack outputs.
4. Run `python -m tools.eos.auth.global_principal_mfa_kms_probe` from the actual task environment using ambient ECS task-role credentials. The current probe pins the local-development role and therefore must not be used unchanged as a production identity verifier; production probe behavior must be separately designed and certified before task activation.
5. Verify EOS startup readiness is `READY` only after the real production KMS synthetic round trip succeeds.
6. Verify wrong key, wrong region, missing task role and denied KMS permissions fail closed.
7. Preserve CloudTrail, stack/change-set, image digest and task-definition evidence.

No production login cutover or MFA factor/enforcement change is part of this infrastructure foundation.

## Historical EKS/IRSA proposal — superseded, do not deploy

`infra/aws/global-principal-mfa-kms.yaml` is an EKS/OIDC/IRSA-specific proposal retained for historical traceability and static contract tests. The production hosting decision is now ECS Fargate. This EKS template is superseded for the selected production path and must not be provisioned as the production MFA identity. Do not create a speculative EKS cluster, IAM OIDC provider or Kubernetes ServiceAccount to satisfy its parameters.

The earlier EKS proposal assumed the exact subject `system:serviceaccount:<namespace>:wilsy-eos-api` and a matching IAM OIDC provider. The read-only inventory did not find a verified production EKS cluster or OIDC provider. Those assumptions are not production evidence. The EKS role, alias and key are not interchangeable with the ECS production resources or the local-development key.

## Security and recovery boundaries

- Never place AWS access keys, session tokens, TOTP seeds, recovery codes, plaintext MFA secrets or database URIs in Git, CloudFormation templates, ConfigMaps or logs.
- Do not give the EOS task the infrastructure administrator profile or ECS execution role.
- Do not reuse the HR S3 provisioning identity for MFA.
- Do not share local-development and production KMS keys or workload roles.
- Do not schedule key deletion as a routine rollback; enrolled factors depend on decrypt access.
- For key compromise, use a governed factor re-enrollment and key-rotation plan. Retain prior decrypt key ARNs only for an approved migration window.
- Preserve CloudTrail and CloudFormation change-set/stack evidence.

## Explicit non-actions

This guide does not provision AWS resources, create change sets, launch tasks, deploy services, modify MongoDB, change DNS, merge PR #398, alter MFA factors or enforce production login cutover. Each remains subject to independent evidence and explicit approval.

# ARTIFACT: infra/aws/README-global-principal-mfa-kms.md
# VERSION: v1.0.3-EOS-GLOBAL-PRINCIPAL-MFA-KMS-OPERATIONS
# AUTHORITY BOUNDARY: KMS architecture and operational guidance only; no provisioning or workload activation.
# TENANT POSTURE: No tenant, principal, membership, session or database records are created or mutated.
# FAIL-CLOSED POSTURE: Local and production identities remain isolated; unverified hosting and infrastructure dependencies block production certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
