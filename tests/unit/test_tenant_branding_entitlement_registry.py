"""Direct certificate for the D21B2B tenant branding entitlement registry.

TITLE: Tenant Branding Entitlement Registry Direct Certificate
VERSION: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove immutable entitlement history, explicit exact-entitlement
         currentness, domain-derived lifecycle transitions, CAS/replay semantics,
         tenant isolation and caller-owned transaction enforcement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_entitlement_registry.py
COLLABORATION / OWNERSHIP: Direct in-memory certificate for D21B2B persistence.
                            Real-Mongo operational certification remains a
                            separate gate. D21B2 remains lifecycle authority.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-CERT establishes
           adversarial evidence for exact indexes, revision-zero creation,
           exact replay, stale replay rejection, legal transitions, transition
           replay, CAS races, transient transaction retry classification,
           corruption rejection and exact tenant isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic entitlement/evidence data and collection
                             doubles only; no credentials, assets or networks.
TENANT BOUNDARY: Every certified persistence/read path binds exact tenant and
                 entitlement identity; foreign reads are absence.
AUTHORITY BOUNDARY: D21B2B registry semantics only; no profile approval, asset
                    resolution, browser presentation, IAM or workspace access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.billing import tenant_branding_entitlement_registry as registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)


NOW = datetime(2026, 9, 25, 15, 0, tzinfo=timezone.utc)
FP = "a" * 128


class Session:
    """Minimal already-active caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor:
    """Bounded deterministic cursor double."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.limit_value: int | None = None

    def limit(self, value: int) -> "Cursor":
        self.limit_value = value
        return self

    def __iter__(self) -> Any:
        rows = self.rows
        if self.limit_value is not None:
            rows = rows[: self.limit_value]
        return iter(deepcopy(rows))


class TransientMongoError(PyMongoError):
    """Synthetic Mongo error carrying only the governed retry label."""

    def has_error_label(self, label: str) -> bool:
        return label == "TransientTransactionError"


class Collection:
    """Small Mongo-like collection double with exact unique-index behavior."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, Any]]] = []
        self.force_duplicate = False
        self.force_cas_miss = False
        self.transient_on_find = False
        self.transient_on_insert = False
        self.transient_on_update = False

    def with_options(self, **_: Any) -> "Collection":
        return self

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append({"key": list(keys), **kwargs})
        return str(kwargs["name"])

    @staticmethod
    def _match(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> Cursor:
        assert session is not None
        self.calls.append(("find", session, deepcopy(query)))
        if self.transient_on_find:
            self.transient_on_find = False
            raise TransientMongoError("transient read")
        return Cursor([row for row in self.rows if self._match(row, query)])

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> dict[str, Any] | None:
        assert session is not None
        row = next((row for row in self.rows if self._match(row, query)), None)
        return None if row is None else deepcopy(row)

    def _violates_unique(self, document: dict[str, Any]) -> bool:
        for index in self.indexes:
            if not index.get("unique"):
                continue
            keys = [name for name, _ in index["key"]]
            expected = tuple(document.get(name) for name in keys)
            if any(
                tuple(row.get(name) for name in keys) == expected
                for row in self.rows
            ):
                return True
        return False

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: object,
    ) -> object:
        assert session is not None
        self.calls.append(("insert_one", session, deepcopy(document)))
        if self.transient_on_insert:
            self.transient_on_insert = False
            raise TransientMongoError("transient insert")
        if self.force_duplicate:
            self.force_duplicate = False
            raise DuplicateKeyError("forced duplicate")
        if self._violates_unique(document):
            raise DuplicateKeyError("unique index")
        self.rows.append(deepcopy(document))
        return object()

    def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        *,
        session: object,
    ) -> object:
        assert session is not None
        self.calls.append(("update_one", session, deepcopy(query)))
        if self.transient_on_update:
            self.transient_on_update = False
            raise TransientMongoError("transient update")
        if self.force_cas_miss:
            self.force_cas_miss = False
            return type("Result", (), {"matched_count": 0})()
        for row in self.rows:
            if self._match(row, query):
                row.update(deepcopy(update["$set"]))
                return type("Result", (), {"matched_count": 1})()
        return type("Result", (), {"matched_count": 0})()


