"""Immutable client-to-matter visibility evidence for Legal Operations.

TITLE: WILSY OS Legal Client Matter Visibility Binding
VERSION: v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING
AUTHORITY: Immutable Legal Operations client-visibility relation evidence only.
EPITOME: Bind one explicit client principal to one canonical tenant-scoped
         CaseMatter through immutable ACTIVE -> REVOKED visibility evidence,
         deriving tenant, matter identity and source-matter fingerprint from P1
         without granting IAM, tenant-wide reads, lifecycle mutation, service,
         billing, payment, settlement, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_visibility_binding.py
COLLABORATION / OWNERSHIP: P1 owns CaseMatter truth; IAM owns principal
                            lifecycle, membership, business role, role assignment
                            and authorization; L8-7A owns only the immutable
                            principal-to-matter visibility relation. Registry,
                            provisioning orchestration, HTTP/client projection,
                            and revocation command admission are later bounded
                            gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING
           establishes factory-only ACTIVE visibility evidence anchored to one
           canonical CaseMatter, a stable tenant/client/matter binding identity,
           deterministic SHA3-512 fingerprints, monotonic ACTIVE -> REVOKED
           lifecycle, explicit grant/revocation actor provenance, chronology
           checks, and no reactivation or inferred authorization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque tenant/principal/matter identifiers and
                             evidence references only. No credentials, tokens,
                             client profile expansion, document content, GPS,
                             provider, billing, payment, or AI payloads.
TENANT BOUNDARY: Tenant, case_matter_id, and source CaseMatter fingerprint are
                 derived exclusively from one exact canonical P1 CaseMatter.
                 Caller-supplied tenant scope is not accepted.
AUTHORITY BOUNDARY: Visibility relation evidence only. ACTIVE does not itself
                    prove current authentication, membership, LEGAL_CLIENT role,
                    read permission, matter access, or HTTP authorization. Every
                    consuming read must independently prove current IAM plus the
                    exact current ACTIVE binding.
FINANCIAL AUTHORITY BOUNDARY: No invoice, payment, execution, settlement, paid,
                              or financial semantics; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable value construction and transition only;
                      no persistence, client, session, transaction, or retry.
FAIL-CLOSED DECLARATION: Direct construction, malformed identities/timestamps/
                         references, non-canonical CaseMatter evidence, illegal
                         state metadata, chronology reversal, repeat revocation,
                         reactivation, and fingerprint drift reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


VERSION: Final[str] = "v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-CLIENT-MATTER-VISIBILITY-BINDING/V1"
IDENTITY_SCHEMA: Final[str] = (
    "WILSY-LEGAL-OPERATIONS-CLIENT-MATTER-VISIBILITY-IDENTITY/V1"
)
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class LegalClientMatterVisibilityStatus(StrEnum):
    """Monotonic visibility states; revoked visibility cannot reactivate."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class LegalClientMatterVisibilityBindingError(ValueError):
    """Stable fail-closed L8-7A client-matter visibility value failure."""

    def __init__(self, code: str) -> None:
        """Create one bounded visibility-binding validation code."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable L8-7A error while retaining the technical cause."""
    error = LegalClientMatterVisibilityBindingError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one canonical opaque identifier without normalization."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"L8_7A_{name.upper()}_INVALID")
    return cast(str, value)


