# G65 Canonical Ethical-Wall Membership and Acknowledgement Contract

**Status:** ENGINEERING CONTRACT PROPOSAL — NOT INSTITUTIONAL RATIFICATION  
**Version:** v1.0.0-G65-MEMBERSHIP-ACKNOWLEDGEMENT-CONTRACT  
**Effective authority:** None until approved through the G64 institutional decision process  
**Runtime posture:** Deny-only; no content clearance or access grant  
**Scope:** Persisted record shape and source-read semantics consumed by G65/G77

## 1. Purpose and limits

This document defines the record shape currently implemented by
`legal_work_ethical_wall_membership_acknowledgement.py`. It makes the engineering
assumptions reviewable instead of leaving them implicit in source code.

It does not establish the institution that owns the data, name an authorized
issuer, ratify a signature or attestation method, approve a retention policy,
provision production collections, or prove that a real content reader enforces
the result. A record fingerprint is an integrity check, not proof of authorship,
delegated authority, institutional approval, or non-repudiation.

## 2. Membership record shape

A current membership document must contain exactly these fields:

- `tenant_id`
- `case_matter_id`
- `practitioner_principal_id`
- `membership_id`
- `revision` (positive integer, strictly increasing per exact scope)
- `status` (must equal `ACTIVE` for the current record)
- `effective_at` (timezone-aware UTC timestamp at whole-second precision)
- `expires_at` (timezone-aware UTC timestamp or null)
- `revoked_at` (timezone-aware UTC timestamp or null)
- `issuer_id`
- `issuer_evidence_reference`
- `fingerprint`

The resolver queries by the exact tenant, matter, principal and active status,
limits results to two, and accepts exactly one matching record. Missing or
ambiguous current records deny. Expiry is exclusive: at `evaluation_time >=
expires_at`, evidence is expired. A revocation effective at or before the
evaluation time denies.

## 3. Acknowledgement record shape

A current acknowledgement document must contain exactly these fields:

- `tenant_id`
- `case_matter_id`
- `practitioner_principal_id`
- `policy_id`
- `policy_revision_fingerprint` (must match the exact current wall revision)
- `acknowledgement_id`
- `revision` (positive integer, strictly increasing per exact scope)
- `status` (must equal `ACTIVE` for the current record)
- `acknowledged_at` (timezone-aware UTC timestamp at whole-second precision)
- `expires_at` (timezone-aware UTC timestamp or null)
- `revoked_at` (timezone-aware UTC timestamp or null)
- `issuer_id`
- `issuer_evidence_reference`
- `fingerprint`

The resolver uses the exact tenant, matter, principal, policy and policy revision
fingerprint in the query. Acknowledgement for a prior policy revision is not
reusable. Missing, ambiguous, expired, revoked, future-effective, malformed or
out-of-scope records deny.

## 4. Fingerprint encoding implemented by G65

The current engineering implementation computes SHA-256 over UTF-8 JSON with
sorted keys, compact separators `(',', ':')`, and ASCII escaping. The
`fingerprint` field and MongoDB `_id` are excluded from the hashed payload.
Timezone-aware datetime values are normalized to UTC and serialized using
ISO-8601 whole-second precision. Unsupported values fail closed.

This encoding must not be treated as an institutionally approved signature
scheme. Before production use, the source owner must approve the canonical
encoding, migration/backfill strategy, key/signature or attestation requirements,
and compatibility policy. Existing records with a different encoding must deny
until migrated and independently verified.

## 5. Transaction and currentness contract

Both lookups must receive the exact same active caller-owned transaction
session. The adapter never starts, commits, retries or aborts a transaction.
The caller owns transaction lifecycle.

G77 reads membership and acknowledgement, validates exact scope and revision,
then reads both again immediately before its terminal decision. Changed
identifiers, revisions or fingerprints deny. Read failure denies.

**Concurrency limitation:** repeated reads in a database transaction do not
necessarily observe a concurrent revocation committed after a snapshot was
established. The production source owner must specify and certify the actual
database read concern/isolation semantics, revocation visibility bound, and any
serialization or generation-check mechanism. Until a real-Mongo adversarial
test proves this property, the implementation must not be described as
race-safe point-of-read enforcement.

## 6. Deployment responsibilities not established by this proposal

Before deployment, an accountable owner must independently approve and evidence:

1. Canonical membership and acknowledgement source identifiers and owners.
2. Exact schema, validation rules, indexes, uniqueness/current-pointer semantics,
   retention, append-only history, revision progression and supersession rules.
3. Issuer identity, issuer delegation, signed/attested evidence format and key
   rotation/revocation semantics.
4. Policy acknowledgement actors, exact policy revision binding, effective
   time, expiry and revocation semantics.
5. Availability, timeout, corruption and inconsistency behavior.
6. Real-Mongo tests for cross-tenant/matter isolation, duplicate current rows,
   concurrent revocation, stale snapshots and point-of-read revalidation.
7. Actual disclosure-boundary tests proving zero content-reader calls and zero
   content bytes on every denial path.

The G64 institutional decision record must be completed and independently
verified for the relevant D01–D10 decisions. This document is not that record.

## 7. Non-negotiable runtime invariant

G65 is a strict evidence projection. G77 remains denial-only and must end in
`G77_INSTITUTIONAL_AUTHORITY_UNRATIFIED` after successful documentary checks.
`SOURCE_VERIFIED_CLEARANCE` and `OPERATIONAL_ACCESS_ENABLED` remain false.
No caller flag, fingerprint, repository merge, successful CI run, or this
engineering proposal can enable confidential content access.

---
**ARTIFACT:** g65-canonical-ethical-wall-membership-acknowledgement-contract.md  
**VERSION:** v1.0.0-G65-MEMBERSHIP-ACKNOWLEDGEMENT-CONTRACT  
**AUTHORITY BOUNDARY:** Engineering proposal only; no institutional approval  
**TENANT POSTURE:** Exact tenant/matter/principal/policy/revision scope  
**FAIL-CLOSED POSTURE:** Unverified, missing, stale, ambiguous or revoked evidence denies  
**FINANCIAL EXECUTION AUTHORITY:** None  
**END OF WILSY OS SOVEREIGN ARTIFACT**
