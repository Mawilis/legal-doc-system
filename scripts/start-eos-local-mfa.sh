#!/usr/bin/env bash
# TITLE: WILSY EOS Local-Development Global Principal MFA Launcher
# VERSION: v1.3.0-CANONICAL-DOTENV-DATABASE-SELECTION
# AUTHORITY: Local-development runtime startup only; no production authority.
# EPITOME: Resolve MONGODB_URI through the canonical EOS kernel precedence (process environment first, nonproduction repository dotenv second), validate the selected target, then verify the dedicated local-development AWS identity and KMS round trip before starting Python EOS.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/start-eos-local-mfa.sh
# COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; Python EOS owns authentication, database connection and application runtime.
# CERTIFICATION OR UPDATE DATE: 2026-11-16
# CHANGELOG:
#   v1.3.0-CANONICAL-DOTENV-DATABASE-SELECTION restores the established
#   launcher workflow by using the canonical EOS kernel resolver, preserving
#   process-environment precedence and nonproduction dotenv selection without
#   exposing the selected URI. Existing target validation and AWS/KMS gates
#   remain unchanged.
#   v1.2.3-EXPLICIT-MONGODB-TARGET corrects the URI preflight branch so valid
#   targets proceed and invalid targets fail closed before AWS/KMS startup.
#   v1.2.2-EXPLICIT-MONGODB-TARGET corrects the production-marker preflight
#   exit contract and refuses startup if either marker is production/prod.
#   v1.2.1-EXPLICIT-MONGODB-TARGET makes either production environment marker
#   fail closed even if the other marker declares a different environment.
#   v1.2.0-EXPLICIT-MONGODB-TARGET validates the canonical MONGODB_URI without
#   printing it. Loopback targets require authenticated rs0 configuration;
#   remote TLS/auth options remain owned by the URI and EOS connector.
#   v1.1.0-LOCAL-VENV-RUNTIME selects the repository .venv Python for both
#   the MFA/KMS startup probe and Uvicorn when available, avoiding an
#   incompatible host Python taking precedence; all role, identity, KMS,
#   host and port gates remain unchanged.
#   v1.0.0-LOCAL-EOS-MFA-LAUNCHER establishes a deterministic local-only
#   launcher using a dedicated AWS CLI assume-role profile, short-lived
#   credentials, a real KMS startup probe and the Python EOS Uvicorn entrypoint.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Clears static AWS credential environment variables; never creates, stores or accepts static credentials; never prints Mongo URI data.
# TENANT BOUNDARY: Launcher performs no tenant or identity record operations; EOS retains all tenant scoping.
# AUTHORITY BOUNDARY: Local-development role only; database identity remains the canonical MONGODB_URI resolved by the EOS kernel, with process-environment precedence and nonproduction dotenv fallback.
# FINANCIAL AUTHORITY BOUNDARY: No financial execution authority; Kennel EOS remains the exclusive financial execution authority.
# FAIL-CLOSED DECLARATION: Missing or structurally unsafe MONGODB_URI after canonical nonproduction resolution, production environment marker, AWS CLI, Python, KMS key ARN, expected role or KMS probe success prevents API startup.

# Reproducible local EOS launch with the dedicated local-development MFA role.
# Resolve through tools.eos.kernel.db so launcher selection matches EOS exactly:
# an explicit process value wins, otherwise nonproduction repository dotenv
# may populate the sole canonical MONGODB_URI. No alternate selector exists.
# The launcher validates only safe URI structure and local replica-set options.
# The EOS database connector remains responsible for authenticated connection,
# TLS, server identity and readiness. No database operation occurs here.
# Invoke with Bash because this governed script is distributed without an
# executable bit.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
else
  PYTHON="$(command -v python || true)"
fi
if [[ -z "$PYTHON" ]]; then
  echo "EOS_LOCAL_MFA_CONFIG_ERROR=PYTHON_REQUIRED" >&2
  exit 2
fi

if "$PYTHON" - <<'PY'
import os

production_markers = {"production", "prod"}
is_production = any(
    os.getenv(name, "").strip().lower() in production_markers
    for name in ("WILSY_ENV", "ENV")
)
raise SystemExit(0 if is_production else 1)
PY
then
  echo "EOS_LOCAL_MFA_CONFIG_ERROR=PRODUCTION_ENVIRONMENT_NOT_ALLOWED" >&2
  exit 2
fi

if ! MONGODB_URI="$("$PYTHON" - <<'PY'
from tools.eos.kernel.db import resolve_mongo_uri

uri = resolve_mongo_uri()
if not uri:
    raise SystemExit(1)
print(uri)
PY
)"; then
  echo "EOS_LOCAL_MFA_CONFIG_ERROR=MONGODB_URI_REQUIRED_OR_UNRESOLVABLE" >&2
  exit 2
fi
export MONGODB_URI

if "$PYTHON" - <<'PY'
import ipaddress
import os
from urllib.parse import parse_qs, urlsplit

raw_uri = os.environ.get("MONGODB_URI", "")
try:
    parsed = urlsplit(raw_uri)
    if parsed.scheme not in {"mongodb", "mongodb+srv"}:
        raise ValueError
    if not parsed.netloc or not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError
    if parsed.fragment:
        raise ValueError
    # Accessing .port validates malformed port syntax without exposing it.
    _ = parsed.port
    options = parse_qs(parsed.query, keep_blank_values=True)
    auth_mechanism = options.get("authMechanism", [""])[0].upper()
    has_authentication = bool(parsed.username) or auth_mechanism in {
        "MONGODB-AWS",
        "MONGODB-X509",
        "GSSAPI",
        "PLAIN",
    }
    if not has_authentication:
        raise ValueError

    hostname = parsed.hostname.rstrip(".").lower()
    is_loopback = hostname == "localhost"
    try:
        is_loopback = is_loopback or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        pass
    if is_loopback:
        replica_set = options.get("replicaSet", [""])[0]
        auth_source = options.get("authSource", [""])[0]
        if replica_set != "rs0" or not auth_source:
            raise ValueError
except (TypeError, ValueError):
    raise SystemExit(1)
PY
then
  :
else
  echo "EOS_LOCAL_MFA_CONFIG_ERROR=MONGODB_URI_INVALID_OR_UNVERIFIABLE_TARGET" >&2
  exit 2
fi

# Preserve MONGODB_URI as the only database selector. Exporting the canonical
# resolver's result ensures later dotenv loading cannot change the selection.

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
"$PYTHON" -m tools.eos.auth.global_principal_mfa_kms_probe
exec "$PYTHON" -m uvicorn tools.eos.api.server:app --host "$HOST" --port "$PORT"

# ARTIFACT: scripts/start-eos-local-mfa.sh
# VERSION: v1.3.0-CANONICAL-DOTENV-DATABASE-SELECTION
# AUTHORITY BOUNDARY: Local-development KMS identity verification and Python EOS startup only; MONGODB_URI remains the sole database connection authority and is selected through the canonical kernel resolver.
# TENANT POSTURE: No tenant, membership, factor or session state is created by the launcher.
# FAIL-CLOSED POSTURE: Missing or unverifiable canonical database target and failed local AWS identity/KMS validation prevent API startup.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
