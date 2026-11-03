# Global-principal MFA KMS deployment contract

**Status:** implementation adapter available; production key binding and factor enrollment remain deployment gates.

## Runtime selection

The EOS API supports an explicitly selected AWS KMS adapter. It is disabled unless all required settings are supplied:

- `WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS`
- `WILSY_GLOBAL_MFA_KMS_KEY_ID=arn:aws:kms:<region>:<12-digit-account-id>:key/<key-id>`
- `AWS_REGION=<same-region-as-key-arn>`
- Optional staged rotation keys: `WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS=<previous-key-arn>,<older-key-arn>`

The configured key must be a **full KMS key ARN**, not an alias or bare key ID. The region must match the ARN. The API obtains credentials only from the AWS SDK's workload credential chain (for example, an ECS task role, EC2 instance profile, or EKS workload identity). Do not place access keys, secret keys, session tokens, or decrypted factor material in application environment variables.

If the provider is absent, unsupported, misconfigured, or inaccessible, the API does not create a local-key fallback. Global MFA verification remains unavailable and global login fails closed.

## Envelope and identity binding

Each TOTP seed is encrypted with AWS KMS `Encrypt` and persisted as a versioned envelope containing the provider, full key ARN and base64 ciphertext. KMS encryption context is:

- `purpose=GLOBAL_PRINCIPAL_TOTP`
- `principal_id=<exact EOS global principal ID>`
- `credential_revision=<current integer credential epoch>`

Decryption must supply the same context. A ciphertext copied to another principal or credential revision is therefore not usable. The application rejects plaintext factor fields and rejects envelopes outside the configured key allow-list.

The current key ARN encrypts new material. Explicitly configured previous key ARNs may decrypt existing envelopes during a staged rotation. Remove an old key from the allow-list only after all dependent factor envelopes have been re-encrypted and independently certified.

## Key creation and governance

Provision the key in the actual production AWS account through the organization's approved infrastructure-as-code and change process. Required properties:

- Symmetric encryption key with `ENCRYPT_DECRYPT` usage.
- Automatic annual key-material rotation enabled.
- Key deletion protection through the KMS deletion waiting period and an independently approved break-glass process.
- Dedicated key for global-principal MFA; do not reuse tenant document, payment, signing or general application keys.
- Key administrators and key users are separate roles.
- Runtime role has only `kms:Encrypt` and `kms:Decrypt` on this exact key.
- CloudTrail management events are retained and monitored.
- Production key ARN and workload role are recorded in the deployment's governed configuration, not committed to source control.

Illustrative runtime IAM statement (replace the ARN and bind the role through the deployment's identity system):

```json
{
  "Effect": "Allow",
  "Action": ["kms:Encrypt", "kms:Decrypt"],
  "Resource": "arn:aws:kms:<region>:<12-digit-account-id>:key/<key-id>",
  "Condition": {
    "StringEquals": {
      "kms:EncryptionContext:purpose": "GLOBAL_PRINCIPAL_TOTP"
    }
  }
}
```

This statement is not a complete key policy. The key policy must also authorize the approved account key administrators and the exact workload role. Do not grant the runtime role `kms:CreateKey`, `kms:PutKeyPolicy`, `kms:ScheduleKeyDeletion`, `kms:DisableKey`, or broad `kms:*`.

## Certification gates before enabling production login

1. Provision the production key and workload identity through approved infrastructure-as-code.
2. Set the three required runtime settings and restart EOS; verify startup composes the KMS adapter without exposing key material.
3. Run a deployment smoke test that encrypts and decrypts a synthetic TOTP seed using the production role and the exact principal/revision encryption context.
4. Prove cross-principal, cross-revision, wrong-key, wrong-region and missing-provider denials.
5. Complete the controlled global MFA enrollment and recovery lifecycle. The adapter's encryption primitive alone does not enroll a factor or authorize MFA reset.
6. Complete real API journey certification against the production KMS adapter and disposable/approved synthetic MongoDB records.
7. Obtain independent security approval before switching production traffic to the global login routes.

**No production key, key ARN, IAM role, MFA factor, or production credential is created by this repository change.**
