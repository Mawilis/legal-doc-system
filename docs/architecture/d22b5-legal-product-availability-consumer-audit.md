# D22B5 Legal Product Availability Consumer Audit

**Audit baseline:** `af2fdba6d8bcf5dc283c85236b8882a5bf260424`
**Runtime:** Python EOS only
**Status:** SOURCE-SEARCH INVENTORY; no authorization behavior changed

## Scope and method

Repository-wide code search for the canonical `resolve_legal_product_availability` symbol identifies the production call sites below. Tests and the projection implementation are listed separately. This is a symbol-reference inventory, not a proof that every dynamic/import-indirect consumer has been found; repeat the search after any refactor and include AST/import-alias review before release.

## Production consumers

| Consumer | How it uses D22B5 | Subscription conjunction | Assessment |
|---|---|---|---|
| `tools/eos/api/legal_operations_router.py` — Legal practice workspace projection | Calls D22B5 inside the existing workspace snapshot transaction before workspace evidence reads. The route also requires its existing four Legal read authorities for the same tenant/principal/role. | No independent subscription lookup in this workspace admission path. D22B5 is explicitly the product-entitlement admission gate; this is valid only if the product contract defines the durable ACTIVE entitlement as the admission source. Do not silently claim this route verifies an active subscription. | Entitlement currentness is enforced through D22B2 current pointer and caller snapshot. Commercial subscription currentness is not established by this call alone. Confirm product contract and add subscription conjunction only if subscription status is an independent admission requirement. |
| `tools/eos/saas/entitlement/legal_commercial_context_projection.py` | Calls D22B5 and then reads canonical tenant subscriptions using the same caller-owned session. | Yes. Requires at most one ACTIVE subscription containing `legal.core`; ACTIVE entitlement requires exactly one such subscription; an ACTIVE subscription without ACTIVE entitlement is rejected. | Correct stronger conjunction for commercial-context decisions. Preserve it. |

## Canonical D22B5 semantics

`legal_product_availability_projection.py` derives the Legal product descriptor and entitlement ID server-side, then calls D22B2 `get_current` with exact tenant scope, exact history/current collections and unchanged caller session. Exact absence is the only condition projected as unavailable. Corruption, malformed hydration, catalogue drift, transaction failure, retry signals, conflicts and persistence outages raise a bounded authority error.

D22B5 maps only `TenantProductEntitlementState.ACTIVE` to `available=True`. It is explicitly descriptive product availability, not IAM, route, workspace, subscription, payment or execution authority.

## Tests found by symbol search

- `tests/unit/test_legal_product_availability_projection.py`
- `tests/unit/test_legal_commercial_context_projection.py`
- `tests/unit/test_legal_practice_workspace_confidentiality_boundary.py`
- `tests/integration/test_legal_operations_practice_workspace_http.py`
- `tests/integration/test_legal_product_availability_projection_real_mongo.py`

The repository also contains a real-Mongo Legal commercial-context projection certificate and a real-Mongo workspace certificate. Their presence is not a substitute for running them on the exact release commit.

## Required release checks

1. Re-run repository-wide search for `resolve_legal_product_availability`, imports/aliases of that symbol, and any direct D22B2 current-entitlement reads used as product gates.
2. Enumerate every route and command that admits Legal product use. Verify its declared product contract: entitlement-only admission versus entitlement-plus-active-subscription admission.
3. Keep commercial-context decisions on the stronger D22B5 + canonical subscription conjunction.
4. Verify every consumer forwards the same active caller-owned session across all evidence reads; no nested transaction or independent snapshot.
5. Verify no client-supplied product, entitlement ID, lifecycle state or availability flag influences admission.
6. Run unit, HTTP and real-Mongo tests against the same branch head. A source inventory is not test certification.

## Ownership lifecycle remains a separate blocker

This audit does not implement tenant ownership evidence or transfer. The current tenant-owner bootstrap is tenant genesis: it creates tenant, membership, authorization-role and business-role records in one transaction after pre-tenant provisioning authority. It does not prove legal/contractual beneficial ownership and is not a transfer, recovery, succession or ownerless-state protocol. Do not reinterpret it as one.

**END OF AUDIT**
