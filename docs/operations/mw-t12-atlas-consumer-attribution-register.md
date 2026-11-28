# MW-T12 — Shared Atlas consumer attribution and wildcard retirement register

VERSION: v1.1.0-COST-BOUNDARY-AND-M04-RELEASE-SEPARATION
AUTHORITY: WILSY OS Core Governance / AGENTS.md
EPITOME: Establish a durable, evidence-classified baseline for shared test Atlas dependencies and explicitly prevent deleting global network access on insufficient consumer evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/operations/mw-t12-atlas-consumer-attribution-register.md
COLLABORATION / OWNERSHIP: MongoDB Atlas project metadata, Python EOS kernel DB authority, legacy deployment evidence, MW-T12 synthetic runbook and nonproduction AWS egress operator.
CERTIFICATION / UPDATE DATE: 2026-11-25
CHANGELOG: v1.1.0-COST-BOUNDARY-AND-M04-RELEASE-SEPARATION closes
the verified zero-compute MW-T12 preparation tranche, distinguishes it from
uncertified Fargate rollback, and releases unrelated M04 Strategy work without
claiming production readiness, wildcard retirement or source-owned task update.
CHANGELOG: v1.0.0-CONTROL-PLANE-BASELINE-AND-CONSUMER-ATTRIBUTION records live provider inventory and separately classified possible consumer surfaces; states independent cutover/rollback proof requirements.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No connection-string credentials, secrets, access keys, exact individual source IP list or client identities copied. Public-wide exposure itself is described without inferring compromise.
TENANT BOUNDARY: Project `legal-doc-test` is shared nonproduction data and not the canonical Founder tenant database.
AUTHORITY BOUNDARY: Read-only inventory evidence; no Atlas deletion, runtime identity grant, IAM changes, production authorization or rollback certificate.
FINANCIAL AUTHORITY BOUNDARY: No Fargate activation; Kennel EOS exclusively.

## Decision / source truth

**State: BLOCKED — existing Atlas wildcard must NOT be removed.** Network allowlist metadata is not a current-connection log. The present control plane cannot establish the complete universe of applications, developers, jobs or support tools that may depend on the unrestricted entry. A new task-owned `/32` does not compensate for `0.0.0.0/0`.

This register is a bounded *consumer-discovery inventory*, not a claim that every consumer has been found. The earliest safe action is owner attribution, target binding and scoped admission **for each known active consumer**. A final independent discovery of unknown consumers is required before a shared wildcard may be retired. No automated code in PR #419 is authorized to delete the shared wildcard.

## Provider-observed inventory (25 November 2026)

Source: connected MongoDB Atlas control-plane reads of project `668cdbbd975c3c0f05fca20c`. This is a point-in-time control-plane snapshot; a live consumer census is unavailable.

| Item | Provider-observed value | Consumer ownership proven? |
| --- | --- | --- |
| Project / cluster | `legal-doc-test` / `legal-doc-test` | Project identified; workload owners not proven |
| Cluster ID / tier | `68610bb095eb641674cd41a3` / FREE | Not an active connection proof |
| Provider / region | AWS / AF_SOUTH_1 | Not a source network proof |
| Cluster state | IDLE; MongoDB 8.0.39 patch | Does not prove no active or scheduled consumers |
| Atlas access entries | 45 total: 44 individual `/32` and one `0.0.0.0/0` | **0 of 45** have an owner comment |
| Wildcard expiration | None observed | **Unrestricted entry remains active** |
| Individual access entries | 44; owner and migration state **unknown** | No bulk delete allowed |
| Database user `wilsonkhanyezi` | `readWriteAnyDatabase` on `admin`; no scope listed | Credential usage unknown |
| Database user `wilsy` | `readWriteAnyDatabase` on `admin`; no scope listed | Credential usage unknown |
| Database user `mwt12_6ba397120017` | `readWrite` only on `wilsy_mwt12_synthetic_9e22c06393a4`; cluster-scoped | Dedicated synthetic credential scope observed; no live Fargate connection |

Source-read limitations: Atlas project allowlist entries have no owner comments and the FREE tier does not provide sufficient client audit telemetry to attribute all historic or intermittent source IPs. No absence of observed traffic is proof of nonuse.

## Candidate consumer relationship matrix

*Repository references are possibilities, not runtime proof. Only the dedicated synthetic credential is mapped to a specific intended MW-T12 task via independent AWS SecureString/task-definition metadata; it has not been used by a running ECS task.*

