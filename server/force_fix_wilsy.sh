#!/usr/bin/env bash
# TITLE: Retired legacy unauthenticated MongoDB role injection
# VERSION: v2.0.0
# AUTHORITY: WILSY EOS Security Engineering
# PURPOSE: Prevent unauthenticated MongoDB role changes and broad application grants.
# SECURITY: This legacy script is intentionally non-operational. It contains no
# credentials and never starts mongosh or changes database authorization.
# CHANGELOG:
# - v2.0.0: Retire unauthenticated role injection and broad service-account grants.
# END OF WILSY OS SOVEREIGN ARTIFACT

set -euo pipefail

printf '%s\n' >&2 \
  "DISABLED: unauthenticated MongoDB role injection is prohibited." \
  "Restore database access only through approved break-glass governance and audited infrastructure changes."
exit 1
