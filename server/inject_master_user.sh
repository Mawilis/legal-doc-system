#!/usr/bin/env bash
# TITLE: Retired legacy master-identity injection
# VERSION: v2.0.0
# AUTHORITY: WILSY EOS Identity and Security Engineering
# PURPOSE: Prevent direct creation of privileged identities outside canonical IAM.
# SECURITY: This legacy script is intentionally non-operational. It contains no
# credentials and cannot write to the users collection.
# CHANGELOG:
# - v2.0.0: Retire direct privileged-user upsert and embedded service credentials.
# END OF WILSY OS SOVEREIGN ARTIFACT

set -euo pipefail

printf '%s\n' >&2 \
  "DISABLED: direct privileged identity injection is prohibited." \
  "Use the canonical global-principal, membership, capacity, MFA and governed role-assignment flows."
exit 1
