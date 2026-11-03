# EOS Runtime-to-Atlas Connection Chain — Evidence and Migration Plan

**Status:** Repository-side connection contract inspected and one production-environment classification defect corrected. Live runtime-to-Atlas binding remains unproven.  
**Repository:** `Mawilis/legal-doc-system`  
**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Scope:** Canonical Python EOS API, MongoDB Atlas business persistence, deployment identity and least-privilege migration.  
**Safety:** Read-only discovery only. No production URI, credential, database user, access-list entry, cluster, cloud role or workload was changed.

## 1. Executive finding

The canonical Python EOS API is designed to use one database authority:

- Runtime variable: `MONGODB_URI`.
- Connection implementation: `tools/eos/kernel/db.py`.
- API composition root: `tools/eos/api/server.py`.
- API startup calls `connect_db()`; shutdown calls `disconnect_db()`.
- The database is selected from the database component of the URI. The URI is therefore deployment authority, not a tenant/request parameter.
- The dedicated EOS image is `infra/docker/Dockerfile.eos`, which starts `tools.eos.api.server:app` on port 9095.
- The Kubernetes target manifest is `k8s/eos-api-production.yaml`. It injects `MONGODB_URI` from Secret `wilsy-eos-runtime-secrets`, key `mongodb-uri`.

This establishes the intended code-level chain:

`deployment secret → MONGODB_URI → tools.eos.kernel.db.connect_db() → PyMongo MongoClient → database encoded in URI → Python EOS registries`

It does **not** establish which Atlas project/cluster is used by a live process. The manifest is a repository artifact, not evidence that it has been applied. The dedicated image-publication workflow publishes an immutable GHCR image; its own authority boundary explicitly excludes deployment, Kubernetes, AWS infrastructure and runtime IAM.

## 2. Runtime artifact map

| Layer | Repository evidence | What it proves | What it does not prove |
| --- | --- | --- | --- |
| Python EOS entrypoint | `infra/docker/Dockerfile.eos` | Python 3.12 image runs Uvicorn `tools.eos.api.server:app` on 9095 as UID 10001 | That an instance is deployed |
| API lifecycle | `tools/eos/api/server.py` | Startup calls `connect_db()`; shutdown calls `disconnect_db()` | Live startup success |
| Database authority | `tools/eos/kernel/db.py` | Only `MONGODB_URI` is resolved; no `MONGO_URI` or `DATABASE_URL` fallback | Actual secret value or Atlas target |
| Kubernetes deployment template | `k8s/eos-api-production.yaml` | Defines 2 replicas, `wilsy-eos-api` ServiceAccount, ClusterIP Service and secret reference for `MONGODB_URI` | That a live Kubernetes cluster or deployment exists |
| Runtime secret example | `k8s/eos-api-runtime-authority.example.yaml` | Documents the expected secret key without embedding a real URI | That the secret has been created or populated |
| Image publication | `.github/workflows/eos-image-publication.yml` | Publishes the Python EOS image with digest/provenance/SBOM | That the image was deployed |
| Atlas discovery workflow | `.github/workflows/eos-atlas-control-plane-discovery.yml` | Defines manual read-only Atlas metadata discovery on a dedicated `atlas-control-plane` runner | EOS runtime connectivity or database authentication |

### Legacy deployment files are not the canonical EOS chain

The repository also contains older Node/WILSY Docker Compose configurations:

- `docker-compose.yml` exposes `PROD_MONGODB_URI`, `TEST_MONGODB_URI` and `ACTIVE_DATABASE` to the legacy `wilsy-os` service and worker.
- `docker-compose.prod.yml` exposes `MONGODB_URI` through the legacy Node image and `server/.env.production`.

These files are not the dedicated Python EOS image/entrypoint. They must not be used as evidence that Python EOS is connected to either Atlas project. In particular, do not use the old production/test selector as the canonical EOS database authority.

## 3. Production-environment classification defect corrected

The Kubernetes EOS manifest sets `WILSY_ENV=production`, but the database connector originally recognized production only through `ENV=production`. That mismatch could classify the manifest's EOS process as development for database security decisions:

- repository dotenv loading could be attempted when the process intended production;
- the development flag could enable invalid TLS certificate/hostname allowances.

The connector has now been corrected so **either** `WILSY_ENV` or `ENV` declaring `production`/`prod` makes the process production. This is deliberately fail-safe: an unset legacy `ENV` no longer downgrades an EOS deployment that sets `WILSY_ENV`.

