# Python EOS-Only Runtime Migration Campaign

**Status:** In progress; no production cutover authorized by this document.  
**Baseline:** `main` at `c26a564802d56be3f2e6875dd94484d3a88f93f3` (reconfirm before implementation).  
**Owner:** WILSY OS Core Engineering  
**Authority boundary:** This plan changes no identity, tenant, legal, billing, payment, audit, execution, or settlement authority.

## Objective

Make Python EOS the only application API authority and remove the Node BFF runtime only after every client-consumed Node-owned contract has a tested, behaviorally equivalent Python EOS implementation. This is a capability migration, not a proxy-target edit.

## Repository-observed routing baseline

The current Vite configuration explicitly routes these surfaces to Python EOS at port 9095:

| Client path | Current target | Notes |
|---|---|---|
| `/api/auth` | Python EOS | Canonical auth router; prefix retained |
| `/auth` | Python EOS on this branch | Legacy alias rewrites to `/api/auth` |
| `/api/billing/platform`, `/api/billing/client` | Python EOS | Rewrites to `/billing/*` |
| `/api/billing/{plans,summary,analytics,credit-scores,forensic-status}` | Python EOS | Read-model subset |
| `/api/kernel` | Python EOS | Prefix retained |
| `/api/tenant-branding` | Python EOS | Prefix retained |
| `/api/legal-operations` | Python EOS | Prefix retained |
| `/api/legal-acceptance` | Python EOS | Prefix retained |
| `/api/tenants`, `/api/employees` | Python EOS | Directory contracts |
| `/api/business/tenants` | Python EOS | Rewrites to `/api/tenants` |
| `/api/plans`, `/api/subscriptions` | Python EOS | Previously forwarded unchanged by the BFF |
| `/api/wilsy-ai/legal-services`, `/api/wilsy-ai/legal-next-actions` | Python EOS | Selective legal routes now use canonical EOS routers |
| `/billing/*`, `/api/billing/*` | Python EOS | `/api/billing/*` rewrites to `/billing/*` |
| `/api/*` general fallback | Python EOS | Unknown/unimplemented routes fail at EOS rather than being sent to Node |
| `/api/generate/pdf` | Node temporarily | Preserves the existing authenticated enterprise PDF renderer until a certified Python equivalent exists |

The current branch routes the general `/api` catch-all directly to Python EOS and makes the Node-owned `POST /api/generate/pdf` route explicit. The observed `server/server.js` entrypoint proxies `/api/auth`, tenant/employee directories, kernel, plans, subscriptions, billing and two selective WILSY AI legal routes to Python EOS; the Vite configuration now routes those contracts directly to their Python targets. The billing alias preserves the existing `/api/billing/*` to `/billing/*` rewrite, and `/api/business/tenants` preserves its alias rewrite to `/api/tenants`.

The Node runtime is **not removable yet**: the PDF route still calls `businessArtifactPdfController.js` and `wilsyEnterprisePdfRenderer.js`, which perform authenticated identity resolution, billing/CRM proof enrichment, request/Merkle proof construction, renderer-specific response headers, and binary PDF streaming. Those semantics do not yet have a certified Python equivalent. The local stack launcher still starts the Node API for that explicit PDF route. The production-surface policy still marks Node server/renderer/package paths `RETAIN`. `orchestrator.js` also names the Node server and a Node worker, but its current reachability from active startup commands must be established before deleting it; `server/package.json` starts `server/server.js`, not `server/app.js`.

The general catch-all is no longer routed to Node, but the BFF process remains temporarily for PDF. The next removal gate is a faithful Python PDF implementation plus caller, identity, tenant, artifact-seal, renderer, binary-response and regression certification.

## Required route parity matrix

For every Express route mounted by `server/server.js`, `server/app.js`, and its route modules, record:

1. HTTP method and canonical path (including aliases and rewrites).
2. Client callers and request/response schema.
3. Authentication, principal, tenant, role, entitlement and resource-scope authorities.
4. Status codes, error contracts, headers, streaming/file semantics and content types.
5. Persistence collections, transaction/session owner, idempotency/replay rules and audit evidence.
6. Financial/legal side effects and the authority that owns each side effect.
7. Python EOS implementation path, exact regression tests, and evidence proving parity.

An endpoint is not considered migrated because a similarly named Python route exists. The contract must preserve behavior and authority boundaries.

## Work sequence and exit gates

### Gate A — Discover and map

- Enumerate every Express mount, route registration, rewrite, websocket, worker entrypoint, scheduled job and runtime dependency.
- Compare against FastAPI routes actually mounted in `tools/eos/api/server.py`, not just files that exist.
- Produce a reviewed route matrix and mark each contract `MIGRATED`, `NOT MIGRATED`, or `NOT APPLICABLE WITH EVIDENCE`.

### Gate B — Wire canonical Python EOS equivalents

- Implement missing equivalents in Python EOS using existing canonical domain services and authorization compositors.
- Preserve response/error and persistence contracts without cloning business authority or bypassing current tenant/transaction boundaries.
- For PDF generation, preserve authenticated identity resolution, tenant scope, artifact integrity/sealing, QR verification and document response semantics; do not substitute an unauthenticated generic PDF endpoint.
- Keep Node routing for every contract that is not yet parity-certified.

### Gate C — Certify behavior

- Add Python tests for request/response schemas, authorization allow/deny, tenant isolation, malformed inputs, unavailable authority, transaction rollback/retry, replay/idempotency and audit outcomes as applicable.
- Run focused tests, full Python suite, repository-integrity guards, security/dependency checks and the real authenticated browser certificate.
- Use isolated real-Mongo certification only with the explicitly configured disposable test URI. Do not fall back to the remote production database if it is unset.

### Gate D — Remove runtime dependency

Only after all route-matrix entries are certified:

- After PDF parity is certified, remove the explicit Vite Node PDF route and the Node API process from the local launcher.
- Remove obsolete Node auth aliases and any remaining Node proxy-only paths.
- Replace or separately migrate any required worker functionality; do not silently discard the Node worker.
- Remove the Node BFF from CI, image builds, deployment manifests and startup docs.
- Reclassify production-surface policy entries only after corresponding runtime consumers are gone and repository guards prove the result.
- Delete Node-only code and dependencies only after reverse-dependency and package-lock analysis proves they are unused.

### Gate E — Production evidence

- Build and publish the immutable Python EOS image from the exact certified commit.
- Verify workload identity, approved runtime configuration, secret/config references, database/audit target and readiness evidence.
- Promote/deploy only through the approved release path with explicit authorization; an image-publish success is not deployment proof.

## Current change

This branch migrates the legacy `/auth/*` Vite alias to Python EOS `/api/auth/*` and adds Python regression checks. It deliberately preserves the general Node `/api` catch-all and does not claim that Node BFF removal or production closure is complete.

## Completion rule

The campaign is closed only when the route matrix is complete, all applicable gates pass on the exact final commit, no production runtime or client route depends on the Node BFF, and deployment evidence proves the intended Python EOS image is serving. Missing evidence means the corresponding gate remains open.
