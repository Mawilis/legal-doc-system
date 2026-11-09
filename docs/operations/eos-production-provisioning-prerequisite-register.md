# TITLE: WILSY EOS Production Provisioning Prerequisite and Evidence Register
# VERSION: v1.0.4-EOS-ECS-TASK-ARN-IDENTITY-BINDING
# AUTHORITY: Wilsy OS Core Governance; evidence register and provisioning gate definition only.
# EPITOME: Track verified facts, missing evidence, accountable approvals and exact exit criteria before any production ECS foundation provisioning or workload activation.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/operations/eos-production-provisioning-prerequisite-register.md
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; AWS platform, database, security and service owners provide evidence within their authority.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.3 records the completed af-south-1 discovery: no ECS/EKS cluster,
#   production runtime stack, production secret metadata, production KMS alias,
#   NAT, VPC endpoint, ingress, ACM certificate or Route 53 zone was reported;
#   the only KMS alias and stack are local-development resources. The sole VPC
#   is default-only and is not approved as the production network.
#   v1.0.2 records expanded read-only discovery coverage for secret metadata,
#   KMS aliases, network primitives, ingress target groups, ACM and Route 53.
#   v1.0.1 pins the production verifier contract to the exact ECS cluster,
#   task family and positive task-definition revision.
#   v1.0.0 establishes a fail-closed evidence register for the selected ECS
#   Fargate production target and the separately controlled workload identity
#   verification milestone. Unknowns are blockers, not inferred values.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: No secret values, access tokens, TOTP material, database credentials or private network secrets are recorded here.
# TENANT BOUNDARY: No tenant, principal, membership, session or database records are created or changed.
# AUTHORITY BOUNDARY: Register only; no AWS mutation, provisioning, task launch, service activation, DNS, database mutation or MFA enforcement authority.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains exclusive.
# FAIL-CLOSED DECLARATION: A prerequisite is satisfied only by independently reviewable evidence; a source template, expected ARN, local test or operator assertion alone is insufficient.

## Decision record

| Item | Recorded decision |
|---|---|
| Intended hosting target | AWS ECS Fargate |
| AWS account | `121014832643` |
| AWS region | `af-south-1` |
| Canonical runtime | Python Kennel EOS API, port `9095` |
| Foundation definition | `infra/aws/eos-production-ecs-foundation.yaml` |
| Runtime identity | Dedicated ECS task role `wilsy-eos-production-task-role` |
| Execution identity | Separate `wilsy-eos-production-execution-role`; never application identity |
| MFA key purpose | `GLOBAL_PRINCIPAL_TOTP`, production-only symmetric KMS key |
| Current provisioning state | NOT PROVISIONED |
| Current task state | NO TASK LAUNCHED / WORKLOAD IDENTITY NOT VERIFIED |
| Production activation | BLOCKED |

The 2026-11-09 read-only discovery established the AWS account identity under the `wilsy-legal-cert` operator profile. In `af-south-1`, it reported no ECS or EKS clusters, no WILSY/EOS production secret metadata, no production KMS alias, no NAT gateway, no VPC endpoint, no Lambda function, no Elastic Beanstalk environment, no running EC2 instance, no load balancer or target group, no ACM certificate and no Route 53 hosted zone. The only reported KMS alias was `alias/wilsy/local-development/global-principal-mfa`; the only CloudFormation stack was `wilsy-eos-global-principal-mfa-local-dev-v3` in `CREATE_COMPLETE`. The only reported VPC (`vpc-05a3c2c855c4dde26`) has the default `172.31.0.0/16` network, three public-IP-assigned subnets and only its default security group. It is not an approved production network and must not be selected for EOS production without a separately reviewed network design. App Runner and Lightsail inventories were unavailable due subscription or endpoint errors; other AWS provider inventories also had unavailable regions. This evidence establishes no known production runtime in the successfully inspected AWS surfaces, not the absence of hosting outside those surfaces or outside AWS. The actual current production host and ingress target remain unverified.

## Evidence register

