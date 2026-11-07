# WILSY EOS Institutional PKI: non-exportable subordinate CA ceremony

This runbook describes the two-host trust ceremony. It does not create external accreditation, approve a signatory mandate, or make a runtime trust anchor active. Execute only after WILSY governance approves the CA profile, KMS key policy, key custodians, offline root custodians, CRL publication host, and recovery procedure.

## 1. Provision the subordinate key inside KMS

Run on an approved online KMS administration host with the approved AWS profile and region. The policy file must be reviewed before use. It must name explicit IAM principals and grant only the required kms:Sign, kms:GetPublicKey, and kms:DescribeKey operations to the intended operators/services. Wildcard principals and wildcard actions are rejected.

    python -m tools.eos.security.institutional_pki_kms_cli provision-subordinate-csr \
      --region af-south-1 \
      --profile APPROVED_KMS_PROFILE \
      --key-policy REVIEWED_KEY_POLICY_JSON \
      --output-dir SECURE_OUTPUT_DIRECTORY \
      --common-name "WILSY EOS Intermediate CA" \
      --organization "Wilsy (Pty) Ltd" \
      --organizational-unit "Institutional PKI" \
      --country-code ZA

The command generates an RSA-3072 asymmetric key with Origin=AWS_KMS, KeyUsage=SIGN_VERIFY, and MultiRegion=false. It retrieves only the public key, asks KMS to sign a PKCS#10 CSR, verifies that CSR locally, and writes the public CSR plus a non-secret key-reference manifest. The private key is not exportable and is never written to disk.

Record the key ARN, key policy approval, operator identity, and public-key fingerprint in the controlled PKI inventory. If provisioning fails after KMS created the key, the CLI reports the ARN for explicit reconciliation; do not silently create replacement keys.

## 2. Sign the CSR under the offline root

Transfer only the CSR to the approved offline root-CA host using the institution's approved media and chain-of-custody process. Verify the CSR subject and public-key fingerprint against the approved change record before signing.

    python -m tools.eos.security.institutional_pki_cli issue-intermediate-kms-csr \
      --root-certificate OFFLINE_ROOT_CERTIFICATE_PEM \
      --root-private-key ENCRYPTED_OFFLINE_ROOT_KEY_PEM \
      --csr TRANSFERRED_SUBORDINATE_CSR_PEM \
      --output-dir OFFLINE_ISSUED_CERTIFICATE_DIRECTORY \
      --common-name "WILSY EOS Intermediate CA" \
      --organization "Wilsy (Pty) Ltd" \
      --organizational-unit "Institutional PKI" \
      --country-code ZA \
      --crl-base-url APPROVED_HTTPS_CRL_BASE_URL

The offline command verifies the CSR signature and exact approved subject, validates the encrypted root key/certificate pair and root path-length profile, and signs an RSA-3072 path-length-zero CA certificate. It writes only the public intermediate certificate. The subordinate private key remains in KMS.

The CRL base URL must be the real approved HTTPS host. Do not substitute an example domain or publish until DNS, TLS, routing, access, monitoring and recovery have been verified.

## 3. Publish the intermediate CA CRL with KMS

The KMS key must match the public key in the issued intermediate certificate and remain enabled with the approved signing profile.

    python -m tools.eos.security.institutional_pki_kms_cli publish-crl \
      --region af-south-1 \
      --profile APPROVED_KMS_PROFILE \
      --key-arn SUBORDINATE_KMS_KEY_ARN \
      --issuer-certificate ISSUED_INTERMEDIATE_CERTIFICATE_PEM \
      --output INTERMEDIATE_CRL_PEM \
      --crl-number STRICTLY_INCREASING_NUMBER \
      --validity-hours 24 \
      --revoke-serial HEX_OR_DECIMAL_SERIAL

Repeat --revoke-serial for each certificate being revoked. Omit it when issuing a routine CRL with no new revocations. CRLs are signed using the KMS-held key; the command validates the KMS key state, algorithm, public-key match, issuer CA profile, CRL structure and signature before writing the public CRL.

## 4. Assemble and publish the complete CRL bundle

The root CRL must be signed by the offline root key. The intermediate CRL must be signed by the KMS-held intermediate key. Assemble exactly one current CRL per configured issuer:

    python -m tools.eos.security.institutional_pki_cli assemble-crl-bundle \
      --crl ROOT_CRL_PEM \
      --crl INTERMEDIATE_CRL_PEM \
      --output COMPLETE_CRL_BUNDLE_PEM

Publish the complete bundle at the approved HTTPS CRL host and configure the runtime to read that exact bundle. The EOS verifier validates issuer signatures, issuer identity, CRL number monotonicity, freshness, completeness and revocation entries. The durable currentness recorder persists the CRL observations. Revoked signer enrollments move from PENDING to PUBLISHED only when the verified current CRL contains the serial under the exact issuer subject.

## 5. Runtime activation and acceptance gate

Install only approved public root/intermediate certificates and the complete CRL bundle in the runtime's controlled trust-material location. Configure the exact trust-anchor fingerprints, required signer EKU, CRL age policy, CRL bundle path and a governed runtime actor reference. Verify the CRL endpoint over the real TLS host. The runtime stays fail-closed until trust files, database indexes, durable CRL currentness and reconciliation callbacks are ready.

Before production use, independently verify:
- Offline root custody, dual control, backup and recovery.
- KMS key policy, IAM separation, audit logging, alarms, key disable/recovery and rotation procedure.
- Issued intermediate certificate and public-key fingerprint match the KMS key.
- Root and intermediate CRL signatures, monotonic numbers, current validity and public distribution.
- Signer identity proofing and signatory mandate evidence against original institutional sources.
- Independent maker-checker approval, revocation, CRL publication and acceptance denial after revocation.
- Authenticated signed-offer acceptance with exact document version, manifest digest, current trust chain and durable audit receipt.

A green software test suite is not a substitute for these operational and institutional approvals. No production key is generated, no real AWS account is modified, and no trust material is activated by CI.
