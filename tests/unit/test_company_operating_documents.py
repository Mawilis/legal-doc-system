"""TITLE: WILSY OS Company Document Lifecycle and HTTP Certificate.
VERSION: v1.4.0-EXACT-STRATEGY-PROJECT-LINK-HTTP-CERT
AUTHORITY: Repository-owned isolated regression evidence, not runtime admission.
EPITOME: Verify independent publication, private drafts, exact scope, immutable
lineage, command replay and honest empty/publication HTTP contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_company_operating_documents.py
COLLABORATION / OWNERSHIP: Company domain, registry, router and canonical IAM metadata.
CERTIFICATION / UPDATE DATE: 2026-11-15
CHANGELOG: v1.4.0-EXACT-STRATEGY-PROJECT-LINK-HTTP-CERT tests
that independently admitted Strategy author and project read scopes bind
current independently published strategy pillar and exact active project
revisions in a majority source transaction, deny mismatched currentness and
foreign actor scopes, and require explicit relationship indexes.
CHANGELOG: v1.3.0-ENTERPRISE-ADMIN-READ-CERT asserts the exact existing
ENTERPRISE_ADMIN read grant while preserving dedicated-reader access and every
author, publish, review, session, foreign-tenant and source-lifecycle denial.
v1.2.0-CURRENT-COMPANY-SESSION-CERT adds canonical session-source, stale and GLOBAL delegation checks.
Prior certification verifies the central read decision with active
company membership and capacity, missing/explicit read grants, no workforce
requirement, preserved author/publisher separation and a typed cursor test double.
CHANGELOG: v1.0.0-COMPANY-DOCUMENT-CONTRACT-CERT adds focused source contract evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic text/actors only; no external infrastructure.
TENANT BOUNDARY: Canonical company fixture and explicit foreign negative cases.
AUTHORITY BOUNDARY: HTTP dependency overrides test projection only; real browser
certificate independently proves canonical IAM and Mongo transactions.
FINANCIAL AUTHORITY BOUNDARY: No financial authority or mutations.
"""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.api import company_operating_document_router as http
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authorization import _BINDINGS
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID as TENANT
from tools.eos.saas.company_operating_document_registry import CompanyOperatingDocumentRegistry
from tools.eos.saas.domain.company_operating_document import (
    CompanyDocumentClass as Class, CompanyDocumentState as State, CompanyDocumentError,
    CompanyDocumentSection, CompanyOperatingDocumentRevision, instant, semantic_fingerprint,
)

NOW = datetime(2026, 11, 13, tzinfo=timezone.utc)
PAYLOAD = {"title": "Synthetic proposal", "document_version": "1.0.0",
           "sections": [{"section_id": "purpose", "title": "Purpose", "body": "Synthetic certification text."}]}
SESSION = SimpleNamespace(in_transaction=True)


class Cursor:
    """Bounded deterministic collection cursor for isolated source contract tests."""
    def __init__(self, rows):
        self.rows = list(rows)
    def __iter__(self):
        return iter(self.rows)
    def sort(self, field, order=None):
        """Support both existing single-index and newer compound-source ordering."""
        if isinstance(field, list) and order is None:
            return Cursor(sorted(self.rows, key=lambda row: tuple(
                row[coordinate] if direction > 0 else row[coordinate]
                for coordinate, direction in field)))
        return Cursor(sorted(self.rows, key=lambda row: row[field], reverse=order < 0))
    def limit(self, limit):
        return Cursor(self.rows[:limit])
    def max_time_ms(self, _limit):
        return self


class Collection:
    """In-memory transport double; does not claim Mongo concurrency certification."""
    def __init__(self):
        self.rows = []
        self.indexes = {}
    def find(self, query, **_kwargs):
        return Cursor(deepcopy([row for row in self.rows if all(row.get(key) == value for key, value in query.items())]))
    def find_one(self, query, **kwargs):
        return next(iter(self.find(query, **kwargs)), None)
    def insert_one(self, row, **_kwargs):
        self.rows.append(deepcopy(row))
    def create_index(self, keys, name, **kwargs):
        self.indexes[name] = {"key": keys, **kwargs}
    def index_information(self):
        return deepcopy(self.indexes)


