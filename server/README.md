# Retired legacy Node backend

This directory contains historical Node/Express implementation and test
artifacts. It is **not** a supported application runtime, API gateway, worker,
database owner, or production deployment target.

Kennel EOS is the existing canonical application/API and business authority.
The supported API is the Python application at
`tools.eos.api.server:app`, served on port 9095. Its business database
lifecycle is owned by the EOS kernel.

The former PM2 application definitions are inert. The old Node API and worker
Dockerfiles fail closed. Legacy production deployment scripts and Kubernetes
manifests are retired. Do not restore or invoke those paths.

Node tooling remains in the repository only where needed for frontend build,
browser certification, or isolated historical test maintenance. This does not
authorize a Node server, Express BFF, Node worker, or Node-owned business
logic.

See the repository-root `DEPLOYMENT.md` and
`docs/architecture/eos-runtime-database-consumer-inventory.md` for the
supported runtime boundary and production gates.
