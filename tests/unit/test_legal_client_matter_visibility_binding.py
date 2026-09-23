"""Direct certificate for the L8-7A legal-client matter visibility value.

TITLE: WILSY OS Legal Client Matter Visibility Binding Certificate
VERSION: v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING-CERT
AUTHORITY: Direct adversarial certification of immutable visibility relation evidence only.
EPITOME: Prove factory-only CaseMatter provenance, stable tenant/client/matter
         identity, deterministic SHA3-512 evidence, immutable ACTIVE -> REVOKED
         lifecycle, chronology and metadata rejection, and absence of IAM,
         lifecycle-command, service, billing, payment, settlement, persistence,
         network, or client-application authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_visibility_binding.py
COLLABORATION / OWNERSHIP: L8-7A domain binding is the sole production subject;
                            P1 CaseMatter supplies source provenance. Registry,
                            provisioning orchestration, IAM, HTTP/client policy,
                            and persistence remain outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING-CERT
           establishes direct proof for canonical grant derivation, stable
           binding identity, source-snapshot differentiation, immutable
           revocation, chronology and malformed-input rejection, forged-state
           rejection, deterministic serialization, and authority-surface absence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers/references only; no
                             credentials, customer data, document payloads,
                             provider secrets, payment data, or production PII.
TENANT BOUNDARY: Assertions require tenant/matter provenance to derive only from
                 exact P1 CaseMatter evidence; no caller tenant argument exists.
AUTHORITY BOUNDARY: Certificate only. Passing tests grant no client visibility,
                    IAM permission, HTTP access, mutation, service, or financial
                    authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Pure unit certificate; no database, session, transaction,
                      network, HTTP, provider, or filesystem mutation.
FAIL-CLOSED DECLARATION: Any malformed identity/evidence/time, non-canonical
                         matter, forged lifecycle metadata, chronology reversal,
                         repeat revocation, direct construction, or source drift
                         must reject rather than become visibility truth.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    IDENTITY_SCHEMA,
    SCHEMA,
    VERSION,
    LegalClientMatterVisibilityBinding,
    LegalClientMatterVisibilityBindingError,
    LegalClientMatterVisibilityStatus,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


BASE = datetime(2026, 9, 23, 18, 0, tzinfo=timezone.utc)
TENANT = "tenant-l8-7a"
CLIENT = "principal-client-l8-7a"
ACTOR = "principal-partner-l8-7a"


def matter() -> CaseMatter:
    """Return one canonical synthetic P1 matter."""
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id="matter-l8-7a",
        matter_reference="CASE-L8-7A",
        opened_at=BASE,
        evidence_reference="matter-registration-evidence",
    )


def binding() -> LegalClientMatterVisibilityBinding:
    """Return one canonical ACTIVE visibility relation."""
    return LegalClientMatterVisibilityBinding.grant(
        client_principal_id=CLIENT,
        case_matter=matter(),
        granted_by_principal_id=ACTOR,
        granted_at=BASE + timedelta(minutes=1),
        evidence_reference="client-visibility-grant",
    )


def assert_code(
    expected: str,
    operation: Any,
) -> None:
    """Assert one exact stable L8-7A failure code."""
    with pytest.raises(LegalClientMatterVisibilityBindingError) as error:
        operation()
    assert error.value.code == expected


def test_grant_is_factory_only_canonical_deterministic_and_immutable() -> None:
    """Grant derives exact P1 scope and no caller may documentary-construct it."""
    assert_code(
        "L8_7A_FACTORY_REQUIRED",
        lambda: LegalClientMatterVisibilityBinding(),
    )

    first = binding()
    second = binding()
    source = matter()

    assert first == second
    assert first.tenant_id == TENANT
    assert first.client_principal_id == CLIENT
    assert first.case_matter_id == source.case_matter_id
    assert first.source_case_matter_fingerprint == source.fingerprint
    assert first.granted_by_principal_id == ACTOR
    assert first.status is LegalClientMatterVisibilityStatus.ACTIVE
    assert first.revoked_by_principal_id is None
    assert first.revoked_at is None
    assert first.revocation_evidence_reference is None
    assert len(first.binding_identity) == 128
    assert len(first.fingerprint) == 128
    assert first.binding_identity == second.binding_identity
    assert first.fingerprint == second.fingerprint
    assert first.to_dict() == second.to_dict()

    with pytest.raises(FrozenInstanceError):
        first.client_principal_id = "principal-other"  # type: ignore[misc]


def test_binding_identity_is_relation_stable_while_source_snapshot_is_explicit() -> None:
    """The relation identity survives matter evolution without hiding source provenance."""
    opened = matter()
    closed = opened.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close",
        occurred_at=BASE + timedelta(hours=1),
    )

    active_from_open = LegalClientMatterVisibilityBinding.grant(
        client_principal_id=CLIENT,
        case_matter=opened,
        granted_by_principal_id=ACTOR,
        granted_at=BASE + timedelta(minutes=1),
        evidence_reference="grant-open",
    )
    active_from_closed = LegalClientMatterVisibilityBinding.grant(
        client_principal_id=CLIENT,
        case_matter=closed,
        granted_by_principal_id=ACTOR,
        granted_at=BASE + timedelta(hours=2),
        evidence_reference="grant-closed",
    )

    assert opened.fingerprint != closed.fingerprint
    assert (
        active_from_open.source_case_matter_fingerprint
        != active_from_closed.source_case_matter_fingerprint
    )
    assert active_from_open.binding_identity == active_from_closed.binding_identity
    assert active_from_open.fingerprint != active_from_closed.fingerprint


def test_revocation_is_monotonic_chronological_and_relation_stable() -> None:
    """ACTIVE may become REVOKED exactly once without mutating the source value."""
    active = binding()
    revoked = active.revoke(
        revoked_by_principal_id="principal-attorney-l8-7a",
        revoked_at=BASE + timedelta(minutes=5),
        evidence_reference="client-visibility-revocation",
    )

    assert active.status is LegalClientMatterVisibilityStatus.ACTIVE
    assert revoked.status is LegalClientMatterVisibilityStatus.REVOKED
    assert revoked.revoked_by_principal_id == "principal-attorney-l8-7a"
    assert revoked.revoked_at == BASE + timedelta(minutes=5)
    assert (
        revoked.revocation_evidence_reference
        == "client-visibility-revocation"
    )
    assert revoked.binding_identity == active.binding_identity
    assert revoked.fingerprint != active.fingerprint

    assert_code(
        "L8_7A_VISIBILITY_ALREADY_REVOKED",
        lambda: revoked.revoke(
            revoked_by_principal_id=ACTOR,
            revoked_at=BASE + timedelta(minutes=6),
            evidence_reference="repeat-revocation",
        ),
    )
    assert_code(
        "L8_7A_REVOCATION_CHRONOLOGY_INVALID",
        lambda: active.revoke(
            revoked_by_principal_id=ACTOR,
            revoked_at=BASE,
            evidence_reference="backdated-revocation",
        ),
    )


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("bad_client", "L8_7A_CLIENT_PRINCIPAL_ID_INVALID"),
        ("bad_actor", "L8_7A_GRANTED_BY_PRINCIPAL_ID_INVALID"),
        ("naive_time", "L8_7A_GRANTED_AT_INVALID"),
        ("blank_reference", "L8_7A_GRANT_EVIDENCE_REFERENCE_INVALID"),
        ("long_reference", "L8_7A_GRANT_EVIDENCE_REFERENCE_INVALID"),
    ],
)
def test_grant_rejects_malformed_caller_inputs(case: str, expected: str) -> None:
    """Malformed caller-controlled relation provenance fails before use."""
    kwargs: dict[str, object] = {
        "client_principal_id": CLIENT,
        "case_matter": matter(),
        "granted_by_principal_id": ACTOR,
        "granted_at": BASE + timedelta(minutes=1),
        "evidence_reference": "grant-evidence",
    }
    if case == "bad_client":
        kwargs["client_principal_id"] = " client "
    elif case == "bad_actor":
        kwargs["granted_by_principal_id"] = ""
    elif case == "naive_time":
        kwargs["granted_at"] = datetime(2026, 9, 23, 18, 1)
    elif case == "blank_reference":
        kwargs["evidence_reference"] = " "
    elif case == "long_reference":
        kwargs["evidence_reference"] = "x" * 513

    assert_code(
        expected,
        lambda: LegalClientMatterVisibilityBinding.grant(**kwargs),  # type: ignore[arg-type]
    )


def test_noncanonical_matter_and_forged_lifecycle_metadata_reject() -> None:
    """Only exact P1 CaseMatter evidence and coherent lifecycle shape are admissible."""
    assert_code(
        "L8_7A_CASE_MATTER_REQUIRED",
        lambda: LegalClientMatterVisibilityBinding.grant(
            client_principal_id=CLIENT,
            case_matter=object(),  # type: ignore[arg-type]
            granted_by_principal_id=ACTOR,
            granted_at=BASE + timedelta(minutes=1),
            evidence_reference="grant",
        ),
    )

    active = binding()
    forged = object.__new__(LegalClientMatterVisibilityBinding)
    for field_name in (
        "tenant_id",
        "client_principal_id",
        "case_matter_id",
        "source_case_matter_fingerprint",
        "granted_by_principal_id",
        "granted_at",
        "grant_evidence_reference",
    ):
        object.__setattr__(forged, field_name, getattr(active, field_name))
    object.__setattr__(
        forged,
        "status",
        LegalClientMatterVisibilityStatus.ACTIVE,
    )
    object.__setattr__(forged, "revoked_by_principal_id", ACTOR)
    object.__setattr__(forged, "revoked_at", BASE + timedelta(minutes=2))
    object.__setattr__(forged, "revocation_evidence_reference", "forged")

    assert_code(
        "L8_7A_ACTIVE_REVOCATION_METADATA_FORBIDDEN",
        forged._validate,  # noqa: SLF001 - adversarial direct value validation.
    )


def test_serialization_carries_only_visibility_evidence_not_authority() -> None:
    """The value exposes relation evidence without turning it into IAM/read truth."""
    payload = binding().to_dict()

    assert set(payload) == {
        "schema",
        "version",
        "binding_identity",
        "tenant_id",
        "client_principal_id",
        "case_matter_id",
        "source_case_matter_fingerprint",
        "granted_by_principal_id",
        "granted_at",
        "grant_evidence_reference",
        "status",
        "revoked_by_principal_id",
        "revoked_at",
        "revocation_evidence_reference",
        "fingerprint",
    }
    assert payload["schema"] == SCHEMA
    assert payload["version"] == VERSION
    assert IDENTITY_SCHEMA.startswith(
        "WILSY-LEGAL-OPERATIONS-CLIENT-MATTER-VISIBILITY"
    )

    forbidden = {
        "permission",
        "authorized",
        "role_id",
        "business_role",
        "instruction_id",
        "document_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
        "paid",
        "settled",
        "gps",
        "latitude",
        "longitude",
        "ai",
    }
    assert forbidden.isdisjoint(payload)


def test_source_has_no_persistence_transport_or_financial_execution_mechanisms() -> None:
    """AST locks L8-7A to a pure domain relation with no hidden I/O authority."""
    module = __import__(
        "tools.eos.legal_operations.domain.legal_client_matter_visibility_binding",
        fromlist=["VERSION"],
    )
    source = inspect.getsource(module)
    tree = ast.parse(source)

    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    names = {
        node.id.casefold()
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    for forbidden in (
        "pymongo",
        "requests",
        "httpx",
        "fastapi",
        "motor",
        "kennel",
        "billing",
        "payment",
        "settlement",
        "invoice",
    ):
        assert all(forbidden not in imported.casefold() for imported in imports)
        assert forbidden not in names

    assert "TODO" not in source
    assert "FIXME" not in source
    assert (
        "END OF WILSY OS SOVEREIGN ARTIFACT"
        in source
    )


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_visibility_binding.py
# VERSION: v1.0.0-L8-7A-LEGAL-CLIENT-MATTER-VISIBILITY-BINDING-CERT
# AUTHORITY BOUNDARY: direct immutable visibility-relation value certificate only
# TENANT POSTURE: exact P1 CaseMatter provenance and derived tenant/matter scope only
# FAIL-CLOSED POSTURE: malformed/provenance/lifecycle/chronology/authority drift must reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