@pytest.fixture
def registry():
    """Create isolated registry transport with explicit fixture-owned indexes."""
    database = {name: Collection() for name in ("company_operating_document_revisions", "company_operating_document_commands")}
    result = CompanyOperatingDocumentRegistry(database)
    result.provision_indexes()
    return result


def command(registry, action="CREATE_DRAFT", expected=0, actor="author", payload=None, key=None):
    """Issue explicitly authorized test commands; IAM is exercised separately."""
    return registry.command(TENANT, Class.MISSION, actor_id=actor, action=action,
        payload=deepcopy(PAYLOAD) if payload is None and action == "CREATE_DRAFT" else payload or {},
        expected_revision=expected, idempotency_key=key or f"synthetic-{action}-{expected}", now=NOW, session=SESSION)


def publication(registry, effective=NOW):
    """Prepare and independently publish synthetic source truth."""
    command(registry)
    command(registry, "SUBMIT", 1)
    return command(registry, "PUBLISH", 2, "publisher", {"approval_reference": "Synthetic approval", "effective_from": instant(effective)})


def test_immutable_lifecycle_and_sha3_evidence(registry):
    """Publication retains submitted content, independently attributed approval and lineage."""
    result = publication(registry)
    assert result.state is State.PUBLISHED
    assert result.sections[0].body == PAYLOAD["sections"][0]["body"]
    assert result.author_principal_id == "author" and result.approved_by_principal_id == "publisher"
    history = registry.history(TENANT, Class.MISSION, session=SESSION)
    assert len(history) == 3 and [item.state for item in history] == [State.DRAFT, State.SUBMITTED, State.PUBLISHED]
    assert history[1].previous_fingerprint == history[0].fingerprint
    assert CompanyOperatingDocumentRevision.from_dict(result.to_dict()) == result
    assert len(result.fingerprint) == 128
    assert semantic_fingerprint({"b": 2, "a": 1}) == semantic_fingerprint({"a": 1, "b": 2})


@pytest.mark.parametrize("action,actor,expected,payload,code", [
    ("PUBLISH", "publisher", 1, {"approval_reference": "synthetic", "effective_from": instant(NOW)}, "PUBLICATION_STATE_INVALID"),
    ("SUBMIT", "another-author", 1, {}, "SUBMISSION_DENIED"),
    ("SUBMIT", "author", 0, {}, "REVISION_CONFLICT"),
])
def test_invalid_lifecycle_never_appends(registry, action, actor, expected, payload, code):
    """Invalid authority, revision or transition cannot create receipt or revision."""
    command(registry)
    with pytest.raises(CompanyDocumentError, match=code):
        command(registry, action, expected, actor, payload)
    assert len(registry.revisions.rows) == len(registry.commands.rows) == 1


def test_self_publication_is_denied_even_with_both_permissions(registry):
    """Independent actor requirement is a source invariant beyond role possession."""
    command(registry); command(registry, "SUBMIT", 1)
    with pytest.raises(CompanyDocumentError, match="INDEPENDENT_APPROVER_REQUIRED"):
        command(registry, "PUBLISH", 2, "author", {"approval_reference": "synthetic", "effective_from": instant(NOW)})
    assert len(registry.revisions.rows) == 2


def test_exact_replay_and_divergent_key(registry):
    """One intent replays its original immutable record even after lifecycle advances."""
    first = command(registry, key="same-key")
    publication_input = deepcopy(PAYLOAD)
    command(registry, "SUBMIT", 1)
    assert command(registry, key="same-key") == first
    publication_input["title"] = "Different intent"
    with pytest.raises(CompanyDocumentError, match="IDEMPOTENCY_CONFLICT"):
        command(registry, payload=publication_input, key="same-key")
    assert len(registry.commands.rows) == 2


@pytest.mark.parametrize("tenant,session", [("foreign-tenant", SESSION), (TENANT, None)])
def test_exact_tenant_and_caller_transaction_required(registry, tenant, session):
    """Neither foreign scope nor missing caller transaction can read source truth."""
    with pytest.raises(CompanyDocumentError):
        registry.history(tenant, Class.MISSION, session=session)
    assert not registry.revisions.rows


