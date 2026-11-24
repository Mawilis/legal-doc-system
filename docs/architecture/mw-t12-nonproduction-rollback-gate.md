# WILSY OS — MW-T12 Controlled Nonproduction Rollback Gate

VERSION: v1.1.0-LOCAL-AUTHENTICATED-EOS-RECOVERY-VERIFIED  
TITLE: MW-T12 Nonproduction Rollback and Independent Recovery Certification  
EPITOME: Operational admission criteria, evidence chain and release-denial policy for the existing Foundation MW-T12 task.  
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/architecture/mw-t12-nonproduction-rollback-gate.md  
COLLABORATION / OWNERSHIP: WILSY OS Engineering; Python EOS source owners; independent recovery verifier.  
CERTIFICATION / UPDATE DATE: 2026-11-24  
CHANGELOG: v1.1.0-LOCAL-AUTHENTICATED-EOS-RECOVERY-VERIFIED records 2026-11-24 Mac execution evidence of isolated host Mongo PRIMARY, authenticated Python EOS shutdown/relaunch, 5/5 browser journeys, independent durable Headquarters source readback and cleanup. This is NOT production rollback or infrastructure restore certification.  
CHANGELOG: v1.0.0-FAIL-CLOSED-DRILL-ADMISSION records the verified project update, maps real infrastructure boundaries and defines a non-destructive admission gate before any rollback.  
AUTHORITY: WILSY OS Core Governance / AGENTS.md  
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.  
SECURITY / PRIVACY POSTURE: No secrets, raw MongoDB URIs, principal identifiers, or infrastructure endpoint inventories in evidence attachments.  
TENANT BOUNDARY: Existing canonical Founder tenant `wilsy` must be preserved; no test operation may mutate shared/production state.  
AUTHORITY BOUNDARY: This runbook is not a deployment, rollback, database mutation, IAM grant or approval to perform one.  
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.  
STATUS: EXECUTION GATE OPEN; ROLLBACK NOT CERTIFIED; PRODUCTION RELEASE BLOCKED.

## Evidence established before this gate

- Project: existing `WILSY OS — Unified Operating Platform Foundation`; work item: `MW-T12 — Certify production readiness and rollback`; task lifecycle: `IN_PROGRESS`.
- Founder screenshot of EOS Activity & discussion on 2026-11-24 at 06:53:34 SAST shows a source-labelled task update with the recorded CI checkpoint `23/23`, commit `840b294865a102ede84f77e3fc83ce4dcaabec19`, local build successful with nonblocking warnings, `NOT CERTIFIED` rollback, `READBACK REQUIRED` Strategy outcome, and blocked production release.
- PR #419 simulation head `f4c6bde8faead62b981c7f78dbe32da0ad3e5056` proves synthetic client comment POST/readback behavior only. It does not prove a real database restore or independent, post-refresh EOS readback.
- Canonical EOS database selector is `MONGODB_URI` in `tools/eos/kernel/db.py`; `scripts/start-eos-local-mfa.sh` is a LOCAL development launcher with an AWS KMS probe. Neither proves a given database is a safe rollback target. A loopback URI can tunnel to remote production. The existence of rollback-named legacy Node code is not endorsement for Python EOS recovery.
- No certified isolated deployment inventory, approved rollback mechanism, independently tested backup or recovery measurement was found in the bounded source inspection. Never infer these facts from project status or GitHub workflow success.

## Gate 1A — local isolated Python EOS service recovery (completed at synthetic scope)

On **2026-11-24**, the Founder supplied the complete terminal output from the Mac run on branch `eos/p0-my-work-operating-graph-programme-20261122`, commit `4b01c7f5ac35c9bcfc6581c3a030624aac849fe4`. The observed results are:

| Evidence | Verified output | Scope limit |
| --- | --- | --- |
| Local isolated persistence | `MW_T12_OWNED_REPLICA_PRIMARY=PASS` | Temporary operator-owned host `mongod`; not Atlas or target deployment |
| Python EOS authenticated recovery | `[MW-T12-SERVICE-RECOVERY] status=PASS scope=RUNNER_OWNED_EOS_AUTHENTICATED_READBACK` | Controlled restart of runner-owned EOS on test port; not deployment rollback |
| Authorization readback | Legal commercial-context and productive-work HTTP 200; unauthorized productive-work HTTP 403, System Services reads HTTP 200 and nonresponder HTTP 403, independently repeated after restart | Synthetic fixture principals, not Founder MFA or real tenant entitlement readback |
| Browser acceptance | `5 passed (49.7s)` | Headquarters work journeys at 1440px, 1760px, 1024px and 390px; Legal capacity preservation |
| Independent durable source readback | `[BROWSER-CERT-DURABLE] scope=headquarters status=verified` | Four distinct synthetic Operations tasks, idempotency identifiers, authenticated completion persistence, owner/tenant boundary and foreign-copy denial |
| Owned resource cleanup | `[BROWSER-CERT-CLEANUP] fixture_database=removed`, `MW_T12_OWNED_MONGO_STOPPED=TRUE` | Test-owned resources only |
| Operator completion | `MW_T12_LOCAL_AUTHENTICATED_EOS_RESTART=RUNNER_PASSED` | Local synthetic service recovery certificate ONLY |
| Release denial | `MW_T12_FULL_INFRASTRUCTURE_RECOVERY_CERTIFIED=FALSE` | Production release remains blocked |

