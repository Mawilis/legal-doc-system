"""WILSY OS — trusted exhaustive Legal Evidence provider coverage verification.

TITLE: Legal Evidence Provider Coverage Verification Service
VERSION: v1.3.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Traverse the separately certified provider coverage page seam from its
         service-owned origin to both terminal pages and issue one immutable,
         anti-fabrication coverage verification bound to the exact observation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_coverage_verification_service.py
COLLABORATION / OWNERSHIP: C4D6B owns non-authorizing page evidence. C4D6C-A
                            owns provider-specific page execution and opaque
                            continuation transport. C4D6C-B owns only trusted
                            exhaustive traversal and in-memory verification.
                            Ownership, disownership, orphan proof, retention,
                            legal hold, abort and deletion authority remain
                            explicitly outside this artifact.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: v1.3.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION hardens exact-service verification acceptance
           by recomputing the canonical aggregate fingerprint from the
           current sealed payload and checking count/tuple consistency.
           Post-issuance mutation therefore fails closed before any
           membership evidence can be consumed downstream.
           v1.2.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION exposes the exact sealed completed-object
           membership fingerprint through the exact issuing coverage service.
           This remains coverage-membership evidence only and adds no
           ownership, disownership, orphan, retention, legal-hold, abort,
           deletion, provider-mutation, persistence or financial authority.
           v1.1.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION introduces
           service-owned traversal from page_reference=None, exact page-scope
           validation, certified C4D6B fingerprint revalidation,
           continuation-cycle rejection, deterministic SHA3-512 aggregate evidence, completed-observation membership
           sealing and private-capability verification issuance.

AUTHORITY BOUNDARY
------------------
This service proves only that the exact injected C4D6B provider seam was
traversed from its origin to terminal continuation for both certified
enumeration kinds at one exact timestamp.

It does NOT prove:
- canonical ownership;
- durable disownership;
- orphan status;
- retention expiry;
- legal-hold release;
- abort authorization;
- deletion authorization;
- provider deletion execution;
- financial authority.

The caller cannot supply a starting continuation reference. Continuations are
accepted only when emitted by the immediately traversed provider page. Provider
or page failures propagate/fail closed. No persistence or provider mutation is
owned here.

Financial execution authority remains exclusively with Kennel EOS.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, cast

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)

VERSION: Final[str] = (
    "v1.3.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION"
)

_SHA3_512_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class LegalEvidenceProviderCoverageVerificationError(RuntimeError):
    """Raised when trusted coverage traversal cannot be certified."""


def _fail(code: str) -> None:
    raise LegalEvidenceProviderCoverageVerificationError(code)


def _utc(name: str, value: datetime) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"L10A2R_C4D6C_B_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _sha(name: str, value: str) -> str:
    if not isinstance(value, str) or _SHA3_512_RE.fullmatch(value) is None:
        _fail(f"L10A2R_C4D6C_B_{name.upper()}_INVALID")
    return value


def _completed_observation_membership_fingerprint(
    observation: LegalEvidenceCompletedObjectObservation,
) -> str:
    """Return a deterministic digest for one validated completed-object observation."""
    if type(observation) is not LegalEvidenceCompletedObjectObservation:
        _fail("L10A2R_C4D6C_B_COMPLETED_OBSERVATION_REQUIRED")

    observation.__post_init__()

    payload = {
        "content_length": observation.content_length,
        "last_modified_at": observation.last_modified_at.isoformat(),
        "object_version_reference": observation.object_version_reference,
        "observed_at": observation.observed_at.isoformat(),
        "provider_integrity_reference": observation.provider_integrity_reference,
        "provider_name": observation.provider_name,
        "storage_reference": observation.storage_reference,
        "tenant_id": observation.tenant_id,
        "write_intent_fingerprint": observation.write_intent_fingerprint,
        "write_intent_metadata_state": (
            observation.write_intent_metadata_state.value
        ),
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha3_512(encoded).hexdigest()


def _verification_fingerprint(
    *,
    tenant_id: str,
    tenant_scope_fingerprint: str,
    provider_name: str,
    observed_at: datetime,
    incomplete_page_fingerprints: tuple[str, ...],
    completed_page_fingerprints: tuple[str, ...],
    completed_observation_fingerprints: tuple[str, ...],
    incomplete_observation_count: int,
    completed_observation_count: int,
) -> str:
    payload = {
        "completed_observation_count": completed_observation_count,
        "completed_observation_fingerprints": completed_observation_fingerprints,
        "completed_page_fingerprints": completed_page_fingerprints,
        "incomplete_observation_count": incomplete_observation_count,
        "incomplete_page_fingerprints": incomplete_page_fingerprints,
        "observed_at": observed_at.isoformat(),
        "provider_name": provider_name,
        "tenant_id": tenant_id,
        "tenant_scope_fingerprint": tenant_scope_fingerprint,
        "verification_version": VERSION,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
    init=False,
)
class LegalEvidenceProviderCoverageVerification:
    """Service-issued proof of exact terminal traversal only.

    Public construction is forbidden. This value proves exhaustive traversal of
    both certified C4D6B enumeration kinds only for one service instance, tenant
    scope, provider and observed_at. It contains no ownership, disownership,
    orphan, retention, hold, abort or deletion authority.
    """

    tenant_id: str
    tenant_scope_fingerprint: str
    provider_name: str
    observed_at: datetime
    incomplete_page_count: int
    completed_page_count: int
    incomplete_observation_count: int
    completed_observation_count: int
    incomplete_page_fingerprints: tuple[str, ...]
    completed_page_fingerprints: tuple[str, ...]
    completed_observation_fingerprints: tuple[str, ...]
    fingerprint: str
    _issuer_capability: object

    def __init__(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        _fail(
            "L10A2R_C4D6C_B_COVERAGE_VERIFICATION_FACTORY_REQUIRED"
        )


class LegalEvidenceProviderCoverageVerificationService:
    """Trusted traversal owner for C4D6B provider page evidence only."""

    __slots__ = (
        "_provider",
        "_verification_capability",
    )

    def __init__(
        self,
        *,
        provider: LegalEvidenceProviderCoverageEnumerationPort,
    ) -> None:
        if provider is None:
            _fail("L10A2R_C4D6C_B_PROVIDER_REQUIRED")

        if not isinstance(
            provider,
            LegalEvidenceProviderCoverageEnumerationPort,
        ):
            _fail("L10A2R_C4D6C_B_PROVIDER_INVALID")

        self._provider = provider
        self._verification_capability = object()

    @staticmethod
    def _validate_page(
        *,
        page: LegalEvidenceProviderEnumerationPage,
        scope: LegalEvidenceProviderDiscoveryScope,
        provider_name: str,
        kind: LegalEvidenceProviderEnumerationKind,
        observed_at: datetime,
    ) -> None:
        if type(page) is not LegalEvidenceProviderEnumerationPage:
            _fail("L10A2R_C4D6C_B_PAGE_REQUIRED")

        # Re-run the certified C4D6B value contract before consuming any page
        # field as trusted coverage evidence. This independently revalidates
        # canonical scope/observation semantics and the page fingerprint
        # against the page's current payload, so post-construction mutation
        # cannot be promoted into C4D6C-B verification authority.
        page.__post_init__()

        if (
            page.tenant_id != scope.tenant_id
            or page.tenant_scope_fingerprint
            != scope.tenant_scope_fingerprint
            or page.provider_name != provider_name
            or page.enumeration_kind is not kind
            or page.observed_at != observed_at
        ):
            _fail("L10A2R_C4D6C_B_PAGE_SCOPE_MISMATCH")

        _sha("page_fingerprint", page.fingerprint)

    def _traverse(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        provider_name: str,
        kind: LegalEvidenceProviderEnumerationKind,
        observed_at: datetime,
    ) -> tuple[tuple[str, ...], int, tuple[str, ...]]:
        page_reference: str | None = None
        seen_references: set[str] = set()
        page_fingerprints: list[str] = []
        completed_observation_fingerprints: list[str] = []
        observation_count = 0

        while True:
            if kind is LegalEvidenceProviderEnumerationKind.INCOMPLETE_WRITE_SESSIONS:
                page = self._provider.list_incomplete_write_session_page(
                    scope,
                    observed_at=observed_at,
                    page_reference=page_reference,
                )
            else:
                page = self._provider.list_completed_object_version_page(
                    scope,
                    observed_at=observed_at,
                    page_reference=page_reference,
                )

            self._validate_page(
                page=page,
                scope=scope,
                provider_name=provider_name,
                kind=kind,
                observed_at=observed_at,
            )

            page_fingerprints.append(page.fingerprint)
            observation_count += len(page.observations)

            if (
                kind
                is LegalEvidenceProviderEnumerationKind.COMPLETED_OBJECT_VERSIONS
            ):
                for observation in page.observations:
                    if type(observation) is not LegalEvidenceCompletedObjectObservation:
                        _fail(
                            "L10A2R_C4D6C_B_COMPLETED_OBSERVATION_REQUIRED"
                        )
                    completed_observation_fingerprints.append(
                        _completed_observation_membership_fingerprint(
                            cast(
                                LegalEvidenceCompletedObjectObservation,
                                observation,
                            )
                        )
                    )

            next_reference = page.next_page_reference

            if next_reference is None:
                break

            if (
                not isinstance(next_reference, str)
                or not next_reference
            ):
                _fail("L10A2R_C4D6C_B_CONTINUATION_INVALID")

            if next_reference in seen_references:
                _fail("L10A2R_C4D6C_B_CONTINUATION_CYCLE")

            seen_references.add(next_reference)
            page_reference = next_reference

        return (
            tuple(page_fingerprints),
            observation_count,
            tuple(completed_observation_fingerprints),
        )

    def verify_coverage(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        provider_name: str,
        observed_at: datetime,
    ) -> LegalEvidenceProviderCoverageVerification:
        """Traverse both page kinds from service-owned origin to terminal pages."""

        if type(scope) is not LegalEvidenceProviderDiscoveryScope:
            _fail("L10A2R_C4D6C_B_SCOPE_REQUIRED")

        if (
            not isinstance(provider_name, str)
            or not provider_name
        ):
            _fail("L10A2R_C4D6C_B_PROVIDER_NAME_INVALID")

        observed = _utc(
            "observed_at",
            observed_at,
        )

        (
            incomplete_fingerprints,
            incomplete_count,
            incomplete_observation_fingerprints,
        ) = self._traverse(
            scope=scope,
            provider_name=provider_name,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .INCOMPLETE_WRITE_SESSIONS
            ),
            observed_at=observed,
        )

        (
            completed_fingerprints,
            completed_count,
            completed_observation_fingerprints,
        ) = self._traverse(
            scope=scope,
            provider_name=provider_name,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .COMPLETED_OBJECT_VERSIONS
            ),
            observed_at=observed,
        )

        if incomplete_observation_fingerprints:
            _fail(
                "L10A2R_C4D6C_B_INCOMPLETE_OBSERVATION_MEMBERSHIP_INVALID"
            )

        digest = _verification_fingerprint(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=provider_name,
            observed_at=observed,
            incomplete_page_fingerprints=incomplete_fingerprints,
            completed_page_fingerprints=completed_fingerprints,
            completed_observation_fingerprints=(
                completed_observation_fingerprints
            ),
            incomplete_observation_count=incomplete_count,
            completed_observation_count=completed_count,
        )

        verified = object.__new__(
            LegalEvidenceProviderCoverageVerification
        )

        object.__setattr__(
            verified,
            "tenant_id",
            scope.tenant_id,
        )
        object.__setattr__(
            verified,
            "tenant_scope_fingerprint",
            scope.tenant_scope_fingerprint,
        )
        object.__setattr__(
            verified,
            "provider_name",
            provider_name,
        )
        object.__setattr__(
            verified,
            "observed_at",
            observed,
        )
        object.__setattr__(
            verified,
            "incomplete_page_count",
            len(incomplete_fingerprints),
        )
        object.__setattr__(
            verified,
            "completed_page_count",
            len(completed_fingerprints),
        )
        object.__setattr__(
            verified,
            "incomplete_observation_count",
            incomplete_count,
        )
        object.__setattr__(
            verified,
            "completed_observation_count",
            completed_count,
        )
        object.__setattr__(
            verified,
            "incomplete_page_fingerprints",
            incomplete_fingerprints,
        )
        object.__setattr__(
            verified,
            "completed_page_fingerprints",
            completed_fingerprints,
        )
        object.__setattr__(
            verified,
            "completed_observation_fingerprints",
            completed_observation_fingerprints,
        )
        object.__setattr__(
            verified,
            "fingerprint",
            digest,
        )
        object.__setattr__(
            verified,
            "_issuer_capability",
            self._verification_capability,
        )

        return verified

    def completed_observation_membership_fingerprint(
        self,
        *,
        verified: object,
        observation: LegalEvidenceCompletedObjectObservation,
    ) -> str | None:
        """Return the exact sealed digest for one completed-object observation.

        Authority:
            Coverage-membership evidence only. This method does not prove
            ownership, disownership or orphan status and grants no retention,
            legal-hold, abort, deletion or provider-mutation authority.

        Tenant / provider scope:
            The verification must have been issued by this exact service
            instance. The observation is revalidated through the canonical
            C4D6C-B membership-fingerprint implementation.

        Mutation / transaction / idempotency:
            Pure read-only in-memory comparison. No provider IO, persistence,
            registry access, transaction lifecycle, clock access or replay
            authority exists here.

        Fail-closed behavior:
            Fabricated or cross-service verification, wrong observation type,
            invalid observation state, or absence from the sealed membership
            tuple returns None.

        Financial boundary:
            No billing, payment, execution or settlement authority. Kennel EOS
            remains the exclusive financial execution authority.
        """
        if not self.accepts_verification(
            verified
        ):
            return None

        if type(observation) is not LegalEvidenceCompletedObjectObservation:
            return None

        try:
            digest = _completed_observation_membership_fingerprint(
                observation
            )
        except (
            LegalEvidenceProviderCoverageVerificationError,
        ):
            return None

        assert type(verified) is LegalEvidenceProviderCoverageVerification

        for member in verified.completed_observation_fingerprints:
            if hmac.compare_digest(
                digest,
                member,
            ):
                return member

        return None

    def contains_completed_observation(
        self,
        *,
        verified: object,
        observation: LegalEvidenceCompletedObjectObservation,
    ) -> bool:
        """Return whether this service sealed the completed observation.

        This compatibility predicate delegates to the exact sealed-digest seam
        and creates no additional authority, persistence or provider mutation.
        """
        return (
            self.completed_observation_membership_fingerprint(
                verified=verified,
                observation=observation,
            )
            is not None
        )

    def accepts_verification(
        self,
        verified: object,
    ) -> bool:
        """Accept only an intact value issued by this exact service instance.

        The private capability proves issuance origin only. Before downstream
        consumption, the current payload is revalidated against the canonical
        aggregate fingerprint and count/tuple relationships. Post-construction
        mutation therefore fails closed.
        """
        if (
            type(verified)
            is not LegalEvidenceProviderCoverageVerification
        ):
            return False

        if (
            verified._issuer_capability
            is not self._verification_capability
        ):
            return False

        try:
            if (
                not isinstance(
                    verified.tenant_id,
                    str,
                )
                or not verified.tenant_id
                or not isinstance(
                    verified.tenant_scope_fingerprint,
                    str,
                )
                or _SHA3_512_RE.fullmatch(
                    verified.tenant_scope_fingerprint
                )
                is None
                or not isinstance(
                    verified.provider_name,
                    str,
                )
                or not verified.provider_name
                or not isinstance(
                    verified.observed_at,
                    datetime,
                )
                or verified.observed_at.tzinfo
                is None
                or verified.observed_at.utcoffset()
                is None
            ):
                return False

            counts = (
                verified.incomplete_page_count,
                verified.completed_page_count,
                verified.incomplete_observation_count,
                verified.completed_observation_count,
            )

            if any(
                not isinstance(
                    count,
                    int,
                )
                or isinstance(
                    count,
                    bool,
                )
                or count < 0
                for count in counts
            ):
                return False

            if (
                type(
                    verified.incomplete_page_fingerprints
                )
                is not tuple
                or type(
                    verified.completed_page_fingerprints
                )
                is not tuple
                or type(
                    verified.completed_observation_fingerprints
                )
                is not tuple
            ):
                return False

            fingerprint_groups = (
                verified.incomplete_page_fingerprints,
                verified.completed_page_fingerprints,
                verified.completed_observation_fingerprints,
            )

            if any(
                not isinstance(
                    fingerprint,
                    str,
                )
                or _SHA3_512_RE.fullmatch(
                    fingerprint
                )
                is None
                for group
                in fingerprint_groups
                for fingerprint
                in group
            ):
                return False

            if (
                verified.incomplete_page_count
                != len(
                    verified.incomplete_page_fingerprints
                )
                or verified.completed_page_count
                != len(
                    verified.completed_page_fingerprints
                )
                or verified.completed_observation_count
                != len(
                    verified.completed_observation_fingerprints
                )
            ):
                return False

            expected = _verification_fingerprint(
                tenant_id=verified.tenant_id,
                tenant_scope_fingerprint=(
                    verified.tenant_scope_fingerprint
                ),
                provider_name=verified.provider_name,
                observed_at=verified.observed_at,
                incomplete_page_fingerprints=(
                    verified.incomplete_page_fingerprints
                ),
                completed_page_fingerprints=(
                    verified.completed_page_fingerprints
                ),
                completed_observation_fingerprints=(
                    verified.completed_observation_fingerprints
                ),
                incomplete_observation_count=(
                    verified.incomplete_observation_count
                ),
                completed_observation_count=(
                    verified.completed_observation_count
                ),
            )
        except (
            AttributeError,
            TypeError,
            ValueError,
        ):
            return False

        return (
            isinstance(
                verified.fingerprint,
                str,
            )
            and hmac.compare_digest(
                verified.fingerprint,
                expected,
            )
        )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderCoverageVerification",
    "LegalEvidenceProviderCoverageVerificationError",
    "LegalEvidenceProviderCoverageVerificationService",
]


# ARTIFACT: legal_evidence_provider_coverage_verification_service.py
# VERSION: v1.3.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION
# AUTHORITY BOUNDARY: trusted exhaustive provider-page traversal evidence only
# START POSTURE: traversal always begins internally at page_reference=None
# TENANT POSTURE: every page must preserve exact tenant scope fingerprint
# TIME POSTURE: one exact observed_at is preserved across both traversals
# CONTINUATION POSTURE: emitted references only; repeated continuation fails closed
# COVERAGE POSTURE: terminal traversal proves coverage observation only
# OWNERSHIP POSTURE: no ownership or durable disownership authority
# ORPHAN POSTURE: no orphan proof or inference
# RETENTION / HOLD POSTURE: no retention or legal-hold authority
# DELETION POSTURE: no abort, delete authorization or provider deletion authority
# PERSISTENCE POSTURE: no durable state is created
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
