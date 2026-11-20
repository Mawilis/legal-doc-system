"""TITLE: WILSY OS Governed Project Task Approval Registry
VERSION: v1.2.0-SCANNED-TASK-EVIDENCE-BINDING
AUTHORITY: Python EOS project task business approval evidence.
EPITOME: Explicit task review request, named reviewer, immutable business
         approval/rejection and revision-bound audit without financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_approval_registry.py
COLLABORATION / OWNERSHIP: Projects router owns exact tenant IAM, entitlement,
         task/project existence, participant currentness, reviewer authority and
         caller-owned MongoDB transactions; this registry owns decision truth.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.2.0-SCANNED-TASK-EVIDENCE-BINDING binds
         a bounded set of immutable scanned attachment IDs into the review
         fingerprint and replay while preserving legacy unbound V1 records.
CHANGELOG: v1.2.0-SCANNED-TASK-EVIDENCE-BINDING adds indexed reviewer-only pending decision
         discovery with bounded source scanning. The router still verifies
         current IAM, ACTIVE participation and project/task existence.
CHANGELOG: v1.2.0-SCANNED-TASK-EVIDENCE-BINDING creates source-owned
         PENDING -> APPROVED/REJECTED decisions with idempotency, CAS and events.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Bounded plain-text rationale, opaque identities,
         canonical checksums, immutable event history; no inferred signatures.
TENANT BOUNDARY: Every source, replay and CAS binds tenant/project/task;
         absent, foreign and wrong-reviewer identities remain indistinguishable.
AUTHORITY BOUNDARY: Business review never changes work status, grants IAM,
         issues financial approval, releases funds or proves signed decisions.
TRANSACTION BOUNDARY: Caller owns snapshot/majority transaction and retries;
         indexes must be provisioned at EOS boot, never on a command request.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes financial actions.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
import re
from typing import Any, Final, Literal

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION: Final[str] = "v1.2.0-SCANNED-TASK-EVIDENCE-BINDING"
SCHEMA: Final[str] = "wilsy.project.approval.v1"
COLLECTION: Final[str] = "wilsy_project_approvals"
EVENT_COLLECTION: Final[str] = "wilsy_project_approval_events"
_ID = re.compile(r"^par-[a-f0-9]{48}$")
_PROJECT = re.compile(r"^prj-[a-f0-9]{48}$")
_TASK = re.compile(r"^ptk-[a-f0-9]{48}$")
_FINGERPRINT = re.compile(r"^[a-f0-9]{128}$")
_RESERVED = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})


class ProjectApprovalError(RuntimeError):
    """Non-disclosing project business approval source error."""

    def __init__(self, code: str) -> None:
        """Carry stable bounded source failure classification."""
        self.code = code
        super().__init__(code)


class ProjectApprovalConflict(ProjectApprovalError):
    """Stale CAS, duplicate source origin or divergent command replay."""


class ProjectApprovalNotFound(ProjectApprovalError):
    """Unknown, foreign or wrong-scoped decision record."""


def _id(value: object, kind: str, max_length: int = 180) -> str:
    """Validate bounded opaque coordinates without accepting reserved tenants."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= max_length
        or value != value.strip() or any(ord(ch) <= 32 for ch in value)
    ):
        raise ProjectApprovalError("PROJECT_APPROVAL_" + kind + "_INVALID")
    if kind == "TENANT" and value.upper() in _RESERVED:
        raise ProjectApprovalError("PROJECT_APPROVAL_TENANT_INVALID")
    pattern = {"APPROVAL": _ID, "PROJECT": _PROJECT, "TASK": _TASK}.get(kind)
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ProjectApprovalError("PROJECT_APPROVAL_" + kind + "_INVALID")
    return value


