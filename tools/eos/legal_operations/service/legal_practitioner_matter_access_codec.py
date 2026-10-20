"""TITLE: WILSY OS Practitioner Matter Access Evidence Codec and Factory.
VERSION: v2.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-FACTORY
AUTHORITY: Python EOS Legal Operations evidence construction and codec only.
EPITOME: Exclusively validates, normalizes, hashes, materializes, serializes
    and hydrates the frozen V1 practitioner/matter access evidence contract.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_practitioner_matter_access_codec.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; registries, currentness
    projection and provisioning consume this service-owned trust boundary.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v2.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-FACTORY
    Add exclusive verified construction, exact V1 normalization, deterministic
    SHA3-512 integrity, canonical serialization and strict hydration.
    2026-10-20 v1.0.0-P47-R30-PRACTITIONER-ACCESS-CODEC
    Established codec parity with the pre-separation domain implementation.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exact field allowlist, strict types, UTC
    normalization and constant deterministic material; rejected data is not logged.
TENANT BOUNDARY: Exact non-pseudo tenant, matter and practitioner identity.
AUTHORITY BOUNDARY: Documentary evidence construction and integrity only;
    no issuance, affirmative access, ethical-wall, IAM, approval or reassignment.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from hashlib import sha3_512
import json
import re
from typing import Final, cast

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    EVIDENCE_VERSION,
    SCHEMA,
    LegalPractitionerMatterAccessDecision,
    LegalPractitionerMatterAccessError,
    LegalPractitionerMatterAccessEvidence,
)


CODEC_VERSION: Final[str] = (
    "v2.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-FACTORY"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)
_FIELDS: Final[frozenset[str]] = frozenset({
    "access_evidence_id",
    "tenant_id",
    "case_matter_id",
    "practitioner_principal_id",
    "revision",
    "decision",
    "effective_from",
    "effective_until",
    "issued_by_principal_id",
    "source_evidence_fingerprint",
    "supersedes_fingerprint",
    "schema",
    "evidence_version",
    "fingerprint",
})


def _fail(code: str) -> None:
    raise LegalPractitionerMatterAccessError(code)


def _identity(name: str, value: object, limit: int = 200) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 33 or ord(character) == 127 for character in value)
    ):
        _fail("P9_R84_" + name.upper() + "_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value, 160)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P9_R84_TENANT_ID_INVALID")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        _fail("P9_R84_" + name.upper() + "_INVALID")
    return cast(str, value)


def _timestamp(name: str, value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail("P9_R84_" + name.upper() + "_INVALID")
    return cast(datetime, value).astimezone(timezone.utc)


def _parse_timestamp(name: str, value: object) -> datetime:
    if type(value) is not str:
        _fail("P9_R84_" + name.upper() + "_INVALID")
    try:
        parsed = datetime.fromisoformat(cast(str, value))
    except ValueError:
        _fail("P9_R84_" + name.upper() + "_INVALID")
        raise AssertionError("unreachable")
    return _timestamp(name, parsed)


def _material_from_values(
    *,
    access_evidence_id: str,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    revision: int,
    decision: LegalPractitionerMatterAccessDecision,
    effective_from: datetime,
    effective_until: datetime | None,
    issued_by_principal_id: str,
    source_evidence_fingerprint: str,
    supersedes_fingerprint: str | None,
    schema: str,
    evidence_version: str,
) -> dict[str, object]:
    return {
        "access_evidence_id": access_evidence_id,
        "tenant_id": tenant_id,
        "case_matter_id": case_matter_id,
        "practitioner_principal_id": practitioner_principal_id,
        "revision": revision,
        "decision": decision.value,
        "effective_from": effective_from.isoformat(),
        "effective_until": (
            None if effective_until is None else effective_until.isoformat()
        ),
        "issued_by_principal_id": issued_by_principal_id,
        "source_evidence_fingerprint": source_evidence_fingerprint,
        "supersedes_fingerprint": supersedes_fingerprint,
        "schema": schema,
        "evidence_version": evidence_version,
    }


def _material(
    evidence: LegalPractitionerMatterAccessEvidence,
) -> dict[str, object]:
    if type(evidence) is not LegalPractitionerMatterAccessEvidence:
        _fail("P9_R84_PERSISTED_SHAPE_INVALID")
    return _material_from_values(
        access_evidence_id=evidence.access_evidence_id,
        tenant_id=evidence.tenant_id,
        case_matter_id=evidence.case_matter_id,
        practitioner_principal_id=evidence.practitioner_principal_id,
        revision=evidence.revision,
        decision=evidence.decision,
        effective_from=evidence.effective_from,
        effective_until=evidence.effective_until,
        issued_by_principal_id=evidence.issued_by_principal_id,
        source_evidence_fingerprint=evidence.source_evidence_fingerprint,
        supersedes_fingerprint=evidence.supersedes_fingerprint,
        schema=evidence.schema,
        evidence_version=evidence.evidence_version,
    )


def _digest(payload: Mapping[str, object]) -> str:
    try:
        encoded = json.dumps(
            dict(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise LegalPractitionerMatterAccessError(
            "P9_R84_PERSISTED_SHAPE_INVALID"
        ) from error
    return sha3_512(encoded).hexdigest()


def _materialize(
    material: Mapping[str, object],
    fingerprint: str,
) -> LegalPractitionerMatterAccessEvidence:
    evidence = object.__new__(LegalPractitionerMatterAccessEvidence)
    for name, value in material.items():
        if name == "decision":
            value = LegalPractitionerMatterAccessDecision(value)
        elif name in {"effective_from", "effective_until"} and value is not None:
            value = datetime.fromisoformat(cast(str, value))
        object.__setattr__(evidence, name, value)
    object.__setattr__(evidence, "fingerprint", fingerprint)
    return evidence


def create_practitioner_matter_access(
    *,
    access_evidence_id: object,
    tenant_id: object,
    case_matter_id: object,
    practitioner_principal_id: object,
    revision: object,
    decision: object,
    effective_from: object,
    effective_until: object,
    issued_by_principal_id: object,
    source_evidence_fingerprint: object,
    supersedes_fingerprint: object,
    schema: object = SCHEMA,
    evidence_version: object = EVIDENCE_VERSION,
    fingerprint: object = "",
) -> LegalPractitionerMatterAccessEvidence:
    """Create verified immutable evidence without granting operational access.

    The factory owns validation order, UTC normalization and SHA3-512. A supplied
    persisted fingerprint is verified against normalized canonical material and
    is never accepted as construction authority. This function performs no I/O,
    persistence, transaction management, IAM decision or policy issuance.
    """
    normalized_access_id = _identity("access_evidence_id", access_evidence_id)
    normalized_tenant = _tenant(tenant_id)
    normalized_matter = _identity("case_matter_id", case_matter_id)
    normalized_practitioner = _identity(
        "practitioner_principal_id", practitioner_principal_id
    )
    normalized_issuer = _identity("issued_by_principal_id", issued_by_principal_id)
    normalized_source = _fingerprint(
        "source_evidence_fingerprint", source_evidence_fingerprint
    )
    normalized_start = _timestamp("effective_from", effective_from)
    normalized_until = (
        None
        if effective_until is None
        else _timestamp("effective_until", effective_until)
    )

    if type(revision) is not int or revision < 1:
        _fail("P9_R84_REVISION_INVALID")
    if type(decision) is not LegalPractitionerMatterAccessDecision:
        _fail("P9_R84_DECISION_INVALID")
    normalized_revision = cast(int, revision)
    normalized_decision = cast(LegalPractitionerMatterAccessDecision, decision)
    if schema != SCHEMA or evidence_version != EVIDENCE_VERSION:
        _fail("P9_R84_SCHEMA_VERSION_INVALID")

    predecessor = (
        None
        if supersedes_fingerprint is None
        else _fingerprint("supersedes_fingerprint", supersedes_fingerprint)
    )
    if normalized_revision == 1 and predecessor is not None:
        _fail("P9_R84_FIRST_REVISION_PREDECESSOR_FORBIDDEN")
    if normalized_revision > 1 and predecessor is None:
        _fail("P9_R84_LATER_REVISION_PREDECESSOR_REQUIRED")
    if normalized_until is not None and normalized_until <= normalized_start:
        _fail("P9_R84_EFFECTIVE_INTERVAL_INVALID")

    material = _material_from_values(
        access_evidence_id=normalized_access_id,
        tenant_id=normalized_tenant,
        case_matter_id=normalized_matter,
        practitioner_principal_id=normalized_practitioner,
        revision=normalized_revision,
        decision=normalized_decision,
        effective_from=normalized_start,
        effective_until=normalized_until,
        issued_by_principal_id=normalized_issuer,
        source_evidence_fingerprint=normalized_source,
        supersedes_fingerprint=predecessor,
        schema=cast(str, schema),
        evidence_version=cast(str, evidence_version),
    )
    computed = _digest(material)
    if fingerprint:
        if _fingerprint("fingerprint", fingerprint) != computed:
            _fail("P9_R84_FINGERPRINT_MISMATCH")
    elif type(fingerprint) is not str:
        _fail("P9_R84_FINGERPRINT_INVALID")
    return _materialize(material, computed)


def encode_practitioner_matter_access(
    evidence: LegalPractitionerMatterAccessEvidence,
) -> dict[str, object]:
    """Serialize and re-verify exact evidence without persistence authority.

    Frozen Python state is not assumed trustworthy: canonical material is
    reconstructed and its SHA3-512 digest must equal the stored fingerprint.
    """
    material = _material(evidence)
    computed = _digest(material)
    if _fingerprint("fingerprint", evidence.fingerprint) != computed:
        _fail("P9_R84_FINGERPRINT_MISMATCH")
    return {**material, "fingerprint": computed}


def decode_practitioner_matter_access(
    payload: Mapping[str, object],
) -> LegalPractitionerMatterAccessEvidence:
    """Hydrate exact persisted V1 evidence and reject absent or forged integrity.

    Unknown fields, missing fields, invalid chronology, noncanonical identity,
    schema drift and fingerprint mismatch fail closed. No persisted value can
    bootstrap, repair or authorize its own integrity.
    """
    if not isinstance(payload, Mapping):
        _fail("P9_R84_PERSISTED_SHAPE_INVALID")
    try:
        if set(payload) != _FIELDS:
            _fail("P9_R84_PERSISTED_SHAPE_INVALID")
    except Exception as error:
        raise LegalPractitionerMatterAccessError(
            "P9_R84_PERSISTED_SHAPE_INVALID"
        ) from error

    try:
        decision = LegalPractitionerMatterAccessDecision(payload["decision"])
    except (ValueError, TypeError):
        _fail("P9_R84_DECISION_INVALID")
        raise AssertionError("unreachable")

    supplied = _fingerprint("fingerprint", payload["fingerprint"])
    raw_until = payload["effective_until"]
    evidence = create_practitioner_matter_access(
        access_evidence_id=payload["access_evidence_id"],
        tenant_id=payload["tenant_id"],
        case_matter_id=payload["case_matter_id"],
        practitioner_principal_id=payload["practitioner_principal_id"],
        revision=payload["revision"],
        decision=decision,
        effective_from=_parse_timestamp(
            "effective_from", payload["effective_from"]
        ),
        effective_until=(
            None
            if raw_until is None
            else _parse_timestamp("effective_until", raw_until)
        ),
        issued_by_principal_id=payload["issued_by_principal_id"],
        source_evidence_fingerprint=payload["source_evidence_fingerprint"],
        supersedes_fingerprint=payload["supersedes_fingerprint"],
        schema=payload["schema"],
        evidence_version=payload["evidence_version"],
        fingerprint=supplied,
    )
    if encode_practitioner_matter_access(evidence) != dict(payload):
        _fail("P9_R84_PERSISTED_SHAPE_INVALID")
    return evidence


def verify_practitioner_matter_access(
    evidence: LegalPractitionerMatterAccessEvidence,
) -> LegalPractitionerMatterAccessEvidence:
    """Return a freshly verified immutable value for a boundary consumer.

    This is a pure integrity operation. It does not determine currentness,
    authorize access, own a transaction, persist evidence or issue policy.
    """
    return decode_practitioner_matter_access(
        encode_practitioner_matter_access(evidence)
    )


__all__ = [
    "CODEC_VERSION",
    "create_practitioner_matter_access",
    "encode_practitioner_matter_access",
    "decode_practitioner_matter_access",
    "verify_practitioner_matter_access",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_codec.py
# VERSION: v2.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-FACTORY
# AUTHORITY BOUNDARY: VERIFIED DOCUMENTARY EVIDENCE CODEC AND FACTORY ONLY
# TENANT POSTURE: EXACT NON-PSEUDO IDENTITY; NO INFERENCE OR REPAIR
# FAIL-CLOSED POSTURE: REJECT ABSENT, FORGED, UNKNOWN OR NONCANONICAL EVIDENCE
# ACCESS / ISSUANCE / ETHICAL-WALL / IAM / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
