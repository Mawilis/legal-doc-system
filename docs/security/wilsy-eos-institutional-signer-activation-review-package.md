# WILSY EOS Institutional Signer — Governance Review and PKI Activation Package

**Status:** preparation package only; not an approval, appointment, trust ceremony record or activation instruction.

**Canonical tenant:** WILSYTENANT-4CD2FZ4O

**Related controls:**
- `docs/security/institutional-trust-ceremony-evidence-control.md`
- `docs/security/institutional-trust-ceremony-evidence-v1.schema.json`
- `docs/security/wilsy-eos-institutional-pki-kms-ceremony.md`
- `docs/security/institutional-signer-evidence-adapter-acceptance.md`

## 1. Non-negotiable activation rule

Institutional signer enrollment, approval and currentness verification remain unavailable unless the relevant authoritative source adapters, source-response trust, policy, institutional approval authority and PKI trust chain have all been formally approved and independently assessed.

The source-adapter framework and Ed25519 verifier are implementation primitives. They do not establish that a network endpoint belongs to DHA, CIPC, a company-secretarial authority or WILSY governance. They do not create legal mandate, appoint a reviewer, grant IAM authority or issue the opaque verifier results.

No positive verifier may be enabled by changing a feature flag, environment variable or deployment setting alone.

## 2. Governance decisions and evidence required

| Gate | Required decision/evidence | Accountable owner to be formally appointed | Current state |
|---|---|---|---|
| Identity proofing source | Formal DHA National Population Register access or approved identity-provider agreement; permitted purpose, data scope, service identity, response authenticity, service levels and audit terms | WILSY Security and Identity Governance | Not onboarded |
| Corporate mandate source | CIPC access and company-secretarial/legal evidence mapping; MOI, board resolutions and mandate scope must supplement director-listing data where required | WILSY Company Secretarial and Legal Governance | Not onboarded |
| Independent approval | Formal appointment instrument, reviewer eligibility, independence rules, recusal, quorum/delegation, approval scope and audit evidence | To be appointed by WILSY governance | Not appointed |
| Maximum evidence age | Approved maximum age per evidence kind, including source-specific semantics and exception handling | Security and Identity Governance with Legal Governance | Not approved |
| Currentness lease | Approved finite lease duration, expiry behavior, clock-skew policy and emergency invalidation | Security Governance | Not approved |
| Reconciliation cadence | Approved polling/reconciliation interval, retry/backoff, rate-limit behavior, outage escalation and recovery objectives | Security Operations with source owners | Not approved |
| Source signing trust | Authoritative source key-discovery and pinning method, key custody, rotation, revocation, response-signature profile and independent assessment | Security Architecture / PKI custodian | Not configured |
| Institutional CA governance | Root and subordinate CA policy, certificate profiles, certificate purpose, validity, revocation, custody and recovery approval | Appointed PKI governance authority | Not approved |

The proposed WILSY-appointed Governance Committee, with an external independent legal reviewer required for institutional CA and signer activation, remains a proposal only. This package does not record its approval or appoint any person or body.

## 3. Policy approval record — intentionally unset

The following values must be explicitly approved and recorded in a versioned policy artefact before any source adapter can be enabled:

- Maximum evidence age for identity proofing.
- Maximum evidence age for signatory mandate.
- Maximum evidence age for independent approval attestation.
- Finite currentness lease duration.
- Reconciliation cadence and retry/backoff policy.
- Source-specific rate limits and outage/fallback behavior.
- Clock-skew tolerance and trusted time source.
- Evidence expiry, withdrawal, correction and revocation semantics.
- Policy effective date, review date, policy owner and approving authority.

No numeric defaults are proposed in this package. Missing, expired, contradictory or unverifiable policy must deny positive verification and signer use.

## 4. Source adapter onboarding and independent assessment

For each source channel, retain the following evidence before configuration:

1. Executed access agreement or documented lawful authority and permitted purpose.
2. Named accountable source owner and escalation contact.
3. Approved service identity and least-privilege credential custody model.
4. Authoritative endpoint and transport-security profile.
5. Provider response signature profile and independently verified trust-anchor/key fingerprint.
6. Field mapping for subject, tenant/entity, certificate, mandate/approval scope, record ID, revision, status, validity and revocation.
7. Source revision and correction semantics, including stale/replayed response handling.
8. Rate limits, timeout, outage, retry and recovery behavior.
9. Data minimisation, retention, audit and incident-notification requirements.
10. Independent security assessment and negative tests proving wrong-source, wrong-tenant, wrong-subject, wrong-certificate, wrong-scope, stale, replayed, expired, withdrawn and revoked evidence is denied.

