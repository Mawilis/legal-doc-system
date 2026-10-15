"""TITLE: WILSY OS Privileged Activation Domain.
VERSION: v1.0.0-P4-R1-PRIVILEGED-ACTIVATION-DOMAIN
AUTHORITY: Immutable normal privileged-activation lifecycle facts only.
EPITOME: Defines one exact, self-issued, short-lived P4 activation without
performing IAM reads, persistence, authorization, or privileged use.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_activation.py
COLLABORATION / OWNERSHIP: Wilsy OS Sovereign IAM P2 eligibility, P3 assurance,
future P4 persistence/orchestration, and future P5 privileged-use composition.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P4-R1 establishes exact-scope self-activation, immutable
ACTIVE-to-REVOKED revision chaining, a 15-minute hard lifetime ceiling,
half-open temporal currentness, deterministic SHA3-512 sealing, and explicit
P2/P3 evidence lineage without creating permission, use, break-glass, or
financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Identifiers and evidence fingerprints only; secret,
credential, proof, bearer, OTP, key, and signature material are forbidden.
TENANT BOUNDARY: TENANT_PRIVILEGED requires one exact tenant; platform-root
scope forbids tenant input. Wildcards and cross-scope use fail closed.
AUTHORITY BOUNDARY: ACTIVATION != ROLE != PERMISSION != PRIVILEGED USE.
FINANCIAL AUTHORITY BOUNDARY: No payment, release, execution, or settlement.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final

from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose


VERSION: Final[str] = "v1.0.0-P4-R1-PRIVILEGED-ACTIVATION-DOMAIN"
SCHEMA: Final[str] = "WILSY-PRIVILEGED-ACTIVATION/V1"
MAXIMUM_ACTIVATION_LIFETIME: Final[timedelta] = timedelta(minutes=15)
ISSUANCE_PERMISSION: Final[str] = "privileged_activation:issue"
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class PrivilegedActivationError(ValueError):
    """Reject malformed or constitutionally invalid P4 activation facts."""


class PrivilegedActivationStatus(StrEnum):
    """Closed normal-activation lifecycle vocabulary.

    Expiry is temporal currentness, not a destructive status transition.
    """

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def _identifier(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "*" in value
    ):
        raise PrivilegedActivationError(name + "_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise PrivilegedActivationError(name + "_INVALID")
    return value


def _moment(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PrivilegedActivationError(name + "_INVALID")
    return value.astimezone(timezone.utc)


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PrivilegedActivationError("REVISION_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class PrivilegedActivation:
    """One immutable normal P4 activation lifecycle revision.

    Institutional semantics:
      - the actor and activated subject are necessarily the same principal;
      - scope is the exact tenant/principal/role/target-class tuple;
      - P2/P3 evidence values are lineage, never live-currentness inference;
      - ACTIVE means lifecycle state only, not current privileged-use authority;
      - P5 must separately require current activation and fresh use-purpose P3;
      - callers own ID creation, clocks, IAM reads, authorization, and storage.
    """

    activation_id: str
    tenant_id: str | None
    principal_id: str
    actor_principal_id: str
    privileged_role_id: str
    target_class: PrivilegedTargetClass

    eligibility_evidence_id: str
    eligibility_evidence_fingerprint: str
    assurance_evidence_id: str
    assurance_evidence_fingerprint: str
    creation_assurance_purpose: PrivilegedAssurancePurpose

    activated_at: datetime
    effective_until: datetime
    status: PrivilegedActivationStatus
    revoked_at: datetime | None

    revision: int
    previous_activation_fingerprint: str | None
    issuance_idempotency_key: str

    def __post_init__(self) -> None:
        """Validate and UTC-normalize the complete immutable authority fact."""
        for name in (
            "activation_id",
            "principal_id",
            "actor_principal_id",
            "privileged_role_id",
            "eligibility_evidence_id",
            "assurance_evidence_id",
            "issuance_idempotency_key",
        ):
            object.__setattr__(self, name, _identifier(name.upper(), getattr(self, name)))

        if self.actor_principal_id != self.principal_id:
            raise PrivilegedActivationError("SELF_ACTIVATION_REQUIRED")

        if not isinstance(self.target_class, PrivilegedTargetClass):
            raise PrivilegedActivationError("TARGET_CLASS_INVALID")

        if self.target_class is PrivilegedTargetClass.TENANT_PRIVILEGED:
            tenant = _identifier("TENANT_ID", self.tenant_id)
            object.__setattr__(self, "tenant_id", tenant)
        elif self.target_class is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT:
            if self.tenant_id is not None:
                raise PrivilegedActivationError("PLATFORM_SCOPE_TENANT_FORBIDDEN")
        else:  # pragma: no cover - enum closure is enforced above
            raise PrivilegedActivationError("TARGET_CLASS_INVALID")

        object.__setattr__(
            self,
            "eligibility_evidence_fingerprint",
            _fingerprint("ELIGIBILITY_EVIDENCE_FINGERPRINT", self.eligibility_evidence_fingerprint),
        )
        object.__setattr__(
            self,
            "assurance_evidence_fingerprint",
            _fingerprint("ASSURANCE_EVIDENCE_FINGERPRINT", self.assurance_evidence_fingerprint),
        )

        if (
            self.creation_assurance_purpose
            is not PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ):
            raise PrivilegedActivationError("CREATION_ASSURANCE_PURPOSE_INVALID")

        activated = _moment("ACTIVATED_AT", self.activated_at)
        effective_until = _moment("EFFECTIVE_UNTIL", self.effective_until)
        object.__setattr__(self, "activated_at", activated)
        object.__setattr__(self, "effective_until", effective_until)

        lifetime = effective_until - activated
        if lifetime <= timedelta(0) or lifetime > MAXIMUM_ACTIVATION_LIFETIME:
            raise PrivilegedActivationError("ACTIVATION_LIFETIME_INVALID")

        if not isinstance(self.status, PrivilegedActivationStatus):
            raise PrivilegedActivationError("STATUS_INVALID")

        revision = _revision(self.revision)
        if revision == 1:
            if self.previous_activation_fingerprint is not None:
                raise PrivilegedActivationError("INITIAL_PREVIOUS_FINGERPRINT_FORBIDDEN")
        else:
            _fingerprint("PREVIOUS_ACTIVATION_FINGERPRINT", self.previous_activation_fingerprint)

        if self.status is PrivilegedActivationStatus.ACTIVE:
            if self.revoked_at is not None or revision != 1:
                raise PrivilegedActivationError("ACTIVE_LIFECYCLE_INVALID")
        else:
            revoked = _moment("REVOKED_AT", self.revoked_at)
            if revoked < activated:
                raise PrivilegedActivationError("REVOKED_AT_INVALID")
            object.__setattr__(self, "revoked_at", revoked)
            if revision < 2:
                raise PrivilegedActivationError("REVOKED_REVISION_INVALID")

    @classmethod
    def issue(
        cls,
        *,
        activation_id: str,
        tenant_id: str | None,
        principal_id: str,
        actor_principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        eligibility_evidence_id: str,
        eligibility_evidence_fingerprint: str,
        assurance_evidence_id: str,
        assurance_evidence_fingerprint: str,
        creation_assurance_purpose: PrivilegedAssurancePurpose,
        activated_at: datetime,
        effective_until: datetime,
        issuance_idempotency_key: str,
    ) -> PrivilegedActivation:
        """Create revision one from explicit facts without reading authority.

        The caller must already have independently established current P2,
        current creation-purpose P3, and the dedicated issuance permission.
        """
        return cls(
            activation_id=activation_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            actor_principal_id=actor_principal_id,
            privileged_role_id=privileged_role_id,
            target_class=target_class,
            eligibility_evidence_id=eligibility_evidence_id,
            eligibility_evidence_fingerprint=eligibility_evidence_fingerprint,
            assurance_evidence_id=assurance_evidence_id,
            assurance_evidence_fingerprint=assurance_evidence_fingerprint,
            creation_assurance_purpose=creation_assurance_purpose,
            activated_at=activated_at,
            effective_until=effective_until,
            status=PrivilegedActivationStatus.ACTIVE,
            revoked_at=None,
            revision=1,
            previous_activation_fingerprint=None,
            issuance_idempotency_key=issuance_idempotency_key,
        )

    def revoke(self, *, revoked_at: datetime) -> PrivilegedActivation:
        """Return the sole terminal successor; resurrection is forbidden."""
        if self.status is not PrivilegedActivationStatus.ACTIVE:
            raise PrivilegedActivationError("ACTIVATION_NOT_ACTIVE")
        return replace(
            self,
            status=PrivilegedActivationStatus.REVOKED,
            revoked_at=revoked_at,
            revision=self.revision + 1,
            previous_activation_fingerprint=self.activation_fingerprint,
        )

    def is_current(
        self,
        *,
        at: datetime,
        tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
    ) -> bool:
        """Resolve exact-scope temporal currentness without authorizing use."""
        try:
            observed = _moment("AT", at)
            principal = _identifier("PRINCIPAL_ID", principal_id)
            role = _identifier("PRIVILEGED_ROLE_ID", privileged_role_id)
            if not isinstance(target_class, PrivilegedTargetClass):
                return False
            tenant = (
                _identifier("TENANT_ID", tenant_id)
                if target_class is PrivilegedTargetClass.TENANT_PRIVILEGED
                else tenant_id
            )
        except PrivilegedActivationError:
            return False

        return (
            self.status is PrivilegedActivationStatus.ACTIVE
            and tenant == self.tenant_id
            and principal == self.principal_id
            and role == self.privileged_role_id
            and target_class is self.target_class
            and self.activated_at <= observed < self.effective_until
        )

    def authority_payload(self) -> dict[str, object]:
        """Return deterministic secret-free semantics for persistence sealing."""
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "activation_id": self.activation_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "actor_principal_id": self.actor_principal_id,
            "privileged_role_id": self.privileged_role_id,
            "target_class": self.target_class.value,
            "eligibility_evidence_id": self.eligibility_evidence_id,
            "eligibility_evidence_fingerprint": self.eligibility_evidence_fingerprint,
            "assurance_evidence_id": self.assurance_evidence_id,
            "assurance_evidence_fingerprint": self.assurance_evidence_fingerprint,
            "creation_assurance_purpose": self.creation_assurance_purpose.value,
            "activated_at": self.activated_at.isoformat(timespec="microseconds"),
            "effective_until": self.effective_until.isoformat(timespec="microseconds"),
            "status": self.status.value,
            "revoked_at": None if self.revoked_at is None else self.revoked_at.isoformat(timespec="microseconds"),
            "revision": self.revision,
            "previous_activation_fingerprint": self.previous_activation_fingerprint,
            "issuance_idempotency_key": self.issuance_idempotency_key,
        }

    @property
    def activation_fingerprint(self) -> str:
        """Return lowercase SHA3-512 over all authority-bearing semantics."""
        canonical = json.dumps(
            self.authority_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        return sha3_512(canonical).hexdigest()

    def fingerprint_matches(self, candidate: object) -> bool:
        """Compare a candidate seal without timing-leaking a valid mismatch."""
        return (
            isinstance(candidate, str)
            and _SHA3_512.fullmatch(candidate) is not None
            and hmac.compare_digest(candidate, self.activation_fingerprint)
        )


__all__ = [
    "VERSION",
    "SCHEMA",
    "MAXIMUM_ACTIVATION_LIFETIME",
    "ISSUANCE_PERMISSION",
    "PrivilegedActivationError",
    "PrivilegedActivationStatus",
    "PrivilegedActivation",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_activation.py
# VERSION: v1.0.0-P4-R1-PRIVILEGED-ACTIVATION-DOMAIN
# AUTHORITY BOUNDARY: immutable normal activation facts only; no grant or use
# TENANT POSTURE: exact tenant/principal/role/target tuple; no wildcards
# LIFETIME: positive and at most 15 minutes; no extension or renewal
# LIFECYCLE: ACTIVE -> REVOKED only; immutable revision/fingerprint chain
# CURRENTNESS: half-open interval; revoked is never current
# P2/P3: evidence lineage only; no historic-currentness inference
# TTL / PERSISTENCE / HTTP: none
# BREAK GLASS: none; P7 remains separate
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# FAIL-CLOSED POSTURE: malformed, crossed, stale, expired, and revoked facts deny
# END OF WILSY OS SOVEREIGN ARTIFACT
