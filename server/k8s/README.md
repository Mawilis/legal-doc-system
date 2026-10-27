# Retired Node deployment manifests

**Status: MIGRATION_ONLY — DO NOT APPLY.**

The former `server/k8s` deployment targeted a Node service on port 4000 and referenced an obsolete predictive-engine image. Its deployment script is retired, and this directory's Kustomization intentionally contains no resources so `kubectl apply -k server/k8s` cannot deploy it.

The canonical Python EOS production target is `k8s/eos-api-production.yaml`, with immutable image publication owned by `.github/workflows/eos-image-publication.yml`.

The old individual YAML files remain as migration evidence only; they do not establish that a production workload exists or is healthy. Do not promote an image or mutate a cluster until the canonical manifest, exact digest, runtime secrets, workload identity, and readiness are independently verified.
