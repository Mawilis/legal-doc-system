#!/usr/bin/env bash
# TITLE: WILSY OS Local Institutional AI + Global Principal MFA Launcher
# VERSION: v1.2.0-NONBILLABLE-MODEL-METADATA-PREFLIGHT
# AUTHORITY: Wilsy OS Core Governance; nonproduction local launch only.
# EPITOME: Supply explicit ephemeral OpenAI provider configuration to the
#          already-certified Python EOS/MFA launcher without changing IAM,
#          commercial entitlement, provider admission or reasoning contracts.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/start-eos-local-ai.sh
# COLLABORATION / OWNERSHIP: Scripts/start-eos-local-mfa.sh owns AWS/KMS and
#          Python EOS startup; reasoning_provider_runtime.py owns the binding;
#          wilsy_ai_reasoning_router.py owns tenant and usage authorization.
# CERTIFICATION / UPDATE DATE: 2026-11-22
# CHANGELOG: v1.2.0-NONBILLABLE-MODEL-METADATA-PREFLIGHT validates
#          current credential/model metadata access using one read-only GET,
#          no inference or quota admission. --probe-only ends without EOS launch.
#          Status is safely classified, never prints credentials/vendor bodies.
# CHANGELOG: v1.2.0-NONBILLABLE-MODEL-METADATA-PREFLIGHT rejects common API key/tracking-id prefixes in the model field before child process launch; no identifier values are logged.
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
#          interactive secret/model, unavailable model metadata, malformed
#          configuration or a failed nonbillable preflight refuse launch.

set +x
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--probe-only" ) ]]; then
  echo "EOS_LOCAL_AI_CONFIG_ERROR=UNSUPPORTED_ARGUMENT" >&2
  exit 2
fi

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

# A non-generative model metadata read. This cannot establish API quota,
# billable execution, current tenant entitlement, or usage finalization.
# urllib uses system certificate verification and makes no automatic retries.
python - <<'PY'
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

model = os.environ["WILSY_AI_REASONING_MODEL"]
key = os.environ["OPENAI_API_KEY"]
url = "https://api.openai.com/v1/models/" + urllib.parse.quote(model, safe="")
request = urllib.request.Request(
    url,
    method="GET",
    headers={"Authorization": "Bearer " + key, "Accept": "application/json"},
)

try:
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            print("EOS_LOCAL_AI_PREFLIGHT=UNEXPECTED_HTTP_STATUS", file=sys.stderr)
            sys.exit(3)
except urllib.error.HTTPError as error:
    status = error.code
    if status in (401, 403):
        reason = "CREDENTIAL_OR_ACCESS_REJECTED"
    elif status == 404:
        reason = "MODEL_NOT_ACCESSIBLE"
    elif status == 429:
        reason = "RATE_LIMIT_OR_QUOTA_UNVERIFIED"
    elif status in (408, 409) or status >= 500:
        reason = "PROVIDER_HTTP_UNAVAILABLE"
    else:
        reason = "PROVIDER_HTTP_REJECTED"
    print("EOS_LOCAL_AI_PREFLIGHT=" + reason, file=sys.stderr)
    print("EOS_LOCAL_AI_PREFLIGHT_HTTP_STATUS=" + str(status), file=sys.stderr)
    sys.exit(3)
except (urllib.error.URLError, TimeoutError, OSError):
    print("EOS_LOCAL_AI_PREFLIGHT=TRANSPORT_UNAVAILABLE", file=sys.stderr)
    sys.exit(3)
except Exception:
    print("EOS_LOCAL_AI_PREFLIGHT=UNCLASSIFIED_FAILURE", file=sys.stderr)
    sys.exit(3)

print("EOS_LOCAL_AI_PREFLIGHT=MODEL_METADATA_VERIFIED_ONLY")
print("EOS_LOCAL_AI_QUOTA=NOT_VERIFIED")
print("EOS_LOCAL_AI_BILLABLE_EXECUTION=NOT_PERFORMED")
PY

if [[ "${1:-}" == "--probe-only" ]]; then
  echo "EOS_LOCAL_AI_NEXT=NO_EOS_LAUNCH_PROBE_ONLY"
  exit 0
fi


echo "EOS_LOCAL_AI_PROVIDER_SELECTOR=CONFIGURED"
echo "EOS_LOCAL_AI_PROVIDER_CREDENTIAL=SUPPLIED_NOT_VERIFIED"
echo "EOS_LOCAL_AI_PROVIDER_MODEL=CONFIGURED_NOT_VERIFIED"
echo "EOS_LOCAL_AI_NEXT=PYTHON_EOS_GLOBAL_PRINCIPAL_MFA_STARTUP"
exec bash "$ROOT_DIR/scripts/start-eos-local-mfa.sh"

# ARTIFACT: scripts/start-eos-local-ai.sh
# VERSION: v1.2.0-NONBILLABLE-MODEL-METADATA-PREFLIGHT
# AUTHORITY BOUNDARY: nonproduction provider configuration only; no IAM or usage grants
# TENANT POSTURE: exact-tenant admission continues inside Python EOS
# FAIL-CLOSED POSTURE: no provider fallback, no synthetic answer, no secret output
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
