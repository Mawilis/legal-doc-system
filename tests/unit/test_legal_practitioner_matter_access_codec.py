"""TITLE: WILSY OS Practitioner Matter Access Codec Certificate.
VERSION: v1.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-CERTIFICATE
AUTHORITY: Reproducible direct certificate for the immutable V1 evidence codec.
EPITOME: Freezes canonical bytes, integrity, validation order, immutability,
    domain separation and zero-authority behavior across hostile inputs.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_matter_access_codec.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; certifies the P47-R33
    domain and service codec without persistence, HTTP or IAM authority.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-CERTIFICATE
    Add deterministic vectors and adversarial construction/hydration coverage.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant values only; cross-tenant mutation invalidates.
AUTHORITY BOUNDARY: Tests documentary encoding only, never access or issuance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    EVIDENCE_VERSION,
    SCHEMA,
    LegalPractitionerMatterAccessDecision,
    LegalPractitionerMatterAccessError,
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    create_practitioner_matter_access,
    decode_practitioner_matter_access,
    encode_practitioner_matter_access,
    verify_practitioner_matter_access,
)


T0 = datetime(2026, 10, 19, 9, 0, tzinfo=timezone.utc)
SOURCE_FINGERPRINT = "a" * 128
ALLOW_VECTOR = (
    "bdf30ec90f91b1e540c700a0f144dfb9689a9578a6ccf9fa87c1e34916d4673a"
    "55aa9ccb177c96fb430eac165956f82d4a42a6036e07c27b26973b744a165c6e"
)
DENY_VECTOR = (
    "74fe22b75f82ace34f56cab313375487f471a7812b8191dda419fa0bcc272afcbd"
    "1f639824562c7f3fb755b8ce560abea12420cc235164259c8d4b071a1e18c0"
)


def _make(**changes: object) -> LegalPractitionerMatterAccessEvidence:
    values: dict[str, object] = {
        "access_evidence_id": "access-evidence-1",
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "practitioner-1",
        "revision": 1,
        "decision": LegalPractitionerMatterAccessDecision.ALLOW,
        "effective_from": T0,
        "effective_until": None,
        "issued_by_principal_id": "actor-1",
        "source_evidence_fingerprint": SOURCE_FINGERPRINT,
        "supersedes_fingerprint": None,
    }
    values.update(changes)
    return create_practitioner_matter_access(**values)


def _code(call: Callable[[], object]) -> str:
    with pytest.raises(LegalPractitionerMatterAccessError) as captured:
        call()
    return captured.value.code


def test_domain_is_state_only_and_has_no_public_constructor_or_codec_logic() -> None:
    domain_path = Path(
        "tools/eos/legal_operations/domain/legal_practitioner_matter_access.py"
    )
    tree = ast.parse(domain_path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imports.isdisjoint({"json", "hashlib", "re"})
    assert not hasattr(LegalPractitionerMatterAccessEvidence, "to_dict")
    assert not hasattr(LegalPractitionerMatterAccessEvidence, "from_dict")
    with pytest.raises(TypeError):
        LegalPractitionerMatterAccessEvidence()  # type: ignore[call-arg]


def test_allow_and_deny_golden_vectors_are_byte_stable() -> None:
    allow = _make()
    deny = _make(
        revision=2,
        decision=LegalPractitionerMatterAccessDecision.DENY,
        effective_from=T0 + timedelta(days=1),
        supersedes_fingerprint=allow.fingerprint,
    )
    assert allow.fingerprint == ALLOW_VECTOR
    assert deny.fingerprint == DENY_VECTOR
    assert len(encode_practitioner_matter_access(allow)) == 14
    assert encode_practitioner_matter_access(allow)["schema"] == SCHEMA
    assert (
        encode_practitioner_matter_access(allow)["evidence_version"]
        == EVIDENCE_VERSION
    )


def test_round_trip_normalizes_timezone_and_unicode_without_ascii_escaping() -> None:
    offset = timezone(timedelta(hours=2))
    value = _make(
        access_evidence_id="toegang-Ω",
        effective_from=datetime(2026, 10, 19, 11, 0, tzinfo=offset),
        effective_until=datetime(2026, 10, 20, 11, 0, tzinfo=offset),
    )
    payload = encode_practitioner_matter_access(value)
    assert payload["access_evidence_id"] == "toegang-Ω"
    assert payload["effective_from"] == "2026-10-19T09:00:00+00:00"
    assert decode_practitioner_matter_access(payload) == value
    assert verify_practitioner_matter_access(value) == value


def test_evidence_is_frozen_and_forged_state_fails_reverification() -> None:
    value = _make()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.tenant_id = "tenant-2"  # type: ignore[misc]
    object.__setattr__(value, "tenant_id", "tenant-2")
    assert _code(lambda: verify_practitioner_matter_access(value)) == (
        "P9_R84_FINGERPRINT_MISMATCH"
    )


@pytest.mark.parametrize("revision", [True, False, 0, -1, 1.0, "1", None])
def test_revision_rejects_booleans_boundaries_and_wrong_types(
    revision: object,
) -> None:
    assert _code(lambda: _make(revision=revision)) == "P9_R84_REVISION_INVALID"


@pytest.mark.parametrize("tenant", ["", " ", "default", "GLOBAL", "root", "*"])
def test_tenant_identity_fails_closed(tenant: object) -> None:
    assert _code(lambda: _make(tenant_id=tenant)) == "P9_R84_TENANT_ID_INVALID"


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"case_matter_id": " matter"}, "P9_R84_CASE_MATTER_ID_INVALID"),
        ({"practitioner_principal_id": True}, "P9_R84_PRACTITIONER_PRINCIPAL_ID_INVALID"),
        ({"issued_by_principal_id": "actor\n"}, "P9_R84_ISSUED_BY_PRINCIPAL_ID_INVALID"),
        ({"source_evidence_fingerprint": "A" * 128}, "P9_R84_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
        ({"decision": "ALLOW"}, "P9_R84_DECISION_INVALID"),
        ({"effective_from": T0.replace(tzinfo=None)}, "P9_R84_EFFECTIVE_FROM_INVALID"),
        ({"effective_until": T0}, "P9_R84_EFFECTIVE_INTERVAL_INVALID"),
        ({"schema": "V2"}, "P9_R84_SCHEMA_VERSION_INVALID"),
        ({"evidence_version": "v2"}, "P9_R84_SCHEMA_VERSION_INVALID"),
        ({"revision": 1, "supersedes_fingerprint": SOURCE_FINGERPRINT}, "P9_R84_FIRST_REVISION_PREDECESSOR_FORBIDDEN"),
        ({"revision": 2, "supersedes_fingerprint": None}, "P9_R84_LATER_REVISION_PREDECESSOR_REQUIRED"),
    ],
)
def test_factory_preserves_stable_fail_closed_codes(
    changes: dict[str, object], expected: str
) -> None:
    assert _code(lambda: _make(**changes)) == expected


def test_hydration_rejects_unknown_missing_forged_and_cross_tenant_documents() -> None:
    payload = encode_practitioner_matter_access(_make())
    extra = {**payload, "self_authorized": True}
    missing = dict(payload)
    missing.pop("case_matter_id")
    forged = {**payload, "fingerprint": "0" * 128}
    cross_tenant = {**payload, "tenant_id": "tenant-2"}
    absent_fingerprint = dict(payload)
    absent_fingerprint.pop("fingerprint")
    for invalid in (extra, missing, absent_fingerprint):
        assert _code(lambda invalid=invalid: decode_practitioner_matter_access(invalid)) == (
            "P9_R84_PERSISTED_SHAPE_INVALID"
        )
    assert _code(lambda: decode_practitioner_matter_access(forged)) == (
        "P9_R84_FINGERPRINT_MISMATCH"
    )
    assert _code(lambda: decode_practitioner_matter_access(cross_tenant)) == (
        "P9_R84_FINGERPRINT_MISMATCH"
    )


def test_validation_order_is_stable_for_multi_fault_documents() -> None:
    payload = encode_practitioner_matter_access(_make())
    payload.update({"decision": "UNKNOWN", "fingerprint": "x"})
    assert _code(lambda: decode_practitioner_matter_access(payload)) == (
        "P9_R84_DECISION_INVALID"
    )
    payload = encode_practitioner_matter_access(_make())
    payload.update({"fingerprint": "x", "effective_from": 7})
    assert _code(lambda: decode_practitioner_matter_access(payload)) == (
        "P9_R84_FINGERPRINT_INVALID"
    )


def test_no_authorization_or_execution_interface_is_exported() -> None:
    import tools.eos.legal_operations.service.legal_practitioner_matter_access_codec as codec

    for name in (
        "grant_matter_access",
        "authorize_matter_access",
        "issue_access_permission",
        "override_ethical_wall",
        "authorize_reassignment",
        "execute_reassignment",
        "execute_payment",
        "settle_payment",
    ):
        assert not hasattr(codec, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_codec.py
# VERSION: v1.0.0-P47-R33-PRACTITIONER-ACCESS-CODEC-CERTIFICATE
# AUTHORITY BOUNDARY: DIRECT CODEC/DOMAIN VERIFICATION ONLY
# TENANT POSTURE: EXACT VALUES AND CROSS-TENANT TAMPER REJECTION
# FAIL-CLOSED POSTURE: HOSTILE SHAPE, TYPE, TIME AND INTEGRITY INPUTS REJECT
# ACCESS / ISSUANCE / ETHICAL-WALL / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