| Consumer class | Concrete inspected evidence | Current active connection established? | Accountable migration evidence still required |
| --- | --- | --- | --- |
| Canonical Python EOS on local Mac | `tools/eos/kernel/db.py` resolves only `MONGODB_URI`; `tools/eos/api/server.py` owns lifecycle | **No** binding to this specific Atlas project verified | Locally verify resolved *host and DB classification only*, session + process ownership and actual egress CIDR without revealing URI |
| Legacy application/test data | `docs/operations/eos-nonproduction-atlas-target-verification.md` observed `test-db` with clients/chats/users/invoices/documents on 2026-11-04 | Historic data, **not** proof of currently running application | Identify actual maintained deployments and runtime owners; separately confirm shutdown or scoped CIDR and data restore |
| Retired Node/legacy deployment configuration | `docker-compose.yml` references `PROD_MONGODB_URI`, `TEST_MONGODB_URI`; historical Node files retained, backend retired | **No** active Node backend inferred | Source-owned decommission record, current machine/container enumeration and evidence no background jobs remain |
| CI and operational jobs | `Jenkinsfile` refers to `TEST_MONGODB_URI`; repository Atlas metadata workflow is manual/read-only and isolated | **No** job execution against this cluster confirmed | Runner/workflow ownership, last successful connection, secret target fingerprint and runner egress source |
| Developer/admin clients | Broad database users `wilsonkhanyezi`, `wilsy`; 44 unlabelled individual source entries | **No** assignment of username to IP or device | Operator/device/source CIDR owner attestation, independent test with narrow source rule, currentness and expiry |
| Nonproduction ECS MW-T12 recovery | Dormant task definitions `:3` historical, `:4` current; SSM `/wilsy/mwt12/nonproduction/synthetic-mongodb-uri`; outbound SG 3 Atlas node `/32` rules independently verified after CloudFormation update | **No** tasks launched, no Fargate public source IP, no authenticated canary read | Explicit paid-drill approval, exact task ENI attribution, task-owned temporary /32, strict Atlas TLS authentication and stable canary across 4→3→4 |
| Unknown third parties, unattended scripts and historic hosts | Neither owner comments nor complete per-client audit evidence available | **UNKNOWN** | An independent closed-world discovery/ownership approval, not merely a signature declaring unknowns absent |

This matrix does **not** authorize production EOS promotion onto the legacy `test-db`. The 2026-11-04 discovery expressly rejected that target for general EOS provisioning.

## Per-source owner record contract

Before any one of the 44 historical `/32` entries is changed, an independent project-controlled evidence record must bind: exact Atlas access-list entry **fingerprint**, responsible human/team, actual workload or operator, source IP/CIDR attribution method and capture time, environment, actual target cluster/database (metadata only), database credential identity/role (not password), replacement CIDR/endpoint or witnessed retirement, last authenticated test and failure recovery, evidence location, validity window and independent reviewer. No attribution may be inferred from an entry's name, absence of comments, or geographic address.

For the two broad database users, require a *separate* owner inventory; a network rule migration does not authorize credential removal, and a credential scope test does not prove network ownership.

## Wildcard retirement admission — all are mandatory

1. **Provider snapshot current:** independently re-read all Atlas entries and DB users immediately before any contemplated change; reject unknown changes and mismatched project/cluster.
2. **Known client coverage:** each known live/scheduled API, worker, developer, CI runner, administrative script and legacy consumer has independently verified source ownership, narrow replacement path and failed-open behavior ruled out.
3. **Unknown client risk resolved:** an accountable independent reviewer confirms through multiple independent sources (deployment inventory, secret target fingerprints, source egress measurements, schedules, operator attestation and any available provider activity) that no unaccounted dependency will be stranded. FREE-tier telemetry insufficiency must be recorded; do not assert proof from missing logs.
4. **Replacement is live:** authenticate every migrated consumer using its own scoped identity and source network, then prove intended read/write or safe read-only operations. No real tenant data copied to synthetic fixtures.
5. **Rollback is prepared:** capture the original full provider entry snapshot/fingerprint; independently prove a reversible provider-controlled network operation with ownership, duration, escalation and safe fallback. An untested ability to re-add `0.0.0.0/0` is not an approved rollback strategy.
6. **Governed approval:** explicit authorized decision for a shared network security change, separate from MW-T12 compute approval and any production authorization.

