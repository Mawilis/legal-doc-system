"""
WILSY OS — P14-R20R22 Legal Work Completion Authority Evidence.

PURPOSE
-------
Represent immutable, deterministic evidence that the already-governed
Legal work-completion authority conjunction was satisfied.

The evidence binds:

    canonical tenant IAM authorization evidence
    ∩ exact Legal work item identity
    ∩ exact historical Legal work assignment identity
    ∩ acting principal
    ∩ explicit timezone-aware evaluation instant

This artifact grants no authority, performs no authorization, owns no
transaction, performs no persistence, mutates no Legal work item, advances
no workflow, satisfies no dependency, and grants no financial authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
from typing import Any, Mapping, cast


SCHEMA = (
    "WILSY-LEGAL-WORK-COMPLETION-"
    "AUTHORITY-EVIDENCE/V1"
)

VERSION = (
    "v1.0.0-P14-R20R22-"
    "WORK-COMPLETION-AUTHORITY-EVIDENCE"
)

_REFERENCE_PREFIX = (
    "legal-work-completion-authority-evidence:"
)


class LegalWorkCompletionAuthorityEvidenceError(
    ValueError
):
    """Fail-closed completion-authority evidence validation error."""


def _fail(code: str) -> None:
    raise LegalWorkCompletionAuthorityEvidenceError(
        code
    )


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(
            "P14_R20R22_"
            + name.upper()
            + "_INVALID"
        )

    text = cast(
        str,
        value,
    )

    if (
        not text
        or text != text.strip()
        or len(text) > limit
    ):
        _fail(
            "P14_R20R22_"
            + name.upper()
            + "_INVALID"
        )

    return text


def _fingerprint(
    name: str,
    value: object,
) -> str:
    text = _text(
        name,
        value,
        limit=128,
    )

    if (
        len(text) != 128
        or text.lower() != text
    ):
        _fail(
            "P14_R20R22_"
            + name.upper()
            + "_INVALID"
        )

    try:
        int(
            text,
            16,
        )
    except ValueError:
        _fail(
            "P14_R20R22_"
            + name.upper()
            + "_INVALID"
        )

    return text


def _moment(
    value: object,
) -> datetime:
    if not isinstance(
        value,
        datetime,
    ):
        _fail(
            "P14_R20R22_EVALUATED_AT_INVALID"
        )

    moment = cast(
        datetime,
        value,
    )

    if (
        moment.tzinfo is None
        or moment.utcoffset() is None
    ):
        _fail(
            "P14_R20R22_EVALUATED_AT_INVALID"
        )

    return moment.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalWorkCompletionAuthorityEvidence:
    """
    Immutable evidence for the full Legal work-completion authority basis.

    No caller supplies the derived reference or fingerprint.
    """

    completion_authority_evidence_id: str

    tenant_id: str
    case_matter_id: str
    work_item_id: str
    work_item_fingerprint: str

    principal_id: str

    assignment_id: str
    assignment_fingerprint: str

    iam_authorization_evidence_reference: str
    iam_authorization_evidence_fingerprint: str

    evaluated_at: datetime

    schema: str = SCHEMA
    version: str = VERSION

    completion_authority_evidence_reference: str = field(
        init=False,
    )

    fingerprint: str = field(
        init=False,
    )

    def __post_init__(self) -> None:
        if (
            self.schema != SCHEMA
            or self.version != VERSION
        ):
            _fail(
                "P14_R20R22_IDENTITY_INVALID"
            )

        evidence_id = _text(
            "completion_authority_evidence_id",
            self.completion_authority_evidence_id,
            limit=160,
        )

        tenant_id = _text(
            "tenant_id",
            self.tenant_id,
            limit=160,
        )

        matter_id = _text(
            "case_matter_id",
            self.case_matter_id,
            limit=160,
        )

        work_id = _text(
            "work_item_id",
            self.work_item_id,
            limit=160,
        )

        work_fingerprint = _fingerprint(
            "work_item_fingerprint",
            self.work_item_fingerprint,
        )

        principal_id = _text(
            "principal_id",
            self.principal_id,
            limit=160,
        )

        assignment_id = _text(
            "assignment_id",
            self.assignment_id,
            limit=160,
        )

        assignment_fingerprint = _fingerprint(
            "assignment_fingerprint",
            self.assignment_fingerprint,
        )

        iam_reference = _text(
            "iam_authorization_evidence_reference",
            self.iam_authorization_evidence_reference,
            limit=320,
        )

        iam_fingerprint = _fingerprint(
            "iam_authorization_evidence_fingerprint",
            self.iam_authorization_evidence_fingerprint,
        )

        evaluated_at = _moment(
            self.evaluated_at
        )

        object.__setattr__(
            self,
            "completion_authority_evidence_id",
            evidence_id,
        )

        object.__setattr__(
            self,
            "tenant_id",
            tenant_id,
        )

        object.__setattr__(
            self,
            "case_matter_id",
            matter_id,
        )

        object.__setattr__(
            self,
            "work_item_id",
            work_id,
        )

        object.__setattr__(
            self,
            "work_item_fingerprint",
            work_fingerprint,
        )

        object.__setattr__(
            self,
            "principal_id",
            principal_id,
        )

        object.__setattr__(
            self,
            "assignment_id",
            assignment_id,
        )

        object.__setattr__(
            self,
            "assignment_fingerprint",
            assignment_fingerprint,
        )

        object.__setattr__(
            self,
            "iam_authorization_evidence_reference",
            iam_reference,
        )

        object.__setattr__(
            self,
            "iam_authorization_evidence_fingerprint",
            iam_fingerprint,
        )

        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )

        digest = self._compute_fingerprint()

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

        object.__setattr__(
            self,
            "completion_authority_evidence_reference",
            _REFERENCE_PREFIX
            + digest,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        """Return the complete semantic authority-evidence payload."""

        return {
            "schema":
                self.schema,
            "version":
                self.version,
            "completion_authority_evidence_id":
                self.completion_authority_evidence_id,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "work_item_id":
                self.work_item_id,
            "work_item_fingerprint":
                self.work_item_fingerprint,
            "principal_id":
                self.principal_id,
            "assignment_id":
                self.assignment_id,
            "assignment_fingerprint":
                self.assignment_fingerprint,
            "iam_authorization_evidence_reference":
                self.iam_authorization_evidence_reference,
            "iam_authorization_evidence_fingerprint":
                self.iam_authorization_evidence_fingerprint,
            "evaluated_at":
                self.evaluated_at.isoformat(),
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        )

        return sha3_512(
            canonical.encode(
                "utf-8"
            )
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Return the strict canonical serialized evidence."""

        return {
            **self.semantic_dict(),
            "completion_authority_evidence_reference":
                self.completion_authority_evidence_reference,
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkCompletionAuthorityEvidence":
        """Hydrate strict canonical serialized evidence."""

        if not isinstance(
            value,
            Mapping,
        ):
            _fail(
                "P14_R20R22_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "version",
            "completion_authority_evidence_id",
            "tenant_id",
            "case_matter_id",
            "work_item_id",
            "work_item_fingerprint",
            "principal_id",
            "assignment_id",
            "assignment_fingerprint",
            "iam_authorization_evidence_reference",
            "iam_authorization_evidence_fingerprint",
            "evaluated_at",
            "completion_authority_evidence_reference",
            "fingerprint",
        }

        payload = cast(
            Mapping[str, object],
            value,
        )

        if set(payload) != required:
            _fail(
                "P14_R20R22_PAYLOAD_SCHEMA_INVALID"
            )

        raw_time_value = payload[
            "evaluated_at"
        ]

        if not isinstance(
            raw_time_value,
            str,
        ):
            _fail(
                "P14_R20R22_EVALUATED_AT_INVALID"
            )

        raw_time = cast(
            str,
            raw_time_value,
        )

        try:
            parsed_evaluated_at = datetime.fromisoformat(
                raw_time
            )
        except ValueError as error:
            raise LegalWorkCompletionAuthorityEvidenceError(
                "P14_R20R22_EVALUATED_AT_INVALID"
            ) from error

        evaluated_at = _moment(
            parsed_evaluated_at
        )

        body = cast(
            Mapping[str, Any],
            payload,
        )

        restored = cls(
            completion_authority_evidence_id=body[
                "completion_authority_evidence_id"
            ],
            tenant_id=body[
                "tenant_id"
            ],
            case_matter_id=body[
                "case_matter_id"
            ],
            work_item_id=body[
                "work_item_id"
            ],
            work_item_fingerprint=body[
                "work_item_fingerprint"
            ],
            principal_id=body[
                "principal_id"
            ],
            assignment_id=body[
                "assignment_id"
            ],
            assignment_fingerprint=body[
                "assignment_fingerprint"
            ],
            iam_authorization_evidence_reference=body[
                "iam_authorization_evidence_reference"
            ],
            iam_authorization_evidence_fingerprint=body[
                "iam_authorization_evidence_fingerprint"
            ],
            evaluated_at=evaluated_at,
            schema=body[
                "schema"
            ],
            version=body[
                "version"
            ],
        )

        supplied_reference = _text(
            "completion_authority_evidence_reference",
            body[
                "completion_authority_evidence_reference"
            ],
            limit=320,
        )

        supplied_fingerprint = _fingerprint(
            "fingerprint",
            body[
                "fingerprint"
            ],
        )

        if not hmac.compare_digest(
            supplied_reference,
            restored.completion_authority_evidence_reference,
        ):
            _fail(
                "P14_R20R22_REFERENCE_MISMATCH"
            )

        if not hmac.compare_digest(
            supplied_fingerprint,
            restored.fingerprint,
        ):
            _fail(
                "P14_R20R22_FINGERPRINT_MISMATCH"
            )

        return restored


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkCompletionAuthorityEvidence",
    "LegalWorkCompletionAuthorityEvidenceError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT:
#   legal_work_completion_authority_evidence.py
# VERSION:
#   v1.0.0-P14-R20R22-WORK-COMPLETION-AUTHORITY-EVIDENCE
# AUTHORITY:
#   NONE — immutable provenance evidence only
# IAM:
#   references canonical tenant authorization evidence; does not replace it
# WORK ASSIGNMENT:
#   binds exact immutable assignment identity and fingerprint
# WORK ITEM:
#   binds exact immutable work-item fingerprint
# TRANSACTION:
#   NONE
# PERSISTENCE:
#   NONE
# WORKFLOW:
#   NONE
# DEPENDENCY:
#   NONE
# NOTIFICATION:
#   NONE
# AI:
#   NONE
# FINANCIAL:
#   NONE
# =============================================================================