**Attestation:** `LOCAL_AUTHENTICATED_PYTHON_EOS_RESTART=CERTIFIED`, `HEADQUARTERS_SYNTHETIC_BROWSER_AND_DURABLE_READBACK=CERTIFIED`. No claim is made of actual Foundation MW-T12 project comment recovery, an independently isolated infrastructure deployment, deployed image rollback, backup restoration of the Python EOS service, production RTO/RPO measurement, live tenant IAM admission, or Strategy outcome attainment.

The browser output was supplied directly by the operator. It is not an independent infrastructure assessor's approval. The suite's durable verifier did independently query the disposable MongoDB source and verify the source-owned work record outcomes rather than accepting UI state as evidence.

**Remaining MW-T12 blockers:** Gate 0 exact Foundation project task/comment readback; Gate 1 isolated nonproduction deployment and backup/rollback mechanism admission; Gates 2–3 actual authorized nonproduction deployment rollback and independently observed recovery; Gate 4 release adjudication. PR #419 remains draft and MW-T12 remains in progress.

## Connection and blast-radius matrix

| Surface | Authority | Preflight or recovery relevance | Allowed action before admission |
| --- | --- | --- | --- |
| `AGENTS.md` | Repository governance | Requires scope discovery, fail-closed certification, one primary file per delivery | Read-only |
| `tools/eos/kernel/db.py` | Python EOS Mongo connection | `MONGODB_URI` can point to shared Atlas or local replicas | Inspect configuration safely; never reveal URI |
| `scripts/start-eos-local-mfa.sh` | Local EOS startup / MFA KMS | Existing local-dev KMS role and canonical database selection; not an isolated drill boundary | Inspect; do not restart or repoint a live EOS |
| `tools/eos/api/projects_router.py` and project registries | Tenant-scoped task/comment source | MW-T12 must be retrieved after refresh with currently admitted authority | Authenticated readback only |
| `client/src/components/workspaces/ProjectsWorkspace.jsx` | Presentation of source-backed project activity | No editor state can serve as recovery evidence | Existing browser readback |
| GitHub PR #419 / Actions | Source + CI evidence, not deployment runtime | Engineering checkpoint, commits and tests | Read-only verification; PR stays draft |
| MongoDB, IAM/KMS, task/evidence storage, deployed runtime | Independently configured infrastructure | Must prove isolation, backup, restoration and access controls | No mutations before explicit admission |

## Gate 0 — independently verify live milestone readback

1. In the existing Foundation project, reopen MW-T12's Activity & discussion after a full refresh.
2. Verify the exact update including 23/23 workflows, commit SHA, `NOT CERTIFIED`, `READBACK REQUIRED`, and `BLOCKED`.
3. Capture EOS source response metadata (record ID, creation time, tenant scope, and response outcome) without cookies, authorization headers, credentials, or raw principal identifiers.
4. A screenshot taken immediately after POST is not independent persistence certification. If readback fails, record `LIVE_READBACK_UNVERIFIED` and do not republish the same comment without checking server history first.

## Gate 1 — controlled nonproduction target admission (mandatory before any drill)

The operator and independent verifier must record all of these facts from authoritative infrastructure inventories:

1. **Distinct deployment:** account, region, cluster/service, image digest, workload role, security boundary, change window and operator. Prove the target is a disposable or dedicated nonproduction deployment; a hostname, `ENV=development`, or loopback port alone is insufficient.
2. **Distinct persistence:** inspect resolved `MONGODB_URI` without logging it, confirm database/cluster identity via the provider and MongoDB read-only metadata. Deny a production/shared Atlas cluster, canonical `wilsy` database, tunnel pointing at live infrastructure, shared KMS key, or shared storage bucket. Synthetic database names are not proof of independent isolation.
3. **Recovery authority:** name the approved Python EOS-compatible deployment rollback/redeploy mechanism and independent verifier; do not use historical Node server migration scripts as proof.
4. **Safety controls:** verify database snapshot/restore point, restore permission, tested backup readability, service stop/start sequencing, abort/rollback thresholds, recoverability of secrets, and cancellation procedures. Preserve audit evidence outside the target that will be restored.
5. **Written approval:** capture exact target identity and approved rollback scope before executing any write, service switch or restore. Missing or inconsistent evidence means `DRILL_ADMISSION=DENIED`.