def pending(
    *,
    tenant_id: str = "tenant-a",
    entitlement_id: str = "branding-entitlement-a",
) -> TenantBrandingEntitlement:
    """Return one exact pending D21B2 entitlement."""
    return create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        branding_tier=TenantBrandingTier.PROFESSIONAL,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )


def active(value: TenantBrandingEntitlement) -> TenantBrandingEntitlement:
    """Derive one exact ACTIVE D21B2 revision."""
    return value.transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )


def collections() -> tuple[Collection, Collection]:
    """Return history/current doubles with the canonical index contract."""
    history, current = Collection(), Collection()
    registry.ensure_indexes(history, current)
    return history, current


def create(
    value: TenantBrandingEntitlement,
    history: Collection,
    current: Collection,
    session: Session,
) -> registry.TenantBrandingEntitlementPersistenceResult:
    """Persist one initial entitlement through the canonical API."""
    return registry.create_or_replay(
        value,
        history,
        current,
        session=session,
    )


def test_index_contract_is_exact_tenant_scoped_unique_and_has_no_ttl() -> None:
    """Exactly three deterministic unique indexes define D21B2B persistence."""
    history, current = collections()
    assert history.indexes == [
        {
            "key": [
                ("tenant_id", 1),
                ("entitlement_id", 1),
                ("lifecycle_revision", 1),
            ],
            "unique": True,
            "name": registry.HISTORY_REVISION_INDEX_NAME,
        },
        {
            "key": [("tenant_id", 1), ("entitlement_fingerprint", 1)],
            "unique": True,
            "name": registry.HISTORY_FINGERPRINT_INDEX_NAME,
        },
    ]
    assert current.indexes == [
        {
            "key": [("tenant_id", 1), ("entitlement_id", 1)],
            "unique": True,
            "name": registry.CURRENT_IDENTITY_INDEX_NAME,
        }
    ]
    assert not any("expireAfterSeconds" in item for item in history.indexes)
    assert not any("expireAfterSeconds" in item for item in current.indexes)


def test_every_operational_path_requires_active_caller_transaction() -> None:
    """Registry cannot silently own or omit the caller transaction."""
    value = pending()
    history, current = collections()
    for bad_session in (None, Session(False)):
        with pytest.raises(
            registry.TenantBrandingEntitlementRegistryTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                history,
                current,
                session=bad_session,
            )
        with pytest.raises(
            registry.TenantBrandingEntitlementRegistryTransactionRequiredError
        ):
            registry.get_current(
                value.tenant_id,
                value.entitlement_id,
                history,
                current,
                session=bad_session,
            )
    assert not any(
        name in dir(registry.TenantBrandingEntitlementRegistry)
        for name in (
            "start_transaction",
            "commit_transaction",
            "abort_transaction",
            "with_transaction",
        )
    )


def test_revision_zero_create_exact_replay_and_session_propagation() -> None:
    """Initial pending evidence persists once and exact replay is idempotent."""
    value = pending()
    history, current = collections()
    session = Session()
    first = create(value, history, current, session)
    replay = create(value, history, current, session)
    assert first.outcome is registry.TenantBrandingEntitlementPersistenceOutcome.CREATED
    assert (
        replay.outcome
        is registry.TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY
    )
    assert first.entitlement == replay.entitlement == value
    assert len(history.rows) == 1
    assert len(current.rows) == 1
    assert all(call[1] is session for call in history.calls + current.calls)


def test_create_rejects_noninitial_or_nonpending_evidence() -> None:
    """Caller cannot inject a pre-transitioned lifecycle snapshot as initial."""
    value = pending()
    activated = active(value)
    history, current = collections()
    session = Session()
    with pytest.raises(registry.TenantBrandingEntitlementRegistryInputError):
        create(activated, history, current, session)


