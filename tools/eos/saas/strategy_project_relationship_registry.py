"""TITLE: WILSY OS Strategy-to-Project Relationship Evidence Registry.
VERSION: v1.0.0-EXACT-PUBLISHED-PILLAR-PROJECT-LINK
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Persist a canonical exact-tenant Strategy publication pillar/project
relationship and append-only audited command evidence without deriving strategy
completion, granting project visibility or changing published Strategy content.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/strategy_project_relationship_registry.py
COLLABORATION / OWNERSHIP: CompanyOperatingDocumentRouter owns IAM, source
verification and majority transactions; ProjectRegistry owns project identity.
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.0.0-EXACT-PUBLISHED-PILLAR-PROJECT-LINK introduces deterministic
SHA3-512 command fingerprints, tenant-scoped unique link and command-event
indexes, exact-replay idempotency, conflict denial and bounded source readback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No source body or identity disclosure on conflicts;
this registry never grants access, authenticates actors or authorizes updates.
TENANT BOUNDARY: Every command and query includes the exact current tenant.
AUTHORITY BOUNDARY: Authenticated Company Strategy author and independent
Projects read/admission are required at the caller; current source publication
and project status are caller-verified in the same transaction.
TRANSACTION BOUNDARY: Caller owns all sessions and transaction retries;
explicit index provisioning never runs inside an implicit source read.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS alone can execute money.
"""
from __future__ import annotations

from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import PyMongoError

VERSION: Final = "v1.0.0-EXACT-PUBLISHED-PILLAR-PROJECT-LINK"
LINK_COLLECTION: Final = "wilsy_strategy_project_links"
EVENT_COLLECTION: Final = "wilsy_strategy_project_link_events"
_LINK_INDEX: Final = "wilsy_strategy_link_exact_project_unique"
_REPLAY_INDEX: Final = "wilsy_strategy_link_command_replay_unique"
_ALLOWED_PILLARS: Final = frozenset(f"pillar-{word}" for word in
    ("one", "two", "three", "four", "five", "six"))


class StrategyProjectLinkError(ValueError):
    """Source-neutral, safe stable error without revealing foreign objects."""

    def __init__(self, code: str) -> None:
        """Expose a bounded contract error; never include source record data."""
        self.code = code
        super().__init__(code)


def _exact(value: object, label: str, *, pattern: str | None = None, maximum: int = 200) -> str:
    """Validate caller-verified identifiers; no normalization or fallback."""
    if not isinstance(value, str) or not value or value.strip() != value or len(value) > maximum:
        raise StrategyProjectLinkError(f"STRATEGY_LINK_{label}_INVALID")
    if pattern and re.fullmatch(pattern, value) is None:
        raise StrategyProjectLinkError(f"STRATEGY_LINK_{label}_INVALID")
    return value


def _fingerprint(data: dict[str, object]) -> str:
    """SHA3-512 of canonical JSON command material excluding delivery metadata."""
    return sha3_512(json.dumps(data, sort_keys=True, ensure_ascii=True,
                              separators=(",", ":")).encode("utf-8")).hexdigest()


def _without_id(row: dict[str, Any]) -> dict[str, Any]:
    """Remove MongoDB's internal identifier from an existing canonical row."""
    return {key: value for key, value in row.items() if key != "_id"}