def _timestamp(name: str, value: object) -> datetime:
    """Require one timezone-aware visibility lifecycle timestamp."""
    if not isinstance(value, datetime):
        _fail(f"L8_7A_{name.upper()}_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        _fail(f"L8_7A_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object) -> str:
    """Require one bounded non-empty evidence reference."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 512
    ):
        _fail(f"L8_7A_{name.upper()}_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 evidence fingerprint."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        _fail(f"L8_7A_{name.upper()}_INVALID")
    return value


def _sha3(payload: dict[str, object]) -> str:
    """Return lowercase SHA3-512 over deterministic canonical JSON."""
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True, init=False)
class LegalClientMatterVisibilityBinding:
    """Immutable relation between one client principal and one CaseMatter.

    :meth:`grant` derives tenant, matter identity, and the source CaseMatter
    fingerprint from exact P1 evidence. :meth:`revoke` creates a new immutable
    REVOKED snapshot with the same stable binding identity. Neither operation
    proves current IAM, LEGAL_CLIENT role, read permission, or actor authority;
    later orchestration must prove those independently before persistence.
    """

    tenant_id: str
    client_principal_id: str
    case_matter_id: str
    source_case_matter_fingerprint: str
    granted_by_principal_id: str
    granted_at: datetime
    grant_evidence_reference: str
    status: LegalClientMatterVisibilityStatus
    revoked_by_principal_id: str | None
    revoked_at: datetime | None
    revocation_evidence_reference: str | None

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject documentary construction; use :meth:`grant`."""
        _fail("L8_7A_FACTORY_REQUIRED")

    @classmethod
    def grant(
        cls,
        *,
        client_principal_id: str,
        case_matter: CaseMatter,
        granted_by_principal_id: str,
        granted_at: datetime,
        evidence_reference: str,
    ) -> "LegalClientMatterVisibilityBinding":
        """Create one ACTIVE visibility relation from exact CaseMatter evidence.

        The factory proves only immutable relation shape and P1 matter provenance.
        It does not prove that the target principal is active, a tenant member,
        assigned the LEGAL_CLIENT role, or otherwise authorized. It also does not
        prove the granting principal's current role/permission. Those checks are
        mandatory responsibilities of the later L8-7 provisioning orchestrator.
        """
        if type(case_matter) is not CaseMatter:
            _fail("L8_7A_CASE_MATTER_REQUIRED")
        try:
            case_matter.__post_init__()
        except Exception as error:
            _fail("L8_7A_CASE_MATTER_INVALID", error)

        client_principal = _identity("client_principal_id", client_principal_id)
        granting_principal = _identity(
            "granted_by_principal_id",
            granted_by_principal_id,
        )
        timestamp = _timestamp("granted_at", granted_at)
        reference = _text("grant_evidence_reference", evidence_reference)

        value = cast(Any, object.__new__(cls))
        object.__setattr__(value, "tenant_id", case_matter.tenant_id)
        object.__setattr__(value, "client_principal_id", client_principal)
        object.__setattr__(value, "case_matter_id", case_matter.case_matter_id)
        object.__setattr__(
            value,
            "source_case_matter_fingerprint",
            case_matter.fingerprint,
        )
        object.__setattr__(
            value,
            "granted_by_principal_id",
            granting_principal,
        )
        object.__setattr__(value, "granted_at", timestamp)
        object.__setattr__(value, "grant_evidence_reference", reference)
        object.__setattr__(
            value,
            "status",
            LegalClientMatterVisibilityStatus.ACTIVE,
        )
        object.__setattr__(value, "revoked_by_principal_id", None)
        object.__setattr__(value, "revoked_at", None)
        object.__setattr__(value, "revocation_evidence_reference", None)
        value._validate()
        return cast("LegalClientMatterVisibilityBinding", value)

    def revoke(
        self,
        *,
        revoked_by_principal_id: str,
        revoked_at: datetime,
        evidence_reference: str,
    ) -> "LegalClientMatterVisibilityBinding":
        """Return the sole permitted visibility transition: ACTIVE -> REVOKED.

        Revocation records actor/time/evidence provenance only. The method does
        not authorize the actor, mutate persistence, delete history, or grant a
        replacement binding. A revoked binding cannot reactivate.
        """
        self._validate()
        if self.status is not LegalClientMatterVisibilityStatus.ACTIVE:
            _fail("L8_7A_VISIBILITY_ALREADY_REVOKED")

        actor = _identity("revoked_by_principal_id", revoked_by_principal_id)
        timestamp = _timestamp("revoked_at", revoked_at)
        if timestamp < self.granted_at:
            _fail("L8_7A_REVOCATION_CHRONOLOGY_INVALID")
        reference = _text(
            "revocation_evidence_reference",
            evidence_reference,
        )

        value = cast(Any, object.__new__(type(self)))
        for field_name in (
            "tenant_id",
            "client_principal_id",
            "case_matter_id",
            "source_case_matter_fingerprint",
            "granted_by_principal_id",
            "granted_at",
            "grant_evidence_reference",
        ):
            object.__setattr__(value, field_name, getattr(self, field_name))
        object.__setattr__(
            value,
            "status",
            LegalClientMatterVisibilityStatus.REVOKED,
        )
        object.__setattr__(value, "revoked_by_principal_id", actor)
        object.__setattr__(value, "revoked_at", timestamp)
        object.__setattr__(
            value,
            "revocation_evidence_reference",
            reference,
        )
        value._validate()
        return cast("LegalClientMatterVisibilityBinding", value)

    def _validate(self) -> None:
        """Revalidate exact immutable relation and monotonic lifecycle shape."""
        _identity("tenant_id", self.tenant_id)
        _identity("client_principal_id", self.client_principal_id)
        _identity("case_matter_id", self.case_matter_id)
        _fingerprint(
            "source_case_matter_fingerprint",
            self.source_case_matter_fingerprint,
        )
        _identity("granted_by_principal_id", self.granted_by_principal_id)
        _timestamp("granted_at", self.granted_at)
        _text("grant_evidence_reference", self.grant_evidence_reference)
        if not isinstance(self.status, LegalClientMatterVisibilityStatus):
            _fail("L8_7A_STATUS_INVALID")

        if self.status is LegalClientMatterVisibilityStatus.ACTIVE:
            if (
                self.revoked_by_principal_id is not None
                or self.revoked_at is not None
                or self.revocation_evidence_reference is not None
            ):
                _fail("L8_7A_ACTIVE_REVOCATION_METADATA_FORBIDDEN")
            return

        if (
            self.revoked_by_principal_id is None
            or self.revoked_at is None
            or self.revocation_evidence_reference is None
        ):
            _fail("L8_7A_REVOCATION_METADATA_REQUIRED")
        _identity("revoked_by_principal_id", self.revoked_by_principal_id)
        revoked_at = _timestamp("revoked_at", self.revoked_at)
        if revoked_at < self.granted_at:
            _fail("L8_7A_REVOCATION_CHRONOLOGY_INVALID")
        _text(
            "revocation_evidence_reference",
            self.revocation_evidence_reference,
        )

    @property
    def binding_identity(self) -> str:
        """Return the stable SHA3-512 identity of tenant/client/matter scope.

        The identity deliberately excludes mutable lifecycle state, actor
        provenance, and source-matter snapshot fingerprint so ACTIVE and REVOKED
        snapshots of the same exact relation share one durable natural identity.
        """
        self._validate()
        return _sha3(
            {
                "schema": IDENTITY_SCHEMA,
                "tenant_id": self.tenant_id,
                "client_principal_id": self.client_principal_id,
                "case_matter_id": self.case_matter_id,
            }
        )

    def _payload(self) -> dict[str, object]:
        """Return exact fingerprint payload without derived fingerprint itself."""
        self._validate()
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "binding_identity": self.binding_identity,
            "tenant_id": self.tenant_id,
            "client_principal_id": self.client_principal_id,
            "case_matter_id": self.case_matter_id,
            "source_case_matter_fingerprint": (
                self.source_case_matter_fingerprint
            ),
            "granted_by_principal_id": self.granted_by_principal_id,
            "granted_at": self.granted_at.isoformat(),
            "grant_evidence_reference": self.grant_evidence_reference,
            "status": self.status.value,
            "revoked_by_principal_id": self.revoked_by_principal_id,
            "revoked_at": (
                None if self.revoked_at is None else self.revoked_at.isoformat()
            ),
            "revocation_evidence_reference": (
                self.revocation_evidence_reference
            ),
        }

    @property
    def fingerprint(self) -> str:
        """Return deterministic SHA3-512 visibility snapshot evidence identity."""
        return _sha3(self._payload())

    def to_dict(self) -> dict[str, object]:
        """Serialize exact visibility evidence with deterministic fingerprint."""
        payload = self._payload()
        payload["fingerprint"] = self.fingerprint
        return payload


__all__ = [
    "IDENTITY_SCHEMA",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterVisibilityBinding",
    "LegalClientMatterVisibilityBindingError",
    "LegalClientMatterVisibilityStatus",
]


# ARTIFACT: legal_client_matter_visibility_binding.py
# VERSION: v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING
# AUTHORITY BOUNDARY: immutable principal-to-canonical-CaseMatter visibility relation evidence only
# TENANT POSTURE: tenant/matter/source fingerprint derive only from exact P1 CaseMatter evidence
# FAIL-CLOSED POSTURE: direct construction, malformed provenance, illegal lifecycle metadata, chronology reversal and reactivation reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
