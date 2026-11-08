#!/usr/bin/env bash
# Reproducible local EOS launch with the dedicated local-development MFA role.
# This script reads the non-secret KMS key ARN from CloudFormation and relies
# on the AWS CLI assume-role profile for short-lived credentials. It never
# creates, stores, or accepts static AWS credentials.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

AWS_REGION="${WILSY_GLOBAL_MFA_KMS_REGION:-af-south-1}"
AWS_ADMIN_PROFILE="${WILSY_EOS_AWS_ADMIN_PROFILE:-wilsy-legal-cert}"
AWS_RUNTIME_PROFILE="${WILSY_EOS_AWS_RUNTIME_PROFILE:-wilsy-eos-mfa-local}"
STACK_NAME="${WILSY_EOS_MFA_LOCAL_STACK_NAME:-wilsy-eos-global-principal-mfa-local-dev-v3}"
HOST="${EOS_HOST:-127.0.0.1}"
PORT="${EOS_PORT:-9095}"

command -v aws >/dev/null 2>&1 || {
  echo "EOS_LOCAL_MFA_CONFIG_ERROR=AWS_CLI_REQUIRED" >&2
  exit 2
}
command -v python >/dev/null 2>&1 || {
  echo "EOS_LOCAL_MFA_CONFIG_ERROR=PYTHON_REQUIRED" >&2
  exit 2
}

KEY_ARN="$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[?OutputKey==`LocalGlobalPrincipalMfaKeyArn`].OutputValue | [0]' \
  --output text --region "$AWS_REGION" --profile "$AWS_ADMIN_PROFILE")"

case "$KEY_ARN" in
  arn:aws:kms:"$AWS_REGION":*:key/*) ;;
  *)
    echo "EOS_LOCAL_MFA_CONFIG_ERROR=EXPECTED_KMS_KEY_ARN_NOT_FOUND" >&2
    exit 2
    ;;
esac

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export AWS_PROFILE="$AWS_RUNTIME_PROFILE"
export AWS_REGION
export AWS_DEFAULT_REGION="$AWS_REGION"
export WILSY_GLOBAL_MFA_KMS_PROVIDER="AWS_KMS"
export WILSY_GLOBAL_MFA_KMS_KEY_ID="$KEY_ARN"
export WILSY_GLOBAL_MFA_KMS_REGION="$AWS_REGION"
unset WILSY_GLOBAL_MFA_KMS_DECRYPT_KEY_IDS

CALLER_ARN="$(aws sts get-caller-identity --query Arn --output text --region "$AWS_REGION")"
case "$CALLER_ARN" in
  arn:aws:sts::*:assumed-role/wilsy-eos-global-mfa-local-development/*) ;;
  *)
    echo "EOS_LOCAL_MFA_CONFIG_ERROR=UNEXPECTED_AWS_RUNTIME_IDENTITY" >&2
    exit 2
    ;;
esac

echo "EOS_LOCAL_MFA_AWS_IDENTITY=VERIFIED"
python -m tools.eos.auth.global_principal_mfa_kms_probe
exec python -m uvicorn tools.eos.api.server:app --host "$HOST" --port "$PORT"
