# TITLE: WILSY EOS Global Principal MFA — Isolated MongoDB Certification Target
# VERSION: v1.0.0-GLOBAL-PRINCIPAL-MFA-MONGO-CERTIFICATION
# AUTHORITY: Local integration certification operations only; no production database authority.
# EPITOME: Establish a dedicated localhost-only MongoDB replica set for Global Principal MFA real-Mongo tests, isolated from the canonical EOS application database.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/eos/global-principal-mfa-certification-mongodb.md
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS owns application persistence and identity truth.
# CERTIFICATION OR UPDATE DATE: 2026-11-09
# CHANGELOG:
#   v1.0.0-GLOBAL-PRINCIPAL-MFA-MONGO-CERTIFICATION documents the isolated
#   single-node replica-set service, test-only connection variables, read-only
#   preflight markers and safe data/volume lifecycle.
# COMPLIANCE: AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
# SECURITY / PRIVACY POSTURE: Test-only localhost database; never accepts or reuses production application credentials.
# TENANT BOUNDARY: Synthetic integration fixtures only; no canonical tenant data is targeted.
# AUTHORITY BOUNDARY: Local certification database only; no application or production persistence authority.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.

# Global Principal MFA — isolated MongoDB certification target

This MongoDB replica set exists only for the Global Principal MFA real-Mongo integration suites. It is deliberately separate from the EOS application database (`wilsy`) and does not reuse the application's `MONGODB_URI`.

## Start the dedicated replica set

From the repository root, with Docker Desktop running:

```bash
docker compose -f infra/docker-compose.global-principal-mfa-cert.yml up -d
```

The service binds only to localhost on port `27019`, runs a single-node replica set named `wilsyGlobalPrincipalCertRS`, and stores data in the dedicated Docker volume `wilsy_global_principal_mfa_cert_data`.

Wait until it is healthy:

```bash
docker compose -f infra/docker-compose.global-principal-mfa-cert.yml ps
```

The service should report `healthy`. Its health check initializes the replica set if needed and waits for its primary.

## Configure only the test process

In the same terminal used for pytest:

```bash
export TEST_GLOBAL_PRINCIPAL_MONGO_URI='mongodb://127.0.0.1:27019/?replicaSet=wilsyGlobalPrincipalCertRS'
export TEST_GLOBAL_PRINCIPAL_MONGO_DATABASE='wilsy_global_principal_mfa_cert'
export TEST_GLOBAL_PRINCIPAL_MONGO_REPLICA_SET='wilsyGlobalPrincipalCertRS'
```

These variables are intentionally distinct from `MONGODB_URI`. Do not copy the application URI into any test variable and do not point these tests at the `wilsy` database.

Run the read-only preflight from the MFA certification instructions. It must print:

```text
CERTIFICATION_URI_CONFIGURED: True
CERTIFICATION_DATABASE: wilsy_global_principal_mfa_cert
REPLICA_SET: wilsyGlobalPrincipalCertRS
PRIMARY_AVAILABLE: True
MONGO_CERTIFICATION_TARGET: VERIFIED
```

Only after that verification should the selected Global Principal MFA integration tests be run.

## Data and lifecycle safeguards

- This is a local, single-node replica set for transaction semantics and integration testing; it is not a production topology.
- Its port is bound to `127.0.0.1`, not exposed on the LAN.
- The named volume is dedicated to this certification service.
- The selected fixtures create uniquely suffixed collections in the dedicated database and drop those collections during teardown.
- Do not run `docker compose down -v` unless you intentionally want to erase this certification volume.
- Do not attach the EOS application runtime to this service.
- No AWS resources, MFA factor records in the application database, or production configuration are changed by starting this stack.

# ARTIFACT: docs/eos/global-principal-mfa-certification-mongodb.md
# VERSION: v1.0.0-GLOBAL-PRINCIPAL-MFA-MONGO-CERTIFICATION
# AUTHORITY BOUNDARY: Local real-Mongo integration testing only; no production data authority.
# TENANT POSTURE: Test-only isolated database; no canonical tenant records are accessed or mutated.
# FAIL-CLOSED POSTURE: Integration tests run only after the test-specific replica-set URI and primary are verified.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
