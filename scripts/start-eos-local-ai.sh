#!/usr/bin/env bash
# TITLE: WILSY OS Local Institutional AI + Global Principal MFA Launcher
# VERSION: v1.1.0-REJECT-CREDENTIAL-LIKE-MODEL-IDENTIFIERS
# AUTHORITY: Wilsy OS Core Governance; nonproduction local launch only.
# EPITOME: Supply explicit ephemeral OpenAI provider configuration to the
#          already-certified Python EOS/MFA launcher without changing IAM,
#          commercial entitlement, provider admission or reasoning contracts.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/start-eos-local-ai.sh
# COLLABORATION / OWNERSHIP: Scripts/start-eos-local-mfa.sh owns AWS/KMS and
#          Python EOS startup; reasoning_provider_runtime.py owns the binding;
#          wilsy_ai_reasoning_router.py owns tenant and usage authorization.
# CERTIFICATION / UPDATE DATE: 2026-11-20
# CHANGELOG: v1.1.0-REJECT-CREDENTIAL-LIKE-MODEL-IDENTIFIERS rejects common API key/tracking-id prefixes in the model field before child process launch; no identifier values are logged.
# CHANGELOG: v1.0.0-LOCAL-AI-PROVIDER-ADMISSION adds a nonpersistent,
#          hidden-key local provider configuration handoff.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Never prints, writes, caches or accepts AI keys
#          in command arguments; disables shell tracing; existing process
#          environment or hidden controlling-terminal input is used only.
# TENANT BOUNDARY: No tenant identifiers, cross-tenant reads or grants.
# AUTHORITY BOUNDARY: Provider transport configuration only. Global Principal,
#          tenant entitlement, provider usage and consent remain EOS governed.
# FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
# FAIL-CLOSED DECLARATION: Production markers, unsupported provider, missing
#          interactive secret/model or malformed configuration refuse launch.

set +x
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

case "${WILSY_ENV:-}" in
  production|Production|PRODUCTION|prod|Prod|PROD)
    echo "EOS_LOCAL_AI_CONFIG_ERROR=PRODUCTION_ENVIRONMENT_NOT_ALLOWED" >&2
    exit 2 ;;
esac
case "${ENV:-}" in
  production|Production|PRODUCTION|prod|Prod|PROD)
    echo "EOS_LOCAL_AI_CONFIG_ERROR=PRODUCTION_ENVIRONMENT_NOT_ALLOWED" >&2
    exit 2 ;;
esac

if [[ -n "${WILSY_AI_REASONING_PROVIDER:-}" && "${WILSY_AI_REASONING_PROVIDER}" != "openai" ]]; then
  echo "EOS_LOCAL_AI_CONFIG_ERROR=UNSUPPORTED_PROVIDER" >&2
  exit 2
fi

if [[ -z "${WILSY_AI_REASONING_MODEL:-}" ]]; then
  if [[ ! -r /dev/tty ]]; then
    echo "EOS_LOCAL_AI_CONFIG_ERROR=MODEL_REQUIRED_NO_TERMINAL" >&2
    exit 2
  fi
  printf 'Approved OpenAI model ID (not a credential): ' >/dev/tty
  IFS= read -r WILSY_AI_REASONING_MODEL </dev/tty || {
    echo "EOS_LOCAL_AI_CONFIG_ERROR=MODEL_INPUT_FAILED" >&2
    exit 2
  }
fi
if [[ ! "${WILSY_AI_REASONING_MODEL}" =~ ^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$ || "${WILSY_AI_REASONING_MODEL}" == key_* || "${WILSY_AI_REASONING_MODEL}" == sk-* || "${WILSY_AI_REASONING_MODEL}" == sk_* ]]; then
  echo "EOS_LOCAL_AI_CONFIG_ERROR=MODEL_ID_INVALID" >&2
  exit 2
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  if [[ ! -r /dev/tty ]]; then
    echo "EOS_LOCAL_AI_CONFIG_ERROR=API_KEY_REQUIRED_NO_TERMINAL" >&2
    exit 2
  fi
  printf 'OpenAI API key (hidden, never saved): ' >/dev/tty
  IFS= read -r -s OPENAI_API_KEY </dev/tty || {
    printf '\n' >/dev/tty
    echo "EOS_LOCAL_AI_CONFIG_ERROR=API_KEY_INPUT_FAILED" >&2
    exit 2
  }
  printf '\n' >/dev/tty
fi
if [[ -z "${OPENAI_API_KEY//[[:space:]]/}" || ${#OPENAI_API_KEY} -gt 4096 ]]; then
  echo "EOS_LOCAL_AI_CONFIG_ERROR=API_KEY_INVALID" >&2
  exit 2
fi

export WILSY_AI_REASONING_PROVIDER=openai
export WILSY_AI_REASONING_MODEL OPENAI_API_KEY

echo "EOS_LOCAL_AI_PROVIDER_SELECTOR=CONFIGURED"
echo "EOS_LOCAL_AI_PROVIDER_CREDENTIAL=SUPPLIED_NOT_VERIFIED"
echo "EOS_LOCAL_AI_PROVIDER_MODEL=CONFIGURED_NOT_VERIFIED"
echo "EOS_LOCAL_AI_NEXT=PYTHON_EOS_GLOBAL_PRINCIPAL_MFA_STARTUP"
exec bash "$ROOT_DIR/scripts/start-eos-local-mfa.sh"

# ARTIFACT: scripts/start-eos-local-ai.sh
# VERSION: v1.1.0-REJECT-CREDENTIAL-LIKE-MODEL-IDENTIFIERS
# AUTHORITY BOUNDARY: nonproduction provider configuration only; no IAM or usage grants
# TENANT POSTURE: exact-tenant admission continues inside Python EOS
# FAIL-CLOSED POSTURE: no provider fallback, no synthetic answer, no secret output
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