| ID | Prerequisite | Current status | Evidence required to close |
|---|---|---|---|
| P-01 | Production account and region | **Verified for target selection** | Repeat read-only STS caller identity immediately before any future change-set review; confirm account `121014832643` and `af-south-1`. The earlier operator identity is not the ECS workload identity. |
| P-02 | Existing live production host and traffic path | **Unverified — no AWS host found in inspected surfaces** | Identify current hosting provider, production API hostname, ingress/load-balancer target and current process/runtime owner. `af-south-1` reported no ECS/EKS cluster, EC2 instance, load balancer, target group or application stack; App Runner and Lightsail inventory was unavailable. Read-only AWS discovery does not rule out non-AWS hosting. |
| P-03 | Key-administrator role | **Missing evidence — only local-development role found** | Supply exact existing IAM role ARN, trust/ownership evidence and approved key-administration scope. Confirm it is separate from task, execution and developer identities. Never substitute the operator user or local-development role. |
| P-04 | Private GHCR credential secret | **Missing evidence — no matching production secret metadata reported** | Exact existing Secrets Manager secret ARN and proof it contains valid ECS `repositoryCredentials` JSON for the selected private package. Do not disclose or commit its value. If encrypted with a customer-managed key, separately prove execution-role decrypt permission and key-policy authorization. |
| P-05 | Production MongoDB URI secret | **Missing evidence — no matching production secret metadata reported** | Exact production-only secret ARN, secret KMS-key access proof where applicable, and owner-approved backing Atlas project, cluster, database, least-privilege database user and connection policy. It must not reference the disposable local certification replica set or an unverified cluster. |
| P-06 | Atlas connectivity and database recovery | **Missing evidence** | Approved network route, source egress identity/IP or private connectivity, Atlas access configuration, backup policy, recent successful restore evidence, monitoring and database owner sign-off. No `0.0.0.0/0` allow-list. |
| P-07 | Published immutable application image | **Missing evidence** | Exact `ghcr.io/...@sha256:<digest>` reference for the release, package pull proof, provenance/attestation, SBOM and image vulnerability review. A local Docker build or CI build without publication is not a published image. |
| P-08 | Network architecture | **Not designed — default VPC rejected as production foundation** | `af-south-1` reports only default VPC `vpc-05a3c2c855c4dde26` (`172.31.0.0/16`), three public subnets and the default security group; no NAT gateway or VPC endpoint was reported. Design and approve a dedicated production VPC, private subnet IDs, route tables, egress path or VPC endpoints, security groups, DNS resolver dependencies and availability-zone coverage. Do not reuse the default VPC as-is. |
| P-09 | HTTPS ingress and domain | **Unverified — no Route 53 zone, ACM certificate or load balancer reported in af-south-1** | Domain registration/control proof, approved hostname, ACM certificate ARN in the correct region, ALB/listener/WAF decision, DNS ownership and cutover/rollback plan. No domain purchase or ownership is assumed. |
| P-10 | Readiness and traffic admission | **Missing implementation evidence** | Dedicated readiness contract that verifies required database and KMS dependencies, plus ALB health-check path/thresholds and startup behavior. The current root route is liveness only and must not be treated as database readiness. |
| P-11 | Durable artifact storage | **Architecture decision required** | Identify canonical durable EOS document/evidence storage, access policy, encryption, retention, backup, restore and audit contracts. ECS task volumes are ephemeral scratch only; they cannot hold authoritative legal/evidence records. |
| P-12 | Operations and recovery | **Missing evidence** | Approved alarms, dashboards, log retention, incident ownership, on-call/escalation, deployment circuit breaker, rollback, capacity/scaling limits, vulnerability response and disaster-recovery objectives. |
| P-13 | CloudFormation foundation review | **Source checks passed; AWS review pending** | Re-run exact-head CI and cfn-lint; independently inspect the generated CloudFormation change set in the approved account/region; review IAM/KMS/secret diffs and resource replacement/deletion behavior. No change set has been created or executed. |
| P-14 | Production task-role identity | **Not verified** | After separate approval and controlled task launch, run `python -m tools.eos.auth.ecs_production_workload_identity_probe` inside the task and retain task ARN, task-definition revision, STS identity and sanitized probe result. |
| P-15 | Task-volume permissions | **Not verified** | Inside the controlled task, prove UID/GID 10001 can write to the intended ephemeral mounts and cannot treat them as durable storage. Record mount and permission results without business data. |
| P-16 | Production MFA readiness | **Blocked** | Confirm production KMS key ARN/region, task-role KMS Encrypt/Decrypt with required encryption context, successful startup readiness, negative tests and CloudTrail evidence. This is not authorization to enroll factors, alter enforcement or cut over login. |

## Exact ECS workload identity verification contract

The dedicated verifier is:

`tools/eos/auth/ecs_production_workload_identity_probe.py`

It is intentionally distinct from the local-development-only verifier:

`tools/eos/auth/global_principal_mfa_kms_probe.py`

The local probe pins `wilsy-eos-global-mfa-local-development`; it is not acceptable production identity evidence.

The production verifier must run from inside the actual ECS container and performs all of the following:

