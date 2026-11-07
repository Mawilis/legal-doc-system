# WILSY EOS Institutional Trust Ceremony Evidence Control

## Purpose

This control defines the evidence package required before the institutional PKI runtime may be activated against production trust material. It supplements, and does not replace, the technical ceremony in [the KMS ceremony runbook](./wilsy-eos-institutional-pki-kms-ceremony.md).

A completed manifest is an evidence index, not proof by itself that the referenced records are authentic. Every reference must resolve to an independently controlled source and be reviewed by an authorized person who is not the evidence producer.

## Required sequence

1. **Governance authorization** — approve the CA profile, purpose, relying parties, signer eligibility rules, key custodians, KMS administrators, signing operators, CRL service owner, recovery plan and change record.
2. **Separation of duties** — identify at least two distinct root custodians, at least two online key administrators, and at least two signing operators. Ensure administrator and signer principals are disjoint in the KMS key policy.
3. **KMS key ceremony** — create the RSA-3072 asymmetric key in the approved account and `af-south-1` region using the reviewed explicit-principal policy. Record the exact key ARN and public-key fingerprint. Do not export, copy, or attempt to recover private key material.
4. **Offline root ceremony** — transfer only the CSR through the approved chain-of-custody process. Independently compare the CSR subject and public-key fingerprint to the approved change record before issuing the intermediate certificate.
5. **CRL publication** — publish the root and intermediate CRLs at the approved real HTTPS endpoint. Verify DNS, certificate chain, hostname, routing, freshness, monotonic CRL numbers, issuer signatures and complete bundle contents from an independent network vantage point.
6. **Signer governance** — resolve identity-proofing, signatory-mandate and maker-checker approval references against their authoritative source records. The existence of a URI or an EOS database row is not proof of identity, capacity, mandate or legal authority.
7. **Independent negative test** — enroll and approve a test signer under separate actors, verify a signed offer, revoke the signer, publish a CRL containing the exact issuer/serial pair, and prove that acceptance is denied both immediately after revocation and after CRL publication. Preserve the audit receipts.
8. **Recovery and monitoring** — demonstrate key disablement, incident escalation, backup/recovery custody controls, CRL publication recovery, expiry alerting and operational ownership without exposing private key material.
9. **Runtime activation review** — a separate reviewer verifies every evidence reference and hash, confirms approvals and actor separation, and authorizes installation of only the approved public trust anchors and CRL bundle.

## Manifest contract

The companion [JSON Schema](./institutional-trust-ceremony-evidence-v1.schema.json) defines the versioned, machine-readable evidence index. It deliberately records public metadata, fingerprints, actor references, approvals and evidence references only.

The schema is a structural contract. It does **not** resolve references, verify signatures, validate external identity documents, prove institutional mandate, attest to external accreditation, or activate runtime trust. Those checks must be performed by the designated independent reviewers and retained in the referenced evidence system.

## Prohibited manifest content

Never place any of the following in the manifest or its evidence index:

- Private keys, PEM private-key blocks, KMS credentials, access keys, session tokens or passwords.
- Raw identity documents or unnecessary personal data.
- Unredacted KMS policies containing sensitive account details beyond the controlled evidence repository's access boundary.
- Root recovery secrets, HSM PINs, backup encryption keys or break-glass credentials.

## Activation decision

The runtime remains fail-closed unless the production deployment has the approved public root/intermediate material, the exact CRL bundle, durable CRL currentness, signer-registry indexes, verifier configuration and governed runtime actor binding.

A green CI run, a syntactically valid manifest, a completed KMS key creation, or a signed certificate alone is never sufficient authorization to activate institutional trust.
