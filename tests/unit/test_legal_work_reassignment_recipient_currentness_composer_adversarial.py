"""TITLE: WILSY OS P9 R78 Recipient Currentness Adversarial Certificate.
VERSION: v1.0.0-P9-R78-RECIPIENT-CURRENTNESS-ADVERSARIAL
ARTIFACT: test_legal_work_reassignment_recipient_currentness_composer_adversarial.py
AUTHORITY: Test-only verification of bounded transaction/currentness controls.
EPITOME: Prove R77 fails closed under dependency, transaction, substitution,
    corruption, call-order, authority-leakage, and interface attacks.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/
    test_legal_work_reassignment_recipient_currentness_composer_adversarial.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R78-RECIPIENT-CURRENTNESS-ADVERSARIAL
    Adds security-significant negative and exact-forwarding coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 controls.
SECURITY / PRIVACY POSTURE: Deterministic fakes only; no PII, logging or DB.
TENANT BOUNDARY: Exact tenant/principal identity and substitution rejection.
AUTHORITY BOUNDARY: Test evidence only; no admission, IAM or reassignment.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Callable

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.legal_operations.orchestration import (
    legal_work_reassignment_recipient_currentness_composer as subject,
)


class RecordingRepository:
    """Deterministic injected read seam with call evidence."""

    def __init__(
        self,
        value: object = None,
        error: Exception | None = None,
        events: list[str] | None = None,
        event: str = "read",
    ) -> None:
        self.value = value
        self.error = error
        self.events = events
        self.event = event
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def resolve(self, *args: object, **kwargs: object) -> object:
        """Record one exact read and return or raise the configured result."""
        self.calls.append((args, kwargs))
        if self.events is not None:
            self.events.append(self.event)
        if self.error is not None:
            raise self.error
        return self.value


class RaisingTransactionMarker:
    """Session double whose transaction marker cannot be evaluated."""

    @staticmethod
    def in_transaction() -> bool:
        """Represent an unavailable driver transaction marker."""
        raise RuntimeError("driver state unavailable")


class TruthyTransactionMarker:
    """Non-boolean truthy marker that must not establish a transaction."""

    def __bool__(self) -> bool:
        """Expose truthiness without the exact boolean authority required."""
        return True


PRINCIPAL_COLLECTION = object()
MEMBERSHIP_COLLECTION = object()


def _principal(principal_id: str = "recipient-1") -> PrincipalAuthority:
    return PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 7)


def _membership(
    principal_id: str = "recipient-1",
    tenant_id: str = "tenant-1",
) -> TenantMembershipAuthority:
    return TenantMembershipAuthority(
        principal_id,
        tenant_id,
        TenantMembershipStatus.ACTIVE,
        11,
    )


def _invoke(
    *,
    tenant_id: object = "tenant-1",
    recipient_principal_id: object = "recipient-1",
    session: object = None,
    principal_repository: object = None,
    membership_repository: object = None,
    principal_collection: object = PRINCIPAL_COLLECTION,
    membership_collection: object = MEMBERSHIP_COLLECTION,
) -> tuple[PrincipalAuthority, TenantMembershipAuthority]:
    return subject.compose_recipient_currentness(
        tenant_id=tenant_id,  # type: ignore[arg-type]
        recipient_principal_id=recipient_principal_id,  # type: ignore[arg-type]
        session=session,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        principal_collection=principal_collection,
        membership_collection=membership_collection,
    )


def _valid() -> tuple[object, RecordingRepository, RecordingRepository]:
    return (
        SimpleNamespace(in_transaction=True),
        RecordingRepository(_principal()),
        RecordingRepository(_membership()),
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (("principal", None), ("membership", None)),
)
def test_missing_collection_injection_fails_before_reads(
    field: str,
    value: object,
) -> None:
    session, principal, membership = _valid()
    kwargs = {f"{field}_collection": value}
    with pytest.raises(subject.LegalWorkReassignmentRecipientCurrentnessError):
        _invoke(
            session=session,
            principal_repository=principal,
            membership_repository=membership,
            **kwargs,
        )
    assert not principal.calls
    assert not membership.calls


@pytest.mark.parametrize("invalid", (None, object(), SimpleNamespace(resolve=1)))
def test_invalid_principal_repository_fails_before_reads(invalid: object) -> None:
    session, _, membership = _valid()
    with pytest.raises(subject.LegalWorkReassignmentRecipientCurrentnessError):
        _invoke(
            session=session,
            principal_repository=invalid,
            membership_repository=membership,
        )
    assert not membership.calls


@pytest.mark.parametrize("invalid", (None, object(), SimpleNamespace(resolve=1)))
def test_invalid_membership_repository_fails_before_reads(invalid: object) -> None:
    session, principal, _ = _valid()
    with pytest.raises(subject.LegalWorkReassignmentRecipientCurrentnessError):
        _invoke(
            session=session,
            principal_repository=principal,
            membership_repository=invalid,
        )
    assert not principal.calls


@pytest.mark.parametrize(
    "session",
    (
        SimpleNamespace(in_transaction=TruthyTransactionMarker()),
        RaisingTransactionMarker(),
        SimpleNamespace(in_transaction=lambda: False),
    ),
)
def test_false_malformed_or_raising_transaction_marker_blocks_all_reads(
    session: object,
) -> None:
    _, principal, membership = _valid()
    with pytest.raises(subject.LegalWorkReassignmentRecipientCurrentnessError):
        _invoke(
            session=session,
            principal_repository=principal,
            membership_repository=membership,
        )
    assert not principal.calls
    assert not membership.calls


@pytest.mark.parametrize(
    ("tenant_id", "recipient_id"),
    (
        ("tenant-1", "recipient-foreign"),
        ("tenant-foreign", "recipient-1"),
    ),
)
def test_requested_identity_substitution_fails_closed(
    tenant_id: str,
    recipient_id: str,
) -> None:
    session, _, _ = _valid()
    principal = RecordingRepository(_principal())
    membership = RecordingRepository(_membership())
    with pytest.raises(subject.LegalWorkReassignmentRecipientCurrentnessError):
        _invoke(
            tenant_id=tenant_id,
            recipient_principal_id=recipient_id,
            session=session,
            principal_repository=principal,
            membership_repository=membership,
        )


@pytest.mark.parametrize(
    ("principal_value", "membership_value"),
    (
        ({"principal_id": "recipient-1"}, _membership()),
        (_principal(), {"tenant_id": "tenant-1"}),
        (None, _membership()),
        (_principal(), None),
    ),
)
def test_corrupt_or_missing_snapshots_fail_with_bounded_error(
    principal_value: object,
    membership_value: object,
) -> None:
    session, _, _ = _valid()
    with pytest.raises(
        subject.LegalWorkReassignmentRecipientCurrentnessError
    ) as failure:
        _invoke(
            session=session,
            principal_repository=RecordingRepository(principal_value),
            membership_repository=RecordingRepository(membership_value),
        )
    assert str(failure.value).startswith("P9_R77_")
    assert "recipient-1" not in str(failure.value)
    assert "tenant-1" not in str(failure.value)


def test_principal_failure_prevents_membership_read_and_is_bounded() -> None:
    session, _, membership = _valid()
    with pytest.raises(
        subject.LegalWorkReassignmentRecipientCurrentnessError
    ) as failure:
        _invoke(
            session=session,
            principal_repository=RecordingRepository(
                error=Exception("sensitive recipient-1 tenant-1")
            ),
            membership_repository=membership,
        )
    assert not membership.calls
    assert str(failure.value) == "P9_R77_PRINCIPAL_AUTHORITY_UNAVAILABLE"


def test_exact_read_order_count_collections_and_session_identity() -> None:
    events: list[str] = []
    session = SimpleNamespace(in_transaction=lambda: True)
    principal = RecordingRepository(_principal(), events=events, event="principal")
    membership = RecordingRepository(
        _membership(), events=events, event="membership"
    )
    result = _invoke(
        session=session,
        principal_repository=principal,
        membership_repository=membership,
    )
    assert events == ["principal", "membership"]
    assert len(principal.calls) == len(membership.calls) == 1
    assert principal.calls[0] == (
        ("recipient-1", PRINCIPAL_COLLECTION),
        {"session": session},
    )
    assert membership.calls[0] == (
        ("recipient-1", "tenant-1", MEMBERSHIP_COLLECTION),
        {"session": session},
    )
    assert result == (_principal(), _membership())
    assert result[0] is principal.value
    assert result[1] is membership.value


def test_composer_exports_no_transaction_write_or_authority_surface() -> None:
    forbidden = (
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
        "insert",
        "update",
        "delete",
        "grant_permission",
        "grant_matter_access",
        "authorize_reassignment",
        "execute_reassignment",
        "persist_reassignment",
        "approve_reassignment",
    )
    for name in forbidden:
        assert not hasattr(subject, name)
    assert subject.__all__ == [
        "VERSION",
        "LegalWorkReassignmentRecipientCurrentnessError",
        "compose_recipient_currentness",
    ]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_recipient_currentness_composer_adversarial.py
# VERSION: v1.0.0-P9-R78-RECIPIENT-CURRENTNESS-ADVERSARIAL
# AUTHORITY BOUNDARY: adversarial unit evidence only
# TENANT POSTURE: exact tenant/principal substitution fails closed
# RECIPIENT ADMISSION / IAM / MATTER / APPROVAL AUTHORITY: NONE
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
