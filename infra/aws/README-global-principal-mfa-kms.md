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

## Local-development stack — separate from production

The local-development path is a separate CloudFormation template:
`infra/aws/global-principal-mfa-kms-local-development.yaml`. It creates
exactly three resources: a customer-managed symmetric KMS key, its dedicated
alias, and the `wilsy-eos-global-mfa-local-development` IAM role.

The role trusts only the exact developer IAM user ARN supplied at deployment.
Its only permissions are `kms:Encrypt` and `kms:Decrypt` on this key, and
only when the encryption context contains
`purpose=GLOBAL_PRINCIPAL_TOTP`. It cannot administer the key, access other
KMS keys, or assume the production EKS role. The administrator user is named
as key administrator but is not granted application encrypt/decrypt use by
this template. No access keys, static credentials, EKS resources, OIDC
providers, production roles, or MongoDB resources are created.

For the currently inspected AWS account, the approved operator profile
resolves to
`arn:aws:iam::121014832643:user/wilsy-legal-cert-operator`. Confirm that
identity immediately before deployment; do not substitute the HR S3
provisioning role.

Create a reviewed change set (first deployment uses change-set type CREATE):

```bash
export AWS_PAGER=""
aws sts get-caller-identity --profile wilsy-legal-cert
aws cloudformation create-change-set \
  --stack-name wilsy-eos-global-principal-mfa-local-dev \
  --change-set-name reviewed-local-mfa-kms \
  --change-set-type CREATE \
  --template-body file://infra/aws/global-principal-mfa-kms-local-development.yaml \
  --parameters \
    ParameterKey=LocalDeveloperPrincipalArn,ParameterValue=arn:aws:iam::121014832643:user/wilsy-legal-cert-operator \
    ParameterKey=KeyAdministratorPrincipalArn,ParameterValue=arn:aws:iam::121014832643:user/wilsy-legal-cert-operator \
  --capabilities CAPABILITY_NAMED_IAM \
  --region af-south-1 --profile wilsy-legal-cert

aws cloudformation describe-change-set \
  --stack-name wilsy-eos-global-principal-mfa-local-dev \
  --change-set-name reviewed-local-mfa-kms \
  --query '{Status:Status,Changes:Changes[*].ResourceChange.{Action:Action,LogicalResourceId:LogicalResourceId,ResourceType:ResourceType}}' \
  --output yaml --region af-south-1 --profile wilsy-legal-cert
```

Review the output. It must contain only the KMS key, KMS alias and dedicated
local-development IAM role. If anything else appears, do not execute it.
After review, execute the change set:

```bash
aws cloudformation execute-change-set \
  --stack-name wilsy-eos-global-principal-mfa-local-dev \
  --change-set-name reviewed-local-mfa-kms \
  --region af-south-1 --profile wilsy-legal-cert

aws cloudformation wait stack-create-complete \
  --stack-name wilsy-eos-global-principal-mfa-local-dev \
  --region af-south-1 --profile wilsy-legal-cert

aws cloudformation describe-stacks \
  --stack-name wilsy-eos-global-principal-mfa-local-dev \
  --query 'Stacks[0].Outputs' --output table \
  --region af-south-1 --profile wilsy-legal-cert
```

Configure a dedicated AWS CLI profile to assume the created role. This stores
profile configuration only; it does not create or store access keys:

```bash
aws configure set role_arn arn:aws:iam::121014832643:role/wilsy-eos-global-mfa-local-development --profile wilsy-eos-mfa-local
aws configure set source_profile wilsy-legal-cert --profile wilsy-eos-mfa-local
aws configure set role_session_name local-eos-mfa --profile wilsy-eos-mfa-local
aws configure set region af-south-1 --profile wilsy-eos-mfa-local
aws sts get-caller-identity --profile wilsy-eos-mfa-local
```

The returned ARN must contain
`assumed-role/wilsy-eos-global-mfa-local-development/`. Then set the
development process environment using the full key ARN from the stack output:

```bash
export AWS_PROFILE=wilsy-eos-mfa-local
export AWS_REGION=af-south-1
export WILSY_GLOBAL_MFA_KMS_PROVIDER=AWS_KMS
export WILSY_GLOBAL_MFA_KMS_KEY_ID=<full-local-development-key-arn>
unset WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS
python -m tools.eos.auth.global_principal_mfa_kms_probe
```

The probe rejects any AWS identity other than the dedicated role and performs
a real synthetic KMS encrypt/decrypt startup round trip. It prints no
credentials, key material, plaintext, or ciphertext. The Python EOS API
performs the same KMS `validate_access()` during startup when this provider
is configured; a failed KMS composition remains unavailable (no local-key
fallback).

For the real process certification, start Python EOS with the same environment
and the existing development MongoDB URI (do not print or paste the URI):

```bash
python -m uvicorn tools.eos.api.server:app --host 127.0.0.1 --port 9095
```

Confirm the API startup logs show successful database initialization and no
`GLOBAL_MFA_KMS_*` composition failure. In a second terminal, with the
approved development replica-set URI exported, run the four real-Mongo suites
covering HTTP login/MFA/session, session authority, SYSTEM session authority
and TOTP verification. Report the test summary and the sanitized KMS probe
output only. Do not paste credentials, enrollment seeds, recovery codes,
tokens, or database URIs. These development results do not certify production.

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
