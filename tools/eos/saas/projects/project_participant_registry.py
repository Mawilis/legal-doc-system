"""TITLE: WILSY OS Governed Project Participant Registry
VERSION: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY
AUTHORITY: Python EOS project-scoped participant persistence and immutable audit.
EPITOME: Explicit project participation roles, source-backed grant/revoke, exact
         tenant/project/principal matching, revision CAS and durable replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_participant_registry.py
COLLABORATION / OWNERSHIP: Projects router authorizes owner commands and
         current principal/membership; task and notes services must additionally
         revalidate current IAM and resource visibility on every operation.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY adds exact-principal project
         discovery through an indexed, bounded tenant/ACTIVE state projection.
         It does not bypass IAM, project entitlement or participant record scope.
CHANGELOG: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY binds replay metadata to
         verified participant revision/fingerprint/type and prevents
         clock rollback during revocation; no previous authority is broadened.
CHANGELOG: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY introduces bounded,
         tenant-scoped participant grants and revocations with immutable audit.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque principals, no employee admission, secrets
         or content. SHA3 integrity is not an institutional digital signature.
TENANT BOUNDARY: Every read, write, audit and replay includes exact tenant and
         project scope, with no root/founder fallback or cross-tenant disclosure.
AUTHORITY BOUNDARY: A participant record is necessary but never sufficient for
         API access; current authenticated principal, membership, capacity,
         role assignment, entitlement and operation must also be checked by EOS.
TRANSACTION BOUNDARY: Caller-owned MongoDB sessions and majority transactions;
         no hidden Mongo client, transaction, role grants or principal creation.
FINANCIAL AUTHORITY BOUNDARY: No payment or financial approval; Kennel EOS only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Any, Final, Literal

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION: Final[str] = "v1.1.0-PRINCIPAL-PROJECT-DISCOVERY"
COLLECTION: Final[str] = "wilsy_project_participants"
EVENT_COLLECTION: Final[str] = "wilsy_project_participant_events"
SCHEMA: Final[str] = "wilsy.project.participant.v1"
_PROJECT = re.compile(r"^prj-[0-9a-f]{48}$")
_DIGEST = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})
PARTICIPANT_ROLES: Final[frozenset[str]] = frozenset({"VIEWER", "CONTRIBUTOR"})


class ProjectParticipantError(RuntimeError):
    """Stable, bounded participant authority failure without identity disclosure."""

    def __init__(self, code: str) -> None:
        """Preserve machine-readable failure code only."""
        self.code = code
        super().__init__(code)


class ProjectParticipantConflict(ProjectParticipantError):
    """Contradictory replay, stale revision or denied grant state."""


class ProjectParticipantNotFound(ProjectParticipantError):
    """Absent and foreign-tenant participant states share one absence result."""


def _identifier(value: object, name: str) -> str:
    """Validate exact opaque identity, including reserved namespace rejection."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 180
        or value != value.strip()
        or any(ord(char) < 33 for char in value)
    ):
        raise ProjectParticipantError("PROJECT_PARTICIPANT_" + name + "_INVALID")
    if name == "TENANT" and value.upper() in _FORBIDDEN:
        raise ProjectParticipantError("PROJECT_PARTICIPANT_TENANT_INVALID")
    if name == "PROJECT" and not _PROJECT.fullmatch(value):
        raise ProjectParticipantError("PROJECT_PARTICIPANT_PROJECT_INVALID")
    return value


