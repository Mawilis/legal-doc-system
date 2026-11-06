# EOS Production Deployment and Security Contract

**Status:** Contract defined; production authority and runtime activation remain unverified.  
**Applies to:** Python EOS API, MongoDB Atlas, AWS KMS, workload identity, deployment secrets, backups and incident response.  
**Related artifacts:**
- `k8s/eos-api-production.yaml`
- `k8s/eos-api-atlas-production-provisioning-plan.md`
- `docs/operations/global-principal-mfa-kms-production-activation.md`

## 1. Release invariants

The EOS production release MUST satisfy every invariant below. A repository manifest, passing CI run, Atlas project, or successful local connection is not proof of a live production deployment.

1. Exactly one explicitly designated EOS runtime database identity is used by the production EOS API.
2. That identity has no `atlasAdmin`, `readWriteAnyDatabase`, `dbAdminAnyDatabase`, project-owner, or Atlas control-plane authority.
3. Test and production use separate Atlas projects (preferred) and always separate database users, credentials, secret stores and connection strings.
4. Atlas network access is restricted to verified production egress addresses or a supported private connectivity path. `0.0.0.0/0` is prohibited.
5. Production backup policy, restore tests, retention and recovery objectives are approved and evidenced.
6. AWS KMS is accessed only through the actual EOS workload identity, with exact-key and encryption-context restrictions. Human operator credentials and static AWS keys are prohibited.
7. Credential rotation and incident response are executable, logged and independently reviewable.
8. Missing or invalid authority fails closed. No fallback to test credentials, local MongoDB, developer identities, or guessed cloud resources is permitted.

## 2. Environment and database identity boundary

### Production