class StrategyProjectRelationshipRegistry:
    """Tenant-scoped project link and immutable event persistence only.

    The caller must independently enforce company document read/author,
    project read and current entitlement, verify the exact published Strategy
    revision/pillar and current project in the same caller-owned transaction.
    This class never supplies a permission or a progress percentage.
    """

    def __init__(self, database: Any) -> None:
        """Bind collections from caller-owned canonical EOS database."""
        if database is None:
            raise StrategyProjectLinkError("STRATEGY_LINK_DATABASE_UNAVAILABLE")
        self.links = database[LINK_COLLECTION]
        self.events = database[EVENT_COLLECTION]

    def ensure_indexes(self) -> None:
        """Explicit administrator DDL outside transactions; no hidden startup."""
        self.links.create_index([("tenant_id", ASCENDING), ("classification", ASCENDING),
                                 ("pillar_id", ASCENDING), ("project_id", ASCENDING)],
                                unique=True, name=_LINK_INDEX)
        self.events.create_index([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                                 unique=True, name=_REPLAY_INDEX)

    def require_indexes(self) -> None:
        """Refuse any command without verified exact scoped unique indexes."""
        try:
            links = self.links.index_information()
            events = self.events.index_information()
        except PyMongoError as exc:
            raise StrategyProjectLinkError("STRATEGY_LINK_INDEX_UNAVAILABLE") from exc
        expected_links = [("tenant_id", 1), ("classification", 1),
                          ("pillar_id", 1), ("project_id", 1)]
        expected_events = [("tenant_id", 1), ("idempotency_key", 1)]
        for indexes, name, fields in ((links, _LINK_INDEX, expected_links),
                                      (events, _REPLAY_INDEX, expected_events)):
            definition = indexes.get(name)
            if not isinstance(definition, dict) or definition.get("unique") is not True or list(
                definition.get("key", [])
            ) != fields:
                raise StrategyProjectLinkError("STRATEGY_LINK_INDEX_UNAVAILABLE")

    def list_links(self, *, tenant_id: str, session: Any, limit: int = 100) -> tuple[dict[str, Any], ...]:
        """Return bounded exact-tenant relationship evidence, never foreign data.

        This read is *not* an authorization decision: caller must verify current
        project visibility and publication currentness for each displayed row.
        """
        tenant = _exact(tenant_id, "TENANT")
        if session is None or type(limit) is not int or not 1 <= limit <= 100:
            raise StrategyProjectLinkError("STRATEGY_LINK_READ_CONTEXT_INVALID")
        try:
            rows = list(self.links.find({"tenant_id": tenant, "classification": "STRATEGY"},
                                        session=session).sort([("pillar_id", 1), ("project_id", 1)]).limit(limit + 1))
        except PyMongoError as exc:
            raise StrategyProjectLinkError("STRATEGY_LINK_SOURCE_UNAVAILABLE") from exc
        if len(rows) > limit:
            raise StrategyProjectLinkError("STRATEGY_LINK_PAGE_LIMIT_EXCEEDED")
        result = tuple(_without_id(row) for row in rows)
        if any(row.get("tenant_id") != tenant or row.get("classification") != "STRATEGY" for row in result):
            raise StrategyProjectLinkError("STRATEGY_LINK_PERSISTED_SCOPE_INVALID")
        return result

    def link(self, *, tenant_id: str, actor_id: str, project_id: str, pillar_id: str,
             strategy_revision: int, strategy_fingerprint: str, project_revision: int,
             idempotency_key: str, recorded_at: str, session: Any) -> dict[str, Any]:
        """Persist one source-proven published-pillar association.

        Repeated matching command+key returns exact event-backed receipt.
        Reusing the same key for changed material or linking a stale
        publication/project revision raises a conflict at caller/source boundary.
        A second identical link under a new key cannot invent a new event.
        """
        tenant = _exact(tenant_id, "TENANT")
        actor = _exact(actor_id, "ACTOR")
        project = _exact(project_id, "PROJECT", pattern=r"prj-[a-f0-9]{48}")
        pillar = _exact(pillar_id, "PILLAR", maximum=64)
        if pillar not in _ALLOWED_PILLARS:
            raise StrategyProjectLinkError("STRATEGY_LINK_PILLAR_INVALID")
        if type(strategy_revision) is not int or strategy_revision < 1:
            raise StrategyProjectLinkError("STRATEGY_LINK_REVISION_INVALID")
        if type(project_revision) is not int or project_revision < 1:
            raise StrategyProjectLinkError("STRATEGY_LINK_PROJECT_REVISION_INVALID")
        digest = _exact(strategy_fingerprint, "FINGERPRINT", pattern=r"[a-f0-9]{128}", maximum=128)
        command = _exact(idempotency_key, "IDEMPOTENCY", maximum=200)
        when = _exact(recorded_at, "TIMESTAMP", maximum=60)
        if session is None:
            raise StrategyProjectLinkError("STRATEGY_LINK_TRANSACTION_REQUIRED")
        material: dict[str, object] = {"tenant_id": tenant, "actor_principal_id": actor,
            "classification": "STRATEGY", "project_id": project, "pillar_id": pillar,
            "strategy_revision": strategy_revision, "strategy_fingerprint": digest,
            "project_revision": project_revision}
        fingerprint = _fingerprint(material)
        try:
            replay = self.events.find_one({"tenant_id": tenant, "idempotency_key": command}, session=session)
            if replay is not None:
                if not compare_digest(str(replay.get("command_fingerprint", "")), fingerprint):
                    raise StrategyProjectLinkError("STRATEGY_LINK_IDEMPOTENCY_CONFLICT")
                existing = self.links.find_one({"tenant_id": tenant, "classification": "STRATEGY",
                    "pillar_id": pillar, "project_id": project}, session=session)
                if existing is None or existing.get("command_fingerprint") != fingerprint:
                    raise StrategyProjectLinkError("STRATEGY_LINK_REPLAY_READBACK_UNVERIFIED")
                return _without_id(existing)
            existing = self.links.find_one({"tenant_id": tenant, "classification": "STRATEGY",
                "pillar_id": pillar, "project_id": project}, session=session)
            if existing is not None:
                raise StrategyProjectLinkError("STRATEGY_LINK_ALREADY_EXISTS")
            record = {**material, "schema": "WILSY-STRATEGY-PROJECT-LINK/V1",
                      "idempotency_key": command, "recorded_at": when,
                      "command_fingerprint": fingerprint}
            self.links.insert_one(record, session=session)
            self.events.insert_one({"schema": "WILSY-STRATEGY-PROJECT-LINK-EVENT/V1",
                "tenant_id": tenant, "idempotency_key": command,
                "command_fingerprint": fingerprint, "project_id": project,
                "pillar_id": pillar, "actor_principal_id": actor, "recorded_at": when},
                session=session)
            readback = self.links.find_one({"tenant_id": tenant, "classification": "STRATEGY",
                "pillar_id": pillar, "project_id": project}, session=session)
            if readback is None or _without_id(readback) != record:
                raise StrategyProjectLinkError("STRATEGY_LINK_READBACK_UNVERIFIED")
            return record
        except PyMongoError as exc:
            raise StrategyProjectLinkError("STRATEGY_LINK_SOURCE_UNAVAILABLE") from exc


# ARTIFACT: strategy_project_relationship_registry.py
# VERSION: v1.0.0-EXACT-PUBLISHED-PILLAR-PROJECT-LINK
# AUTHORITY BOUNDARY: Caller independently verifies published document and project IAM/currentness.
# TENANT POSTURE: Exact tenant-scoped keys, immutable audited idempotency and no foreign lookup.
# FAIL-CLOSED POSTURE: Missing indexes/replay/source and unverified readback abort commands.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
