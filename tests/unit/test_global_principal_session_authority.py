"""TITLE: WILSY OS Global Principal Session Authority Certification.
VERSION: v1.4.0-REVALIDATION-TRACE-HANDOFF-TESTS
AUTHORITY: Adversarial unit verification of global-principal session and refresh authority.
EPITOME: Verifies exact tenant-aware workspace revalidation, revision-bound session
         currentness, refresh rotation and fail-closed revocation semantics.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_global_principal_session_authority.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-15.
CHANGELOG:
    2026-11-15 v1.4.0-REVALIDATION-TRACE-HANDOFF-TESTS exercises actual
    concurrent worker trace handoff, strict trace rejection, telemetry fault
    isolation, and unchanged currentness and revocation outcomes.
    2026-11-15 v1.3.0-REVALIDATION-READ-TIMING-TESTS certifies opt-in,
    trace-bound stage and wall-clock observations without private authority
    data, and proves telemetry failure cannot influence currentness.
    2026-11-15 v1.2.0-SESSIONLESS-CURRENTNESS-CONCURRENCY-TESTS proves all
    five independent sessionless revalidation reads overlap while retaining
    exact records and no cross-request cache.
    2026-11-08 v1.1.0-GLOBAL-PRINCIPAL-HEADQUARTERS-SESSION-TESTS updates workspace-mapping mutation tests to accept and
    assert tenant-aware workspace resolution arguments.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities and in-memory persistence only;
    no production credentials, sessions or tenant records are accessed.
TENANT BOUNDARY: Every test preserves exact principal and tenant scope.
AUTHORITY BOUNDARY: Unit certification only; no session or IAM authority is created.
TRANSACTION BOUNDARY: In-memory caller-owned transaction markers only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from datetime import datetime, timezone
from threading import Barrier
from typing import Any, cast
from types import SimpleNamespace

import pytest
from pymongo.errors import PyMongoError
from starlette.requests import Request

from tools.eos.auth import global_principal_session_authority as authority_module
from tools.eos.auth import authentication as authentication_module
from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority,
    GlobalPrincipalSessionRejected,
    GlobalPrincipalSessionUnavailable,
)
from tools.eos.auth.membership_selection_challenge import SelectedMembershipContext
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus


class Transaction:
    in_transaction = True


class Collection:
    def __init__(self):
        self.rows = []

    def create_index(self, *args, **kwargs):
        return kwargs.get("name", "test-index")

    def insert_one(self, doc, session=None):
        self.rows.append(dict(doc))
        return SimpleNamespace(inserted_id=len(self.rows))

    def find_one(self, query, session=None):
        return next((dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items()
                    if not isinstance(v, dict) and k != "expires_at")
                    and (not isinstance(query.get("expires_at"), dict)
                    or row["expires_at"] > query["expires_at"]["$gt"])), None)

    def find_one_and_update(self, query, update, return_document=None, session=None):
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items()
                    if not isinstance(v, dict))
                    and row["expires_at"] > query["expires_at"]["$gt"]), None)
        if row is None:
            return None
        row.update(update["$set"])
        return dict(row)

    def update_one(self, query, update, upsert=False, session=None):
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
        if row is None:
            return SimpleNamespace(matched_count=0)
        row.update(update["$set"])
        return SimpleNamespace(matched_count=1)

    def update_many(self, query, update, session=None):
        count = 0
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                row.update(update["$set"])
                count += 1
        return SimpleNamespace(modified_count=count)


class Authorities:
    def __init__(self):
        self.credential_revision = 2
        self.membership_revision = 3
        self.capacity_revision = 5
        self.principal_status = PrincipalStatus.ACTIVE
        self.membership_status = TenantMembershipStatus.ACTIVE
        self.capacity_status = TenantBusinessRoleStatus.ACTIVE

    def principal(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, status=self.principal_status)

    def credential(self, principal_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id,
                               credential_revision=self.credential_revision, mfa_enabled=True)

    def membership(self, principal_id, tenant_id, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id,
                               revision=self.membership_revision, status=self.membership_status)

    def capacity(self, principal_id, tenant_id, role, *, session=None):
        return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, business_role=role,
                               revision=self.capacity_revision, status=self.capacity_status)


def setup(monkeypatch):
    authorities = Authorities()
    sessions, refresh = Collection(), Collection()
    monkeypatch.setattr(
        "tools.eos.auth.global_principal_session_authority.create_access_token",
        lambda *args, **kwargs: "signed-access-token",
    )
    service = GlobalPrincipalSessionAuthority(
        sessions=cast(Any, sessions), refresh_tokens=cast(Any, refresh),
        principal_repository=SimpleNamespace(get=authorities.principal),
        credential_repository=SimpleNamespace(get_by_principal=authorities.credential),
        membership_repository=SimpleNamespace(resolve=authorities.membership),
        business_role_repository=SimpleNamespace(resolve_business_role=authorities.capacity),
        tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    )
    selected = SelectedMembershipContext("principal-A", "tenant-A", "tenant_owner",
                                         "EXECUTIVE_COMMAND_CENTRE", 2, 3, 5)
    return service, authorities, sessions, refresh, selected


def issue(service, selected):
    return service.issue_after_mfa(selected, session=Transaction(),
                                   now=datetime(2026, 11, 3, tzinfo=timezone.utc))


def test_issue_persists_digest_only_and_binds_exact_authority(monkeypatch):
    service, _, sessions, refresh, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    assert receipt.session_reference == sessions.rows[0]["session_reference"]
    assert receipt.refresh_token not in str(refresh.rows[0])
    assert refresh.rows[0]["principal_id"] == "principal-A"
    assert refresh.rows[0]["tenant_id"] == "tenant-A"
    assert sessions.rows[0]["membership_revision"] == 3
    assert sessions.rows[0]["capacity_revision"] == 5


def test_session_persistence_failure_propagates_without_transaction_ownership(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    class BrokenSessions:
        def insert_one(self, *_args, **_kwargs):
            raise PyMongoError("synthetic persistence failure")
    cast(Any, service)._sessions = cast(Any, BrokenSessions())
    transaction = Transaction()
    with pytest.raises(GlobalPrincipalSessionUnavailable, match="PERSISTENCE_FAILED"):
        service.issue_after_mfa(selected, session=transaction)
    assert transaction.in_transaction is True


def test_issue_requires_caller_owned_transaction(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    with pytest.raises(GlobalPrincipalSessionRejected, match="TRANSACTION_REQUIRED"):
        service.issue_after_mfa(selected, session=SimpleNamespace(in_transaction=False))


def test_refresh_is_single_use_and_rotates(monkeypatch):
    service, _, _, refresh, selected = setup(monkeypatch)
    first = issue(service, selected)
    rotated = service.rotate_refresh_token(
        first.refresh_token, session=Transaction(),
        now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc))
    assert rotated.session_reference == first.session_reference
    assert rotated.refresh_token != first.refresh_token
    assert refresh.rows[0]["consumed_at"] is not None
    with pytest.raises(GlobalPrincipalSessionRejected, match="GLOBAL_REFRESH_INVALID"):
        service.rotate_refresh_token(first.refresh_token, session=Transaction(),
                                     now=datetime(2026, 11, 3, 0, 2, tzinfo=timezone.utc))


def test_credential_revision_change_rejects_refresh(monkeypatch):
    service, authorities, _, refresh, selected = setup(monkeypatch)
    first = issue(service, selected)
    authorities.credential_revision = 3
    with pytest.raises(GlobalPrincipalSessionRejected, match="CREDENTIAL_STALE"):
        service.rotate_refresh_token(first.refresh_token, session=Transaction(),
                                     now=datetime(2026, 11, 3, 0, 1, tzinfo=timezone.utc))
    assert len(refresh.rows) == 1


def test_membership_and_capacity_revision_changes_invalidate_currentness(monkeypatch):
    service, authorities, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    authorities.membership_revision = 4
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)
    authorities.membership_revision = 3
    authorities.capacity_revision = 6
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)


def test_sessionless_currentness_overlaps_independent_revalidation_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Request currentness retains all facts but does not serialize independent IO."""

    service, authorities, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    gate = Barrier(5, timeout=2)
    observed: list[str] = []

    def principal(principal_id: str, *, session: object = None) -> object:
        assert session is None
        gate.wait()
        observed.append("principal")
        return authorities.principal(principal_id)

    def credential(principal_id: str, *, session: object = None) -> object:
        assert session is None
        gate.wait()
        observed.append("credential")
        return authorities.credential(principal_id)

    def membership(
        principal_id: str, tenant_id: str, *, session: object = None
    ) -> object:
        assert session is None
        gate.wait()
        observed.append("membership")
        return authorities.membership(principal_id, tenant_id)

    def capacity(
        principal_id: str, tenant_id: str, role: str, *, session: object = None
    ) -> object:
        assert session is None
        gate.wait()
        observed.append("capacity")
        return authorities.capacity(principal_id, tenant_id, role)

    def tenant(tenant_id: str, *, session: object = None) -> object:
        assert session is None
        gate.wait()
        observed.append("tenant")
        return SimpleNamespace(tenant_id=tenant_id)

    service._principals = SimpleNamespace(get=principal)
    service._credentials = SimpleNamespace(get_by_principal=credential)
    service._memberships = SimpleNamespace(resolve=membership)
    service._capacities = SimpleNamespace(resolve_business_role=capacity)
    service._tenant_resolver = tenant

    assert service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    assert sorted(observed) == [
        "capacity",
        "credential",
        "membership",
        "principal",
        "tenant",
    ]