- Production Atlas organization, project, cluster, database name, deployment region and runtime network path MUST be recorded from the actual selected production deployment.
- Create one dedicated database user for the Python EOS API in the production project.
- Scope the user to the exact EOS database and only the required collections/actions.
- Prefer a reviewed custom MongoDB role for the EOS collection/action inventory. If built-in roles are used, `readWrite` on the exact EOS database is the maximum interim allowance and requires a documented exception; never use `readWriteAnyDatabase` or `atlasAdmin`.
- Do not grant user administration, role administration, database administration, cluster administration, backup administration or Atlas project control to the runtime user.
- Keep the URI in the deployment secret manager (Kubernetes Secret or the actual platform's equivalent). The URI must never be committed, printed, placed in CI logs or copied into tickets.
- EOS production must receive only `MONGODB_URI` from the approved deployment secret. `TEST_MONGODB_URI`, local MongoDB and CI replica-set URIs are forbidden.

### Test and CI

- Test uses a separate Atlas project/cluster or disposable CI replica set and a distinct database user.
- Test credentials must not authenticate to production.
- CI secrets and production deployment secrets must have separate access policies and rotation schedules.
- The `legal-doc-test` project is treated as non-production until a formally approved classification says otherwise.

### Known inventory; not yet an authority decision

The Atlas inventory observed two FREE-tier clusters in AWS `AF_SOUTH_1`:
- Project `Wilsy`, cluster `legalDocSystem`.
- Project `legal-doc-test`, cluster `legal-doc-test`.

The inventory does not prove which cluster, if either, is used by the deployed EOS API. Neither cluster is automatically designated production by its name, region or presence. A dedicated production target must be selected and certified before a production URI is issued.

## 3. Atlas network access

- Prohibit `0.0.0.0/0` and equivalent unrestricted internet access.
- Prefer private endpoints/private networking where supported by the chosen runtime platform.
- Otherwise allow only fixed, verified NAT egress addresses for the EOS production workload and separately approved operator access.
- Do not assume a developer workstation address is a production workload address.
- Every access-list entry must carry an owner, purpose, environment and review/expiry reference in its comment or associated access register.
- Review and remove stale entries only after mapping them to a verified consumer and confirming no live workload depends on them.
- Never bulk-delete the current 100-entry Wilsy or 45-entry test lists as a substitute for attribution.
- Revalidate connectivity from the deployed workload after each network policy change.

### Current observed exception

The `legal-doc-test` project currently has a `0.0.0.0/0` entry. This is a security exception and must be removed after its consumers are identified and migrated to restricted paths. The Atlas connector available during this work supports inspection and allow-list creation but did not expose a deletion operation; no change is represented as completed.

The Wilsy project has 100 access-list entries without comments. These require owner attribution before cleanup. The current observed inventory has no `0.0.0.0/0` entry in that project.

## 4. Database privilege and user lifecycle

The production runtime principal MUST:
- Be named for the EOS workload, not a person.
- Be unique to the production environment.
- Have only the minimum database role(s) required by the runtime.
- Be scoped to the production EOS database and, where feasible, required collections.
- Be non-interactive and unavailable for human login or administrative use.
- Be rotated without placing the replacement secret in source control or logs.

Atlas administrators and break-glass operators are separate identities protected by MFA and independent approval. Atlas API keys are control-plane credentials and must never be used as MongoDB application credentials.

A user/role migration requires:
1. Inventory actual databases, collections, indexes, transactions and commands used by EOS.
2. Create the replacement principal with the proposed least-privilege role.
3. Inject its URI into a non-production deployment first.
4. Run the full integration suite, including transaction, index, change-stream (if used), and tenant-isolation tests.
5. Validate production-like read/write paths and denied administrative operations.
6. Perform a controlled production cutover with rollback credentials held in the secret manager.
7. Revoke the old principal after successful observation and rollback expiry.

Do not rotate or revoke existing users before the production consumer and rollback path are known.

## 5. Backup, restore and disaster recovery

Before production approval, the service owner and data owner MUST define:
- Recovery Point Objective (RPO).
- Recovery Time Objective (RTO).
- Backup frequency and retention.
- Point-in-time recovery requirement.
- Backup encryption and key ownership.
- Geographic/region recovery strategy and data residency constraints.
- Restore authority and separation of duties.

Production Atlas backup must be enabled with a tier and policy that supports the approved RPO/RTO. For workloads requiring point-in-time recovery, configure continuous backup where supported by the selected Atlas tier. Snapshot-only backup is not equivalent to point-in-time recovery.

Certification evidence MUST include:
1. A successful backup-policy inspection.
2. A restore into an isolated recovery target, not over the live production cluster.
3. Application-level integrity checks and representative EOS read/write tests against the restored target.
4. Measured restore duration and data-loss window.
5. Evidence that restored credentials and network access remain isolated from production.
6. A recorded approval and next restore-test date.

A backup being enabled is not a restore test. A successful disposable CI replica-set test is not a production backup/restore certificate.

## 6. AWS KMS and workload identity

- First prove where the EOS API actually runs and which workload identity it receives.
- Use a dedicated role/service identity for the EOS API. Do not reuse the human IAM operator, HR bucket provisioner, node role by assumption, or another service's role.
- For EKS, verify the live cluster, issuer/OIDC provider, ServiceAccount subject and role trust relationship before adding an annotation or binding.
- For ECS or another platform, use its native task/workload identity mechanism.
- Use a symmetric KMS key in the actual workload region; record its exact ARN and key policy.
- Grant the runtime role only `kms:Encrypt` and `kms:Decrypt` on that exact key, conditioned on `kms:EncryptionContext:purpose=GLOBAL_PRINCIPAL_TOTP`.
- Application encryption context must continue binding the exact principal ID and credential revision.
- Keep key administration, disablement, deletion scheduling and break-glass recovery outside the runtime role.
- Retain and alert on CloudTrail KMS events under the platform security logging policy.
- Do not inject static AWS access keys or a developer profile into the deployment.
- KMS readiness requires a successful startup encrypt/decrypt probe and an end-to-end enrollment/migration test using the actual deployed workload identity.

No live EOS host, Kubernetes cluster identity, production KMS key ARN or dedicated EOS runtime role has yet been proven by the available inventory. Therefore KMS activation remains disabled until these facts are independently established.

## 7. Secrets and credential rotation

All production secrets MUST be stored in an approved secret manager and exposed only to the intended workload.

Rotation rules:
- Maintain an owner, secret identifier, creation date, last-rotation date, next-rotation date and emergency revocation procedure for every production credential.
- Rotate MongoDB runtime credentials on a documented schedule and immediately after suspected exposure, staff departure affecting access, or relevant incident.
- Use overlap rotation: create/enable replacement, deploy and verify it, then revoke the old credential. Avoid simultaneous blind rotation across all replicas.
- Rotate Atlas control-plane API keys independently from MongoDB database users.
- Rotate KMS keys through the documented envelope-key migration procedure; retain old decrypt-key ARNs only for the approved transition window.
- Rotate internal service secrets and signing keys independently from database and KMS credentials.
- Never echo secret values, full connection URIs, TOTP seeds, provisioning URIs, access tokens or private key material in command output, logs, screenshots or issue comments.
- Test rotation in non-production and record rollback evidence before production execution.

## 8. Incident response

### Suspected MongoDB credential compromise
1. Declare incident and appoint incident commander.
2. Preserve Atlas audit/activity evidence, application logs, identity-provider events and relevant network telemetry.
3. Identify affected user, project, database, time window and access paths.
4. Create replacement least-privilege credentials in the secret manager.
5. Deploy replacement credentials and verify healthy database operations.
6. Revoke compromised credentials and remove unauthorized network entries after preserving evidence.
7. Review database reads/writes, administrative actions, exports and privilege changes.
8. Assess tenant/data impact; invoke legal, privacy and customer notification procedures as required.
9. Validate integrity, restore from a known-good backup if required, and document corrective actions.

### Suspected KMS/workload identity compromise
1. Block MFA enrollment/migration operations if envelope integrity or key authority is uncertain.
2. Preserve CloudTrail and workload identity logs.
3. Revoke or constrain the affected workload identity through the platform's approved emergency process.
4. Do not immediately schedule key deletion; preserve decryptability and evidence.
5. Assess unauthorized decrypt/encrypt activity and affected principal envelopes.
6. Rotate to a new approved key and re-encrypt through the controlled migration procedure if required.
7. Revoke affected sessions and perform independently verified MFA recovery where warranted.
8. Resume only after key policy, identity trust, audit evidence and end-to-end probes pass.

### Repeated authentication attacks
The EOS identity controls must apply rate limits, bounded lockout, credential revision/session revocation and security-event audit. Recovery must not disclose whether an email/principal exists. Unlocking must follow the approved risk/recovery workflow; elapsed time alone must not silently restore a suspected compromised identity.

## 9. Required production evidence

The release evidence bundle MUST contain, with secrets redacted:
- Actual runtime platform, deployment ID and immutable image digest.
- Verified workload identity and least-privilege role policy.
- Atlas organization/project/cluster/database identity.
- Production runtime database user name, roles and database scope (never its password or URI).
- Network path and allow-list/private-endpoint evidence.
- Separate test/prod secret references and access-control policy.
- Backup configuration and successful isolated restore report with RPO/RTO measurements.
- KMS key ARN, key-policy review, workload trust proof, CloudTrail evidence and successful startup probe.
- Credential rotation rehearsal and incident-response tabletop results.
- CI and deployed end-to-end certification reports.
- Independent security and data-owner approval.

## 10. Execution gates and current disposition

| Gate | Acceptance evidence | Current disposition |
| --- | --- | --- |
| Runtime platform | Live deployment and workload identity inspected | **Blocked — host not identified** |
| Production Atlas target | Project/cluster/database tied to live EOS deployment | **Blocked — not proven** |
| Dedicated runtime DB user | Exact DB-scoped least-privilege identity | **Not provisioned/certified** |
| Test/prod separation | Distinct projects/users/secrets verified | **Partially observed; deployment binding unproven** |
| Network restriction | No public-wide rule; only attributed workload/operator paths | **Open — test project has 0.0.0.0/0** |
| Wilsy allow-list ownership | All entries attributed and reviewed | **Open — 100 uncommented entries** |
| Backup/restore | Approved policy and isolated restore evidence | **Not certified** |
| AWS workload identity | Live host identity and role trust verified | **Blocked — host not identified** |
| KMS | Exact key, role, context policy and live probe | **Not activated** |
| Rotation/IR | Rehearsal and incident tabletop evidence | **Not certified** |

### Go/no-go rule

Production release is **NO-GO** while any required gate above is blocked or open. Do not infer readiness from a passing CI pipeline, a configured manifest, or the mere existence of Atlas clusters.

The next safe execution sequence is: identify the actual EOS runtime and its deployment secret references; map the live database target; select or provision the production Atlas target; establish restricted network access; provision the dedicated runtime user; rehearse credential cutover; certify backups/restores; prove workload identity and KMS; then run the deployed end-to-end release suite.

**No production credentials, Atlas access entries, database users, cloud roles, keys or clusters are changed by this contract.**
