"""TITLE: Strategy Project Relationship Exact-Source Registry Certificate.
VERSION: v1.0.0-LINK-REGISTRY-UNIT-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Verify source-independent tenant isolation, canonical command replay,
unique-index admission, pillar identity and audited link persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_strategy_project_relationship_registry.py
COLLABORATION / OWNERSHIP: StrategyProjectRelationshipRegistry, source-authorized
Company Strategy and Projects router contracts; no authenticated claims.
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.0.0-LINK-REGISTRY-UNIT-CERT tests verified in-memory persistence,
idempotent event replay, conflicts, absence of automatic DDL and cross-tenant
read isolation. Real Mongo transaction and HTTP browser tests remain separate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities only; no live DB or credentials.
TENANT BOUNDARY: Exact synthetic tenant scope; no wildcard or root fallback.
AUTHORITY BOUNDARY: Caller must independently source-certify current documents,
Projects entitlements and IAM before invoking registry methods.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from copy import deepcopy
import pytest

from tools.eos.saas.strategy_project_relationship_registry import (
    LINK_COLLECTION, EVENT_COLLECTION, StrategyProjectLinkError,
    StrategyProjectRelationshipRegistry,
)

TENANT = "WILSYTENANT-SYNTHETIC"
FOREIGN = "WILSYTENANT-FOREIGN"
ACTOR = "principal-synthetic"
PROJECT = "prj-" + "a" * 48
OTHER_PROJECT = "prj-" + "b" * 48
SESSION = object()


class Cursor:
    """Minimal session-free test transport cursor; real Mongo remains an independent gate."""
    def __init__(self, rows):
        """Retain an isolated snapshot to prevent mutation of persisted data."""
        self.rows = list(rows)

    def sort(self, keys):
        """Sort by the fields requested by source registry."""
        return Cursor(sorted(self.rows, key=lambda item: tuple(item.get(key, "") for key, _ in keys)))

    def limit(self, count):
        """Implement bounded page for exact tenant list source."""
        return Cursor(self.rows[:count])

    def __iter__(self):
        """Yield snapshot rows rather than an open Mongo cursor."""
        return iter(self.rows)


class Collection:
    """Mutable test double simulating exact equality Mongo queries and indexes."""
    def __init__(self):
        """Create an initially empty collection with no indexes."""
        self.rows = []
        self.indexes = {}

    def create_index(self, keys, *, name, **options):
        """Record explicit metadata DDL, not implicit query DDL."""
        self.indexes[name] = {"key": list(keys), **options}

    def index_information(self):
        """Report deterministic source index metadata."""
        return deepcopy(self.indexes)

    def find(self, query, *, session):
        """Require a caller-supplied session and exact query matches."""
        assert session is SESSION
        return Cursor(deepcopy([row for row in self.rows if all(row.get(k) == v for k, v in query.items())]))

    def find_one(self, query, *, session):
        """Fetch an isolated source row or None without broadening predicates."""
        return next(iter(self.find(query, session=session)), None)

    def insert_one(self, row, *, session):
        """Append one immutable event/link source row."""
        assert session is SESSION
        self.rows.append(deepcopy(row))


@pytest.fixture
def registry():
    """Build two independent source collections and explicit registry indexes."""
    database = {LINK_COLLECTION: Collection(), EVENT_COLLECTION: Collection()}
    result = StrategyProjectRelationshipRegistry(database)
    result.ensure_indexes()
    return result


def create(registry, *, tenant=TENANT, actor=ACTOR, project=PROJECT,
           pillar="pillar-one", revision=3, project_revision=6,
           command="stable-command"):
    """Issue an already source-authorized synthetic registry command."""
    return registry.link(tenant_id=tenant, actor_id=actor, project_id=project,
                         pillar_id=pillar, strategy_revision=revision,
                         strategy_fingerprint="a" * 128,
                         project_revision=project_revision,
                         idempotency_key=command, recorded_at="2026-11-22T22:00:00Z",
                         session=SESSION)


def test_unique_index_gate_is_explicit_and_fail_closed():
    """Never silently create indexes during a source command."""
    registry = StrategyProjectRelationshipRegistry({
        LINK_COLLECTION: Collection(), EVENT_COLLECTION: Collection()})
    with pytest.raises(StrategyProjectLinkError, match="STRATEGY_LINK_INDEX_UNAVAILABLE"):
        registry.require_indexes()
    assert registry.links.indexes == {} and registry.events.indexes == {}
    registry.ensure_indexes()
    registry.require_indexes()


def test_exact_idempotency_and_immutable_audit(registry):
    """A matching command replays exact evidence but creates no second event."""
    registry.require_indexes()
    one = create(registry)
    again = create(registry)
    assert one == again
    assert len(registry.links.rows) == len(registry.events.rows) == 1
    assert one["pillar_id"] == "pillar-one"
    assert one["project_id"] == PROJECT
    assert one["strategy_revision"] == 3 and one["project_revision"] == 6
    assert len(one["command_fingerprint"]) == 128
    assert "completion_percent" not in one and "financial_execution" not in one
    assert registry.list_links(tenant_id=TENANT, session=SESSION) == (one,)


def test_conflicting_replay_and_duplicate_identity_denied(registry):
    """One command key cannot be reassigned or a second link silently minted."""
    create(registry)
    with pytest.raises(StrategyProjectLinkError, match="STRATEGY_LINK_IDEMPOTENCY_CONFLICT"):
        create(registry, project=OTHER_PROJECT)
    with pytest.raises(StrategyProjectLinkError, match="STRATEGY_LINK_ALREADY_EXISTS"):
        create(registry, command="different-command")
    assert len(registry.links.rows) == len(registry.events.rows) == 1


def test_foreign_tenant_never_leaks_relationship_identity(registry):
    """Foreign scope is an independent exact lookup; no match is inferred."""
    create(registry)
    assert registry.list_links(tenant_id=FOREIGN, session=SESSION) == ()
    foreign = create(registry, tenant=FOREIGN)
    assert foreign["tenant_id"] == FOREIGN
    assert registry.list_links(tenant_id=TENANT, session=SESSION)[0]["tenant_id"] == TENANT
    assert len(registry.links.rows) == 2


@pytest.mark.parametrize("changes,expected", [
    ({"pillar": "pillar-seven"}, "STRATEGY_LINK_PILLAR_INVALID"),
    ({"revision": 0}, "STRATEGY_LINK_REVISION_INVALID"),
    ({"project_revision": 0}, "STRATEGY_LINK_PROJECT_REVISION_INVALID"),
    ({"project": "foreign"}, "STRATEGY_LINK_PROJECT_INVALID"),
    ({"tenant": ""}, "STRATEGY_LINK_TENANT_INVALID"),
    ({"actor": ""}, "STRATEGY_LINK_ACTOR_INVALID"),
])
def test_malformed_source_proofs_never_write(registry, changes, expected):
    """Reject unverified source coordinates before any persistence."""
    with pytest.raises(StrategyProjectLinkError, match=expected):
        create(registry, **changes)
    assert registry.links.rows == [] and registry.events.rows == []


# ARTIFACT: test_strategy_project_relationship_registry.py
# VERSION: v1.0.0-LINK-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: Synthetic registry contract only, never actual IAM.
# TENANT POSTURE: Strict scoped event and row readback checks.
# FAIL-CLOSED POSTURE: Missing DDL or diverged replay fails certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
