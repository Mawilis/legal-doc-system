#!/usr/bin/env bash
# TITLE: Retired legacy tenant self-authorization bootstrap
# VERSION: v2.0.0
# AUTHORITY: WILSY EOS Security Engineering
# PURPOSE: Prevent service-account self-grant of MongoDB tenant privileges.
# SECURITY: This legacy script is intentionally non-operational. It contains no
# credentials and must not be used to provision MongoDB roles.
# CHANGELOG:
# - v2.0.0: Retire hard-coded service credentials and self-authorizing grants.
# END OF WILSY OS SOVEREIGN ARTIFACT

set -euo pipefail

printf '%s\n' >&2 \
  "DISABLED: legacy tenant self-authorization is prohibited." \
  "Use the governed infrastructure provisioning workflow with an external administrator identity."
exit 1
