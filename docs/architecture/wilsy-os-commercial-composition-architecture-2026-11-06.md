# WILSY OS Commercial Composition Architecture

**Report:** EOS-CC-01  
**Date:** 2026-11-06  
**Status:** Architecture proposal backed by an implemented, non-authoritative offer catalogue  
**Scope:** Standalone products, bundles and commercial model compatibility

## Executive decision

WILSY OS should be sold as a composable business operating system. A customer may acquire one product, a named bundle of products, or a negotiated enterprise composition. The same product identity and platform foundations should work across industries and business models.

The platform must preserve five independent facts:

1. **Product identity** — what WILSY builds and supports.
2. **Offer composition** — which products a named commercial offer includes.
3. **Commercial agreement** — what a tenant has contracted, on what terms.
4. **Product entitlement** — which product lifecycle has been positively issued to that tenant.
5. **IAM authority** — which principal may perform which operation on which resource.

No fact in an earlier layer implies a fact in a later layer. In particular, a bundle does not grant a permission, and an invoice or subscription display does not create an operational capability.

## Existing EOS foundation discovered

The remote PR #342 head already contains:

- D22A closed tenant product catalogue: Legal Operations, Billing, CRM and HR.
- D22B3 product-to-commercial-feature mappings for Legal Operations and CRM.
- Positive Legal Operations entitlement composition and separate CRM Core entitlement resolution.
- Subscription lifecycle ownership in SubscriptionRegistry.
- Global principal, membership and tenant business-role authorities.
- EOS workspace bootstrap projection from current durable identity and role evidence.

The D22A catalogue explicitly excludes wildcard enterprise products and separates WILSY AI and Tenant Branding as value-added service authorities. Billing and HR are product identities but are not yet positively mapped by D22B3. This report does not claim they are purchasable or operationally activatable today.

## Implemented work package: explicit offer catalogue

Added `tools/eos/saas/entitlement/commercial_offer_catalogue.py` and a direct test certificate.

The catalogue describes four standalone offers and three explicit bundles:

| Offer | Composition |
|---|---|
| Legal Operations | Legal Operations |
| Billing | Billing |
| CRM | CRM |
| HR | HR |
| Professional Services | Legal Operations + CRM + Billing |
| Business Operations | CRM + HR + Billing |
| Enterprise Operations | Legal Operations + Billing + CRM + HR |

The offer identifiers are distinct from TenantProductId. Bundle members are explicit, unique, and drawn from the canonical product catalogue. Each descriptor is immutable, strict-hydratable and SHA3-512 fingerprinted. Every offer declares supported packaging metadata: recurring subscription, perpetual license, usage-based, enterprise agreement and custom contract.

This is deliberately a **catalogue-only** implementation. It does not create price, term, tenant purchase, invoice, payment, subscription, entitlement, role, permission, route access or workspace admission. The inclusion of a product in an offer does not make that product available to a tenant.

## Target composition flow

```text
Product catalogue (D22A)
        |
        v
Offer catalogue (explicit standalone / bundle composition)
        |
        v
Tenant commercial agreement (future governed authority)
        |
        v
Subscription / contract lifecycle (existing canonical owners)
        |
        v
Per-product entitlement issuance (existing / extended D22B owners)
        |
        v
EOS workspace capability projection (presentation only)
        |
        v
Independent IAM and resource authorization on every operation
```

For a bundle purchase, orchestration must resolve each included product independently, verify its own commercial mapping and eligibility, then issue each entitlement through the product's canonical lifecycle authority. Partial success must not be presented as an all-or-nothing bundle activation. The future transaction coordinator must define atomicity, retry, unknown-commit recovery and compensation before activation is enabled.

## Required next commercial authorities

1. **Offer agreement registry:** tenant, offer, contract reference, effective dates, renewal/termination terms and immutable evidence. No browser-supplied tenant or price authority.
2. **Commercial model policy:** exact eligibility per product and tenant agreement. Usage metering must not itself authorize use.
3. **Product mapping completion:** Billing and HR require reviewed feature identities and entitlement owners before activation.
4. **Bundle composition orchestrator:** per-product idempotency, same-tenant correlation, explicit transaction ownership, stale revision handling, unknown-commit reconciliation and audit evidence.
5. **Lifecycle reconciliation:** contract changes, partial failure, renewal, cancellation and product retirement must converge without IAM side effects.
6. **Pricing and financial execution:** separate governed pricing/quotation and Kennel EOS financial execution; never put price or payment behavior in this catalogue.
7. **Commercial administration UI:** show contracted, pending, active, suspended, expired and unavailable states only from canonical server projections.

## Business-model portability

The product architecture must not encode assumptions such as law firm, company size, country, seat count or industry into product identity. Those are contract dimensions, tenant configuration, industry profiles or policy attributes. The product remains the same product when used by a sole proprietor, a professional firm, an SME, a multinational or a public institution.

Commercial models are not interchangeable entitlements. A perpetual license, usage-based agreement and enterprise agreement require distinct contract semantics, metering or term evidence. A single display label must not collapse those semantics.

## Security invariants

- G68 remains deny-only for confidential Legal workspace access until independently approved.
- Product and offer catalogues are not authorization sources.
- Tenant Owner commercial visibility does not imply Legal Practice access.
- A professional Legal Partner capacity remains distinct from Tenant Owner capacity.
- Global principal, active membership, selected capacity, MFA and current session controls remain intact.
- SubscriptionRegistry remains the sole subscription lifecycle authority.
- Kennel EOS remains the financial execution authority.
- No billing enforcement, production credential changes, deployment or PR merge is authorized by this work.

## Acceptance gates

- Catalogue descriptors are immutable and canonical.
- Unknown offers, products, altered membership, duplicates and fingerprint drift fail closed.
- No offer descriptor contains tenant, principal, price, subscription, entitlement, role, permission, payment or settlement state.
- Bundle activation cannot begin until product-level entitlement authorities and transactional recovery are certified.
- Tenant and principal isolation is proven using real replica-set integration tests before any activation service is introduced.
