"""WILSY OS HR Document Commit-Reconciliation Outcome Domain.

TITLE: HR Document Commit-Reconciliation Outcome
VERSION: v1.0.0-P0-C12F6E1-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Represent immutable durable evidence that a later HR reconciliation
transaction proved one frozen commit uncertainty to be either already
committed exactly or recovered by exact replay-safe persistence.

EPITOME:
FROZEN HR COMMIT UNCERTAINTY
+ EXACT RECONSTRUCTED HR DOCUMENT
+ LATER RECONCILIATION PROOF
-> IMMUTABLE RECONCILIATION OUTCOME EVIDENCE

CLOSED OUTCOME VOCABULARY:
- COMMITTED_CONFIRMED
- COMMIT_RECOVERED

AUTHORITY BOUNDARY:
Pure immutable reconciliation-outcome evidence only.
This artifact grants no persistence, provider IO, provider deletion,
orphan determination, original Mongo-commit-failure determination,
retention/disposal authority, IAM, HTTP, payroll, billing, payment,
settlement or financial execution authority.

UNCERTAINTY POSTURE:
The original HrDocumentCommitUncertainty remains immutable and is never
mutated or replaced by this evidence.

FAIL-CLOSED POSTURE:
Unknown transaction outcome does not produce reconciliation evidence.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/hr_document_commit_reconciliation_outcome.py

CERTIFICATION / UPDATE DATE: 2026-10-05

CHANGELOG:
2026-10-05 v1.0.0-P0-C12F6E1-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME
establishes immutable restart-safe HR reconciliation outcome evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, cast

from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentDomainError,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    HrDocumentCommitUncertainty,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F6E1-"
    "HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME"
)

SCHEMA: Final[str] = (
    "WILSY-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME/V1"
)

_OUTCOME_PREFIX: Final[str] = (
    "hr-document-commit-reconciliation-outcome:"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_PSEUDO_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "*",
        "default",
        "global",
        "global_root",
        "master",
        "root",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "outcome_id",
    "tenant_id",
    "uncertainty_id",
    "uncertainty_fingerprint",
    "document_version_id",
    "document_fingerprint",
    "outcome",
    "reconciled_at",
    "schema",
    "outcome_version",
    "fingerprint",
)


class HrDocumentCommitReconciliationOutcome(
    StrEnum
):
    """Closed durable reconciliation outcome vocabulary."""

    COMMITTED_CONFIRMED = (
        "COMMITTED_CONFIRMED"
    )

    COMMIT_RECOVERED = (
        "COMMIT_RECOVERED"
    )


class HrDocumentCommitReconciliationOutcomeError(
    ValueError
):
    """Stable fail-closed F6E1 outcome-domain error."""


def _fail(
    code: str,
) -> None:
    raise HrDocumentCommitReconciliationOutcomeError(
        code
    )


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(
            value
        ) is None
    ):
        _fail(
            f"P0_C12F6E1_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if (
        tenant.casefold()
        in _PSEUDO_TENANTS
    ):
        _fail(
            "P0_C12F6E1_TENANT_REQUIRED"
        )

    return tenant


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or _SHA3_RE.fullmatch(
            value
        ) is None
    ):
        _fail(
            f"P0_C12F6E1_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _utc(
    name: str,
    value: object,
) -> datetime:
    if isinstance(
        value,
        str,
    ):
        try:
            value = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError:
            _fail(
                f"P0_C12F6E1_{name.upper()}_INVALID"
            )

    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"P0_C12F6E1_{name.upper()}_UTC_REQUIRED"
        )

    return cast(
        datetime,
        value,
    ).astimezone(
        timezone.utc
    )


def _serialize_value(
    value: object,
) -> object:
    if isinstance(
        value,
        datetime,
    ):
        return value.isoformat()

    if isinstance(
        value,
        HrDocumentCommitReconciliationOutcome,
    ):
        return value.value

    return value


def _outcome_identity(
    *,
    tenant_id: str,
    uncertainty_id: str,
    uncertainty_fingerprint: str,
    document_version_id: str,
    document_fingerprint: str,
    outcome: HrDocumentCommitReconciliationOutcome,
    reconciled_at: datetime,
) -> str:
    payload = {
        "tenant_id":
            tenant_id,
        "uncertainty_id":
            uncertainty_id,
        "uncertainty_fingerprint":
            uncertainty_fingerprint,
        "document_version_id":
            document_version_id,
        "document_fingerprint":
            document_fingerprint,
        "outcome":
            outcome.value,
        "reconciled_at":
            reconciled_at.isoformat(),
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return (
        _OUTCOME_PREFIX
        + hashlib.sha3_512(
            raw
        ).hexdigest()
    )


def _fingerprint(
    payload: Mapping[
        str,
        object,
    ],
) -> str:
    raw = json.dumps(
        dict(
            payload
        ),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        raw
    ).hexdigest()


def _expected_document(
    uncertainty: HrDocumentCommitUncertainty,
) -> HrDocument:
    try:
        return uncertainty.to_hr_document()

    except Exception as error:
        raise HrDocumentCommitReconciliationOutcomeError(
            "P0_C12F6E1_EXPECTED_DOCUMENT_RECONSTRUCTION_INVALID"
        ) from error


def _validate_document_binding(
    *,
    uncertainty: HrDocumentCommitUncertainty,
    document: HrDocument,
) -> None:
    if type(
        uncertainty
    ) is not HrDocumentCommitUncertainty:
        _fail(
            "P0_C12F6E1_UNCERTAINTY_REQUIRED"
        )

    if type(
        document
    ) is not HrDocument:
        _fail(
            "P0_C12F6E1_HR_DOCUMENT_REQUIRED"
        )

    try:
        uncertainty.__post_init__()
        document.__post_init__()

    except Exception as error:
        raise HrDocumentCommitReconciliationOutcomeError(
            "P0_C12F6E1_INPUT_CORRUPTION"
        ) from error

    expected = _expected_document(
        uncertainty
    )

    if document != expected:
        _fail(
            "P0_C12F6E1_HR_DOCUMENT_MISMATCH"
        )

    if (
        document.tenant_id
        != uncertainty.tenant_id
        or document.document_version_id
        != uncertainty.document_version_id
        or not hmac.compare_digest(
            document.fingerprint,
            expected.fingerprint,
        )
    ):
        _fail(
            "P0_C12F6E1_HR_DOCUMENT_BINDING_MISMATCH"
        )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentCommitReconciliationOutcomeEvidence:
    """Immutable durable evidence of one proven reconciliation result."""

    outcome_id: str

    tenant_id: str
    uncertainty_id: str
    uncertainty_fingerprint: str

    document_version_id: str
    document_fingerprint: str

    outcome: HrDocumentCommitReconciliationOutcome
    reconciled_at: datetime

    schema: str = SCHEMA
    outcome_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )

        uncertainty_id = _identity(
            "uncertainty_id",
            self.uncertainty_id,
        )

        uncertainty_fingerprint = _sha3(
            "uncertainty_fingerprint",
            self.uncertainty_fingerprint,
        )

        document_version_id = _identity(
            "document_version_id",
            self.document_version_id,
        )

        document_fingerprint = _sha3(
            "document_fingerprint",
            self.document_fingerprint,
        )

        if (
            type(
                self.outcome
            )
            is not HrDocumentCommitReconciliationOutcome
        ):
            _fail(
                "P0_C12F6E1_OUTCOME_INVALID"
            )

        reconciled = _utc(
            "reconciled_at",
            self.reconciled_at,
        )

        if (
            self.schema != SCHEMA
            or self.outcome_version != VERSION
        ):
            _fail(
                "P0_C12F6E1_SCHEMA_INVALID"
            )

        expected_id = _outcome_identity(
            tenant_id=tenant,
            uncertainty_id=(
                uncertainty_id
            ),
            uncertainty_fingerprint=(
                uncertainty_fingerprint
            ),
            document_version_id=(
                document_version_id
            ),
            document_fingerprint=(
                document_fingerprint
            ),
            outcome=self.outcome,
            reconciled_at=reconciled,
        )

        if (
            not isinstance(
                self.outcome_id,
                str,
            )
            or not hmac.compare_digest(
                self.outcome_id,
                expected_id,
            )
        ):
            _fail(
                "P0_C12F6E1_OUTCOME_ID_MISMATCH"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "uncertainty_id",
            uncertainty_id,
        )
        object.__setattr__(
            self,
            "uncertainty_fingerprint",
            uncertainty_fingerprint,
        )
        object.__setattr__(
            self,
            "document_version_id",
            document_version_id,
        )
        object.__setattr__(
            self,
            "document_fingerprint",
            document_fingerprint,
        )
        object.__setattr__(
            self,
            "reconciled_at",
            reconciled,
        )

        payload = {
            field: _serialize_value(
                getattr(
                    self,
                    field,
                )
            )
            for field in _FIELDS[:-1]
        }

        digest = _fingerprint(
            payload
        )

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                _fail(
                    "P0_C12F6E1_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable outcome evidence."""

        return {
            field: _serialize_value(
                getattr(
                    self,
                    field,
                )
            )
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[
            str,
            object,
        ],
    ) -> "HrDocumentCommitReconciliationOutcomeEvidence":
        """Strictly hydrate exact immutable reconciliation outcome."""

        if (
            not isinstance(
                payload,
                Mapping,
            )
            or set(
                payload
            ) != set(
                _FIELDS
            )
        ):
            _fail(
                "P0_C12F6E1_SCHEMA_INVALID"
            )

        values = dict(
            payload
        )

        stored_fingerprint = values.pop(
            "fingerprint"
        )

        try:
            values[
                "outcome"
            ] = HrDocumentCommitReconciliationOutcome(
                cast(
                    str,
                    values[
                        "outcome"
                    ],
                )
            )

            values[
                "reconciled_at"
            ] = _utc(
                "reconciled_at",
                values[
                    "reconciled_at"
                ],
            )

            values[
                "fingerprint"
            ] = stored_fingerprint

            return cls(
                **cast(
                    Any,
                    values,
                )
            )

        except HrDocumentCommitReconciliationOutcomeError:
            raise

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise HrDocumentCommitReconciliationOutcomeError(
                "P0_C12F6E1_HYDRATION_INVALID"
            ) from error