Until all six gates hold, output **`MW_T12_ATLAS_WILDCARD_RETIREMENT=BLOCKED`**. A PR comment or operator assertion cannot by itself certify a live consumer census.

## Governed closure decision — no-cost preparation versus live release

**Decision date: 2026-11-25.** The *zero-paid-compute preparation workstream* may be marked ENGINEERING_PREPARATION_COMPLETE based on existing scoped certificates, but this is NOT an assertion that the single MW-T12 Project task has reached `DONE`. Its existing source-owned status must remain `IN_PROGRESS` until governed authorized completion independently reads back from EOS. No GitHub comment may substitute for that source update.

| Phase | Decision | Evidence / required completion |
| --- | --- | --- |
| Exact-source local regression and offline rollback preparation | Preparation complete | 23/23 GitHub exact-head CI on `6922f9a5d849677302caaf64f598138762e02308`; earlier source-version, same-data and loopback EOS recovery evidence are separate, not a production-grade image drill |
| Dormant immutable-image-backed ECS metadata | Complete | Historical/current secure task definitions `:3`/`:4` registered/read back; no ECS task started |
| Reviewed AWS destination egress | Complete | CloudFormation three TCP/27017 node rules executed and actual closed SG independently verified; zero ECS compute |
| Running local Python EOS destination | Network-only source attribution complete | Mac EOS port-9095 listener owns three established peers matching fresh DNS of distinct `Wilsy / legalDocSystem` cluster; no observed `legal-doc-test` peers |
| Authenticated local EOS credential/database binding | Not certified; noncritical to already completed *network* preparation | Independent auth/current database verification must not print credentials, should be source-owned and must not be confused with socket identity |
| Shared test-cluster consumer census and wildcard retirement | Security gate blocked | 45 entries/one wildcard, zero owner comments; unrelated legacy/test consumers still not attributed; no deletion permitted |
| Live image recovery current → historical → current | Future cost-bearing certification gate | Requires explicit bounded financial authorization, authenticated synthetic durable-canary readback, proven storage persistence and restore, exact image provenance and independent rollback evidence |
| Production promotion | BLOCKED | No qualified live rollback or release authorization |

### Scope and schedule boundary

**Do not perform another local EOS socket-classification iteration without new contradictory evidence.** The network target is independently matched to `Wilsy / legalDocSystem`; current shell lack of `MONGODB_URI` is not a service failure. Do not treat the separate `legal-doc-test` legacy wildcard as proof of local EOS exposure. This remains a distinct security backlog dependency.

**Release M04 Strategy delivery to continue in parallel now:** the existing Foundation Project, governed My Work/Daily Attention task graph, accountable owner, published strategic objective and source-owned tasks remain the approved work surfaces. Do not create another project, change release authority or report an unverified EOS task write as persisted. MW-T12 may be revisited at the next explicit, funded nonproduction recovery acceptance gate, rather than gating unrelated application development.

The trigger to reopen the *cost-bearing* MW-T12 tranche is an authorized budget/drill window plus per-consumer impact acknowledgement, approved bounded task launch, scoped Atlas access operation and an independently executable verification/rollback plan. No implied approval arises from `PROCEED` on no-cost development.

## Nonproduction rollback-drill status

The previously approved CloudFormation *outbound* network-only change has executed with actual SG readback: three Atlas destinations on TCP/27017, no inbound ingress, zero ECS compute. This is not equivalent to Atlas *inbound* access-list admission. Synthetic task definitions `:3`/`:4` are registered but dormant. Exact-source-IP bootstrap, private/temporary access, authenticated current→historical→current readback, durable canary and measured restore remain **UNCERTIFIED**.

**Final state:** MW-T12 IN_PROGRESS · PR #419 DRAFT · Atlas wildcard UNCHANGED · Paid Fargate task NOT LAUNCHED · Production BLOCKED.

---

ARTIFACT: docs/operations/mw-t12-atlas-consumer-attribution-register.md  
VERSION: v1.1.0-COST-BOUNDARY-AND-M04-RELEASE-SEPARATION  
AUTHORITY BOUNDARY: Consumer evidence and fail-closed decision register only.  
TENANT POSTURE: Shared nonproduction; no real tenant reads or writes.  
FAIL-CLOSED POSTURE: No consumer-coverage proof, no wildcard deletion.  
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.  
END OF WILSY OS SOVEREIGN ARTIFACT