Provider I/O must remain outside MongoDB transactions. A provider outage is a verification failure, never an empty evidence set or permission to reuse stale positive state.

## 5. Physical PKI ceremony checklist

The ceremony must be separately scheduled and conducted under approved dual-control custody. No step below is authorised by this document.

### Root and subordinate CA
- [ ] Approve certificate policy, root/intermediate profiles, cryptographic algorithms and validity periods.
- [ ] Appoint named ceremony participants, custodians, witnesses and independent observers.
- [ ] Verify offline ceremony environment, media controls, entropy source, time source and tamper-evident custody records.
- [ ] Generate the root key offline under dual control.
- [ ] Record public-key fingerprint, certificate fingerprint, ceremony transcript and custody attestations.
- [ ] Generate and sign the subordinate CA certificate under the approved root ceremony.
- [ ] Import the subordinate signing key into the approved HSM/KMS using the approved import/wrapping procedure.
- [ ] Verify key ARN, region, key policy, usage restrictions, public-key correspondence and independent cryptographic challenge.
- [ ] Verify that no private key material is exposed to application configuration, logs, source control or ordinary runtime memory.

### Revocation and trust distribution
- [ ] Provision the approved CRL hostname and DNS ownership.
- [ ] Configure TLS and certificate validation for the CRL distribution point.
- [ ] Publish a signed CRL and verify signature, freshness, serial-number semantics and cache behavior.
- [ ] Perform an independent negative revocation test proving a revoked certificate is rejected.
- [ ] Establish CRL availability monitoring, expiry alarms, emergency revocation and recovery procedures.
- [ ] Bind the institutional verifier to the approved trust chain and revocation source only after independent validation.

### Signer governance
- [ ] Complete identity proofing and retain source provenance.
- [ ] Complete company mandate verification and exact signing-scope assessment.
- [ ] Obtain independent approval from the formally appointed authority.
- [ ] Confirm requester/reviewer separation and reviewer authority.
- [ ] Verify certificate subject, key usage, extended key usage, tenant and certificate fingerprint bindings.
- [ ] Execute enrollment, approval, currentness, expiry and revocation negative-path tests.
- [ ] Obtain independent sign-off of the evidence manifest and ceremony record.

## 6. Runtime activation gates

Activation requires all of the following, each with immutable evidence references and independent sign-off:

1. Approved source access and accountable owners for all three evidence channels.
2. Approved and versioned freshness/currentness/reconciliation policy.
3. Formal appointment and active authority of the independent institutional approval function.
4. Independently assessed source adapters and source-response signing-key trust.
5. Completed physical root/subordinate CA ceremony and approved HSM/KMS custody.
6. Operational CRL distribution, TLS, monitoring and independently successful revocation rejection.
7. Verifier integration that alone can issue the opaque positive enrollment/currentness results.
8. Authenticated route, real replica-set, transaction, replay, concurrency, cross-tenant and outage certification.
9. Security, Legal Governance and PKI authority sign-off against the evidence schema and control document.
10. Explicit production change approval and a rehearsed rollback/revocation plan.

A failed or missing gate keeps the verifier unavailable. Development test fixtures are not production trust material.

## 7. Audit and evidence manifest

Use the existing versioned schema at `docs/security/institutional-trust-ceremony-evidence-v1.schema.json`. The ceremony evidence control document defines the sequence and evidence requirements. Every evidence item should have a stable source record/reference, revision, cryptographic digest, collection time, custody/approver identity and verification outcome. Do not put secrets or private key material into the manifest.

The final manifest must distinguish:
- planned evidence;
- evidence collected but not independently verified;
- independently verified evidence;
- rejected or superseded evidence;
- outstanding exceptions and their approved disposition.

## 8. Current decision record

- Governance Committee proposal: **awaiting formal approval**.
- External independent legal reviewer requirement: **awaiting formal approval and appointment**.
- DHA/CIPC/company-secretarial source owners and access: **not established**.
- Evidence age, lease and reconciliation policy: **not approved**.
- Source adapters: **provider-neutral framework only; no live providers configured**.
- Root/subordinate CA ceremony: **not performed**.
- HSM/KMS subordinate key: **not imported or activated by this work**.
- CRL hostname/DNS/TLS: **not provisioned by this work**.
- Institutional verifier production activation: **not authorised**.

No production trust material, AWS resources, signer records or deployment state is changed by this package.