def _time(value: object) -> datetime:
    """Reject naive domain input and normalize to UTC for canonical evidence."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectParticipantError("PROJECT_PARTICIPANT_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _from_bson_time(value: object) -> datetime:
    """Normalize PyMongo UTC-naive BSON reads without relaxing domain inputs."""
    if not isinstance(value, datetime):
        raise ProjectParticipantError("PROJECT_PARTICIPANT_TIMESTAMP_INVALID")
    return _time(value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value)


def _digest(data: dict[str, object]) -> str:
    """Compute deterministic, unkeyed SHA3-512 integrity over semantic state."""
    return sha3_512(json.dumps(
        data, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ProjectParticipant:
    """One explicit project role assignment; no admission or permission implied.

    ACTIVE means the grant is not revoked, not that the principal is currently
    employed, authenticated, entitled, licensed or authorized for any command.
    """

    tenant_id: str
    project_id: str
    principal_id: str
    role: Literal["VIEWER", "CONTRIBUTOR"]
    state: Literal["ACTIVE", "REVOKED"]
    revision: int
    granted_by_principal_id: str
    updated_by_principal_id: str
    created_at: datetime
    updated_at: datetime
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact state and reject a mismatched persisted fingerprint."""
        for value, name in (
            (self.tenant_id, "TENANT"), (self.project_id, "PROJECT"),
            (self.principal_id, "PRINCIPAL"),
            (self.granted_by_principal_id, "GRANTOR"),
            (self.updated_by_principal_id, "ACTOR"),
        ):
            _identifier(value, name)
        if self.role not in PARTICIPANT_ROLES or self.state not in ("ACTIVE", "REVOKED"):
            raise ProjectParticipantError("PROJECT_PARTICIPANT_ROLE_STATE_INVALID")
        if type(self.revision) is not int or self.revision < 1:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_REVISION_INVALID")
        created, updated = _time(self.created_at), _time(self.updated_at)
        if updated < created:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_TIMESTAMP_ORDER_INVALID")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)
        computed = _digest(self.canonical())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not _DIGEST.fullmatch(self.fingerprint)
            or not compare_digest(self.fingerprint, computed)
        ):
            raise ProjectParticipantError("PROJECT_PARTICIPANT_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", computed)

    def canonical(self) -> dict[str, object]:
        """Return the exact stable serialization excluding derived checksum."""
        return {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "principal_id": self.principal_id,
            "role": self.role, "state": self.state, "revision": self.revision,
            "granted_by_principal_id": self.granted_by_principal_id,
            "updated_by_principal_id": self.updated_by_principal_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_dict(self) -> dict[str, object]:
        """Expose source-owned state without treating the checksum as a signature."""
        return {**self.canonical(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, row: dict[str, object]) -> ProjectParticipant:
        """Fail closed on missing, extraneous or tampered stored participant fields."""
        fields = {
            "schema", "tenant_id", "project_id", "principal_id", "role",
            "state", "revision", "granted_by_principal_id",
            "updated_by_principal_id", "created_at", "updated_at", "fingerprint",
        }
        if not isinstance(row, dict) or set(row) != fields or row["schema"] != SCHEMA:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_RECORD_INVALID")
        data = {key: row[key] for key in fields if key != "schema"}
        for key in ("created_at", "updated_at"):
            raw = data[key]
            try:
                data[key] = _from_bson_time(raw) if isinstance(raw, datetime) else _time(datetime.fromisoformat(raw)) if isinstance(raw, str) else _from_bson_time(raw)
            except (TypeError, ValueError) as error:
                raise ProjectParticipantError("PROJECT_PARTICIPANT_TIMESTAMP_INVALID") from error
        try:
            return cls(**data)
        except TypeError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_RECORD_INVALID") from error

    def change(
        self, *, role: str, state: str, actor_principal_id: str,
        expected_revision: int, occurred_at: datetime,
    ) -> ProjectParticipant:
        """Require exact revision and explicit state transition, never implicit revival."""
        _identifier(actor_principal_id, "ACTOR")
        if type(expected_revision) is not int or expected_revision != self.revision:
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_REVISION_CONFLICT")
        if self.state != "ACTIVE" or state != "REVOKED":
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_TRANSITION_DENIED")
        if role != self.role:
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_ROLE_CHANGE_DENIED")
        stamp = _time(occurred_at)
        if stamp < self.updated_at:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_TIMESTAMP_ORDER_INVALID")
        return replace(
            self, state="REVOKED", revision=self.revision + 1,
            updated_by_principal_id=actor_principal_id, updated_at=stamp,
            fingerprint="",
        )


class ProjectParticipantRegistry:
    """Tenant/project-bound participant grants with immutable audit and replay.

    Before invoking this persistence layer, the EOS HTTP composition must verify
    the current project, independent owner permission, product entitlement and
    current principal/membership eligibility. No reads skip session boundaries.
    """

    def __init__(self, participants: Any, events: Any) -> None:
        """Adopt caller-provided collections without creating indexes or sessions."""
        if participants is None or events is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_COLLECTION_REQUIRED")
        self._participants = participants
        self._events = events

    @staticmethod
    def ensure_indexes(participants: Any, events: Any) -> None:
        """Create additive exact-tenant identities and audit-replay indexes."""
        try:
            participants.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("principal_id", ASCENDING)],
                unique=True, name="wilsy_project_participant_identity_unique",
            )
            participants.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("state", ASCENDING), ("principal_id", ASCENDING)],
                name="wilsy_project_participant_active_list",
            )
            participants.create_index(
                [("tenant_id", ASCENDING), ("principal_id", ASCENDING),
                 ("state", ASCENDING), ("project_id", ASCENDING)],
                name="wilsy_project_participant_principal_projects",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name="wilsy_project_participant_replay_unique",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("project_id", ASCENDING),
                 ("principal_id", ASCENDING), ("revision", ASCENDING)],
                unique=True, name="wilsy_project_participant_event_revision_unique",
            )
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_INDEX_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, project_id: str, principal_id: str,
        session: Any, require_active: bool = True,
    ) -> ProjectParticipant:
        """Read exact participant; foreign/revoked/absent reveal no record."""
        if session is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SESSION_REQUIRED")
        predicate = {
            "tenant_id": _identifier(tenant_id, "TENANT"),
            "project_id": _identifier(project_id, "PROJECT"),
            "principal_id": _identifier(principal_id, "PRINCIPAL"),
        }
        if require_active:
            predicate["state"] = "ACTIVE"
        try:
            row = self._participants.find_one(predicate, session=session)
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_READ_UNAVAILABLE") from error
        if row is None:
            raise ProjectParticipantNotFound("PROJECT_PARTICIPANT_NOT_FOUND")
        return ProjectParticipant.hydrate({key: value for key, value in row.items() if key != "_id"})

    def page(
        self, *, tenant_id: str, project_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectParticipant, ...], bool]:
        """List one bounded active exact-project page with stable ordering."""
        if session is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SESSION_REQUIRED")
        if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_PAGE_INVALID")
        query = {
            "tenant_id": _identifier(tenant_id, "TENANT"),
            "project_id": _identifier(project_id, "PROJECT"),
            "state": "ACTIVE",
        }
        try:
            cursor = self._participants.find(query, session=session).sort(
                [("principal_id", ASCENDING)],
            ).skip(offset).limit(limit + 1)
            rows = tuple(ProjectParticipant.hydrate(
                {key: val for key, val in row.items() if key != "_id"},
            ) for row in cursor)
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_LIST_UNAVAILABLE") from error
        return rows[:limit], len(rows) > limit

    def projects_for_principal(
        self, *, tenant_id: str, principal_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectParticipant, ...], bool]:
        """Discover only ACTIVE project assignments for this exact principal.

        This registry reveals only participation facts. The caller separately
        requires current IAM, membership, entitlement and source project read
        for each returned project before displaying business content.
        """
        if session is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SESSION_REQUIRED")
        if (
            type(limit) is not int or not 1 <= limit <= 100
            or type(offset) is not int or offset < 0
        ):
            raise ProjectParticipantError("PROJECT_PARTICIPANT_PAGE_INVALID")
        query = {
            "tenant_id": _identifier(tenant_id, "TENANT"),
            "principal_id": _identifier(principal_id, "PRINCIPAL"),
            "state": "ACTIVE",
        }
        try:
            cursor = self._participants.find(query, session=session).sort(
                [("project_id", ASCENDING)],
            ).skip(offset).limit(limit + 1)
            records = tuple(ProjectParticipant.hydrate(
                {key: value for key, value in row.items() if key != "_id"},
            ) for row in cursor)
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_LIST_UNAVAILABLE") from error
        return records[:limit], len(records) > limit

    def _replay(
        self, *, tenant_id: str, key: str, request_digest: str,
        session: Any,
    ) -> ProjectParticipant | None:
        """Replay only an identical prior command, never a coincidentally equal state."""
        if session is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SESSION_REQUIRED")
        _identifier(tenant_id, "TENANT")
        if not isinstance(key, str) or not 1 <= len(key) <= 200 or key != key.strip():
            raise ProjectParticipantError("PROJECT_PARTICIPANT_KEY_INVALID")
        try:
            row = self._events.find_one(
                {"tenant_id": tenant_id, "idempotency_key": key}, session=session,
            )
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_REPLAY_UNAVAILABLE") from error
        if row is None:
            return None
        if row.get("request_digest") != request_digest:
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_DIVERGENT_REPLAY")
        snapshot = row.get("result_snapshot")
        if not isinstance(snapshot, dict):
            raise ProjectParticipantError("PROJECT_PARTICIPANT_EVENT_INVALID")
        result = ProjectParticipant.hydrate(snapshot)
        if (
            result.tenant_id != tenant_id
            or result.project_id != row.get("project_id")
            or result.principal_id != row.get("principal_id")
            or result.revision != row.get("revision")
            or result.fingerprint != row.get("result_fingerprint")
            or result.updated_by_principal_id != row.get("actor_principal_id")
            or row.get("schema") != "wilsy.project.participant.event.v1"
            or row.get("event_type") not in {
                "PROJECT_PARTICIPANT_GRANTED", "PROJECT_PARTICIPANT_REVOKED",
            }
        ):
            raise ProjectParticipantError("PROJECT_PARTICIPANT_EVENT_INVALID")
        return result

    def _append(
        self, *, outcome: ProjectParticipant, key: str, digest: str,
        event_type: str, session: Any,
    ) -> None:
        """Write audit evidence in the same caller-owned transaction as grant."""
        try:
            self._events.insert_one({
                "tenant_id": outcome.tenant_id, "project_id": outcome.project_id,
                "principal_id": outcome.principal_id, "revision": outcome.revision,
                "event_type": event_type, "idempotency_key": key,
                "request_digest": digest, "result_fingerprint": outcome.fingerprint,
                "result_snapshot": outcome.to_dict(),
                "actor_principal_id": outcome.updated_by_principal_id,
                "occurred_at": outcome.updated_at, "schema": "wilsy.project.participant.event.v1",
            }, session=session)
        except DuplicateKeyError as error:
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_EVENT_CONFLICT") from error
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_AUDIT_UNAVAILABLE") from error

    def grant(
        self, *, tenant_id: str, project_id: str, principal_id: str,
        role: str, actor_principal_id: str, idempotency_key: str,
        occurred_at: datetime, session: Any,
    ) -> ProjectParticipant:
        """Insert one explicit grant; revoked assignments cannot silently revive."""
        coords = {
            "tenant_id": _identifier(tenant_id, "TENANT"),
            "project_id": _identifier(project_id, "PROJECT"),
            "principal_id": _identifier(principal_id, "PRINCIPAL"),
            "role": role, "actor": _identifier(actor_principal_id, "ACTOR"),
        }
        digest = _digest({"command": "grant", **coords})
        old = self._replay(tenant_id=tenant_id, key=idempotency_key, request_digest=digest, session=session)
        if old is not None:
            return old
        if role not in PARTICIPANT_ROLES:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_ROLE_INVALID")
        result = ProjectParticipant(
            tenant_id=tenant_id, project_id=project_id, principal_id=principal_id,
            role=role, state="ACTIVE", revision=1,
            granted_by_principal_id=actor_principal_id,
            updated_by_principal_id=actor_principal_id,
            created_at=_time(occurred_at), updated_at=_time(occurred_at),
        )
        if session is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SESSION_REQUIRED")
        try:
            self._participants.insert_one(result.to_dict(), session=session)
        except DuplicateKeyError as error:
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_ALREADY_ASSIGNED") from error
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_WRITE_UNAVAILABLE") from error
        self._append(
            outcome=result, key=idempotency_key, digest=digest,
            event_type="PROJECT_PARTICIPANT_GRANTED", session=session,
        )
        return result

    def revoke(
        self, *, tenant_id: str, project_id: str, principal_id: str,
        actor_principal_id: str, expected_revision: int,
        idempotency_key: str, occurred_at: datetime, session: Any,
    ) -> ProjectParticipant:
        """Revoke a currently active grant using exact authorizer and CAS."""
        digest = _digest({
            "command": "revoke", "tenant_id": tenant_id,
            "project_id": project_id, "principal_id": principal_id,
            "actor": actor_principal_id, "expected_revision": expected_revision,
        })
        old = self._replay(tenant_id=tenant_id, key=idempotency_key, request_digest=digest, session=session)
        if old is not None:
            return old
        current = self.get(
            tenant_id=tenant_id, project_id=project_id,
            principal_id=principal_id, session=session,
        )
        new = current.change(
            role=current.role, state="REVOKED",
            actor_principal_id=actor_principal_id,
            expected_revision=expected_revision, occurred_at=occurred_at,
        )
        try:
            result = self._participants.update_one({
                "tenant_id": tenant_id, "project_id": project_id,
                "principal_id": principal_id, "state": "ACTIVE",
                "revision": current.revision, "fingerprint": current.fingerprint,
            }, {"$set": new.to_dict()}, session=session)
        except PyMongoError as error:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_WRITE_UNAVAILABLE") from error
        if result.matched_count != 1:
            raise ProjectParticipantConflict("PROJECT_PARTICIPANT_REVISION_CONFLICT")
        self._append(
            outcome=new, key=idempotency_key, digest=digest,
            event_type="PROJECT_PARTICIPANT_REVOKED", session=session,
        )
        return new


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "VERSION", "SCHEMA",
    "ProjectParticipant", "ProjectParticipantRegistry", "ProjectParticipantError",
    "ProjectParticipantConflict", "ProjectParticipantNotFound", "PARTICIPANT_ROLES",
]

# ARTIFACT: project_participant_registry.py
# VERSION: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY
# AUTHORITY BOUNDARY: record persistence only; EOS HTTP admission remains necessary
# TENANT POSTURE: exact tenant, project and principal; no privileged fallback
# FAIL-CLOSED POSTURE: absent, revoked, foreign, stale, divergent and tampered deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
