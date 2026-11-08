#!/usr/bin/env bash
set -euo pipefail

cat >&2 <<'NOTICE'
This legacy Node deployment path has been retired.
Kennel EOS is the canonical application/API runtime.

Do not install server/ Node dependencies, run PM2, execute legacy migrations,
or route production traffic through this script. Deploy only through the
reviewed Python EOS deployment workflow and its approved operational gates.
NOTICE

exit 1