def test_current_read_is_exact_and_cross_tenant_absence_is_silent() -> None:
    """Exact tenant/entitlement currentness hydrates; foreign scope is absent."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)
    assert (
        registry.get_current(
            value.tenant_id,
            value.entitlement_id,
            history,
            current,
            session=session,
        )
        == value
    )
    with pytest.raises(registry.TenantBrandingEntitlementRegistryNotFoundError):
        registry.get_current(
            "tenant-b",
            value.entitlement_id,
            history,
            current,
            session=session,
        )


def test_transition_derives_domain_state_and_advances_explicit_current() -> None:
    """PENDING -> ACTIVE -> SUSPENDED is domain-derived and revisioned."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)

    activated = registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    assert activated.outcome is registry.TenantBrandingEntitlementPersistenceOutcome.TRANSITIONED
    assert activated.entitlement.lifecycle_state is TenantBrandingEntitlementState.ACTIVE
    assert activated.entitlement.lifecycle_revision == 1

    suspended = registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.SUSPENDED,
        expected_revision=1,
        evidence_reference="suspension-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    assert suspended.entitlement.lifecycle_state is TenantBrandingEntitlementState.SUSPENDED
    assert suspended.entitlement.lifecycle_revision == 2
    assert len(history.rows) == 3
    assert len(current.rows) == 1


def test_exact_transition_replay_is_idempotent_but_changed_replay_rejects() -> None:
    """Same revision command replays exactly; changed evidence cannot reuse it."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)
    first = registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    replay = registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    assert (
        replay.outcome
        is registry.TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY
    )
    assert replay.entitlement == first.entitlement
    with pytest.raises(registry.TenantBrandingEntitlementRegistryConflictError):
        registry.transition(
            tenant_id=value.tenant_id,
            entitlement_id=value.entitlement_id,
            target_state=TenantBrandingEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="different-activation",
            evidence_fingerprint=FP,
            occurred_at=NOW,
            history_collection=history,
            current_collection=current,
            session=session,
        )


def test_stale_revision_and_illegal_terminal_transition_fail_closed() -> None:
    """Current revision and D21B2 lifecycle legality remain mandatory."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)
    registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.REVOKED,
        expected_revision=1,
        evidence_reference="revocation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    with pytest.raises(registry.TenantBrandingEntitlementRegistryConflictError):
        registry.transition(
            tenant_id=value.tenant_id,
            entitlement_id=value.entitlement_id,
            target_state=TenantBrandingEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="reactivate",
            evidence_fingerprint=FP,
            occurred_at=NOW,
            history_collection=history,
            current_collection=current,
            session=session,
        )
    with pytest.raises(registry.TenantBrandingEntitlementRegistryConflictError):
        registry.transition(
            tenant_id=value.tenant_id,
            entitlement_id=value.entitlement_id,
            target_state=TenantBrandingEntitlementState.REVOKED,
            expected_revision=0,
            evidence_reference="stale",
            evidence_fingerprint=FP,
            occurred_at=NOW,
            history_collection=history,
            current_collection=current,
            session=session,
        )


def test_historical_initial_replay_cannot_obscure_advanced_currentness() -> None:
    """Revision-zero replay after activation is stale and cannot rewind current."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)
    registry.transition(
        tenant_id=value.tenant_id,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
        history_collection=history,
        current_collection=current,
        session=session,
    )
    with pytest.raises(
        registry.TenantBrandingEntitlementRegistryConflictError,
        match="D21B2B_STALE_INITIAL_REPLAY",
    ):
        create(value, history, current, session)
    assert (
        registry.get_current(
            value.tenant_id,
            value.entitlement_id,
            history,
            current,
            session=session,
        ).lifecycle_state
        is TenantBrandingEntitlementState.ACTIVE
    )


def test_history_and_current_corruption_fail_closed() -> None:
    """Corrupt history or compact pointer cannot become current authority."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)

    original_history = deepcopy(history.rows[0])
    history.rows[0]["entitlement_payload"]["fingerprint"] = "f" * 128
    with pytest.raises(
        registry.TenantBrandingEntitlementRegistryPersistedRecordInvalidError
    ):
        registry.get_current(
            value.tenant_id,
            value.entitlement_id,
            history,
            current,
            session=session,
        )
    history.rows[0] = original_history

    current.rows[0]["entitlement_fingerprint"] = "e" * 128
    with pytest.raises(
        registry.TenantBrandingEntitlementRegistryPersistedRecordInvalidError
    ):
        registry.get_current(
            value.tenant_id,
            value.entitlement_id,
            history,
            current,
            session=session,
        )


