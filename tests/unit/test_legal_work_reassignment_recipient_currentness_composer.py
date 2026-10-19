"""TITLE: WILSY OS P9 Recipient Currentness Composer RED Certificate.
VERSION: v1.0.1-P9-R76R1-RECIPIENT-CURRENTNESS-RED
ARTIFACT: tests/unit/test_legal_work_reassignment_recipient_currentness_composer.py
AUTHORITY: Test-only transaction-bound canonical identity currentness.
EPITOME: Resolve exact principal and tenant membership in one active transaction.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_recipient_currentness_composer.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.1-P9-R76R1-RECIPIENT-CURRENTNESS-RED
    Corrects four broad exception assertions that masked missing code.
    2026-10-19 v1.0.0-P9-R76-RECIPIENT-CURRENTNESS-RED
    Establishes failure-first canonical-read and transaction test contracts.
TENANT BOUNDARY: Exact principal and principal/tenant membership pair.
AUTHORITY BOUNDARY: Read-time identity consistency only, not admission.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)


class Reader:
    def __init__(self, value: object = None, error: Exception | None = None):
        self.value = value
        self.error = error
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def resolve(self, *args: object, **kwargs: object) -> object:
        self.calls.append((args, kwargs))
        if self.error is not None:
            raise self.error
        return self.value


def _principal(
    status: PrincipalStatus = PrincipalStatus.ACTIVE,
    principal_id: str = "recipient-1",
) -> PrincipalAuthority:
    return PrincipalAuthority(principal_id, status, 7)


def _membership(
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    tenant_id: str = "tenant-1",
) -> TenantMembershipAuthority:
    return TenantMembershipAuthority(
        "recipient-1", tenant_id, status, 11
    )


PRINCIPAL_COLLECTION = object()
MEMBERSHIP_COLLECTION = object()


def _module():
    return import_module(
        "tools.eos.legal_operations.orchestration."
        "legal_work_reassignment_recipient_currentness_composer"
    )


def _invoke(
    *,
    tenant_id: str = "tenant-1",
    recipient_principal_id: str = "recipient-1",
    session: object = None,
    principal_reader: object = None,
    membership_reader: object = None,
) -> object:
    return _module().compose_recipient_currentness(
        tenant_id=tenant_id,
        recipient_principal_id=recipient_principal_id,
        session=session,
        principal_repository=principal_reader,
        membership_repository=membership_reader,
        principal_collection=PRINCIPAL_COLLECTION,
        membership_collection=MEMBERSHIP_COLLECTION,
    )


def _case(
    *,
    principal: object = None,
    membership: object = None,
    active: bool = True,
) -> tuple[object, Reader, Reader]:
    session = SimpleNamespace(in_transaction=active)
    return (
        session,
        Reader(_principal() if principal is None else principal),
        Reader(_membership() if membership is None else membership),
    )


def _composer_error():
    return _module().LegalWorkReassignmentRecipientCurrentnessError


def test_active_exact_reads_return_unchanged_canonical_snapshots() -> None:
    session, principal_reader, membership_reader = _case()
    result = _invoke(
        session=session,
        principal_reader=principal_reader,
        membership_reader=membership_reader,
    )
    assert result[0] is principal_reader.value
    assert result[1] is membership_reader.value
    assert result[0].revision == 7
    assert result[1].revision == 11
    assert principal_reader.calls == [
        (("recipient-1", PRINCIPAL_COLLECTION), {"session": session})
    ]
    assert membership_reader.calls == [
        (
            ("recipient-1", "tenant-1", MEMBERSHIP_COLLECTION),
            {"session": session},
        )
    ]


def test_missing_transaction_rejected_before_reads() -> None:
    _, principal_reader, membership_reader = _case()
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            session=None,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
        )
    assert not principal_reader.calls
    assert not membership_reader.calls


def test_inactive_transaction_rejected_before_reads() -> None:
    session, principal_reader, membership_reader = _case(active=False)
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
        )
    assert not principal_reader.calls
    assert not membership_reader.calls


def test_invalid_tenant_rejected_before_reads() -> None:
    session, principal_reader, membership_reader = _case()
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            tenant_id="default",
            session=session,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
        )
    assert not principal_reader.calls
    assert not membership_reader.calls


def test_inactive_principal_fails_closed() -> None:
    session, _, membership_reader = _case()
    error = _composer_error()
    principal_reader = Reader(_principal(PrincipalStatus.REVOKED))
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
        )


def test_inactive_membership_fails_closed() -> None:
    session, principal_reader, _ = _case()
    error = _composer_error()
    membership_reader = Reader(
        _membership(TenantMembershipStatus.SUSPENDED)
    )
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
        )


def test_foreign_tenant_membership_fails_closed() -> None:
    session, principal_reader, _ = _case()
    error = _composer_error()
    membership_reader = Reader(
        _membership(tenant_id="tenant-foreign")
    )
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
        )


def test_missing_principal_fails_closed() -> None:
    session, _, membership_reader = _case()
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=Reader(
                error=LookupError("PRINCIPAL_AUTHORITY_NOT_FOUND")
            ),
            membership_reader=membership_reader,
        )
    assert not membership_reader.calls


def test_missing_membership_fails_closed() -> None:
    session, principal_reader, _ = _case()
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=principal_reader,
            membership_reader=Reader(
                error=LookupError("TENANT_MEMBERSHIP_NOT_FOUND")
            ),
        )


def test_principal_repository_failure_fails_closed() -> None:
    session, _, membership_reader = _case()
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=Reader(error=RuntimeError("READ_FAILED")),
            membership_reader=membership_reader,
        )
    assert not membership_reader.calls


def test_membership_repository_failure_fails_closed() -> None:
    session, principal_reader, _ = _case()
    error = _composer_error()
    with pytest.raises(error):
        _invoke(
            session=session,
            principal_reader=principal_reader,
            membership_reader=Reader(error=RuntimeError("READ_FAILED")),
        )


def test_no_admission_execution_or_persistence_interface() -> None:
    module = _module()
    for name in (
        "execute_reassignment",
        "authorize_reassignment",
        "grant_matter_access",
        "approve_reassignment",
        "persist_reassignment",
        "issue_authorization",
    ):
        assert not hasattr(module, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_recipient_currentness_composer.py
# VERSION: v1.0.1-P9-R76R1-RECIPIENT-CURRENTNESS-RED
# AUTHORITY BOUNDARY: transaction-bound identity reads only
# RECIPIENT ADMISSION / MATTER ACCESS AUTHORITY: NONE
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