def test_revalidation_timing_is_opt_in_trace_bound_and_fault_isolated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Diagnostics expose only closed timing fields and cannot change currentness."""

    service, authorities, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    observations: list[dict[str, object]] = []

    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    monkeypatch.setattr(
        authentication_module,
        "emit_request_timing",
        lambda **kwargs: observations.append(kwargs),
    )
    gate = Barrier(5, timeout=2)
    executed: list[str] = []

    def synchronized(name: str, operation: Any) -> Any:
        def invoke(*args: Any, **kwargs: Any) -> Any:
            gate.wait()
            executed.append(name)
            return operation(*args, **kwargs)

        return invoke

    service._principals = SimpleNamespace(
        get=synchronized("principal", authorities.principal)
    )
    service._credentials = SimpleNamespace(
        get_by_principal=synchronized("credential", authorities.credential)
    )
    service._memberships = SimpleNamespace(
        resolve=synchronized("membership", authorities.membership)
    )
    service._capacities = SimpleNamespace(
        resolve_business_role=synchronized("capacity", authorities.capacity)
    )
    service._tenant_resolver = synchronized(
        "tenant", lambda tenant_id, *, session=None: SimpleNamespace(tenant_id=tenant_id)
    )

    trace_id = "TRC-ABCDEFGH-123456"
    correlation = authentication_module.establish_request_timing_correlation(
        Request(
            {
                "type": "http",
                "headers": [(b"x-trace-id", trace_id.encode("ascii"))],
            }
        )
    )
    assert correlation == trace_id

    assert service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    assert {value["stage"] for value in observations} == {
        "GLOBAL_SESSION_REVALIDATE_PRINCIPAL",
        "GLOBAL_SESSION_REVALIDATE_CREDENTIAL",
        "GLOBAL_SESSION_REVALIDATE_MEMBERSHIP",
        "GLOBAL_SESSION_REVALIDATE_CAPACITY",
        "GLOBAL_SESSION_REVALIDATE_TENANT",
        "GLOBAL_SESSION_REVALIDATE",
    }
    assert all(value["outcome"] == "OK" for value in observations)
    assert all(value["correlation"] == trace_id for value in observations)
    assert all(isinstance(value["duration_ms"], float) for value in observations)
    assert sorted(executed) == ["capacity", "credential", "membership", "principal", "tenant"]
    serialized = repr(observations)
    assert "principal-A" not in serialized
    assert "tenant-A" not in serialized
    assert "tenant_owner" not in serialized

    count_when_enabled = len(observations)
    monkeypatch.delenv("WILSY_MY_WORK_TIMING")
    assert service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    assert len(observations) == count_when_enabled

    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    correlation_token = authentication_module._TIMING_CORRELATION.set("invalid-trace")
    invalid_trace_event_count = len(observations)
    assert service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    assert len(observations) == invalid_trace_event_count
    authentication_module._TIMING_CORRELATION.reset(correlation_token)

    correlation_token = authentication_module._TIMING_CORRELATION.set("TRACE_UNAVAILABLE")
    absent_trace_event_count = len(observations)
    assert service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    assert len(observations) == absent_trace_event_count
    authentication_module._TIMING_CORRELATION.reset(correlation_token)

    authorities.membership_status = TenantMembershipStatus.SUSPENDED
    assert not service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )
    assert observations[-1]["stage"] == "GLOBAL_SESSION_REVALIDATE"
    assert observations[-1]["outcome"] == "REJECTED"

    monkeypatch.setattr(
        authentication_module,
        "emit_request_timing",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("diagnostic fault")),
    )
    authorities.membership_status = TenantMembershipStatus.ACTIVE
    assert service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )


def test_access_token_credential_epoch_must_match_persisted_session(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    assert not service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
        expected_credential_revision=99,
    )


def test_workspace_mapping_change_invalidates_existing_global_session(monkeypatch):
    service, _, _, _, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    monkeypatch.setattr(
        authority_module,
        "resolve_workspace_id",
        lambda _role, *, tenant_id=None: "DIFFERENT_WORKSPACE",
    )
    assert not service.is_session_current(
        principal_id="principal-A",
        tenant_id="tenant-A",
        session_reference=receipt.session_reference,
    )


def test_cross_tenant_session_lookup_and_revocation_are_isolated(monkeypatch):
    service, _, sessions, refresh, selected = setup(monkeypatch)
    receipt = issue(service, selected)
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-B",
                                          session_reference=receipt.session_reference)
    assert service.revoke_session(principal_id="principal-A", tenant_id="tenant-A",
                                  session_reference=receipt.session_reference, session=Transaction())
    assert sessions.rows[0]["revoked_at"] is not None
    assert refresh.rows[0]["revoked_at"] is not None
    assert not service.is_session_current(principal_id="principal-A", tenant_id="tenant-A",
                                          session_reference=receipt.session_reference)

# ARTIFACT: test_global_principal_session_authority.py
# VERSION: v1.4.0-REVALIDATION-TRACE-HANDOFF-TESTS
# AUTHORITY BOUNDARY: adversarial unit certification of global session lifecycle only
# TENANT POSTURE: exact principal and tenant scope remain isolated
# FAIL-CLOSED POSTURE: stale or divergent workspace, revision and session authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