def test_integrity_corruption_is_not_empty(registry):
    """Altered stored content never becomes lawful unpublished state."""
    command(registry)
    registry.revisions.rows[0]["sections"][0]["body"] = "Tampered"
    with pytest.raises(CompanyDocumentError, match="INTEGRITY_INVALID"):
        registry.history(TENANT, Class.MISSION, session=SESSION)


def test_digest_valid_illegal_first_publication_is_rejected(registry):
    """A digest alone cannot replace submitted lineage and independent approval."""
    published = publication(registry)
    registry.revisions.rows = [replace(published, revision=1, previous_fingerprint=None).to_dict()]
    with pytest.raises(CompanyDocumentError, match="LINEAGE_INVALID"):
        registry.history(TENANT, Class.MISSION, session=SESSION)


def test_future_publication_remains_private_until_effective(registry):
    """Publication and effective reader visibility are distinct source facts."""
    publication(registry, NOW + timedelta(days=1))
    assert registry.current(TENANT, Class.MISSION, session=SESSION, now=NOW) is None
    assert registry.current(TENANT, Class.MISSION, session=SESSION, now=NOW, review=True).state is State.PUBLISHED


def test_missing_command_indexes_fail_without_ddl(registry):
    """Runtime commands never silently provision arbitration indexes."""
    registry.commands.indexes.clear()
    with pytest.raises(CompanyDocumentError, match="INDEX_PROVISIONING_REQUIRED"):
        registry.require_command_indexes()
    assert not registry.commands.indexes


@pytest.mark.parametrize("changes", [
    {"title": " "}, {"document_version": "01.0.0"},
    {"sections": [{"section_id": "bad\"id", "title": "X", "body": "Y"}]},
    {"sections": [{"section_id": "x", "title": "X", "body": "Y"}] * 2},
])
def test_invalid_proposals_never_write(registry, changes):
    """Invalid bounded content is rejected before any institutional artifact persists."""
    with pytest.raises(CompanyDocumentError):
        command(registry, payload={**deepcopy(PAYLOAD), **changes})
    assert not registry.revisions.rows


def http_client(monkeypatch, registry, privileged=False):
    """Test HTTP projections only; production IAM remains exercised by real browser."""
    app = FastAPI(); app.include_router(http.router, prefix="/api")
    app.dependency_overrides[http._require_current_company_session] = lambda: None
    actor = SimpleNamespace(tenant_id=TENANT, identity=SimpleNamespace(identity_id="author"))
    app.dependency_overrides[http._READ] = lambda: actor
    app.dependency_overrides[http._MAY_AUTHOR] = lambda: actor if privileged else None
    app.dependency_overrides[http._MAY_PUBLISH] = lambda: None
    monkeypatch.setattr(http, "_transaction", lambda context, callback, **kwargs: callback(registry, SESSION))
    return TestClient(app)


def test_http_private_content_and_counts_are_not_leaked(monkeypatch, registry):
    """Ordinary readers see honest empty state; private revision/history is denied."""
    command(registry)
    client = http_client(monkeypatch, registry)
    view = client.get("/api/company-operating-documents/MISSION")
    assert view.status_code == 200 and view.headers["cache-control"] == "no-store"
    assert view.json()["state"] == "NOT_YET_PUBLISHED" and view.json()["document"] is None
    assert view.json()["current_revision"] == 0
    assert client.get("/api/company-operating-documents/MISSION/revisions").json()["items"] == []
    assert client.get("/api/company-operating-documents/MISSION?review=true").status_code == 403
    assert client.get("/api/company-operating-documents/MISSION?revision=1").status_code == 404


def test_http_current_approved_and_privileged_review(monkeypatch, registry):
    """Published content is source-owned; authorized authors can review later drafts."""
    published = publication(registry)
    command(registry, expected=3, payload={**deepcopy(PAYLOAD), "document_version": "2.0.0"})
    client = http_client(monkeypatch, registry, privileged=True)
    assert client.get("/api/company-operating-documents/MISSION").json()["document"]["fingerprint"] == published.fingerprint
    review = client.get("/api/company-operating-documents/MISSION?review=true").json()
    assert review["state"] == "DRAFT" and "SUBMIT" in review["available_actions"]
    assert "sections" not in client.get("/api/company-operating-documents/MISSION/revisions").json()["items"][0]



