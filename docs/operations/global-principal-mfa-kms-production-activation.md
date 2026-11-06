# Global Principal MFA — AWS KMS Production Activation

Date: 2026-11-03  
Status: **Implementation present; production activation requires deployment-owned AWS key and workload identity.**  
Scope: EOS global-principal TOTP enrollment, proof-based legacy-factor migration, verification and session issuance.

## 1. What is implemented

The EOS codebase now contains:

- `AwsKmsGlobalMfaEnvelope` in `tools/eos/auth/global_principal_mfa_kms_envelope.py`.
- AWS KMS envelope encryption using the workload's ambient AWS credential chain; no static AWS access keys, local master-key fallback or plaintext persistence.
- Encryption-context binding to `purpose=GLOBAL_PRINCIPAL_TOTP`, exact `principal_id` and `credential_revision`.
- Strict key-ARN and region validation, explicit allowlisting of previous key ARNs for staged key rotation, and a startup encrypt/decrypt probe.
- One-time global MFA enrollment with encrypted pending factor, five-attempt confirmation limit, single-use challenge and credential-revision increment.
- Proof-based legacy TOTP migration requiring global password authentication, exact active principal mapping and valid existing TOTP proof. Legacy factor rows remain intact until the legacy authentication cutover.
- Global login, explicit membership/capacity selection, MFA verification, refresh, logout, enrollment and legacy migration HTTP routes.
- Caller-owned MongoDB transactions for factor/challenge/session state changes.

The AWS adapter is deliberately opt-in. EOS does not claim KMS readiness merely because the Python package is installed.

## 2. Required deployment configuration

The deployment owner must create or designate a **symmetric AWS KMS key** in the same AWS region as the API workload. The current WILSY South Africa deployment target is `af-south-1`; use that region only if the production workload is actually deployed there.

Set these variables in the secret/configuration manager for the EOS API workload:

```dotenv
WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS
WILSY_GLOBAL_MFA_KMS_KEY_ID=arn:aws:kms:af-south-1:123456789012:key/REPLACE_WITH_REAL_KEY_UUID
AWS_REGION=af-south-1
# Optional: comma-separated previous key ARNs during an approved key migration.
WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS=
```

Replace the account and key identifiers with the real values from the production AWS account. The example ARN is a placeholder, not a usable key.

Do not put access keys, secret keys, plaintext TOTP seeds or master-key material in these variables. The application must obtain AWS credentials from its workload identity / standard AWS credential provider chain (for example, an ECS task role, EKS IRSA role or EC2 instance profile). Do not use a developer's personal AWS credentials in production.

## 3. Minimum KMS permissions

Grant the dedicated EOS API workload role permission to call only:

- `kms:Encrypt`
- `kms:Decrypt`

Scope `Resource` to the exact MFA key ARN. The key policy must also permit that workload role; an IAM policy alone is insufficient if the key policy does not delegate access.

Constrain both operations with the encryption-context condition:

```json
{
  "StringEquals": {
    "kms:EncryptionContext:purpose": "GLOBAL_PRINCIPAL_TOTP"
  }
}
```

Do not grant `kms:ScheduleKeyDeletion`, `kms:DisableKey`, `kms:PutKeyPolicy` or broad account-wide KMS permissions to the runtime role. Keep key administration and break-glass recovery separate from the API workload identity. CloudTrail KMS events should be retained under the platform's security logging policy.

## 4. Startup and readiness behavior

On connected EOS startup:

1. Required MongoDB indexes are installed.
2. The KMS adapter is constructed only when `WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS` is explicitly set.
3. The adapter encrypts and decrypts a random, synthetic startup probe using a non-user principal context.
4. The recovered value is compared in constant time.
5. Only after a successful probe is the KMS envelope exposed to enrollment/migration routes and the TOTP verifier composed.

If configuration, credentials, key policy, region, encryption or decryption fails, KMS composition remains unavailable. Global MFA enrollment, migration and verification return fail-closed service-unavailable responses. Do not bypass this by setting a local secret or injecting a test decryptor into production.

The startup probe does not create a MongoDB record and does not touch a user's MFA factor.

## 5. Existing-principal activation sequence

For a principal with an existing legacy TOTP factor:

1. Confirm the exact global principal and credential migration record is approved and active.
2. Call `POST /api/auth/global/mfa/migrate-legacy` with the global email/password and a current code from the existing authenticator.
3. The service requires one exact legacy `otp_secrets.user_id == principal_id` row, an ACTIVE PrincipalAuthority and current credential revision.
4. EOS encrypts the existing seed with KMS and stores the new principal-scoped envelope transactionally.
5. The legacy row is retained during compatibility; do not delete it before the separately certified legacy login/session cutover.

For a principal with no existing factor and `mfa_enabled=false`:

1. Call `POST /api/auth/global/mfa/enrollment/start` with global credentials.
2. Display the returned provisioning URI / secret once in a no-store enrollment screen and have the user add it to an authenticator.
3. Call `POST /api/auth/global/mfa/enrollment/confirm` with the one-time challenge and current six-digit code.
4. On success, the factor is activated, the credential revision advances, and the user must sign in again.

An account with MFA already enabled but a missing/stale factor must use independently verified recovery. Password-only reenrollment is intentionally rejected.

## 6. Rotation and incident response

- Enable AWS KMS automatic rotation where supported by the selected symmetric key configuration.
- AWS-managed rotation of the same KMS key preserves decryption of historical ciphertext under that key ARN.
- For migration to a different KMS key ARN, deploy the new key as the encrypt key and add the old full ARN to `WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS` for the controlled transition.
- Re-encrypt stored factor envelopes in a separately reviewed, idempotent migration. Remove the old ARN from the decrypt allowlist only after inventory proves no live factor references it and rollback retention expires.
- On suspected compromise, disable the affected key only under incident command, block global MFA routes, revoke affected global sessions, rotate/re-enroll factors using independently verified recovery, and preserve audit evidence.
- Never log provisioning secrets, TOTP values, decrypted seeds, ciphertext payloads, AWS credentials or full challenge tokens.

## 7. Production go/no-go checklist

- [ ] Production AWS account and region confirmed.
- [ ] Dedicated symmetric KMS key ARN recorded in deployment configuration.
- [ ] Dedicated EOS workload role attached to the actual runtime.
- [ ] Key policy and IAM policy restricted to the workload role and MFA encryption context.
- [ ] CloudTrail KMS events retained and monitored.
- [ ] EOS startup KMS probe succeeds in the deployed environment.
- [ ] MongoDB replica-set transaction support and required indexes are ready.
- [ ] Synthetic enrollment and legacy-factor migration exercised end-to-end against the real deployed KMS adapter.
- [ ] Enrollment secret and provisioning URI are never cached or logged by the frontend/proxy.
- [ ] Independent security review signs off the key policy, recovery process and session cutover.
- [ ] Legacy tenant-bound login/refresh/session compatibility cutover is separately certified.

**Release rule:** a passing unit test or disposable-Mongo test is not production KMS certification. Do not enable global-principal login for real users until the actual deployment identity passes the KMS startup probe and the end-to-end production-like journey is certified.
