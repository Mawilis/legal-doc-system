# WILSY EOS Global Principal MFA — AWS KMS provisioning

**Status:** Infrastructure definition committed; AWS deployment and runtime binding are not yet performed.
**Region:** `af-south-1`
**Branch:** `eos/kennel-eos-production-runtime-20261108`

## Discovery findings

- The Python EOS KMS adapter is `tools/eos/auth/global_principal_mfa_kms_envelope.py`.
- It requires `WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS`,
  `WILSY_GLOBAL_MFA_KMS_KEY_ID` as a full key ARN, and `AWS_REGION`.
- The adapter calls KMS `Encrypt` and `Decrypt` with encryption context
  `purpose=GLOBAL_PRINCIPAL_TOTP`, `principal_id=<principal>`, and
  `credential_revision=<revision>`. Startup calls `validate_access()`, which
  performs a synthetic encrypt/decrypt round trip. There is no local-key fallback.
- The repository declares Kubernetes ServiceAccount `wilsy-eos-api`, but its
  production manifest deliberately has no AWS role annotation. Its existing
  runtime-authority contract says the EKS OIDC identity and approved role trust
  have not yet been proven.
- Atlas project `Wilsy` (`668ce033a92d5c6d67e7b1d8`) has cluster
  `legalDocSystem`, AWS `AF_SOUTH_1`, currently Free tier. Its `wilsy`
  database contains the global-principal MFA factors, enrollment challenges,
  sessions and refresh tokens. The separate `wilsy_audit` database is present,
  but this discovery does not certify it as an independent production audit
  deployment.
- A separate Atlas project `legal-doc-test` also exists. Do not use its
  cluster or test database credentials for production EOS.
- AWS profile `wilsy-legal-cert` resolves to IAM user
  `arn:aws:iam::121014832643:user/wilsy-legal-cert-operator`; profile
  `wilsy-legal-s3-cert` resolves to the same user. The user currently has the
  AWS-managed `AdministratorAccess` policy attached, in addition to
  `IAMUserChangePassword` and `SignInLocalDevelopmentAccess`. This establishes
  an administrative provisioning identity, not an approved EOS runtime
  identity. Do not grant this administrator direct application KMS use.
- Profile `wilsy-hr-s3-provisioner` resolves to the separate
  `WilsyHrDocumentBucketProvisioner` role and must not be repurposed for MFA.
- The AWS-managed `alias/aws/s3` key is not an MFA key.

## What this stack creates

`global-principal-mfa-kms.yaml` creates in the deploying AWS account:

1. One dedicated symmetric customer-managed KMS key, with automatic annual
   rotation enabled and a 30-day deletion waiting period.
2. Alias `alias/wilsy/global-principal-mfa`.
3. IAM role `wilsy-eos-global-mfa-runtime`, trusting only the supplied EKS
   OIDC provider and exact `system:serviceaccount:<namespace>:wilsy-eos-api`
   subject.
4. Runtime identity and key-policy grants limited to `kms:Encrypt` and
   `kms:Decrypt` on this key, with
   `kms:EncryptionContext:purpose=GLOBAL_PRINCIPAL_TOTP`.
5. An optional, separate local-development role grant. It is absent unless an
   explicit IAM role ARN is supplied as `LocalDevelopmentPrincipalArn`.

Key administration is a separate existing role parameter; it is not granted to
the EOS runtime. The stack creates no users, access keys, static credentials,
MongoDB resources, production sessions, or MFA factor data.

## Mandatory pre-deployment proof

Do not deploy this stack until all of these values have been obtained from the
actual AWS account and target cluster:

- Account identity and approved key-administrator role ARN.
- Existing EKS cluster name, region, issuer URL and corresponding IAM OIDC
  provider ARN.
- Exact namespace containing the deployed `wilsy-eos-api` ServiceAccount.
- Proof that this is the actual target runtime cluster and not a stale/example
  manifest.

The AWS account inventory performed on 2026-11-08 found no EKS clusters in
any of the 18 enabled regions, no IAM OIDC providers, and no existing EOS
runtime IAM role. No CloudFormation stacks were listed in `af-south-1`.
The current repository deployment authority document identifies Python
Kennel EOS as the supported API runtime but explicitly marks production
hosting, ingress and workload identity as unverified. The checked-in Kubernetes
and Helm files are stale/unverified and are not evidence of a live EKS target.
The Vercel connector also returned no project connected to this repository.

The administrator profile is sufficient to investigate or provision AWS
infrastructure, subject to account-level controls, but it does not establish
the actual production runtime. This EKS-specific stack is therefore not ready
to deploy. Do not create a speculative EKS cluster, OIDC provider, or service
account merely to satisfy its parameters. A separate local-development
provisioning path must use a dedicated least-privilege IAM role assumed by the
approved operator; do not give the EOS process the administrator profile or
its broad permissions.

Example discovery commands (run using the approved infrastructure-admin
profile, not the HR S3 certification identity):