def test_duplicate_insert_and_cas_miss_signal_whole_transaction_retry() -> None:
    """Races never become conflict/persistence success inside same transaction."""
    value = pending()
    history, current = collections()
    session = Session()
    history.force_duplicate = True
    with pytest.raises(registry.TenantBrandingEntitlementRegistryRetryRequiredError):
        create(value, history, current, session)

    history, current = collections()
    create(value, history, current, session)
    current.force_cas_miss = True
    with pytest.raises(registry.TenantBrandingEntitlementRegistryRetryRequiredError):
        registry.transition(
            tenant_id=value.tenant_id,
            entitlement_id=value.entitlement_id,
            target_state=TenantBrandingEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activation-1",
            evidence_fingerprint=FP,
            occurred_at=NOW,
            history_collection=history,
            current_collection=current,
            session=session,
        )


@pytest.mark.parametrize("surface", ["find", "insert", "update"])
def test_transient_transaction_labels_are_governed_retry_signals(surface: str) -> None:
    """Explicit Mongo transient labels always require whole-transaction retry."""
    value = pending()
    history, current = collections()
    session = Session()

    if surface == "find":
        history.transient_on_find = True
        with pytest.raises(registry.TenantBrandingEntitlementRegistryRetryRequiredError):
            create(value, history, current, session)
        return

    if surface == "insert":
        history.transient_on_insert = True
        with pytest.raises(registry.TenantBrandingEntitlementRegistryRetryRequiredError):
            create(value, history, current, session)
        return

    create(value, history, current, session)
    current.transient_on_update = True
    with pytest.raises(registry.TenantBrandingEntitlementRegistryRetryRequiredError):
        registry.transition(
            tenant_id=value.tenant_id,
            entitlement_id=value.entitlement_id,
            target_state=TenantBrandingEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activation-1",
            evidence_fingerprint=FP,
            occurred_at=NOW,
            history_collection=history,
            current_collection=current,
            session=session,
        )


def test_current_pointer_contains_no_profile_asset_browser_or_financial_material() -> None:
    """Currentness remains compact entitlement metadata only."""
    value = pending()
    history, current = collections()
    session = Session()
    create(value, history, current, session)
    row = current.rows[0]
    forbidden = {
        "logo",
        "logo_url",
        "logo_asset_reference",
        "primary_color",
        "secondary_color",
        "accent_color",
        "email_identity",
        "favicon",
        "custom_domain",
        "profile_id",
        "principal_id",
        "role",
        "permission",
        "price",
        "amount",
        "currency",
        "bank",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(row)


def test_no_transaction_ownership_or_runtime_side_effect_surface() -> None:
    """Registry stays persistence-only and never acquires transport authority."""
    names = set(dir(registry.TenantBrandingEntitlementRegistry))
    assert {
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
        "with_transaction",
        "requests",
        "httpx",
        "axios",
    }.isdisjoint(names)


# ARTIFACT: test_tenant_branding_entitlement_registry.py
# VERSION: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct D21B2B persistence/currentness evidence only; no profile, asset, browser, IAM or financial authority
# TENANT POSTURE: exact tenant/entitlement persistence and foreign-absence behavior only
# FAIL-CLOSED POSTURE: transaction absence, corruption, stale/divergent replay, CAS and transient races reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
