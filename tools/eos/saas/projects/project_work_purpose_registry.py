"""TITLE: WILSY OS Project Work Purpose Source Registry
VERSION: v1.1.3-TYPED-PURPOSE-REVISION-BOUNDARY
AUTHORITY: Projects EOS source-owned work metadata; not IAM.
EPITOME: Persist source-owned Operating / Platform Build labels with exact
task-revision CAS, immutable event evidence and replay-safe commands.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/projects/project_work_purpose_registry.py
COLLABORATION / OWNERSHIP: Projects router authorizes commands; ProjectTaskRegistry
validates current task; My Work consumes validated current purpose evidence.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.1.3-TYPED-PURPOSE-REVISION-BOUNDARY narrows
persisted dynamic revision fields before arithmetic/typing and preserves
strict audit denial without unsafe object comparisons.
CHANGELOG: v1.1.2-STRONGER-PURPOSE-EVENT-PROVENANCE verifies
event type, actor, timestamp and fixed digest format against canonical
current source before either single or bounded-batch projection.
CHANGELOG: v1.1.1-DUPLICATE-PURPOSE-SOURCE-GATE
rejects even two different revision records for one task in a supposedly
unique current batch; corruption never silently picks the last row.
CHANGELOG: v1.1.0-BOUNDED-PURPOSE-PROVENANCE-BATCH
adds task-bounded batch source/audit reads for large exact-principal attention
queues, rejecting duplicate, divergent or corrupt evidence without N+1 calls.
CHANGELOG: v1.0.2-STALE-TASK-PURPOSE-CAS-RECOVERY preserves
audited purpose revision when its attached task revision has advanced, while
displaying UNCLASSIFIED without stale provenance; the owner can explicitly
reclassify using correct metadata CAS instead of being trapped in conflict.
CHANGELOG: v1.0.1-EXPLICIT-PURPOSE-REVISION-READBACK returns
current purpose revision exclusively for the source-owned classification
command and separately verifies the task revision; My Work retains the
strict existing audience_evidence projection contract.
CHANGELOG: v1.0.0-PROJECT-WORK-PURPOSE-CAS-AUDIT introduces exact-tenant
classification snapshots and immutable events with SHA3-512 semantic checks,
bounded reason, actor-bound replay and independent source-revision currentness.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No secret or task body stored in label records;
no fabricated critical gate, approvals, metrics or privileged role inheritance.
TENANT BOUNDARY: All queries and indexes lead with tenant_id and project_id.
AUTHORITY BOUNDARY: Registry is not callable without current Projects IAM
admission at router; neither principal nor role can be chosen by the client.
TRANSACTION BOUNDARY: Caller owns one MongoDB transaction for task read,
label CAS and event; no internal client/session or DDL on request.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
from typing import Any, Final, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.projects.project_task_registry import ProjectTask

VERSION: Final = "v1.1.3-TYPED-PURPOSE-REVISION-BOUNDARY"
COLLECTION: Final = "wilsy_project_work_purposes"
EVENT_COLLECTION: Final = "wilsy_project_work_purpose_events"
AUDIENCES: Final = frozenset({"OPERATING", "PLATFORM_BUILD"})


class WorkPurposeError(RuntimeError):
    """Bounded failure code; no source details or credentials."""

    def __init__(self, code: str) -> None:
        """Return stable machine-readable failure only."""
        self.code = code
        super().__init__(code)


class WorkPurposeConflict(WorkPurposeError):
    """Stale task or purpose revision, or divergent replay."""


def _digest(payload: dict[str, object]) -> str:
    """Canonical deterministic semantic digest; not a digital signature."""
    return sha3_512(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":"), default=str).encode()).hexdigest()


def _coordinate(value: object) -> bool:
    """Reject missing, padded, control-bearing or unbounded coordinates."""
    return isinstance(value, str) and 1 <= len(value) <= 200 and value == value.strip() and all(ord(c) >= 33 for c in value)


def _verify(row: dict[str, object], task: ProjectTask) -> dict[str, object]:
    """Verify stored label provenance, scope and digest before projection."""
    semantic = {key: value for key, value in row.items() if key not in {"_id", "fingerprint"}}
    revision = semantic.get("revision")
    task_revision = semantic.get("task_revision")
    recorded_at = semantic.get("recorded_at")
    reason = semantic.get("reason")
    if (semantic.get("tenant_id") != task.tenant_id
            or semantic.get("project_id") != task.project_id
            or semantic.get("task_id") != task.task_id
            or semantic.get("audience") not in AUDIENCES
            or type(task_revision) is not int or task_revision < 1
            or type(revision) is not int or revision < 1
            or not _coordinate(semantic.get("actor_principal_id"))
            or not _coordinate(semantic.get("evidence_ref"))
            or not isinstance(recorded_at, str)
            or not recorded_at.endswith("+00:00")
            or not isinstance(reason, str)
            or not 10 <= len(reason) <= 1000
            or semantic.get("critical_gate") is not False
            or semantic.get("critical_gate_evidence_ref") is not None
            or not isinstance(row.get("fingerprint"), str)
            or not compare_digest(row["fingerprint"], _digest(semantic))):
        raise WorkPurposeError("PROJECT_WORK_PURPOSE_SOURCE_INVALID")
    return semantic


def _audit_event_valid(
    event: dict[str, object], semantic: dict[str, object],
    fingerprint: str,
) -> bool:
    """Require immutable event identity, actor, time and source checksum parity."""
    replay = event.get("request_fingerprint")
    return (
        event.get("event_type") == "WORK_PURPOSE_CLASSIFIED"
        and event.get("tenant_id") == semantic["tenant_id"]
        and event.get("project_id") == semantic["project_id"]
        and event.get("task_id") == semantic["task_id"]
        and event.get("revision") == semantic["revision"]
        and event.get("actor_principal_id") == semantic["actor_principal_id"]
        and event.get("recorded_at") == semantic["recorded_at"]
        and event.get("evidence_ref") == semantic["evidence_ref"]
        and event.get("result_fingerprint") == fingerprint
        and _coordinate(event.get("idempotency_key"))
        and isinstance(replay, str) and len(replay) == 128
        and all(char in "0123456789abcdef" for char in replay)
    )


class ProjectWorkPurposeRegistry:
    """Two independently indexed source collections; all writes caller-transaction-owned."""

    def __init__(self, current: Any, events: Any) -> None:
        """Accept trusted collections without creating a client."""
        if current is None or events is None:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_COLLECTION_REQUIRED")
        self.current, self.events = current, events

    @staticmethod
    def ensure_indexes(current: Any, events: Any) -> None:
        """Provision exact compound identity, replay and immutable event indexes."""
        try:
            current.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING)], name="wilsy_project_work_purpose_unique",
                unique=True)
            events.create_index([
                ("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                name="wilsy_project_work_purpose_replay_unique", unique=True)
            events.create_index([
                ("tenant_id", ASCENDING), ("project_id", ASCENDING),
                ("task_id", ASCENDING), ("revision", ASCENDING)],
                name="wilsy_project_work_purpose_event_revision_unique", unique=True)
        except PyMongoError as error:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_INDEX_UNAVAILABLE") from error

    def current_for_task(self, *, task: ProjectTask, session: Any) -> dict[str, object] | None:
        """Read only a currently attested exact task revision or remain unclassified."""
        if session is None:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_SESSION_REQUIRED")
        query = {"tenant_id": task.tenant_id, "project_id": task.project_id, "task_id": task.task_id}
        try:
            row = self.current.find_one(query, session=session)
        except PyMongoError as error:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_READ_UNAVAILABLE") from error
        if row is None:
            return None
        value = _verify(row, task)
        try:
            event = self.events.find_one({
                **query, "revision": value["revision"],
                "result_fingerprint": row["fingerprint"],
            }, session=session)
        except PyMongoError as error:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_AUDIT_UNAVAILABLE") from error
        if event is None or not _audit_event_valid(event, value, cast(str, row["fingerprint"])):
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_AUDIT_INVALID")
        if value["task_revision"] != task.revision:
            # A task update invalidates purpose truth, not the purpose's own
            # durable revision. Reclassification must CAS that real revision.
            return {"audience": "UNCLASSIFIED", "purpose_revision": value["revision"],
                    "evidence_ref": None, "source_revision": None,
                    "critical_gate": False}
        return {
            "tenant_id": task.tenant_id, "source": "PROJECTS",
            "record_id": task.task_id, "source_revision": task.revision,
            "audience": value["audience"], "purpose_revision": value["revision"],
            "evidence_ref": value["evidence_ref"], "source_verified": True,
            "critical_gate": False, "critical_gate_evidence_ref": None,
        }

    def current_for_tasks(
        self, *, tasks: list[ProjectTask], session: Any,
    ) -> dict[str, dict[str, object] | None]:
        """Read all source-audited purposes in bounded batches, never N+1.

        Caller must have already admitted these tasks under its own exact
        assignee, tenant and active project participation. This method only
        consumes that admitted list; it cannot expand visibility.
        """
        if session is None or len(tasks) > 10000:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_BATCH_INVALID")
        if not tasks:
            return {}
        tenant = tasks[0].tenant_id
        by_id: dict[str, ProjectTask] = {}
        for task in tasks:
            if task.tenant_id != tenant or task.task_id in by_id:
                raise WorkPurposeError("PROJECT_WORK_PURPOSE_BATCH_SCOPE_INVALID")
            by_id[task.task_id] = task
        result: dict[str, dict[str, object] | None] = {
            task_id: None for task_id in by_id
        }
        ids = list(by_id)
        for start in range(0, len(ids), 200):
            batch = ids[start:start + 200]
            try:
                rows = list(self.current.find({
                    "tenant_id": tenant, "task_id": {"$in": batch},
                }, session=session))
            except PyMongoError as error:
                raise WorkPurposeError("PROJECT_WORK_PURPOSE_READ_UNAVAILABLE") from error
            audited: dict[tuple[str, int], tuple[ProjectTask, dict[str, object]]] = {}
            seen_current: set[str] = set()
            for row in rows:
                task = by_id.get(row.get("task_id"))
                if task is None or task.task_id in seen_current:
                    raise WorkPurposeError("PROJECT_WORK_PURPOSE_BATCH_SCOPE_INVALID")
                seen_current.add(task.task_id)
                value = _verify(row, task)
                key = task.task_id, cast(int, value["revision"])
                if key in audited:
                    raise WorkPurposeError("PROJECT_WORK_PURPOSE_SOURCE_INVALID")
                audited[key] = (task, row)
            if not audited:
                continue
            selectors = [{
                "project_id": task.project_id, "task_id": task.task_id,
                "revision": revision, "result_fingerprint": row["fingerprint"],
            } for (task_id, revision), (task, row) in audited.items()]
            try:
                events = list(self.events.find({
                    "tenant_id": tenant, "$or": selectors,
                }, session=session))
            except PyMongoError as error:
                raise WorkPurposeError("PROJECT_WORK_PURPOSE_AUDIT_UNAVAILABLE") from error
            matched: set[tuple[str, int]] = set()
            for event in events:
                key = event.get("task_id"), event.get("revision")
                verified = audited.get(key)
                if verified is None or key in matched or not _audit_event_valid(
                    event, _verify(verified[1], verified[0]),
                    cast(str, verified[1]["fingerprint"]),
                ):
                    raise WorkPurposeError("PROJECT_WORK_PURPOSE_AUDIT_INVALID")
                matched.add(key)
            if matched != set(audited):
                raise WorkPurposeError("PROJECT_WORK_PURPOSE_AUDIT_INVALID")
            for (task_id, revision), (task, row) in audited.items():
                value = _verify(row, task)
                if value["task_revision"] != task.revision:
                    result[task_id] = {
                        "audience": "UNCLASSIFIED", "purpose_revision": revision,
                        "evidence_ref": None, "source_revision": None,
                        "critical_gate": False,
                    }
                else:
                    result[task_id] = {
                        "tenant_id": task.tenant_id, "source": "PROJECTS",
                        "record_id": task.task_id, "source_revision": task.revision,
                        "audience": value["audience"], "purpose_revision": revision,
                        "evidence_ref": value["evidence_ref"], "source_verified": True,
                        "critical_gate": False, "critical_gate_evidence_ref": None,
                    }
        return result

    def classify(
        self, *, task: ProjectTask, actor_principal_id: str, audience: str,
        reason: str, expected_task_revision: int, expected_purpose_revision: int,
        idempotency_key: str, session: Any, now: datetime,
    ) -> dict[str, object]:
        """Write audited label with current-task CAS and deterministic replay."""
        if session is None:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_SESSION_REQUIRED")
        if (not _coordinate(actor_principal_id) or not _coordinate(idempotency_key)
                or audience not in AUDIENCES or type(expected_task_revision) is not int
                or type(expected_purpose_revision) is not int
                or expected_purpose_revision < 0 or not isinstance(reason, str)
                or reason != reason.strip() or not 10 <= len(reason) <= 1000
                or not isinstance(now, datetime) or now.tzinfo is None):
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_COMMAND_INVALID")
        if task.revision != expected_task_revision:
            raise WorkPurposeConflict("PROJECT_WORK_PURPOSE_TASK_REVISION_CONFLICT")
        scope = {"tenant_id": task.tenant_id, "project_id": task.project_id, "task_id": task.task_id}
        request = _digest({**scope, "actor_principal_id": actor_principal_id,
                           "audience": audience, "reason": reason,
                           "expected_task_revision": expected_task_revision,
                           "expected_purpose_revision": expected_purpose_revision})
        try:
            replay = self.events.find_one({
                "tenant_id": task.tenant_id, "idempotency_key": idempotency_key,
            }, session=session)
        except PyMongoError as error:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_READ_UNAVAILABLE") from error
        if replay is not None:
            if replay.get("request_fingerprint") != request or any(
                replay.get(key) != value for key, value in scope.items()
            ):
                raise WorkPurposeConflict("PROJECT_WORK_PURPOSE_REPLAY_CONFLICT")
            current = self.current.find_one(scope, session=session)
            if current is None or current.get("fingerprint") != replay.get("result_fingerprint"):
                raise WorkPurposeConflict("PROJECT_WORK_PURPOSE_REPLAY_STALE")
            return _verify(current, task)
        try:
            previous = self.current.find_one(scope, session=session)
        except PyMongoError as error:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_READ_UNAVAILABLE") from error
        if previous is not None:
            _verify(previous, task)
        revision = 0 if previous is None else cast(int, previous["revision"])
        if revision != expected_purpose_revision:
            raise WorkPurposeConflict("PROJECT_WORK_PURPOSE_REVISION_CONFLICT")
        new_revision = revision + 1
        evidence_ref = "project-work-purpose:" + _digest({
            **scope, "revision": new_revision, "request": request,
        })[:64]
        semantic: dict[str, object] = {
            **scope, "audience": audience, "task_revision": task.revision,
            "revision": new_revision, "actor_principal_id": actor_principal_id,
            "reason": reason, "evidence_ref": evidence_ref,
            "critical_gate": False, "critical_gate_evidence_ref": None,
            "recorded_at": now.astimezone(timezone.utc).isoformat(),
        }
        candidate = {**semantic, "fingerprint": _digest(semantic)}
        try:
            if previous is None:
                self.current.insert_one(candidate.copy(), session=session)
            else:
                result = self.current.replace_one({
                    **scope, "revision": revision,
                    "fingerprint": previous["fingerprint"],
                }, candidate.copy(), session=session)
                if result.matched_count != 1:
                    raise WorkPurposeConflict("PROJECT_WORK_PURPOSE_REVISION_CONFLICT")
            self.events.insert_one({
                **scope, "revision": new_revision, "event_type": "WORK_PURPOSE_CLASSIFIED",
                "actor_principal_id": actor_principal_id,
                "idempotency_key": idempotency_key,
                "request_fingerprint": request,
                "result_fingerprint": candidate["fingerprint"],
                "evidence_ref": evidence_ref,
                "recorded_at": semantic["recorded_at"],
            }, session=session)
        except DuplicateKeyError as error:
            raise WorkPurposeConflict("PROJECT_WORK_PURPOSE_REVISION_CONFLICT") from error
        except PyMongoError as error:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_WRITE_UNAVAILABLE") from error
        return semantic


__all__ = ["VERSION", "COLLECTION", "EVENT_COLLECTION",
           "ProjectWorkPurposeRegistry", "WorkPurposeError", "WorkPurposeConflict"]

# ARTIFACT: project_work_purpose_registry.py
# VERSION: v1.1.3-TYPED-PURPOSE-REVISION-BOUNDARY
# AUTHORITY BOUNDARY: Source-owned metadata, no IAM or command authorization.
# TENANT POSTURE: Exact task/tenant/project revision and actor coordinates.
# FAIL-CLOSED POSTURE: Missing audit or stale task returns no category.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
