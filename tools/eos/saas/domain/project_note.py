"""TITLE: WILSY OS Tenant Project Note Domain
VERSION: v1.1.0-IMMUTABLE-STICKY-COLOUR-EVIDENCE
AUTHORITY: Python EOS canonical tenant Projects domain facts.
EPITOME: Immutable, independently revisioned project notes with source-verifiable
         identity, author ownership, chronological audit coordinates, soft
         archive and SHA3-512 state integrity. No IAM or persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/project_note.py
COLLABORATION / OWNERSHIP: ProjectNoteRegistry and Projects router; EOS owns
         tenant, authentication, entitlement, records and transaction admission.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-IMMUTABLE-STICKY-COLOUR-EVIDENCE adds an optional validated sticky colour to new and revised notes while preserving original fingerprints and field shape for existing colourless notes; revision and author authority unchanged.
CHANGELOG: v1.1.0-IMMUTABLE-STICKY-COLOUR-EVIDENCE rejects retired platform/root tenant aliases
         as invalid note tenancy instead of relying solely on HTTP admission.
CHANGELOG: v1.1.0-IMMUTABLE-STICKY-COLOUR-EVIDENCE defines strict source-backed note state
         without authorizing notes as project approvals or signed decisions.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No HTML interpretation; text is bounded and no
         user input can assert authorship, project ownership or evidence rank.
TENANT BOUNDARY: Explicit tenant and project coordinates; no fallback aliases.
AUTHORITY BOUNDARY: Revision and author invariants only; EOS IAM and project
         record visibility must be verified before any registry operation.
FINANCIAL AUTHORITY BOUNDARY: Notes do not approve or authorize payments;
         Kennel EOS remains the only financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha3_512
from hmac import compare_digest
import json
import re
from typing import Final

VERSION: Final[str] = "v1.1.0-IMMUTABLE-STICKY-COLOUR-EVIDENCE"
SCHEMA: Final[str] = "wilsy.project.note.v1"
NOTE_COLOURS: Final[frozenset[str]] = frozenset({"yellow", "blue", "mint", "rose", "violet", "slate"})
_NOTE_ID = re.compile(r"^pnt-[0-9a-f]{48}$")
_PROJECT_ID = re.compile(r"^prj-[0-9a-f]{48}$")
_HEX_512 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})


class ProjectNoteError(ValueError):
    """Stable note lifecycle or corruption validation error."""

    def __init__(self, code: str) -> None:
        """Preserve one bounded machine-readable domain failure code."""
        self.code = code
        super().__init__(code)


def _identifier(name: str, value: object) -> str:
    """Validate canonical opaque identity without resolving authority."""
    if (
        not isinstance(value, str) or not value or value != value.strip()
        or len(value) > 180 or any(ord(ch) < 32 for ch in value)
    ):
        raise ProjectNoteError("PROJECT_NOTE_" + name.upper() + "_INVALID")
    return value


def _instant(name: str, value: object, *, nullable: bool = False) -> datetime | None:
    """Normalize a timezone-aware instant to UTC, rejecting implicit time zones."""
    if value is None and nullable:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectNoteError("PROJECT_NOTE_" + name.upper() + "_INVALID")
    return value.astimezone(timezone.utc)


def _body(value: object) -> str:
    """Accept meaningful bounded plain text, including line breaks, but no controls."""
    if (
        not isinstance(value, str) or not value.strip() or value != value.strip()
        or len(value) > 10000
        or any(ord(ch) < 32 and ch not in "\n\t" for ch in value)
    ):
        raise ProjectNoteError("PROJECT_NOTE_BODY_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class ProjectNote:
    """One author-owned, exact-project note aggregate.

    A note is descriptive collaboration content. It is never an approval,
    project status change, permission grant, decision, evidence signature,
    legal act, or financial command. Only the caller-owned registry may persist
    a revision after independent EOS authorization.
    """

    tenant_id: str
    project_id: str
    note_id: str
    author_principal_id: str
    body: str
    created_at: datetime
    updated_at: datetime
    revision: int = 1
    archived_at: datetime | None = None
    colour: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate complete aggregate and verify supplied persisted fingerprint."""
        _identifier("tenant_id", self.tenant_id)
        if self.tenant_id.upper() in _FORBIDDEN_TENANTS:
            raise ProjectNoteError("PROJECT_NOTE_TENANT_ID_INVALID")
        _identifier("author_principal_id", self.author_principal_id)
        if not isinstance(self.project_id, str) or not _PROJECT_ID.fullmatch(self.project_id):
            raise ProjectNoteError("PROJECT_NOTE_PROJECT_ID_INVALID")
        if not isinstance(self.note_id, str) or not _NOTE_ID.fullmatch(self.note_id):
            raise ProjectNoteError("PROJECT_NOTE_ID_INVALID")
        _body(self.body)
        if self.colour is not None and self.colour not in NOTE_COLOURS:
            raise ProjectNoteError("PROJECT_NOTE_COLOUR_INVALID")
        created = _instant("created_at", self.created_at)
        updated = _instant("updated_at", self.updated_at)
        archived = _instant("archived_at", self.archived_at, nullable=True)
        assert created is not None and updated is not None
        if updated < created or (archived is not None and archived < updated):
            raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_ORDER_INVALID")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)
        object.__setattr__(self, "archived_at", archived)
        if type(self.revision) is not int or self.revision < 1:
            raise ProjectNoteError("PROJECT_NOTE_REVISION_INVALID")
        if self.schema != SCHEMA or self.version != VERSION:
            raise ProjectNoteError("PROJECT_NOTE_SCHEMA_VERSION_INVALID")
        computed = sha3_512(json.dumps(
            self._payload(), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not _HEX_512.fullmatch(self.fingerprint)
            or not compare_digest(self.fingerprint, computed)
        ):
            raise ProjectNoteError("PROJECT_NOTE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def _payload(self) -> dict[str, object]:
        """Return canonical persisted semantics excluding the derived fingerprint."""
        payload = {
            "tenant_id": self.tenant_id, "project_id": self.project_id,
            "note_id": self.note_id, "author_principal_id": self.author_principal_id,
            "body": self.body, "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(), "revision": self.revision,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "schema": self.schema, "version": self.version,
        }
        if self.colour is not None:
            payload["colour"] = self.colour
        return payload

    def to_dict(self) -> dict[str, object]:
        """Serialize exact source-owned state for persistence or transport."""
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> ProjectNote:
        """Hydrate only complete, version-matched records and check integrity."""
        expected = {
            "tenant_id", "project_id", "note_id", "author_principal_id",
            "body", "created_at", "updated_at", "revision", "archived_at",
            "schema", "version", "fingerprint",
        }
        if not isinstance(value, dict) or not expected.issubset(value) or not set(value).issubset(expected | {"colour"}):
            raise ProjectNoteError("PROJECT_NOTE_DOCUMENT_INVALID")
        fields = dict(value)
        for name in ("created_at", "updated_at", "archived_at"):
            raw = fields[name]
            if raw is None and name == "archived_at":
                continue
            if not isinstance(raw, str):
                raise ProjectNoteError("PROJECT_NOTE_" + name.upper() + "_INVALID")
            try:
                fields[name] = datetime.fromisoformat(raw)
            except (TypeError, ValueError) as error:
                raise ProjectNoteError("PROJECT_NOTE_" + name.upper() + "_INVALID") from error
        try:
            return cls(**fields)
        except TypeError as error:
            raise ProjectNoteError("PROJECT_NOTE_DOCUMENT_INVALID") from error

    def revise(
        self, *, actor_principal_id: str, expected_revision: int,
        body: str, updated_at: datetime, colour: str | None = None,
    ) -> ProjectNote:
        """Revise only the original author's non-archived note with CAS intent."""
        self._require_writer(actor_principal_id, expected_revision)
        stamp = _instant("updated_at", updated_at)
        assert stamp is not None
        if stamp < self.updated_at:
            raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_ORDER_INVALID")
        return replace(
            self, body=_body(body), revision=self.revision + 1,
            colour=self.colour if colour is None else colour,
            updated_at=stamp, fingerprint="",
        )

    def archive(
        self, *, actor_principal_id: str, expected_revision: int,
        archived_at: datetime,
    ) -> ProjectNote:
        """Soft archive an author's note without deleting historical evidence."""
        self._require_writer(actor_principal_id, expected_revision)
        stamp = _instant("archived_at", archived_at)
        assert stamp is not None
        if stamp < self.updated_at:
            raise ProjectNoteError("PROJECT_NOTE_TIMESTAMP_ORDER_INVALID")
        return replace(
            self, archived_at=stamp, updated_at=stamp,
            revision=self.revision + 1, fingerprint="",
        )

    def _require_writer(self, principal_id: str, revision: int) -> None:
        """Require exact author possession, current revision and nonterminal state."""
        _identifier("actor_principal_id", principal_id)
        if principal_id != self.author_principal_id:
            raise ProjectNoteError("PROJECT_NOTE_AUTHOR_DENIED")
        if type(revision) is not int or revision != self.revision:
            raise ProjectNoteError("PROJECT_NOTE_REVISION_CONFLICT")
        if self.archived_at is not None:
            raise ProjectNoteError("PROJECT_NOTE_ARCHIVED")


__all__ = ["VERSION", "SCHEMA", "NOTE_COLOURS", "ProjectNote", "ProjectNoteError"]

# ARTIFACT: project_note.py
# VERSION: v1.1.0-IMMUTABLE-STICKY-COLOUR-EVIDENCE
# AUTHORITY BOUNDARY: immutable author-owned note lifecycle only
# TENANT POSTURE: exact tenant and project coordinates, no default tenant
# FAIL-CLOSED POSTURE: source signature/integrity, author and CAS checks fail closed
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
