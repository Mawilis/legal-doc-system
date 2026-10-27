# Python EOS-only API runtime migration

**Status:** implementation in progress; production closure requires exact-head CI and runtime certification.

## Canonical target
- Python EOS ASGI application: `tools.eos.api.server:app`, port 9095.
- Vite is a development client only; all API proxy paths terminate at Python EOS.
- The API BFF no longer owns transport or PDF presentation.
- Node files retained only for migration/reference and legacy test compatibility are classified `MIGRATION_ONLY`, not as production runtime authority.

## Migrated route contracts

| Browser path | Python EOS target | Contract |
|---|---|---|
| `/api/auth/**` | `/api/auth/**` | Existing canonical authenticated auth router |
| `/auth/**` | rewrite to `/api/auth/**` | Compatibility alias only |
| `/api/tenants/**` | `/api/tenants/**` | Existing tenant router |
| `/api/business/tenants/**` | rewrite to `/api/tenants/**` | Compatibility alias only |
| `/api/employees/**` | `/api/employees/**` | Existing employee router |
| `/api/kernel/**` | `/api/kernel/**` | Existing kernel router |
| `/api/plans/**` | `/api/plans/**` | Existing plan router |
| `/api/subscriptions/**` | `/api/subscriptions/**` | Existing subscription router |
| `/api/billing/**` | `/api/billing/**` | Existing Python billing router; financial mutations retain Kennel EOS boundaries |
| `/api/legal-acceptance/**` | `/api/legal-acceptance/**` | Existing authenticated legal-acceptance router |
| `/api/legal-operations/**` | `/api/legal-operations/**` | Existing guarded Legal Operations routers |
| `/api/wilsy-ai/legal-services/**` | `/api/wilsy-ai/legal-services/**` | Existing Python EOS legal-services router |
| `/api/wilsy-ai/legal-next-actions/**` | `/api/wilsy-ai/legal-next-actions/**` | Existing Python EOS advisory router |
| `/api/generate/pdf` | `/api/generate/pdf` | Authenticated presentation-only PDF export |

## PDF authority contract
The Python PDF route requires the canonical authenticated identity dependency, caps the serialized request at 10 MiB and rendered fields at 120, rejects a caller-selected top-level tenant context that differs from the authenticated request context, and produces SHA-512 / SHA3-512 integrity digests. These are hashes, not signatures. Caller-supplied payloads are explicitly labeled **source unverified**. The endpoint creates no legal issuance, invoice, payment, settlement, institutional ratification, or matter-disclosure authority.

## Certification required before production promotion
- Run focused PDF router tests and the Python EOS suite.
- Run client build/static checks and the authenticated browser certification.
- Prove route parity against the prior BFF contract, especially billing PDF consumers and alias paths.
- Verify deployment manifest, image digest, runtime configuration, workload identity, and live readiness.
- Do not delete remaining Node migration/reference files until their non-runtime consumers and tests are proven absent.
