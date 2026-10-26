# WILSY OS

### Sovereign Legal & Enterprise Operating System

[![Repository Integrity](https://github.com/Mawilis/legal-doc-system/actions/workflows/repository-integrity.yml/badge.svg)](https://github.com/Mawilis/legal-doc-system/actions/workflows/repository-integrity.yml) [![Production CI](https://github.com/Mawilis/legal-doc-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Mawilis/legal-doc-system/actions/workflows/ci.yml) [![P9 Integrated Authority Certification](https://github.com/Mawilis/legal-doc-system/actions/workflows/p9-binding-transaction-index-certification.yml/badge.svg?branch=cert%2Fp9-binding-transaction-index-closure-20261026)](https://github.com/Mawilis/legal-doc-system/actions/workflows/p9-binding-transaction-index-certification.yml) [![Release Posture](https://img.shields.io/badge/production-not--declared-orange)](https://github.com/Mawilis/legal-doc-system/blob/main/RELEASES.md) [![Public Status Ledger](https://img.shields.io/badge/status-governed--development-blue)](https://github.com/Mawilis/legal-doc-system/blob/main/tools/eos/governance/public_project_status.json) ![Python/Kennel EOS Authority](https://img.shields.io/badge/authority-Python%2FKennel%20EOS-5b21b6)

WILSY OS is a governed platform for legal operations and enterprise workflows,
designed around explicit tenant scope, provenance-bearing evidence, and
fail-closed authority. Python EOS owns sovereign business and intelligence
truth; Node is transport/orchestration/BFF only where retained; Kennel EOS
exclusively owns financial execution authority.

## Why WILSY OS

WILSY OS makes operational boundaries inspectable: authorization precedes
retrieval, no evidence means no fact, and advisory intelligence cannot silently
become approval or execution. The repository is in pre-production while
mainline reconciliation and promotion remain in progress.

## Sovereign Authority Model

- Python EOS is sovereign business and intelligence truth.
- Node is transport/orchestration/BFF only where retained.
- Kennel EOS exclusively owns financial execution authority.
- Authorization precedes retrieval; tenant scope is explicit and fail-closed.
- Static certification is not live-runtime certification.

## Current Program State

Current frontier: `MAINLINE_RECONCILIATION_AND_PRODUCTION_PROMOTION`.
Production readiness is not declared.

## Milestone Ledger

<!-- WILSY_PUBLIC_STATUS_START -->
```json
{
  "authority": "Wilsy OS Core Governance",
  "canonical_truth": "Python EOS governs business, intelligence, tenant, and execution evidence.",
  "current_frontier": "P9_INTEGRATED_LEGAL_OPS_RECONCILIATION",
  "financial_execution_authority": "Kennel EOS exclusively",
  "governance_version": "v1.1.0-investor-evidence-ledger",
  "milestones": [
    {
      "name": "Executive intelligence spine",
      "result": "FROZEN",
      "state": "CLOSED"
    },
    {
      "name": "M0 mainline divergence discovery",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "R1–R4 anomaly remediation",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "P0 repository integrity firewall",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "P1 production surface inventory",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "P2 dominant production-boundary decomposition",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "M4 controlled fast-forward promotion to main",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "M6 protected main / required checks",
      "result": "PASS",
      "state": "CLOSED"
    },
    {
      "name": "Production release",
      "result": null,
      "state": "NOT_DECLARED"
    },
    {
      "evidence_commit": "ae525b4d229e6eb6dcc0502ce630c7b9298dc973",
      "evidence_url": "https://github.com/Mawilis/legal-doc-system/pull/246",
      "limitation": "Does not certify integrated P9 source, production index migration, ethical-wall enforcement, or matter-content authorization.",
      "name": "P9 focused binding index and transaction rollback certification",
      "result": "PASS",
      "scope": "Focused disposable real-Mongo index, replay, tenant-isolation and transaction-rollback certification; candidate workflow passed.",
      "state": "CLOSED"
    },
    {
      "evidence_url": "https://github.com/Mawilis/legal-doc-system/pull/229",
      "limitation": "Full branch-to-main semantic adjudication, authority-chain proof and integrated certification remain open.",
      "name": "P9 integrated Legal Ops mainline reconciliation",
      "result": null,
      "state": "IN_PROGRESS"
    },
    {
      "limitation": "Badge and release-policy changes are proposed on a review branch; public mainline changes only after governed review and merge.",
      "name": "Investor-facing governance ledger and release signals",
      "result": null,
      "state": "IN_PROGRESS"
    }
  ],
  "project": "WILSY OS",
  "release_posture": "governed development; focused P9 index/transaction certification passed on candidate commit; integrated Legal Ops production release not declared",
  "schema_version": 1,
  "status": "governed-development",
  "tenant_posture": "tenant scope is explicit and fail-closed",
  "updated": "2026-10-26"
}
```
<!-- WILSY_PUBLIC_STATUS_END -->

The ledger above is generated from
`tools/eos/governance/public_project_status.json`; it is never manually
maintained.

## Security & Fail-Closed Governance

Malformed identity, missing tenant scope, unavailable authority, and stale
repository truth fail closed. See [SECURITY.md](SECURITY.md) and
[GOVERNANCE.md](GOVERNANCE.md).

## Production Surface

Canonical domain and authorization surfaces live under `tools/eos`. Runtime
transport and retained client projections are bounded by the Python EOS
contracts. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Release Governance

Historical tags remain documented as pre-governance legacy release markers.
This campaign creates no production release tag. See [RELEASES.md](RELEASES.md).

## Due Diligence

Review executable source, persisted evidence contracts, tenant boundaries,
integrity checks, and the distinction between static proof and live runtime.
Generated catalogs and README projections never outrank canonical source.

## Verification

```bash
python tools/eos/governance/public_status.py --check
python tools/eos/governance/repository_integrity_guard.py --staged
```