```bash
aws sts get-caller-identity --profile <approved-infrastructure-admin>
aws eks list-clusters --region af-south-1 --profile <approved-infrastructure-admin>
aws eks describe-cluster --name <verified-cluster> --region af-south-1 \
  --query 'cluster.identity.oidc.issuer' --output text \
  --profile <approved-infrastructure-admin>
aws iam list-open-id-connect-providers --profile <approved-infrastructure-admin>
```

Match the issuer URL to the IAM OIDC provider ARN exactly. Obtain the key
administrator role from the approved platform governance owner; do not use the
runtime role as key administrator.

## Deploy after discovery

Use a reviewed CloudFormation change set in `af-south-1`. Do not execute an
unreviewed stack update. The EKS stack described here remains blocked until a
real target cluster and issuer are independently verified. Local-development
key provisioning must be a separate template/stack and must not create or imply
production workload identity.

```bash
aws cloudformation create-change-set \
  --stack-name wilsy-eos-global-principal-mfa \
  --change-set-name reviewed-mfa-kms-provisioning \
  --template-body file://infra/aws/global-principal-mfa-kms.yaml \
  --parameters \
    ParameterKey=EosEksOidcProviderArn,ParameterValue=<verified-oidc-provider-arn> \
    ParameterKey=EosEksOidcIssuerHostPath,ParameterValue=<issuer-host-and-id-path> \
    ParameterKey=EosServiceAccountSubject,ParameterValue=system:serviceaccount:<namespace>:wilsy-eos-api \
    ParameterKey=KeyAdministratorRoleArn,ParameterValue=<approved-key-admin-role-arn> \
  --capabilities CAPABILITY_NAMED_IAM \
  --region af-south-1 --profile <approved-infrastructure-admin>

aws cloudformation describe-change-set \
  --stack-name wilsy-eos-global-principal-mfa \
  --change-set-name reviewed-mfa-kms-provisioning \
  --region af-south-1 --profile <approved-infrastructure-admin>
```

Only execute after independently reviewing that the change set contains exactly
the dedicated key, alias and role described above. The key-administrator role
must already exist in the same AWS account; CloudFormation does not create it. Capture the output key ARN
and role ARN as deployment evidence.

## Bind the actual workload

After the stack succeeds, annotate the actual EOS ServiceAccount with the
CloudFormation output role ARN using the approved Kubernetes deployment
workflow. Do not add an annotation to a manifest with a guessed account/role.
Configure the existing EOS runtime ConfigMap with:

```yaml
global-principal-mfa-kms-provider: AWS_KMS
global-principal-mfa-kms-key-id: <full-customer-managed-key-arn>
global-principal-mfa-kms-region: af-south-1
global-principal-mfa-kms-decrypt-key-ids: ""
```

The production Deployment already maps these ConfigMap keys to the adapter's
environment variables. Never put AWS access keys, TOTP seeds, or plaintext
factor secrets in ConfigMaps, Git, or logs.

For local development, authorize a separately provisioned developer role in
the key policy using `LocalDevelopmentPrincipalArn`. Configure the local
AWS profile to assume that role; do not reuse `wilsy-legal-cert-operator`
without a separate explicit review and authorization. The local shell uses
`AWS_PROFILE=<approved-local-eos-profile>` and the same key ARN/region
variables. Do not store static AWS credentials in `.env`.

## Certification gates (development first)

1. Restart Python EOS so the process reloads the environment.
2. Confirm startup `validate_access()` succeeds without logging plaintext or
   ciphertext. A failed probe must leave MFA unavailable.
3. Run focused adapter tests for correct encryption context, wrong principal,
   wrong credential revision, wrong key, malformed envelope, unavailable KMS,
   and denied IAM permissions.
4. Run connected MongoDB replica-set tests for enrollment start/confirm,
   TOTP verification, one-time challenge consumption, atomic session issuance,
   refresh and logout. Use the canonical connected development/test target
   explicitly; do not treat the Free Atlas cluster as production authority.
5. Complete authenticated browser certification against the Python EOS API.
6. Only after all development gates pass may production readiness be reviewed.
   This change does not authorize production activation.

## MongoDB boundary

The MFA ciphertext envelope is stored by the existing Python EOS factor
repository in the canonical `wilsy` database. KMS protects the TOTP secret;
MongoDB stores the encrypted envelope and associated factor metadata. Do not
create another MFA collection or duplicate identity/session authority.

Atlas discovery shows the current `Wilsy/legalDocSystem` cluster is Free tier.
The repository's own production provisioning plan requires an explicitly
approved production Atlas target, dedicated database principal, TLS URI and
network policy. The cluster's existence and its replica-set topology do not
satisfy those production gates. Keep development certification separate from
production provisioning.

## Rollback and incident handling

- Disable or remove the runtime role binding to stop new KMS operations.
- Do not schedule key deletion as a routine rollback; existing enrolled factors
  depend on decrypt access.
- For compromise, follow a governed factor re-enrollment and key-rotation plan.
  Keep prior key ARNs in the adapter decrypt keyring only for the approved
  migration window.
- Preserve CloudTrail and CloudFormation change-set/stack evidence.