Changes:
- `tools/eos/kernel/db.py`: production detection checks both environment markers.
- `tests/unit/test_kernel_db_configuration_authority.py`: regression coverage added for WILSY_ENV-only production, dotenv suppression, fail-closed missing URI and strict TLS certificate/hostname validation.

The tests must pass in CI before this fix is treated as certified. No live deployment has been restarted or changed by this repository correction.

## 4. Atlas inventory — observed but not bound to EOS

The connected Atlas account exposes two projects in AWS `AF_SOUTH_1`:

| Atlas project | Cluster | Tier | Paused | Atlas state | MongoDB |
| --- | --- | --- | --- | --- | --- |
| `Wilsy` | `legalDocSystem` | FREE | No | IDLE | 8.0.36 |
| `legal-doc-test` | `legal-doc-test` | FREE | No | IDLE | 8.0.36 |

Atlas `IDLE` is the reported provider state; it is not evidence of an authenticated EOS application connection or active production traffic.

No authoritative source currently binds `MONGODB_URI` in a live EOS deployment to either cluster. Do not infer production from the project name `Wilsy`, cluster name `legalDocSystem`, region or account ownership. The test project name is also not proof of its actual consumers.

### Existing Atlas users observed

| Project | User | Listed role | Scope |
| --- | --- | --- | --- |
| Wilsy | `wilsonkhanyezi` | `atlasAdmin` on `admin` | Cluster `legalDocSystem` |
| Wilsy | `khanyeziw` | `atlasAdmin` on `admin` | Cluster `Cluster0` (not in the current cluster inventory) |
| legal-doc-test | `wilsonkhanyezi` | `readWriteAnyDatabase` on `admin` | No cluster scope listed |
| legal-doc-test | `wilsy` | `readWriteAnyDatabase` on `admin` | No cluster scope listed |

These are observed account-level users, not proof that any one of them is used by the EOS API. None is approved as the dedicated production EOS runtime identity. Do not revoke or alter them until consumer attribution and rollback are complete.

## 5. Network-access evidence

| Project | Entries | Public-wide IPv4 rule | Comments |
| --- | ---: | ---: | ---: |
| Wilsy | 100 | 0 | 0 |
| legal-doc-test | 45 | 1 (`0.0.0.0/0`) | 0 |

The test project's unrestricted entry is a confirmed exposure of the network perimeter, not proof of successful access or compromise. The 100 Wilsy entries are not attributable from their blank comments. Do not bulk-delete either list.

The Atlas integration available for this discovery can inspect and add access-list entries, but does not expose a deletion operation. No network policy change was made.

## 6. Runtime host and deployment evidence

The previously inspected AWS account inventory found no EKS clusters in any of its 18 enabled regions and no ECS clusters or running EC2 instances in the queried regions. The local Kubernetes context was unset. The connected Vercel account had no matching project. The repository's EOS image workflow is publication-only, not deployment.

These checks do not exclude hosting in another cloud account, another AWS account, a non-AWS platform, a privately operated cluster or a self-hosted machine. They do mean that no inspected source currently proves the host for the Python EOS workload.

The Atlas control-plane workflow is a manual metadata-discovery workflow requiring a dedicated runner and Atlas OAuth secrets. It is not a runtime deployment workflow and cannot establish the EOS runtime's source egress IP or workload identity.

## 7. Canonical target and identity migration design

Do not choose a production Atlas target until the deployed workload's secret reference and actual database target are tied together through trusted deployment evidence.

Once the target is proven:

1. Record the live deployment platform, deployment identifier, immutable EOS image digest, namespace/service/task identity and region.
2. Inspect the deployment secret **by metadata/reference only**. Do not print, export or copy the URI. Resolve its host and database fingerprint inside a controlled, secret-safe process.
3. Match that fingerprint to the Atlas project and cluster using Atlas control-plane metadata. Record project ID, cluster ID/name, database name and region; never record credentials.
4. Attribute every live consumer of the current database users and every Atlas network entry. Include Python EOS API replicas, workers, Node/BFF services, scheduled jobs, migrations, administrative operators, CI and support tooling.
5. Select the production project/cluster only after data ownership, environment, residency, backup tier, network path and runtime ownership are approved. If neither existing FREE cluster satisfies production controls, provision a separate production target through a separately approved change; do not silently promote a test cluster.
6. Inventory the actual EOS database operations and collection set. Design a custom role scoped to the exact database and necessary actions. A temporary built-in `readWrite` on the exact EOS database may be considered only with a time-bounded exception and evidence; `readWriteAnyDatabase`, `atlasAdmin`, `dbAdminAnyDatabase` and control-plane roles are prohibited for the app.
7. Create a new unique production-only database user. Keep its secret in the actual platform secret manager. Test and production identities must not authenticate across environments.
8. Test the candidate identity against a production-like disposable/isolated target: startup indexes, transactions, read/write paths, change streams if used, tenant isolation, and explicit denial of administrative operations.
9. Establish the runtime's fixed egress/private endpoint and replace broad Atlas access with only verified consumer ranges. Preserve a rollback path.
10. Perform an overlap cutover: deploy new credential, verify every replica/worker and application operation, observe stability, then revoke the old user after rollback expiry. Rotate the test project independently.
11. Validate Atlas backup policy and perform an isolated restore before production approval.

