"""
TITLE: CRM Email Template Transactional Read Contract Certificate
VERSION: v1.0.0-CRM-TEMPLATE-TRANSACTIONAL-READ-RED
AUTHORITY: WILSY OS Core Governance
EPITOME: Verify explicit caller-session support on every public template read.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_crm_email_template_transactional_reads.py
COLLABORATION: WILSY OS sovereign engineering
CERTIFICATION DATE: 2026-10-07
CHANGELOG:
    v1.0.0: Establish five independent public session-contract regressions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE:
    Structural contract only; no credentials or external I/O.
TENANT BOUNDARY:
    Public registry reads must support caller-owned session propagation.
AUTHORITY BOUNDARY:
    Session support is not authorization, entitlement, or record access.
FINANCIAL AUTHORITY BOUNDARY:
    No payment, settlement, or financial execution authority.
"""

from __future__ import annotations

import inspect

import pytest

from tools.eos.crm.persistence.crm_email_template_registry import (
    CrmEmailTemplateRegistry,
)


@pytest.mark.parametrize(
    "method_name",
    (
        "get_template",
        "list_templates",
        "get_revision",
        "get_latest_revision",
        "list_revisions",
    ),
)
def test_public_read_accepts_explicit_caller_session(
    method_name: str,
) -> None:
    """Require an explicit session parameter on each registry read.

    This structural contract does not establish actual database forwarding.
    Behavioral unit and real-Mongo certificates are required separately.
    """
    method = getattr(CrmEmailTemplateRegistry, method_name)

    parameters = inspect.signature(method).parameters

    assert "session" in parameters, (
        f"CRM_TEMPLATE_READ_SESSION_PARAMETER_MISSING:{method_name}"
    )

    parameter = parameters["session"]

    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, (
        f"CRM_TEMPLATE_READ_SESSION_NOT_KEYWORD_ONLY:{method_name}"
    )

    assert parameter.default is None, (
        f"CRM_TEMPLATE_READ_SESSION_NOT_OPTIONAL:{method_name}"
    )



class _ReadCollection:
    """Capture exact read calls without a database or durable mutation."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find_one(
        self,
        query: object,
        **kwargs: object,
    ) -> None:
        self.calls.append(("find_one", query, kwargs))
        return None

    def find(
        self,
        query: object,
        **kwargs: object,
    ) -> list[object]:
        self.calls.append(("find", query, kwargs))
        return []


@pytest.mark.parametrize(
    "method_name",
    (
        "get_template",
        "list_templates",
        "get_revision",
        "get_latest_revision",
        "list_revisions",
    ),
)
def test_public_read_forwards_exact_session(
    method_name: str,
) -> None:
    """Forward the caller's exact session to the underlying read operation.

    This certificate tests forwarding only, not transaction consistency,
    current entitlement, record visibility, or read authorization.
    """
    collection = _ReadCollection()
    session = object()

    args: dict[str, object] = {
        "tenant_id": "tenant-a",
    }

    if method_name != "list_templates":
        args["template_id"] = "template-a"

    if method_name == "get_revision":
        args["revision"] = 1

    if method_name in ("get_template", "list_templates"):
        args["metadata_collection"] = collection
    else:
        args["revision_collection"] = collection

    method = getattr(CrmEmailTemplateRegistry, method_name)

    result = method(**args, session=session)

    assert len(collection.calls) == 1, (
        f"CRM_TEMPLATE_READ_CALL_COUNT_INVALID:{method_name}"
    )

    _, query, kwargs = collection.calls[0]

    assert isinstance(query, dict)
    assert query["tenant_id"] == "tenant-a"

    if method_name != "list_templates":
        assert query["template_id"] == "template-a"

    assert kwargs.get("session") is session, (
        f"CRM_TEMPLATE_READ_SESSION_IDENTITY_LOST:{method_name}"
    )

    if method_name.startswith("list_"):
        assert result == ()
    else:
        assert result is None


# ARTIFACT: test_crm_email_template_transactional_reads.py
# VERSION: v1.0.0-CRM-TEMPLATE-TRANSACTIONAL-READ-RED
# AUTHORITY BOUNDARY: structural public read session contract only
# TENANT POSTURE: exact tenant isolation remains mandatory
# FAIL-CLOSED POSTURE: missing session API fails certification
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