def test_strategy_project_link_http_requires_exact_independent_source_and_stable_readback(monkeypatch, registry):
    """Company Strategy relationships require BOTH company and project permission."""
    from tools.eos.saas.strategy_project_relationship_registry import (
        LINK_COLLECTION, EVENT_COLLECTION, StrategyProjectRelationshipRegistry,
    )
    from tools.eos.saas.domain.project import ProjectStatus

    now = datetime.now(timezone.utc)
    project_id = "prj-" + "a" * 48
    proposal = {"title": "Approved synthetic strategy", "document_version": "1.0.0",
                "sections": [{"section_id": "pillar-one", "title": "One OS", "body": "Synthetic source objective."}]}
    draft = registry.command(TENANT, Class.STRATEGY, actor_id="author",
        action="CREATE_DRAFT", payload=proposal, expected_revision=0,
        idempotency_key="strategy-draft", now=now, session=SESSION)
    submitted = registry.command(TENANT, Class.STRATEGY, actor_id="author",
        action="SUBMIT", payload={}, expected_revision=draft.revision,
        idempotency_key="strategy-submit", now=now, session=SESSION)
    publication = registry.command(TENANT, Class.STRATEGY, actor_id="publisher",
        action="PUBLISH", payload={"approval_reference": "independent-proof",
                                "effective_from": instant(now - timedelta(days=1))},
        expected_revision=submitted.revision, idempotency_key="strategy-publish",
        now=now, session=SESSION)
    database = {LINK_COLLECTION: Collection(), EVENT_COLLECTION: Collection()}
    source = StrategyProjectRelationshipRegistry(database)
    source.ensure_indexes()
    actor = SimpleNamespace(tenant_id=TENANT, identity=SimpleNamespace(identity_id="author"))
    project = SimpleNamespace(project_id=project_id, name="Existing operating foundation",
                              revision=6, status=ProjectStatus.ACTIVE)
    monkeypatch.setattr(http.kernel_db, "get_database", lambda: database)
    monkeypatch.setattr(http, "_project_source",
                        lambda db, tenant, identity, session: project)
    monkeypatch.setattr(http, "_transaction",
                        lambda context, callback, **kw: callback(registry, SESSION))
    app = FastAPI()
    app.include_router(http.router, prefix="/api")
    app.dependency_overrides[http._require_current_company_session] = lambda: None
    app.dependency_overrides[http._READ] = lambda: actor
    app.dependency_overrides[http._AUTHOR] = lambda: actor
    app.dependency_overrides[http._PROJECT_READ] = lambda: actor
    client = TestClient(app)
    endpoint = "/api/company-operating-documents/STRATEGY/project-links"
    empty = client.get(endpoint)
    assert empty.status_code == 200 and empty.json()["items"] == []
    assert empty.json()["strategy_progress"] is None

    payload = {"pillar_id": "pillar-one", "project_id": project_id,
               "expected_strategy_revision": publication.revision,
               "expected_project_revision": project.revision}
    first = client.post(endpoint, json=payload, headers={"Idempotency-Key": "strategy-first"})
    assert first.status_code == 201, first.text
    assert first.json()["relationship_state"] == "RECORDED_NOT_OUTCOME_CERTIFIED"
    assert first.json()["strategy_progress"] is None
    assert client.post(endpoint, json=payload, headers={"Idempotency-Key": "strategy-first"}).json() == first.json()
    assert len(database[LINK_COLLECTION].rows) == len(database[EVENT_COLLECTION].rows) == 1

    linked = client.get(endpoint)
    assert linked.status_code == 200
    assert linked.json()["items"][0]["pillar_id"] == "pillar-one"
    assert linked.json()["items"][0]["project_id"] == project_id
    assert linked.json()["items"][0]["state"] == "VERIFIED_CURRENT"
    assert linked.json()["strategy_progress"] is None

    invalid = client.post(endpoint, json={**payload, "expected_project_revision": 5},
                          headers={"Idempotency-Key": "different"})
    assert invalid.status_code == 409
    assert len(database[LINK_COLLECTION].rows) == 1
    app.dependency_overrides[http._PROJECT_READ] = lambda: SimpleNamespace(
        tenant_id="OTHER", identity=SimpleNamespace(identity_id="author"))
    assert client.get(endpoint).status_code == 403
    assert client.post(endpoint, json=payload, headers={"Idempotency-Key": "foreign"}).status_code == 403


