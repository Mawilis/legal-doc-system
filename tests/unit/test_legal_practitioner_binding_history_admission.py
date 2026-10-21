"""TITLE: WILSY OS Practitioner Binding History Admission Contract.
VERSION: v1.0.0-P12C-R4N-P4C10-R3-ADMISSION-RED-CONTRACT
AUTHORITY: Negative-only test-first actor-to-matter disclosure admission.
EPITOME: Require exact canonical IAM, active transaction, own-tenant
    scope and independently established object disclosure authority.
ABSOLUTE CANONICAL PATH: tests/unit/test_legal_practitioner_binding_history_admission.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.0.0-P12C-R4N-P4C10-R3-ADMISSION-RED-CONTRACT
    Freezes negative admission conditions before production service exists.
SECURITY / PRIVACY POSTURE: No privileged data or content disclosure.
TENANT BOUNDARY: Exact actor, tenant and binding required.
AUTHORITY BOUNDARY: No evidence-only or caller-manufactured IAM admission.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""

from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.service.legal_practitioner_binding_history_disclosure_service import (
    PractitionerBindingHistoryDisclosureDenied,
    admit_practitioner_binding_history_read,
)

VERSION = "v1.0.0-P12C-R4N-P4C10-R3-ADMISSION-RED-CONTRACT"


def _invoke(
    *,
    actor: object = "actor-1",
    tenant: object = "tenant-1",
    binding: object = "binding-1",
    session: object = None,
) -> object:
    return admit_practitioner_binding_history_read(
        authenticated_principal_id=actor,
        tenant_id=tenant,
        binding_id=binding,
        principal_repository=None,
        membership_repository=None,
        business_role_repository=None,
        role_assignment_repository=None,
        matter_collection=None,
        binding_collection=None,
        wall_collection=None,
        practitioner_access_collection=None,
        session=session,
    )


def test_admission_interface_cannot_receive_preconstructed_iam_truth() -> None:
    params = inspect.signature(
        admit_practitioner_binding_history_read
    ).parameters
    required = {
        "authenticated_principal_id",
        "tenant_id",
        "binding_id",
        "principal_repository",
        "membership_repository",
        "business_role_repository",
        "role_assignment_repository",
        "matter_collection",
        "binding_collection",
        "wall_collection",
        "practitioner_access_collection",
        "session",
    }
    assert required <= set(params)
    assert "authorization_decision" not in params
    assert "iam_decision" not in params
    assert "authorized" not in params
    assert not any(
        p.kind is inspect.Parameter.VAR_KEYWORD
        for p in params.values()
    )


@pytest.mark.parametrize(
    "session",
    [
        None,
        SimpleNamespace(in_transaction=False),
    ],
    ids=["absent_transaction", "inactive_transaction"],
)
def test_absent_or_inactive_transaction_denies(session: object) -> None:
    with pytest.raises(PractitionerBindingHistoryDisclosureDenied):
        _invoke(session=session)


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("actor", ""),
        ("actor", " actor-1 "),
        ("actor", None),
        ("tenant", ""),
        ("tenant", " tenant-1 "),
        ("tenant", None),
        ("binding", ""),
        ("binding", " binding-1 "),
        ("binding", None),
    ],
)
def test_malformed_scope_never_admits(
    field: str,
    invalid: object,
) -> None:
    kwargs: dict[str, object] = {
        "actor": "actor-1",
        "tenant": "tenant-1",
        "binding": "binding-1",
        "session": SimpleNamespace(in_transaction=True),
    }
    kwargs[field] = invalid
    with pytest.raises(PractitionerBindingHistoryDisclosureDenied):
        _invoke(**kwargs)


def test_missing_canonical_repositories_never_admit() -> None:
    with pytest.raises(PractitionerBindingHistoryDisclosureDenied):
        _invoke(session=SimpleNamespace(in_transaction=True))


# ARTIFACT: test_legal_practitioner_binding_history_admission.py
# VERSION: v1.0.0-P12C-R4N-P4C10-R3-ADMISSION-RED-CONTRACT
# AUTHORITY BOUNDARY: negative-only test-first admission contract
# TENANT POSTURE: exact actor/tenant/matter scope required
# FAIL-CLOSED POSTURE: missing authority denies, never permits content
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
