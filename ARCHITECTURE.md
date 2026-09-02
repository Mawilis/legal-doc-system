# Architecture

The sovereign path is:

`request -> Python EOS domain/authorization -> governed persistence/evidence`

Node services provide transport and orchestration only. Intelligence surfaces
produce advisory, provenance-bearing outputs and cannot grant authority.
Tenant scope is explicit on governed reads and writes; cross-tenant inference
is prohibited. Kennel EOS remains the exclusive financial execution boundary.

Repository governance is enforced by
`tools/eos/governance/repository_integrity_guard.py` and deterministic
`public_status.py` README drift checking. Documentation and generated maps are
projections, not runtime authorities.
