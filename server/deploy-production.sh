#!/usr/bin/env bash
set -euo pipefail

# TITLE: Retired Node API deployment entrypoint
# VERSION: v1.0.0-RETIRED-NODE-BFF-DEPLOY
# AUTHORITY: No deployment authority.
# EPITOME: Prevents the obsolete Node API BFF deployment path from being invoked.
# ABSOLUTE CANONICAL PATH: server/deploy-production.sh
# CERTIFICATION / UPDATE DATE: 2026-10-27
# CHANGELOG: The former Node server.js / port 4000 deployment is retired. The canonical
#            Python EOS image is built by .github/workflows/eos-image-publication.yml
#            and deployed through the reviewed root k8s/eos-api-production.yaml manifest.
# SECURITY / PRIVACY POSTURE: Does not inspect or print environment values, credentials,
#                             cluster state, or production configuration.
# FAIL-CLOSED POSTURE: Always exits nonzero. No image build, kubectl mutation, or rollout occurs.

echo "NODE_BFF_DEPLOYMENT_RETIRED: use the reviewed Python EOS image publication and deployment workflow." >&2
exit 2

# ARTIFACT: server/deploy-production.sh
# AUTHORITY BOUNDARY: No deployment authority.
# FAIL-CLOSED POSTURE: Deployment is disabled.
# END OF WILSY OS SOVEREIGN ARTIFACT
