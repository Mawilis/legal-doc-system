#!/usr/bin/env bash
# TITLE: Retired legacy MongoDB application-account elevation
# VERSION: v2.0.0
# AUTHORITY: WILSY EOS Security Engineering
# PURPOSE: Prevent application identities from managing MongoDB users or roles.
# SECURITY: This legacy script is intentionally non-operational. It contains no
# credentials and cannot grant userAdmin or other administrative privileges.
# CHANGELOG:
# - v2.0.0: Retire application-account self-elevation and privileged role grants.
# END OF WILSY OS SOVEREIGN ARTIFACT

set -euo pipefail

printf '%s\n' >&2 \
  "DISABLED: application-account role administration is prohibited." \
  "Provision least-privilege database roles through the governed infrastructure workflow."
exit 1
