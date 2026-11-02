"""Sheriff appointment evidence registry unit certificate.

TITLE: WILSY OS Sheriff Office Appointment Evidence Registry Certificate
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REGISTRY-UNIT-CERT
AUTHORITY: Synthetic tenant-scoped immutable registry behavior only.
EPITOME: Prove transaction, replay, lineage, overlap, currentness and isolation semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_office_appointment_authority_registry.py
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.sheriff_office_appointment_authority import (
    SheriffOfficeAppointmentAuthority,
)
from tools.eos.legal_operations.registry.sheriff_office_appointment_authority_registry import (
    SheriffOfficeAppointmentAuthorityRegistry,
    SheriffOfficeAppointmentConflictError,
    SheriffOfficeAppointmentNotFoundError,
    SheriffOfficeAppointmentPersistedRecordInvalidError,
    SheriffOfficeAppointmentTransactionRequiredError,
)

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)
TENANT = "tenant-sheriff-registry"
PRINCIPAL = "principal-sheriff"
OFFICE = "office-jhb"
DISTRICT = "district-jhb"


class _Cursor(list[dict[str, Any]]):
    def sort(self, key_or_list: Any, direction: int | None = None) -> "_Cursor":
        fields = (
            key_or_list
            if isinstance(key_or_list, list)
            else [(key_or_list, direction or 1)]
        )
        values = list(self)
        for key, order in reversed(fields):
            values.sort(key=lambda item: item[key], reverse=order < 0)
        return _Cursor(values)


class _Collection:
    def __init__(self) -> None:
        self.values: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, dict[str, Any]]] = []

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append((keys, kwargs))
        return str(kwargs.get("name", ""))

    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
        assert session.in_transaction
        return next(
            (
                dict(value)
                for value in self.values
                if all(value.get(key) == expected for key, expected in query.items())
            ),
            None,
        )

    def find(self, query: dict[str, Any], *, session: Any) -> _Cursor:
        assert session.in_transaction
        return _Cursor(
            [
                dict(value)
                for value in self.values
                if all(value.get(key) == expected for key, expected in query.items())
            ]
        )

    def insert_one(self, value: dict[str, Any], *, session: Any) -> None:
        assert session.in_transaction
        for existing in self.values:
            if (
                existing["tenant_id"] == value["tenant_id"]
                and existing["appointment_id"] == value["appointment_id"]
                and existing["revision"] == value["revision"]
            ):
                raise DuplicateKeyError("identity")
            if (
                existing["tenant_id"] == value["tenant_id"]
                and existing["fingerprint"] == value["fingerprint"]
            ):
                raise DuplicateKeyError("fingerprint")
        self.values.append(dict(value))


class _Session:
    in_transaction = True


def _registry() -> tuple[SheriffOfficeAppointmentAuthorityRegistry, _Collection]:
    collection = _Collection()
    return SheriffOfficeAppointmentAuthorityRegistry(collection), collection


def _authority(**overrides: object) -> SheriffOfficeAppointmentAuthority:
    values: dict[str, object] = {
        "tenant_id": TENANT,
        "appointment_id": "appointment-1",
        "revision": 1,
        "principal_id": PRINCIPAL,
        "sheriff_office_id": OFFICE,
        "district_id": DISTRICT,
        "appointment_kind": "PERMANENT",
        "appointment_instrument_reference": "gazette:notice-1",
        "appointment_instrument_fingerprint": "a" * 128,
        "office_scope_instrument_reference": "gazette:notice-1:schedule",
        "office_scope_instrument_fingerprint": "b" * 128,
        "fidelity_fund_certificate_reference": "sabfs:ffc-2026-1",
        "fidelity_fund_certificate_fingerprint": "c" * 128,
        "appointment_effective_from": NOW - timedelta(days=30),
        "appointment_effective_until": None,
        "certificate_valid_from": NOW - timedelta(days=5),
        "certificate_valid_until": NOW + timedelta(days=360),
        "verified_by_principal_id": "tenant-admin",
        "verified_at": NOW - timedelta(days=1),
        "supersedes_fingerprint": None,
    }
    values.update(overrides)
    return SheriffOfficeAppointmentAuthority(**values)  # type: ignore[arg-type]


def _successor(
    predecessor: SheriffOfficeAppointmentAuthority,
    *,
    revision: int = 2,
    effective_from: datetime = NOW + timedelta(minutes=1),
    **overrides: object,
) -> SheriffOfficeAppointmentAuthority:
    values: dict[str, object] = {
        "tenant_id": predecessor.tenant_id,
        "appointment_id": predecessor.appointment_id,
        "revision": revision,
        "principal_id": predecessor.principal_id,
        "sheriff_office_id": predecessor.sheriff_office_id,
        "district_id": predecessor.district_id,
        "appointment_kind": predecessor.appointment_kind,
        "appointment_instrument_reference": predecessor.appointment_instrument_reference,
        "appointment_instrument_fingerprint": predecessor.appointment_instrument_fingerprint,
        "office_scope_instrument_reference": predecessor.office_scope_instrument_reference,
        "office_scope_instrument_fingerprint": predecessor.office_scope_instrument_fingerprint,
        "fidelity_fund_certificate_reference": "sabfs:ffc-renewed",
        "fidelity_fund_certificate_fingerprint": "d" * 128,
        "appointment_effective_from": effective_from,
        "appointment_effective_until": None,
        "certificate_valid_from": effective_from,
        "certificate_valid_until": effective_from + timedelta(days=365),
        "verified_by_principal_id": "tenant-admin",
        "verified_at": effective_from,
        "supersedes_fingerprint": predecessor.fingerprint,
    }
    values.update(overrides)
    return SheriffOfficeAppointmentAuthority(**values)  # type: ignore[arg-type]


def test_every_read_and_write_requires_active_caller_transaction() -> None:
    registry, collection = _registry()
    inactive = type("Inactive", (), {"in_transaction": False})()

    with pytest.raises(
        SheriffOfficeAppointmentTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.get_history_if_any(TENANT, "appointment-1", session=inactive)

    with pytest.raises(
        SheriffOfficeAppointmentTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(_authority(), session=inactive)

    assert collection.values == []


def test_indexes_are_tenant_first_unique_and_never_ttl() -> None:
    registry, collection = _registry()
    registry.ensure_indexes()

    names = {options["name"] for _, options in collection.indexes}
    assert names == {
        "sheriff_office_appointment_identity_unique",
        "sheriff_office_appointment_fingerprint_unique",
        "sheriff_office_appointment_principal_currentness",
        "sheriff_office_appointment_office_currentness",
    }
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)
    assert collection.indexes[0][0][0] == ("tenant_id", 1)
    assert collection.indexes[0][1]["unique"] is True


def test_exact_create_and_exact_replay_return_same_immutable_fact() -> None:
    registry, collection = _registry()
    value = _authority()

    created = registry.create_or_replay(value, session=_Session())
    replayed = registry.create_or_replay(value, session=_Session())

    assert created == value
    assert replayed == value
    assert len(collection.values) == 1


def test_same_identity_with_divergent_content_fails_closed() -> None:
    registry, _ = _registry()
    value = _authority()
    registry.create_or_replay(value, session=_Session())

    divergent = _authority(
        fidelity_fund_certificate_reference="sabfs:other-certificate",
        fidelity_fund_certificate_fingerprint="d" * 128,
    )
    with pytest.raises(
        SheriffOfficeAppointmentConflictError,
        match="DIVERGENT_REPLAY",
    ):
        registry.create_or_replay(divergent, session=_Session())


def test_revision_gap_and_wrong_predecessor_reject() -> None:
    registry, _ = _registry()
    first = _authority()

    with pytest.raises(
        SheriffOfficeAppointmentConflictError,
        match="REVISION_GAP",
    ):
        registry.create_or_replay(
            _successor(first, revision=3),
            session=_Session(),
        )

    registry.create_or_replay(first, session=_Session())
    wrong = _successor(first, supersedes_fingerprint="e" * 128)
    with pytest.raises(
        SheriffOfficeAppointmentConflictError,
        match="PREDECESSOR_MISMATCH",
    ):
        registry.create_or_replay(wrong, session=_Session())


def test_successor_history_and_currentness_are_effective_dated() -> None:
    registry, _ = _registry()
    first = _authority()
    second = _successor(first)
    registry.create_or_replay(first, session=_Session())
    registry.create_or_replay(second, session=_Session())

    before = registry.list_current_for_principal(
        TENANT,
        PRINCIPAL,
        NOW,
        session=_Session(),
    )
    after = registry.list_current_for_principal(
        TENANT,
        PRINCIPAL,
        NOW + timedelta(minutes=1),
        session=_Session(),
    )
    history = registry.get_history(TENANT, first.appointment_id, session=_Session())

    assert before == (first,)
    assert after == (second,)
    assert history == (first, second)


def test_expired_latest_revision_does_not_resurrect_predecessor() -> None:
    registry, _ = _registry()
    first = _authority()
    revoked_at = NOW
    second = _successor(
        first,
        effective_from=NOW - timedelta(minutes=1),
        appointment_effective_until=revoked_at,
        certificate_valid_from=NOW - timedelta(days=2),
        certificate_valid_until=NOW + timedelta(days=2),
        verified_at=NOW - timedelta(minutes=1),
    )
    registry.create_or_replay(first, session=_Session())
    registry.create_or_replay(second, session=_Session())

    assert registry.list_current_for_principal(
        TENANT,
        PRINCIPAL,
        NOW,
        session=_Session(),
    ) == ()


def test_same_principal_can_hold_distinct_office_appointments() -> None:
    registry, _ = _registry()
    first = _authority()
    second = _authority(
        appointment_id="appointment-cape-town",
        sheriff_office_id="office-cpt",
        district_id="district-cpt",
        appointment_instrument_reference="gazette:notice-2",
        appointment_instrument_fingerprint="d" * 128,
        office_scope_instrument_reference="gazette:notice-2:schedule",
        office_scope_instrument_fingerprint="e" * 128,
        fidelity_fund_certificate_reference="sabfs:ffc-cape-town",
        fidelity_fund_certificate_fingerprint="f" * 128,
    )

    registry.create_or_replay(first, session=_Session())
    registry.create_or_replay(second, session=_Session())

    current = registry.list_current_for_principal(
        TENANT,
        PRINCIPAL,
        NOW,
        session=_Session(),
    )
    assert {item.sheriff_office_id for item in current} == {OFFICE, "office-cpt"}


def test_two_principals_may_be_appointed_to_same_office() -> None:
    registry, _ = _registry()
    first = _authority()
    second = _authority(
        appointment_id="appointment-second-sheriff",
        principal_id="principal-second-sheriff",
        appointment_instrument_reference="gazette:notice-3",
        appointment_instrument_fingerprint="d" * 128,
        office_scope_instrument_reference="gazette:notice-3:schedule",
        office_scope_instrument_fingerprint="e" * 128,
        fidelity_fund_certificate_reference="sabfs:ffc-2026-3",
        fidelity_fund_certificate_fingerprint="f" * 128,
    )

    registry.create_or_replay(first, session=_Session())
    registry.create_or_replay(second, session=_Session())

    current = registry.list_current_for_office(
        TENANT,
        OFFICE,
        NOW,
        session=_Session(),
    )
    assert {item.principal_id for item in current} == {
        PRINCIPAL,
        "principal-second-sheriff",
    }


def test_overlapping_appointment_family_for_same_principal_and_office_rejects() -> None:
    registry, _ = _registry()
    registry.create_or_replay(_authority(), session=_Session())
    overlapping = _authority(
        appointment_id="appointment-duplicate",
        appointment_instrument_reference="gazette:notice-duplicate",
        appointment_instrument_fingerprint="d" * 128,
        office_scope_instrument_reference="gazette:notice-duplicate:schedule",
        office_scope_instrument_fingerprint="e" * 128,
        fidelity_fund_certificate_reference="sabfs:ffc-duplicate",
        fidelity_fund_certificate_fingerprint="f" * 128,
    )

    with pytest.raises(
        SheriffOfficeAppointmentConflictError,
        match="PRINCIPAL_OFFICE_OVERLAP",
    ):
        registry.create_or_replay(overlapping, session=_Session())


def test_cross_tenant_lookup_is_ordinary_absence() -> None:
    registry, _ = _registry()
    registry.create_or_replay(_authority(), session=_Session())

    with pytest.raises(SheriffOfficeAppointmentNotFoundError):
        registry.get_revision(
            "foreign-tenant",
            "appointment-1",
            1,
            session=_Session(),
        )


def test_corrupt_persisted_scope_or_lineage_fails_closed() -> None:
    registry, collection = _registry()
    value = _authority()
    registry.create_or_replay(value, session=_Session())
    collection.values[0]["sheriff_office_id"] = "foreign-office"

    with pytest.raises(SheriffOfficeAppointmentPersistedRecordInvalidError):
        registry.get_history(TENANT, "appointment-1", session=_Session())


# ARTIFACT: test_sheriff_office_appointment_authority_registry.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: exact-tenant persistence and currentness only
# TENANT POSTURE: foreign tenant absence is non-disclosing
# FAIL-CLOSED POSTURE: transaction, replay, lineage, overlap and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