def _body(value: object) -> str:
    """Require a human-authored, bounded and nonempty plain-text rationale."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 3000
        or value != value.strip()
        or any(ord(ch) < 32 and ch not in "\n\t" for ch in value)
    ):
        raise ProjectApprovalError("PROJECT_APPROVAL_RATIONALE_INVALID")
    return value


def _time(value: object) -> datetime:
    """Require a timezone-aware instant for new decisions."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectApprovalError("PROJECT_APPROVAL_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _load_time(value: object) -> datetime:
    """Interpret timezone-naive PyMongo BSON UTC instants on hydration only."""
    if isinstance(value, str):
        try:
            return _time(datetime.fromisoformat(value))
        except (ValueError, TypeError) as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_TIME_INVALID") from error
    if isinstance(value, datetime):
        return _time(value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value)
    raise ProjectApprovalError("PROJECT_APPROVAL_TIME_INVALID")


def _digest(payload: dict[str, object]) -> str:
    """Return a semantic SHA3-512 integrity digest, not a digital signature."""
    return sha3_512(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def approval_id_for_request(
    tenant_id: str, project_id: str, task_id: str,
    requester_principal_id: str, idempotency_key: str,
) -> str:
    """Derive stable approval identity from one exact authorized command origin."""
    components = (
        _id(tenant_id, "TENANT"), _id(project_id, "PROJECT"),
        _id(task_id, "TASK"), _id(requester_principal_id, "REQUESTER"),
        _id(idempotency_key, "KEY", 200),
    )
    return "par-" + sha3_512("\0".join(components).encode("utf-8")).hexdigest()[:48]


@dataclass(frozen=True, slots=True)
class ProjectApproval:
    """Task-specific review request with one accountable named reviewer."""

    tenant_id: str
    project_id: str
    task_id: str
    approval_id: str
    requester_principal_id: str
    reviewer_principal_id: str
    rationale: str
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    requested_at: datetime
    decided_at: datetime | None = None
    decision_rationale: str | None = None
    revision: int = 1
    fingerprint: str = ""
    evidence_attachment_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate coherent source truth and detect fingerprint tampering."""
        for kind, value in (
            ("TENANT", self.tenant_id), ("PROJECT", self.project_id),
            ("TASK", self.task_id), ("APPROVAL", self.approval_id),
            ("REQUESTER", self.requester_principal_id),
            ("REVIEWER", self.reviewer_principal_id),
        ):
            _id(value, kind)
        if self.requester_principal_id == self.reviewer_principal_id:
            raise ProjectApprovalError("PROJECT_APPROVAL_SELF_REVIEW_DENIED")
        _body(self.rationale)
        if (
            not isinstance(self.evidence_attachment_ids, tuple)
            or len(self.evidence_attachment_ids) > 10
            or len(set(self.evidence_attachment_ids)) != len(self.evidence_attachment_ids)
        ):
            raise ProjectApprovalError("PROJECT_APPROVAL_EVIDENCE_INVALID")
        for attachment_id in self.evidence_attachment_ids:
            if (
                not isinstance(attachment_id, str)
                or re.fullmatch(r"pat-[a-f0-9]{48}", attachment_id) is None
            ):
                raise ProjectApprovalError("PROJECT_APPROVAL_EVIDENCE_INVALID")
        created = _time(self.requested_at)
        object.__setattr__(self, "requested_at", created)
        if self.status == "PENDING":
            if self.revision != 1 or self.decided_at is not None or self.decision_rationale is not None:
                raise ProjectApprovalError("PROJECT_APPROVAL_STATE_INVALID")
        elif self.status in {"APPROVED", "REJECTED"}:
            if self.revision != 2 or self.decided_at is None or self.decision_rationale is None:
                raise ProjectApprovalError("PROJECT_APPROVAL_STATE_INVALID")
            _body(self.decision_rationale)
            instant = _time(self.decided_at)
            if instant < created:
                raise ProjectApprovalError("PROJECT_APPROVAL_TIME_ORDER_INVALID")
            object.__setattr__(self, "decided_at", instant)
        else:
            raise ProjectApprovalError("PROJECT_APPROVAL_STATE_INVALID")
        calculated = _digest(self._canonical())
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or _FINGERPRINT.fullmatch(self.fingerprint) is None
            or not compare_digest(self.fingerprint, calculated)
        ):
            raise ProjectApprovalError("PROJECT_APPROVAL_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", calculated)

    def _canonical(self) -> dict[str, object]:
        """Serialize old and new source records without rewriting legacy hashes."""
        canonical: dict[str, object] = {
            "schema": SCHEMA, "tenant_id": self.tenant_id,
            "project_id": self.project_id, "task_id": self.task_id,
            "approval_id": self.approval_id,
            "requester_principal_id": self.requester_principal_id,
            "reviewer_principal_id": self.reviewer_principal_id,
            "rationale": self.rationale, "status": self.status,
            "requested_at": self.requested_at.isoformat(),
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "decision_rationale": self.decision_rationale,
            "revision": self.revision,
        }
        if self.evidence_attachment_ids:
            canonical["evidence_attachment_ids"] = list(self.evidence_attachment_ids)
        return canonical

    def to_dict(self) -> dict[str, object]:
        """Expose complete authoritative state with its integrity digest."""
        return {**self._canonical(), "fingerprint": self.fingerprint}

    @classmethod
    def hydrate(cls, source: dict[str, object]) -> ProjectApproval:
        """Reject unrecognized or missing persisted fields and forged revisions."""
        required = {
            "schema", "tenant_id", "project_id", "task_id", "approval_id",
            "requester_principal_id", "reviewer_principal_id", "rationale",
            "status", "requested_at", "decided_at", "decision_rationale",
            "revision", "fingerprint",
        }
        if (
            not isinstance(source, dict)
            or set(source) not in (required, required | {"evidence_attachment_ids"})
            or source["schema"] != SCHEMA
        ):
            raise ProjectApprovalError("PROJECT_APPROVAL_RECORD_INVALID")
        args = {key: value for key, value in source.items() if key != "schema"}
        if "evidence_attachment_ids" in args:
            if not isinstance(args["evidence_attachment_ids"], list):
                raise ProjectApprovalError("PROJECT_APPROVAL_EVIDENCE_INVALID")
            args["evidence_attachment_ids"] = tuple(args["evidence_attachment_ids"])
        args["requested_at"] = _load_time(args["requested_at"])
        if args["decided_at"] is not None:
            args["decided_at"] = _load_time(args["decided_at"])
        try:
            return cls(**args)
        except TypeError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_RECORD_INVALID") from error

    def decide(
        self, *, reviewer_principal_id: str,
        decision: Literal["APPROVED", "REJECTED"],
        rationale: str, expected_revision: int, occurred_at: datetime,
    ) -> ProjectApproval:
        """Allow exactly the assigned reviewer one terminal revision transition."""
        if _id(reviewer_principal_id, "REVIEWER") != self.reviewer_principal_id:
            raise ProjectApprovalNotFound("PROJECT_APPROVAL_NOT_FOUND")
        if type(expected_revision) is not int or expected_revision != self.revision:
            raise ProjectApprovalConflict("PROJECT_APPROVAL_REVISION_CONFLICT")
        if self.status != "PENDING" or decision not in ("APPROVED", "REJECTED"):
            raise ProjectApprovalConflict("PROJECT_APPROVAL_TERMINAL")
        return replace(
            self, status=decision, decision_rationale=_body(rationale),
            decided_at=_time(occurred_at), revision=2, fingerprint="",
        )


class ProjectApprovalRegistry:
    """Transactional append/create and CAS decision registry with durable events."""

    def __init__(self, approvals: Any, events: Any) -> None:
        """Adopt supplied collections without creating Mongo clients or sessions."""
        if approvals is None or events is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_COLLECTIONS_REQUIRED")
        self._approvals = approvals
        self._events = events

    @staticmethod
    def ensure_indexes(approvals: Any, events: Any) -> None:
        """Install exact scope, reviewer inbox, idempotency and event indexes."""
        try:
            approvals.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("approval_id", ASCENDING),
            ], unique=True, name="wilsy_project_approval_identity_unique")
            approvals.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("reviewer_principal_id", ASCENDING), ("status", ASCENDING),
                ("requested_at", DESCENDING), ("approval_id", ASCENDING),
            ], name="wilsy_project_approval_reviewer_inbox")
            approvals.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("requested_at", DESCENDING),
            ], name="wilsy_project_approval_task_timeline")
            approvals.create_index([
                ("tenant_id", ASCENDING), ("reviewer_principal_id", ASCENDING),
                ("status", ASCENDING), ("requested_at", DESCENDING),
                ("approval_id", ASCENDING),
            ], name="wilsy_project_approval_principal_inbox")
            events.create_index([
                ("tenant_id", ASCENDING), ("actor_principal_id", ASCENDING),
                ("idempotency_key", ASCENDING),
            ], unique=True, name="wilsy_project_approval_command_unique")
            events.create_index([
                ("tenant_id", ASCENDING), ("approval_id", ASCENDING),
                ("revision", ASCENDING),
            ], unique=True, name="wilsy_project_approval_event_revision")
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_INDEX_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, project_id: str, task_id: str,
        approval_id: str, session: Any,
    ) -> ProjectApproval:
        """Read exact task-scoped decision or conceal absence/foreign identity."""
        if session is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SESSION_REQUIRED")
        query = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "task_id": _id(task_id, "TASK"),
            "approval_id": _id(approval_id, "APPROVAL"),
        }
        try:
            record = self._approvals.find_one(query, session=session)
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_READ_UNAVAILABLE") from error
        if record is None:
            raise ProjectApprovalNotFound("PROJECT_APPROVAL_NOT_FOUND")
        return ProjectApproval.hydrate({key: value for key, value in record.items() if key != "_id"})

    def list_page(
        self, *, tenant_id: str, project_id: str, task_id: str,
        session: Any, limit: int = 50, offset: int = 0,
    ) -> tuple[tuple[ProjectApproval, ...], bool]:
        """List exact-project and task decisions without tenant-wide scanning."""
        if session is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SESSION_REQUIRED")
        if (
            type(limit) is not int or not 1 <= limit <= 100
            or type(offset) is not int or offset < 0
        ):
            raise ProjectApprovalError("PROJECT_APPROVAL_PAGE_INVALID")
        query = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "task_id": _id(task_id, "TASK"),
        }
        try:
            cursor = self._approvals.find(query, session=session).sort([
                ("requested_at", DESCENDING), ("approval_id", ASCENDING),
            ]).skip(offset).limit(limit + 1)
            rows = tuple(ProjectApproval.hydrate({
                key: value for key, value in raw.items() if key != "_id"
            }) for raw in cursor)
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_READ_UNAVAILABLE") from error
        return rows[:limit], len(rows) > limit

    def pending_for_reviewer(
        self, *, tenant_id: str, reviewer_principal_id: str,
        session: Any, max_items: int = 10000,
    ) -> tuple[ProjectApproval, ...]:
        """Read pending reviewer-only source records for further IAM filtering.

        This query never constitutes authorization: caller must check each
        returned project's ACTIVE contributor record and current entitlement
        in the same snapshot. A safety bound rejects oversized inboxes rather
        than silently claiming a truncated verified result.
        """
        if session is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SESSION_REQUIRED")
        if type(max_items) is not int or not 1 <= max_items <= 10000:
            raise ProjectApprovalError("PROJECT_APPROVAL_CAPACITY_INVALID")
        query = {
            "tenant_id": _id(tenant_id, "TENANT"),
            "reviewer_principal_id": _id(reviewer_principal_id, "REVIEWER"),
            "status": "PENDING",
        }
        try:
            cursor = self._approvals.find(query, session=session).sort([
                ("requested_at", DESCENDING), ("approval_id", ASCENDING),
            ]).limit(max_items + 1)
            rows = tuple(ProjectApproval.hydrate({
                key: value for key, value in row.items() if key != "_id"
            }) for row in cursor)
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_INBOX_UNAVAILABLE") from error
        if len(rows) > max_items:
            raise ProjectApprovalError("PROJECT_APPROVAL_INBOX_CAPACITY_EXCEEDED")
        if any(
            row.tenant_id != tenant_id
            or row.reviewer_principal_id != reviewer_principal_id
            or row.status != "PENDING" for row in rows
        ):
            raise ProjectApprovalError("PROJECT_APPROVAL_INBOX_INVALID")
        return rows

    def _replay(
        self, *, tenant_id: str, actor_principal_id: str,
        idempotency_key: str, fingerprint: str, session: Any,
    ) -> ProjectApproval | None:
        """Return certified original state or reject divergent evidence."""
        try:
            event = self._events.find_one({
                "tenant_id": tenant_id,
                "actor_principal_id": actor_principal_id,
                "idempotency_key": idempotency_key,
            }, session=session)
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_EVENT_UNAVAILABLE") from error
        if event is None:
            return None
        if event.get("request_fingerprint") != fingerprint:
            raise ProjectApprovalConflict("PROJECT_APPROVAL_DIVERGENT_REPLAY")
        saved = event.get("result_snapshot")
        if not isinstance(saved, dict):
            raise ProjectApprovalError("PROJECT_APPROVAL_EVENT_INVALID")
        result = ProjectApproval.hydrate(saved)
        if (
            event.get("approval_id") != result.approval_id
            or event.get("result_fingerprint") != result.fingerprint
            or event.get("revision") != result.revision
            or event.get("project_id") != result.project_id
            or event.get("task_id") != result.task_id
            or event.get("tenant_id") != result.tenant_id
            or event.get("actor_principal_id") not in {
                result.requester_principal_id, result.reviewer_principal_id,
            }
        ):
            raise ProjectApprovalError("PROJECT_APPROVAL_EVENT_INVALID")
        return result

    def _append_event(
        self, *, record: ProjectApproval, actor: str,
        key: str, request_digest: str, session: Any,
    ) -> None:
        """Append immutable command/result evidence in the same transaction."""
        self._events.insert_one({
            "schema": "wilsy.project.approval.event.v1",
            "tenant_id": record.tenant_id, "project_id": record.project_id,
            "task_id": record.task_id, "approval_id": record.approval_id,
            "actor_principal_id": actor,
            "idempotency_key": key,
            "request_fingerprint": request_digest,
            "result_fingerprint": record.fingerprint,
            "result_snapshot": record.to_dict(),
            "event_type": "PROJECT_APPROVAL_REQUESTED"
            if record.revision == 1 else "PROJECT_APPROVAL_" + record.status,
            "revision": record.revision,
            "occurred_at": record.requested_at if record.revision == 1 else record.decided_at,
        }, session=session)

    def create_or_replay(
        self, *, approval: ProjectApproval, idempotency_key: str, session: Any,
    ) -> ProjectApproval:
        """Create a pending review and durable origin in one caller transaction."""
        if session is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SESSION_REQUIRED")
        if (
            approval.status != "PENDING"
            or approval.approval_id != approval_id_for_request(
                approval.tenant_id, approval.project_id, approval.task_id,
                approval.requester_principal_id, idempotency_key,
            )
        ):
            raise ProjectApprovalConflict("PROJECT_APPROVAL_ORIGIN_INVALID")
        key = _id(idempotency_key, "KEY", 200)
        request_claim: dict[str, object] = {
            "command": "REQUEST",
            "tenant_id": approval.tenant_id,
            "project_id": approval.project_id,
            "task_id": approval.task_id,
            "actor": approval.requester_principal_id,
            "reviewer": approval.reviewer_principal_id,
            "rationale": approval.rationale,
        }
        if approval.evidence_attachment_ids:
            request_claim["evidence_attachment_ids"] = list(
                approval.evidence_attachment_ids,
            )
        digest = _digest(request_claim)
        original = self._replay(
            tenant_id=approval.tenant_id,
            actor_principal_id=approval.requester_principal_id,
            idempotency_key=key, fingerprint=digest, session=session,
        )
        if original is not None:
            if original.revision != 1:
                raise ProjectApprovalError("PROJECT_APPROVAL_EVENT_INVALID")
            return original
        try:
            self._approvals.insert_one(approval.to_dict(), session=session)
            self._append_event(
                record=approval, actor=approval.requester_principal_id,
                key=key, request_digest=digest, session=session,
            )
        except DuplicateKeyError as error:
            raise ProjectApprovalConflict("PROJECT_APPROVAL_DUPLICATE") from error
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_WRITE_UNAVAILABLE") from error
        return approval

    def decide_or_replay(
        self, *, tenant_id: str, project_id: str, task_id: str,
        approval_id: str, reviewer_principal_id: str,
        decision: Literal["APPROVED", "REJECTED"],
        rationale: str, expected_revision: int,
        occurred_at: datetime, idempotency_key: str, session: Any,
    ) -> ProjectApproval:
        """Commit a named reviewer's once-only decision with CAS/replay audit."""
        if session is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SESSION_REQUIRED")
        actor = _id(reviewer_principal_id, "REVIEWER")
        key = _id(idempotency_key, "KEY", 200)
        digest = _digest({
            "command": "DECIDE", "tenant_id": _id(tenant_id, "TENANT"),
            "project_id": _id(project_id, "PROJECT"),
            "task_id": _id(task_id, "TASK"),
            "approval_id": _id(approval_id, "APPROVAL"),
            "actor": actor, "decision": decision, "rationale": _body(rationale),
            "expected_revision": expected_revision,
        })
        original = self._replay(
            tenant_id=tenant_id, actor_principal_id=actor,
            idempotency_key=key, fingerprint=digest, session=session,
        )
        if original is not None:
            if (
                original.approval_id != approval_id
                or original.reviewer_principal_id != actor
                or original.status != decision or original.revision != 2
            ):
                raise ProjectApprovalError("PROJECT_APPROVAL_EVENT_INVALID")
            return original
        current = self.get(
            tenant_id=tenant_id, project_id=project_id, task_id=task_id,
            approval_id=approval_id, session=session,
        )
        updated = current.decide(
            reviewer_principal_id=actor, decision=decision,
            rationale=rationale, expected_revision=expected_revision,
            occurred_at=occurred_at,
        )
        coords = {
            "tenant_id": tenant_id, "project_id": project_id,
            "task_id": task_id, "approval_id": approval_id,
            "revision": current.revision, "fingerprint": current.fingerprint,
        }
        try:
            match = self._approvals.update_one(
                coords, {"$set": updated.to_dict()}, session=session,
            )
            if match.matched_count != 1:
                raise ProjectApprovalConflict("PROJECT_APPROVAL_REVISION_CONFLICT")
            self._append_event(
                record=updated, actor=actor, key=key,
                request_digest=digest, session=session,
            )
        except DuplicateKeyError as error:
            raise ProjectApprovalConflict("PROJECT_APPROVAL_DUPLICATE") from error
        except PyMongoError as error:
            raise ProjectApprovalError("PROJECT_APPROVAL_WRITE_UNAVAILABLE") from error
        return updated


__all__ = [
    "VERSION", "SCHEMA", "COLLECTION", "EVENT_COLLECTION",
    "ProjectApproval", "ProjectApprovalRegistry",
    "ProjectApprovalError", "ProjectApprovalConflict", "ProjectApprovalNotFound",
    "approval_id_for_request",
]

# ARTIFACT: project_approval_registry.py
# VERSION: v1.2.0-SCANNED-TASK-EVIDENCE-BINDING
# AUTHORITY BOUNDARY: source business review only, not financial or IAM
# TENANT POSTURE: exact tenant/project/task/reviewer and transaction replay
# FAIL-CLOSED POSTURE: unknown, self-review, stale, divergent, foreign denied
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
