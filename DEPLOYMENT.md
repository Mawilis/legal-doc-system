# WILSY OS Deployment Guide

## Local Development
```bash
npm run dev
npm run test:pipeline
Docker Deployment
Bash
docker-compose up -d --build
Production Commands
Bash
npm run seed:master          # Root anchor
npm run test:pipeline        # Full test
npm run onboard <file.json>  # Onboard tenant
Environment Variables
Copy .env.example → .env and configure MONGODB_URI.

Recommended Production Stack
Docker + Docker Compose

MongoDB Atlas (or self-hosted)

PM2 or Docker for process management

Nginx as reverse proxy (SSL)

Your Sovereign Onboarding System is now 100% complete.
You have:

Professional forms

Strict validation

Multiple polished scripts

API endpoint

Docker support

Postman collection

Full documentation

Final Test Sequence:

Bash
npm run test:pipeline
npm run onboard server/data/royal-logistics-onboarding.json

## Python EOS legal-evidence reconciliation deployment gate

The canonical Python EOS application is launched by
`python -m uvicorn tools.eos.api.server:app --host 0.0.0.0 --port 9095`.
The dedicated internal route is
`POST /api/legal-operations/evidence-provider/reconciliation`; it is not the
generic `/runtime/execute` endpoint.

Before enabling an approved internal caller, configure these values through the
deployment secret/configuration manager (never commit credentials or production
URIs):

- `MONGODB_URI`: canonical business database URI.
- `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI`: separately approved
  audit database URI. It must resolve to a different host/database target from
  `MONGODB_URI`.
- Existing canonical workload trust settings:
  `WILSY_INTERNAL_AUTH_SERVICE_ID`,
  `WILSY_INTERNAL_AUTH_AUDIENCE`,
  `WILSY_INTERNAL_AUTH_KEY_ID`, and
  `WILSY_INTERNAL_AUTH_SECRET`.
- `WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID`: fixed server-owned
  tenant identifier, sourced from the approved reconciliation deployment scope.
- `WILSY_LEGAL_EVIDENCE_S3_BUCKET` and
  `WILSY_LEGAL_EVIDENCE_S3_REGION`: the existing Legal Evidence provider's
  bucket and region, not the separate HR-document bucket. The production
  Kubernetes manifest binds these through the `wilsy-eos-runtime` ConfigMap
  keys `legal-evidence-s3-bucket` and `legal-evidence-s3-region`.
  `WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID` is optional only if the approved
  storage policy does not require a customer-managed KMS key.
- The tenant identifier is bound from Secret key
  `legal-evidence-reconciliation-tenant-id`; do not infer it from a request.

An authorized deployment operator must run the audit-index provisioner with
the exact same two URI variables that the application will use:

```bash
python -m tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_audit_provisioner
```

Record its `AUDIT_TARGET_FINGERPRINT` output in the deployment change record
and compare it with the sanitized fingerprint emitted by runtime bootstrap.
The provisioner creates/verifies audit indexes; runtime startup verifies those
indexes read-only and refuses to enable the composition when they are absent or
the audit target aliases the business target. Neither fingerprint contains URI
credentials. Do not copy production URI values into logs, pull requests, or
support tickets.

The request body must be UTF-8 JSON with exactly one field,
`idempotency_key`; that exact body is signed by the existing internal
workload transport. Each retry requires a fresh signed nonce. The route
reauthorizes every retry and replays only the exact stored result for the same
authenticated service, operation key, signed body, and server-resolved scope.

Production remains NO-GO until the actual internal caller is approved and wired
to this exact path/body contract, the deployment audit fingerprint parity is
observed, the unified production security audit passes, and operational review
accepts the end-to-end HTTP/real-Mongo certification.

