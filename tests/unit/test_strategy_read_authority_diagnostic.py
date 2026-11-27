"""Read-only Strategy IAM diagnostic unit certificate.

TITLE: WILSY OS Strategy IAM Local Diagnostic Certificate
VERSION: v1.0.0-STRATEGY-OWNER-DIAGNOSTIC-CERT
AUTHORITY BOUNDARY: Synthetic dependency substitution; no MongoDB or IAM mutations.
COMPLIANCE: Synthetic principals only. No user email, JWT, credentials or data writes.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.eos.ops import strategy_read_authority_diagnostic as diagnostic


def test_compares_project_and_strategy_for_exact_owner_scope_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pairs: list[tuple[str, str, str]] = []
    monkeypatch.setattr(diagnostic, "connect_db", lambda: (True, "connected"))
    monkeypatch.setattr(diagnostic, "get_database", lambda: object())
    monkeypatch.setattr(diagnostic, "get_role_assignment_repository", lambda: object())

    def evaluate(**kwargs):
        pairs.append((kwargs["tenant_id"], kwargs["operation"], kwargs["selected_business_role"]))
        return SimpleNamespace(
            authorized=kwargs["operation"] == "project_detail",
            reason=SimpleNamespace(value="BUSINESS_ROLE_INELIGIBLE"),
        )

    monkeypatch.setattr(diagnostic, "authorize_tenant_operation", evaluate)
    monkeypatch.setattr(
        diagnostic.TenantBusinessRoleRepository, "resolve_business_role",
        lambda *args, **kwargs: SimpleNamespace(status=SimpleNamespace(value="ACTIVE")),
    )

    def resolve(principal_id, tenant_id, role_id):
        if role_id == "COMPANY_DOCUMENT_READER":
            raise diagnostic.RoleAssignmentNotFoundError("synthetic missing")
        return SimpleNamespace(status=SimpleNamespace(value="ACTIVE"))

    monkeypatch.setattr(diagnostic.RoleAssignmentRepository, "resolve", resolve)
    result = diagnostic.inspect("synthetic-principal")
    assert pairs == [
        (diagnostic.WILSY_COMPANY_TENANT_ID, "project_detail", "tenant_owner"),
        (diagnostic.WILSY_COMPANY_TENANT_ID, "company_operating_document_read", "tenant_owner"),
    ]
    assert result["PROJECTS"] == "AUTHORIZED"
    assert result["STRATEGY"] == "BUSINESS_ROLE_INELIGIBLE"
    assert result["OWNER_CAPACITY"] == "ACTIVE"
    assert result["ASSIGNMENT_COMPANY_DOCUMENT_READER"] == "NOT_FOUND"


def test_missing_explicit_principal_rejected_without_database_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def never_connect():
        raise AssertionError("no DB connection permitted")

    monkeypatch.setattr(diagnostic, "connect_db", never_connect)
    with pytest.raises(ValueError, match="EXPLICIT_PRINCIPAL_REQUIRED"):
        diagnostic.inspect(" ")


def test_missing_local_db_is_not_interpreted_as_missing_iam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(diagnostic, "connect_db", lambda: (False, "unavailable"))
    with pytest.raises(RuntimeError, match="EOS_DATABASE_UNAVAILABLE"):
        diagnostic.inspect("synthetic-principal")


# ARTIFACT: tests/unit/test_strategy_read_authority_diagnostic.py
# VERSION: v1.0.0-STRATEGY-OWNER-DIAGNOSTIC-CERT
# AUTHORITY BOUNDARY: isolated test readback only.
# END OF WILSY OS SOVEREIGN ARTIFACT
