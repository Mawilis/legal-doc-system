# Releases and Tag Governance

## Current release posture

**Production release: NOT DECLARED.** No production release tag is issued by this campaign. Historical tags are preserved as legacy release markers for auditability; they describe prior repository states and do not override current governance contracts.

## Tagging policy

- **Release tags** use semantic versioning (vMAJOR.MINOR.PATCH) only for a reviewed, merged, release-certified commit.
- **Candidate and certification work** remains on named branches and pull requests. A green focused workflow is not a production release and must not be promoted into a release tag.
- **Milestone records** live in the canonical public-status ledger and link to the exact PR/commit evidence. Milestone completion is scoped to the evidence recorded, not inferred from a tag name.
- **No mutable or retroactive release tags.** A published release tag must identify the exact immutable commit reviewed for that release.
- Before a future release, verify repository integrity, public-status drift, relevant Python/EOS certification, tenant boundaries, required CI gates, deployment-owned authority and Kennel EOS financial ownership.

## Current P9 evidence

- Focused binding index/transaction rollback certification candidate: [PR #246](https://github.com/Mawilis/legal-doc-system/pull/246), commit ae525b4d229e6eb6dcc0502ce630c7b9298dc973.
- Integrated practitioner-matter binding and reassignment implementation: [PR #229](https://github.com/Mawilis/legal-doc-system/pull/229), still draft and not mergeable at the last verified snapshot.
- The focused certification does not establish integrated P9 production readiness, ethical-wall enforcement, matter-content authorization, or production index migration.

A passing static or focused test is not a live deployment claim.
