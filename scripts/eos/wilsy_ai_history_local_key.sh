#!/usr/bin/env bash
# WILSY OS Sovereign Development Key Bootstrap
# TITLE: EOS Local Encrypted AI Conversation History Key Loader
# VERSION: v1.0.0-MW-T11-LOCAL-KEY-ADMISSION
# AUTHORITY: WILSY OS Core Governance
# EPITOME: Load one stable, locally owned 256-bit key into the existing
#          Python EOS process environment without logging the key or invoking
#          paid KMS. Not a production key-management mechanism.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/eos/wilsy_ai_history_local_key.sh
# COLLABORATION / OWNERSHIP: Python EOS local runtime startup; no Node backend.
# CERTIFICATION / UPDATE DATE: 2026-11-25
# CHANGELOG: v1.0.0-MW-T11-LOCAL-KEY-ADMISSION provides one guarded
#            user-private local key file and fail-closed validation.
# COMPLIANCE: AGENTS.md; POSIX shell development key boundary; no production key admission
# AUTHORITY BOUNDARY: Development process environment only; Python EOS is source owner
# SECURITY / PRIVACY POSTURE: No secret printed, committed, copied to logs or
#                             placed inside repository files.
# TENANT BOUNDARY: Secret is process master material; AES-GCM AAD binds each
#                  encrypted conversation to current EOS tenant and principal.
# FINANCIAL AUTHORITY BOUNDARY: No KMS paid call or financial action.
#
# Use: source scripts/eos/wilsy_ai_history_local_key.sh
# Then restart Python EOS from the SAME shell with the existing MFA launcher.
#
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  printf 'WILSY_AI_HISTORY_KEY=SOURCE_THIS_SCRIPT_NOT_EXECUTE\n' >&2
  exit 2
fi
_wilsy_ai_key_dir="${HOME}/.config/wilsy-os"
_wilsy_ai_key_file="${_wilsy_ai_key_dir}/dev-ai-history-key.b64"
umask 077
if [[ -L "${_wilsy_ai_key_file}" ]]; then
  printf 'WILSY_AI_HISTORY_KEY=SYMLINK_DENIED\n' >&2
  return 2
fi
if ! mkdir -p "${_wilsy_ai_key_dir}"; then
  printf 'WILSY_AI_HISTORY_KEY=DIRECTORY_UNAVAILABLE\n' >&2
  return 2
fi
if ! python - "${_wilsy_ai_key_file}" <<'PY'
import base64
import os
import pathlib
import secrets
import stat
import sys

path = pathlib.Path(sys.argv[1])
if path.is_symlink():
    raise SystemExit("WILSY_AI_HISTORY_KEY=SYMLINK_DENIED")
try:
    descriptor = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
except FileExistsError:
    pass
else:
    with os.fdopen(descriptor, "w", encoding="ascii") as stream:
        stream.write(base64.b64encode(secrets.token_bytes(32)).decode("ascii") + "\n")
mode = path.stat().st_mode
if not stat.S_ISREG(mode):
    raise SystemExit("WILSY_AI_HISTORY_KEY=FILE_INVALID")
os.chmod(path, 0o600)
encoded = path.read_text(encoding="ascii").strip()
try:
    payload = base64.b64decode(encoded, validate=True)
except ValueError:
    raise SystemExit("WILSY_AI_HISTORY_KEY=ENCODING_INVALID")
if len(payload) != 32:
    raise SystemExit("WILSY_AI_HISTORY_KEY=LENGTH_INVALID")
PY
then
  unset WILSY_AI_HISTORY_KEY_B64
  return 2
fi
export WILSY_AI_HISTORY_KEY_B64
WILSY_AI_HISTORY_KEY_B64="$(cat "${_wilsy_ai_key_file}")"
unset _wilsy_ai_key_dir _wilsy_ai_key_file
printf 'WILSY_AI_HISTORY_KEY=CONFIGURED_LOCAL_DEVELOPMENT\n'
printf 'WILSY_AI_HISTORY_KEY_NOTE=RESTART_PYTHON_EOS_IN_THIS_SHELL\n'

# ARTIFACT: wilsy_ai_history_local_key.sh
# VERSION: v1.0.0-MW-T11-LOCAL-KEY-ADMISSION
# AUTHORITY BOUNDARY: local key provisioning only; EOS owns all durable records
# TENANT POSTURE: not an IAM grant or tenant switch
# FAIL-CLOSED POSTURE: refuses symlink, malformed key or insecure file
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