def test_strategy_link_http_denies_unprovisioned_indexes(monkeypatch, registry):
    """Link writes never self-provision unique indexes in business requests."""
    from tools.eos.saas.strategy_project_relationship_registry import LINK_COLLECTION, EVENT_COLLECTION

    database = {LINK_COLLECTION: Collection(), EVENT_COLLECTION: Collection()}
    monkeypatch.setattr(http.kernel_db, "get_database", lambda: database)
    actor = SimpleNamespace(tenant_id=TENANT, identity=SimpleNamespace(identity_id="author"))
    app = FastAPI()
    app.include_router(http.router, prefix="/api")
    app.dependency_overrides[http._require_current_company_session] = lambda: None
    app.dependency_overrides[http._READ] = lambda: actor
    app.dependency_overrides[http._AUTHOR] = lambda: actor
    app.dependency_overrides[http._PROJECT_READ] = lambda: actor
    client = TestClient(app)
    result = client.post("/api/company-operating-documents/STRATEGY/project-links",
        headers={"Idempotency-Key": "strict-index"},
        json={"pillar_id": "pillar-one", "project_id": "prj-" + "a" * 48,
              "expected_strategy_revision": 3, "expected_project_revision": 6})
    assert result.status_code == 503
    assert result.json()["detail"]["error"] == "STRATEGY_LINK_INDEX_UNAVAILABLE"
    assert database[LINK_COLLECTION].indexes == {} and database[EVENT_COLLECTION].indexes == {}


def test_enterprise_admin_read_is_explicit_and_all_other_document_authority_remains_dedicated():
    """Only Enterprise Admin adds read; author, publish and review stay separately scoped."""
    permissions = {"company_operating_document:read", "company_operating_document:author", "company_operating_document:publish"}
    for role, grants in ROLE_PERMISSIONS_MAP.items():
        expected = {"company_operating_document:read"} if role == "ENTERPRISE_ADMIN" else set()
        if not role.startswith("COMPANY_DOCUMENT_"):
            assert permissions.intersection(grants) == expected
    for suffix in ("read", "author", "publish"):
        assert _BINDINGS["company_operating_document_" + suffix] == "company_operating_document:" + suffix


@pytest.mark.parametrize("grants,action,authorized", [
    (("ENTERPRISE_ADMIN",), "read", True),
    (("COMPANY_DOCUMENT_READER",), "read", True),
    (("COMPANY_DOCUMENT_AUTHOR",), "read", True),
    (("COMPANY_DOCUMENT_READER",), "author", False),
    (("COMPANY_DOCUMENT_READER",), "publish", False),
])
def test_central_document_read_iam_separates_capacity_from_permission(grants, action, authorized):
    """Current company membership/capacity never substitutes for a read grant.

    Uses the real central IAM evaluator with synthetic current repositories;
    no session token, workforce employment, canonical assignment or mutation.
    Read permission grants no author/publisher capability.
    """
    from tools.eos.auth.principal_status import PrincipalStatus
    from tools.eos.auth.tenant_membership import TenantMembershipStatus
    from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
    from tools.eos.auth.role_assignment import RoleAssignmentStatus
    from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
    from tools.eos.auth.tenant_authorization import authorize_tenant_operation, TenantAuthorizationReason
    from tools.eos.auth.permission_namespace import permission_metadata

    principal_id = "synthetic-read-boundary"
    permission = "company_operating_document:" + action
    operation = "company_operating_document_" + action
    membership = SimpleNamespace(resolve=lambda pid, tid: SimpleNamespace(
        principal_id=pid, tenant_id=tid, status=TenantMembershipStatus.ACTIVE))
    principal = SimpleNamespace(resolve=lambda pid: SimpleNamespace(
        principal_id=pid, status=PrincipalStatus.ACTIVE))

    def resolve_role(pid, tid, role):
        if role == "tenant_owner":
            return SimpleNamespace(principal_id=pid, tenant_id=tid, business_role=role,
                                   status=TenantBusinessRoleStatus.ACTIVE)
        if role in grants:
            return SimpleNamespace(principal_id=pid, tenant_id=tid, role_id=role,
                                   status=RoleAssignmentStatus.ACTIVE)
        raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")

    roles = SimpleNamespace(resolve=resolve_role)
    decision = authorize_tenant_operation(principal_id=principal_id, tenant_id=TENANT,
        permission_id=permission, operation=operation, principal_repository=principal,
        membership_repository=membership, business_role_repository=roles,
        role_assignment_repository=roles, selected_business_role="tenant_owner")
    assert decision.authorized is authorized
    assert decision.reason is (TenantAuthorizationReason.AUTHORIZED if authorized
                               else TenantAuthorizationReason.PERMISSION_NOT_GRANTED)
    assert decision.business_role == "tenant_owner"
    assert permission_metadata(permission).workforce_currentness_required is False


