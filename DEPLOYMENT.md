# WILSY OS deployment

## Canonical runtime

Kennel EOS is the existing canonical application/API and business authority.
The supported API runtime is Python:

```bash
python -m uvicorn tools.eos.api.server:app --host 0.0.0.0 --port 9095
```

The repository-root `Dockerfile`, `Dockerfile.eos`, and
`docker-compose.prod.yml` define the Python EOS candidate runtime. The durable
worker is a separate Python process and is opt-in through the
`python-workers` Compose profile.

## Development

Use the repository's supported development stack:

```bash
npm run dev
npm run dev:kernel
```

Node is used here for frontend build and browser-test tooling only. It is not
the application API, business runtime, database owner, worker, or deployment
authority.

## Retired backend paths

The former Node/Express BFF, PM2 launch definitions, Node worker image,
Node deployment scripts, and legacy server Kubernetes deployment overlay are
retired. Do not run `pm2`, `npm start` from `server/`, legacy deployment
scripts, or manifests under `server/k8s/`. Those entrypoints are disabled or
fail closed.

## Production gate

A successful build or CI run is not production authorization. Production
activation requires the exact reviewed Python EOS artifact, approved secrets
and workload identity, verified Mongo replica-set connectivity, independent
security review, and explicit operational approval. Do not activate the
optional worker or perform database migrations without their separate approval.

## Legal-evidence reconciliation

The dedicated internal route is
`POST /api/legal-operations/evidence-provider/reconciliation`; it is not the
generic `/runtime/execute` endpoint.

Production remains NO-GO until the actual internal caller is approved and
wired to this exact path/body contract, the deployment audit fingerprint
parity is observed, the unified production security audit passes, and
operational review accepts the end-to-end HTTP/real-Mongo certification.
