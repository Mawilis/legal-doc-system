from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.domain.legal_work_ethical_wall_membership_acknowledgement import (
    AcknowledgementState, MembershipState, WallAcknowledgementEvidence, WallMembershipEvidence,
)
from tools.eos.legal_operations.registry import legal_work_ethical_wall_membership_acknowledgement_registry as registry

NOW = datetime(2026, 10, 30, 10, 0, tzinfo=UTC)


class Session:
    in_transaction = True


class Cursor(list[dict[str, object]]):
    def sort(self, key: str, direction: int) -> "Cursor":
        return Cursor(sorted(self, key=lambda row: row[key], reverse=direction < 0))

    def limit(self, maximum: int) -> "Cursor":
        return Cursor(self[:maximum])


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []

    def create_index(self, keys: object, **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs.get("name", "index"))

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        assert session.in_transaction is True  # type: ignore[union-attr]
        return Cursor([dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())])

    def find_one(self, query: dict[str, object], *, session: object) -> dict[str, object] | None:
        rows = self.find(query, session=session)
        return rows[0] if rows else None

    def insert_one(self, document: dict[str, object], *, session: object) -> None:
        assert session.in_transaction is True  # type: ignore[union-attr]
        self.rows.append(dict(document))


def membership(**changes: object) -> WallMembershipEvidence:
    values: dict[str, object] = {
        "membership_id": "membership-a", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a", "policy_id": "wall-a",
        "policy_fingerprint": "1" * 128, "practitioner_principal_id": "practitioner-a",
        "state": MembershipState.INCLUDED, "effective_at": NOW,
        "expires_at": NOW + timedelta(days=3), "issuer_principal_id": "issuer-a",
        "issuer_authorization_reference": "issuer-auth-a",
        "issuer_authorization_fingerprint": "2" * 128,
        "evidence_reference": "membership-evidence-a", "evidence_fingerprint": "3" * 128,
    }
    values.update(changes)
    return WallMembershipEvidence(**values)  # type: ignore[arg-type]


def acknowledgement(**changes: object) -> WallAcknowledgementEvidence:
    values: dict[str, object] = {
        "acknowledgement_id": "ack-a", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a", "policy_id": "wall-a",
        "policy_fingerprint": "1" * 128, "practitioner_principal_id": "practitioner-a",
        "membership_fingerprint": "4" * 128, "state": AcknowledgementState.ACKNOWLEDGED,
        "acknowledged_by_principal_id": "practitioner-a",
        "independently_verified_by_principal_id": "verifier-a",
        "verification_authorization_reference": "verifier-auth-a",
        "verification_authorization_fingerprint": "5" * 128,
        "acknowledged_at": NOW, "expires_at": NOW + timedelta(days=1),
        "evidence_reference": "ack-evidence-a", "evidence_fingerprint": "6" * 128,
    }
    values.update(changes)
    return WallAcknowledgementEvidence(**values)  # type: ignore[arg-type]


def make_registry():
    memberships, acknowledgements = Collection(), Collection()
    return registry.WallMembershipAcknowledgementRegistry(memberships, acknowledgements), memberships, acknowledgements


def test_indexes_are_unique_and_no_ttl_or_duplicate_key_pattern():
    value, memberships, acknowledgements = make_registry()
    value.ensure_indexes()
    assert len(memberships.indexes) == 2
    assert len(acknowledgements.indexes) == 2
    assert all("expireAfterSeconds" not in options for _, options in memberships.indexes + acknowledgements.indexes)
    assert memberships.indexes[0][1]["unique"] is True
    assert acknowledgements.indexes[0][1]["unique"] is True


def test_append_and_exact_replay_are_idempotent_and_history_is_tenant_scoped():
    value, _, _ = make_registry()
    first = membership()
    assert value.append_membership(first, session=Session()) == first
    assert value.append_membership(first, session=Session()) == first
    assert value.list_membership_history("tenant-a", "matter-a", "wall-a", "practitioner-a", session=Session()) == (first,)
    assert value.list_membership_history("tenant-b", "matter-a", "wall-a", "practitioner-a", session=Session()) == ()


def test_divergent_replay_and_orphan_revision_reject():
    value, _, _ = make_registry()
    first = membership()
    value.append_membership(first, session=Session())
    with pytest.raises(registry.WallEvidenceConflict, match="DIVERGENT_REPLAY"):
        value.append_membership(membership(evidence_reference="different"), session=Session())
    with pytest.raises(registry.WallEvidenceConflict, match="STALE_REVISION"):
        value.append_membership(membership(revision=3, predecessor_fingerprint="f" * 128), session=Session())


def test_revocation_is_terminal_for_membership_and_acknowledgement():
    value, _, _ = make_registry()
    first = membership()
    value.append_membership(first, session=Session())
    revoked = membership(
        revision=2, predecessor_fingerprint=first.fingerprint,
        state=MembershipState.REVOKED, effective_at=NOW + timedelta(hours=1),
    )
    value.append_membership(revoked, session=Session())
    reopened = membership(
        revision=3, predecessor_fingerprint=revoked.fingerprint,
        effective_at=NOW + timedelta(hours=2),
    )
    with pytest.raises(registry.WallEvidenceConflict, match="TERMINAL_REVOKED"):
        value.append_membership(reopened, session=Session())


def test_acknowledgement_history_is_separate_and_transaction_bound():
    value, _, _ = make_registry()
    first = acknowledgement()
    assert value.append_acknowledgement(first, session=Session()) == first
    assert value.list_acknowledgement_history("tenant-a", "matter-a", "wall-a", "practitioner-a", session=Session()) == (first,)
    with pytest.raises(registry.WallEvidenceTransactionRequired):
        value.list_acknowledgement_history("tenant-a", "matter-a", "wall-a", "practitioner-a", session=SimpleNamespace(in_transaction=False))


def test_persisted_fingerprint_corruption_fails_closed():
    value, memberships, _ = make_registry()
    first = membership()
    value.append_membership(first, session=Session())
    memberships.rows[0]["fingerprint"] = "f" * 128
    with pytest.raises(registry.WallEvidencePersistedInvalid):
        value.list_membership_history("tenant-a", "matter-a", "wall-a", "practitioner-a", session=Session())