## 8. Required proof bundle

A runtime-to-Atlas chain is considered proven only when all of the following are linked by immutable deployment/change identifiers:

- Live EOS deployment metadata and image digest.
- Actual platform-native workload identity.
- Secret-manager object identifier/version and access policy (never its value).
- Secret-safe host/database fingerprint derived from the live URI.
- Matching Atlas project/cluster identity and database name.
- Runtime user name, role definitions and exact database/collection scope.
- Runtime egress/private-network identity and corresponding Atlas allow-list evidence.
- Successful authenticated startup and end-to-end tests from the actual workload.
- Backup configuration and isolated restore report.
- Approved migration/cutover/rollback record and old-credential revocation evidence.

A repository manifest, an Atlas cluster existing, an image being published, or a CI replica-set test is not sufficient on its own.

## 9. Current gate disposition

| Gate | State |
| --- | --- |
| Canonical Python EOS DB variable and lifecycle | **Established in source** |
| Production environment detection | **Corrected in source; CI pending** |
| Actual EOS runtime host | **Unproven** |
| Live deployment secret reference/version | **Unproven** |
| Runtime URI host/database fingerprint | **Unproven; secret not inspected or exposed** |
| Atlas production project/cluster mapping | **Unproven** |
| Dedicated production EOS database user | **Not provisioned/certified** |
| Consumer attribution for existing users | **Open** |
| Restricted Atlas network access | **Open; test project has 0.0.0.0/0** |
| Backup/restore certification | **Not evidenced** |

**Release decision: NO-GO for production credential migration or production activation.** The repository-side security correction and evidence map are safe to advance; live credentials remain untouched until the complete chain is proven.


## 8. Critical correction: the full application has additional Mongo clients

The earlier description of `MONGODB_URI` as the sole application MongoDB URI authority is incomplete. Source inspection of the mounted subscription and plan routers found two independent module-level clients:

| Registry | URI precedence | Database selection | Collection |
|---|---|---|---|
| Subscription | `WILSY_SUBSCRIPTION_MONGO_URI` → `MONGODB_URI` → localhost fallback | URI default database, fallback `wilsy` | `subscriptions` |
| Plan | `WILSY_PLAN_MONGO_URI` → `MONGODB_URI` → localhost fallback | `WILSY_PLAN_MONGO_DATABASE` → URI default → `wilsy` | `plans` |

The canonical kernel client remains a third independent composition. These three clients may share the same Atlas target if configured identically, but that is not guaranteed by source.

Both dedicated registries use a localhost fallback if their dedicated URI and `MONGODB_URI` are absent. This must be treated as a fail-closed configuration defect candidate: the API can otherwise import successfully while billing registry calls target a local MongoDB instead of the deployment-owned EOS database. Production behavior depends on actual environment variables, which have not been verified.

Subscription creation invokes `_ensure_indexes` and creates four indexes at runtime. Plan catalogue reads perform read-only index validation; explicit `PlanRegistry.provision_indexes` owns plan DDL.

**Required resolution before runtime role design:**
1. Remove independent URI/database authorities or prove and enforce one canonical injected database/client contract.
2. Remove localhost fallbacks for production and fail startup/readiness when required database configuration is absent.
3. Preserve caller-owned session propagation across subscription/entitlement composition.
4. Move subscription index DDL to the separate provisioner and keep runtime verification read-only.
5. Compare redacted fingerprints for canonical kernel, subscription and plan targets before any Atlas role/user work.

This correction supersedes any earlier statement that all EOS Python persistence is proven to use only the kernel `MONGODB_URI`.