def record_hr_document_commit_reconciliation_outcome(
    *,
    uncertainty: HrDocumentCommitUncertainty,
    document: HrDocument,
    outcome: HrDocumentCommitReconciliationOutcome,
    reconciled_at: datetime,
) -> HrDocumentCommitReconciliationOutcomeEvidence:
    """Create one exact durable reconciliation outcome from proven inputs."""

    _validate_document_binding(
        uncertainty=uncertainty,
        document=document,
    )

    if type(
        outcome
    ) is not HrDocumentCommitReconciliationOutcome:
        _fail(
            "P0_C12F6E1_OUTCOME_INVALID"
        )

    reconciled = _utc(
        "reconciled_at",
        reconciled_at,
    )

    # A later reconciliation proof must strictly follow the original
    # uncertainty detection. Equal timestamps are not sufficient.
    if reconciled <= uncertainty.detected_at:
        _fail(
            "P0_C12F6E1_RECONCILED_AT_NOT_LATER_THAN_UNCERTAINTY"
        )

    outcome_id = _outcome_identity(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=(
            uncertainty.uncertainty_id
        ),
        uncertainty_fingerprint=(
            uncertainty.fingerprint
        ),
        document_version_id=(
            document.document_version_id
        ),
        document_fingerprint=(
            document.fingerprint
        ),
        outcome=outcome,
        reconciled_at=reconciled,
    )

    return HrDocumentCommitReconciliationOutcomeEvidence(
        outcome_id=outcome_id,
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=(
            uncertainty.uncertainty_id
        ),
        uncertainty_fingerprint=(
            uncertainty.fingerprint
        ),
        document_version_id=(
            document.document_version_id
        ),
        document_fingerprint=(
            document.fingerprint
        ),
        outcome=outcome,
        reconciled_at=reconciled,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "HrDocumentCommitReconciliationOutcome",
    "HrDocumentCommitReconciliationOutcomeEvidence",
    "HrDocumentCommitReconciliationOutcomeError",
    "record_hr_document_commit_reconciliation_outcome",
]


# ARTIFACT: tools/eos/saas/domain/hr_document_commit_reconciliation_outcome.py
# VERSION: v1.0.0-P0-C12F6E1-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME
# AUTHORITY: immutable HR reconciliation-outcome evidence only
# OUTCOMES: COMMITTED_CONFIRMED / COMMIT_RECOVERED only
# UNCERTAINTY MUTATION AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# PROVIDER DELETE AUTHORITY: none
# RETENTION/DISPOSAL AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