1. Requires `ECS_CONTAINER_METADATA_URI_V4` and restricts its endpoint to the ECS link-local metadata host `169.254.170.2`.
2. Reads the task-scoped metadata endpoint and requires a task ARN in account `121014832643`, region `af-south-1`, cluster `wilsy-eos-production`, task family `wilsy-eos-production-api` and a positive task-definition revision.
3. Requires `AWS_REGION=af-south-1`.
4. Requires `WILSY_ECS_EXPECTED_TASK_ROLE_ARN` to equal the exact production task-role ARN.
5. Calls STS through the task's ambient credential chain and requires the actual assumed-role ARN to be `wilsy-eos-production-task-role`. The execution role, local role, IAM user, administrator and any other role are rejected.
6. Builds the canonical EOS KMS adapter from environment, requires the production account/region key ARN, and performs a synthetic encrypt/decrypt round trip with the canonical purpose/principal/revision encryption context.
7. Requires the task ARN resource path itself to be `task/wilsy-eos-production/<32-character-task-id>`; metadata cannot claim the approved cluster while supplying an ARN for another cluster or a malformed/short task ID.
8. Emits sanitized pass/fail markers only; it never prints credentials, secret values, ciphertext, plaintext or TOTP material.

The foundation injects the expected task-role ARN from `!GetAtt EosProductionTaskRole.Arn`. This is an expectation, not proof. The verifier also binds the metadata TaskARN resource path to the exact approved cluster name and a 32-character task ID, independently of the metadata Cluster field. Only the STS response observed from the actual task can prove the effective runtime identity. A static test, local execution, administrator CLI session, CloudFormation output or task-definition registration cannot close P-14.

Run the verifier only after an explicitly approved task launch:

```bash
python -m tools.eos.auth.ecs_production_workload_identity_probe
```

A zero exit status proves the task metadata, exact task role and synthetic KMS capability at that moment. It does not prove database readiness, ingress, durable storage, legal application acceptance, production MFA enrollment or authorization to enable production login.

## Provisioning and activation sequence

1. Close the evidence requirements P-02 through P-12 with named owners and reviewable evidence.
2. Obtain explicit approval to prepare and inspect a CloudFormation change set. Preparation must be non-executing and the full change set must be reviewed before any execution request.
3. Obtain separate explicit approval before executing a foundation change set that creates IAM roles, KMS key, ECS cluster, log group and task definition.
4. Independently inspect stack outputs and effective IAM/KMS policies after provisioning.
5. Obtain separate explicit approval for a controlled one-off ECS task launch using the pinned image and reviewed network configuration.
6. Run P-14 and P-15 from inside that task. Verify the exact task ARN, task definition, task role, execution role separation, KMS round trip, readiness and volume behavior.
7. Close remaining operational, database, ingress, durable-storage and recovery gates.
8. Only after a separately reviewed service/ingress design and explicit deployment approval may a production service or traffic route be activated.
9. MFA factor/enforcement changes and login cutover require their own independent authorization and certification. They are not implied by any earlier gate.

## Current milestone outcome

- The intended AWS account and region are recorded from read-only discovery. The completed `af-south-1` inventory reported no ECS/EKS production cluster, production secrets, production KMS alias, NAT, VPC endpoint, load balancer/target group, ACM certificate or Route 53 zone. The sole VPC is default-only and explicitly rejected as a production network foundation. The only KMS alias and CloudFormation stack are local-development resources. App Runner and Lightsail inventory was unavailable, so the discovery is not a global proof that no production host exists. The inventory script reports candidate secret metadata, KMS aliases, VPC/subnet/security-group/NAT/VPC endpoint inventory, load-balancer target groups, ACM certificates and Route 53 hosted zones without reading secret values.
- The ECS foundation now injects the exact expected task-role ARN into the task environment.
- The production-only verifier and synthetic unit tests are added to the repository; the verifier pins the approved ECS cluster, task family and positive revision, and validates that the TaskARN resource path independently names that cluster and a 32-character task ID. These tests remain source-level checks, not runtime identity evidence.
- The operations runbook distinguishes the production verifier from the local-development probe.
- Actual production hosting, key-administrator role, secret ARNs, Atlas target/network, published image digest, VPC/subnets/egress, domain/ACM/ingress, readiness, durable storage and recovery evidence remain open.
- No AWS resource has been created, no CloudFormation change set has been executed, no ECS task has been launched, no production deployment or DNS change has occurred, no database has been mutated, no PR has been merged, and no MFA factor/enforcement change has been made.

# ARTIFACT: docs/operations/eos-production-provisioning-prerequisite-register.md
# VERSION: v1.0.4-EOS-ECS-TASK-ARN-IDENTITY-BINDING
# AUTHORITY BOUNDARY: Evidence tracking and release-gate documentation only; no provisioning or production activation.
# TENANT POSTURE: No tenant, principal, membership, session or database records are created or changed.
# FAIL-CLOSED POSTURE: Unverified dependencies remain blockers; only independently reviewable evidence closes a prerequisite.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