def test_enterprise_admin_company_document_read_is_canonical_tenant_fenced():
    """The static read grant cannot cross the company-document tenant boundary."""
    from tools.eos.auth.tenant_authorization import (
        TenantAuthorizationReason,
        authorize_tenant_operation,
    )

    unavailable = SimpleNamespace(resolve=lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("foreign company-document scope must deny before any authority read")
    ))
    decision = authorize_tenant_operation(
        principal_id="synthetic-enterprise-admin",
        tenant_id="foreign-company-tenant",
        permission_id="company_operating_document:read",
        operation="company_operating_document_read",
        principal_repository=unavailable,
        membership_repository=unavailable,
        business_role_repository=unavailable,
        role_assignment_repository=unavailable,
    )
    assert decision.authorized is False
    assert decision.reason is TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH


@pytest.mark.parametrize("reference,current,status,code", [
    (None, True, 401, "SESSION_REQUIRED"),
    ("synthetic-reference", False, 401, "SESSION_STALE"),
    ("synthetic-reference", None, 503, "SESSION_SOURCE_UNAVAILABLE"),
    ("synthetic-reference", True, 200, None),
])
def test_company_session_boundary_reuses_current_canonical_session(monkeypatch, reference, current, status, code):
    """A missing/stale session differs from unavailable currentness and legal absence."""
    def check(*args):
        assert args == (TENANT, "reader", reference)
        if current is None:
            raise RuntimeError("Synthetic source outage")
        return current
    monkeypatch.setattr(http, "AuthRegistry", lambda: SimpleNamespace(is_session_current=check))
    identity = http.SovereignIdentity(principal_scope="TENANT", tenant_id=TENANT,
        identity_id="reader", session_reference=reference, auth_method="JWT", status=PrincipalStatus.ACTIVE, username=None, email=None)
    if status == 200:
        assert http._require_current_company_session(identity) is None
    else:
        with pytest.raises(http.HTTPException) as error:
            http._require_current_company_session(identity)
        assert error.value.status_code == status
        detail = cast(dict[str, Any], cast(object, error.value.detail))
        assert detail["error"].endswith(code)


def test_global_company_session_is_already_validated_by_canonical_authentication(monkeypatch):
    """GLOBAL admission remains owned by the existing selected-capacity authenticator."""
    def wrong_owner():
        raise AssertionError("GLOBAL sessions must not use legacy tenant session storage")
    monkeypatch.setattr(http, "AuthRegistry", wrong_owner)
    assert http._require_current_company_session(http.SovereignIdentity(principal_scope="GLOBAL", tenant_id=TENANT, identity_id="reader", session_reference=None, auth_method="JWT", status=PrincipalStatus.ACTIVE, username=None, email=None)) is None

# ARTIFACT: test_company_operating_documents.py
# VERSION: v1.4.0-EXACT-STRATEGY-PROJECT-LINK-HTTP-CERT
# AUTHORITY BOUNDARY: Isolated contract regression only; no production admission.
# TENANT POSTURE: Exact canonical fixture scope and foreign negative assertions.
# FAIL-CLOSED POSTURE: Incomplete source, lineage or authorization cannot pass.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