### Read-only local operator inspection

From the repository root on the operator's Mac, with the correct virtual environment active, inspect only sanitized booleans. This never connects, reads tenant data, deploys or authorizes a drill:

```bash
cd ~/legal-doc-system
source .venv/bin/activate
python - <<'PY'
import os
from urllib.parse import urlsplit
prod = any(os.getenv(k, '').strip().lower() in {'production', 'prod'} for k in ('ENV','WILSY_ENV'))
uri = os.getenv('MONGODB_URI','')
try:
    parsed = urlsplit(uri)
    has_db = bool(parsed.path.strip('/'))
    has_auth = bool(parsed.username)
    target_kind = 'SRV_REMOTE' if parsed.scheme == 'mongodb+srv' else 'STANDARD_OR_OTHER'
except (ValueError, TypeError):
    has_db, has_auth, target_kind = False, False, 'INVALID'
print('PRODUCTION_MARKER_PRESENT=' + str(prod).upper())
print('EXPLICIT_URI_SET=' + str(bool(uri)).upper())
print('MONGO_URI_KIND=' + target_kind)
print('DATABASE_NAMED=' + str(has_db).upper())
print('AUTH_CONFIG_PRESENT=' + str(has_auth).upper())
print('NONPRODUCTION_ISOLATION=NOT_VERIFIED')
print('DRILL_ADMISSION=DENIED_PENDING_INDEPENDENT_EVIDENCE')
PY
```

Do not paste raw environment variables, `MONGODB_URI`, AWS identity credentials or session tokens in issues or project comments. The inspection intentionally does not claim production safety, even if all booleans appear favorable. If canonical EOS resolves a nonproduction dotenv fallback, the explicit-process check can be incomplete; compare with the canonical resolver using a redacted operator-only method before admission.

## Gate 2 — controlled rollback exercise (only after Gate 1 passes)

Capture baseline application release digest and health, replica and storage state, source-backed MW-T12 comment readback, task revisions/counts, current IAM denials and audit continuity. Use the independently approved, infrastructure-specific rollback mechanism to restore the previous known-good **nonproduction** release without mutating production resources. Record exact start/end timestamps, action identity, image digest, alarms, health results and any data-loss interval. Abort on tenant/IAM mismatch, missing backup, unexpected endpoint or material data-integrity discrepancy. No script in this document executes rollback.

## Gate 3 — recovery and independent evidence

Return the isolated target to the intended tested release. A separate verifier must independently confirm:

- API and Python EOS readiness, session/IAM denial and exact-tenant boundaries.
- Known task and comment source readback after recovery, with revision/timestamp and audit consistency.
- Required index/replica/storage readiness and absence of unauthorized side effects.
- Measured RTO/RPO (if available) with observation method, and evidence of any failed check; do not substitute targets or guesses for measured results.
- Redacted logs, build digests, recovery run ID and actual reviewer decision attached to existing MW-T12 via authorized EOS evidence/comment surfaces.

## Gate 4 — release decision

`MW_T12=IN_PROGRESS`, `ROLLBACK=NOT_CERTIFIED`, `STRATEGY_OUTCOME=READBACK_REQUIRED`, `PRODUCTION_RELEASE=BLOCKED`, `PR_419=DRAFT` remain in force until readback, authorized independent nonproduction rollback, restore verification, and source-owned certification are all complete. Record a separately read-back-verified outcome on the existing task; do not create a duplicate Foundation project/task, auto-grant Founder IAM, or infer Strategy attainment from CI.

---

ARTIFACT: docs/architecture/mw-t12-nonproduction-rollback-gate.md  
VERSION: v1.1.0-LOCAL-AUTHENTICATED-EOS-RECOVERY-VERIFIED  
AUTHORITY BOUNDARY: Non-executable engineering admission contract; Python EOS remains source owner.  
TENANT POSTURE: Canonical Founder tenant and all shared/production targets remain untouched.  
FAIL-CLOSED POSTURE: Any unknown environment identity, recovery capability, backup, permission or verification prevents certification.  
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.  
END OF WILSY OS SOVEREIGN ARTIFACT
