"""S6-A3 direct production wiring certificate."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

SERVER = Path("tools/eos/api/server.py")
BRIDGE = Path("tools/eos/api/authority_bridge_router.py")


def test_startup_owns_all_s6_index_ddl() -> None:
    source = SERVER.read_text(encoding="utf-8")

    for required in (
        "InternalServiceReplayRegistry.ensure_indexes(",
        "InternalServiceWorkloadCredentialRegistry(",
        "PrivilegedWorkloadTrustCurrentnessRegistry(",
        "PrivilegedNoninteractiveSecurityProofRegistry(",
        "PrivilegedSecurityAssuranceEvidenceRegistry(",
    ):
        assert required in source


def test_request_path_has_no_index_ddl() -> None:
    source = BRIDGE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    fn = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name
        == "_authorize_production_request"
    )

    segment = ast.get_source_segment(
        source,
        fn,
    )

    assert segment is not None
    assert "ensure_indexes" not in segment
    assert "create_index" not in segment


def test_mounted_route_uses_production_s6_path() -> None:
    source = BRIDGE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    fn = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name == "authorize"
    )

    segment = ast.get_source_segment(
        source,
        fn,
    )

    assert segment is not None
    assert (
        "_authorize_production_request("
        in segment
    )
    assert "authorize_request(" not in segment


def test_transaction_is_held_until_policy_authorization() -> None:
    source = BRIDGE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    fn = next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        and node.name
        == "_authorize_production_request"
    )

    segment = ast.get_source_segment(
        source,
        fn,
    )

    assert segment is not None

    for required in (
        ".start_session()",
        ".start_transaction()",
        "service.compose(",
        "authorization_provider(",
        ".commit_transaction()",
        ".abort_transaction()",
    ):
        assert required in segment

    assert (
        segment.index(
            "service.compose("
        )
        < segment.index(
            "authorization_provider("
        )
        < segment.index(
            ".commit_transaction()"
        )
    )


def test_production_surface_accepts_no_caller_principal_or_proof() -> None:
    from tools.eos.api.authority_bridge_router import (
        _authorize_production_request,
    )

    params = set(
        inspect.signature(
            _authorize_production_request
        ).parameters
    )

    for forbidden in (
        "principal_id",
        "proof_reference",
        "workload_proof_reference",
    ):
        assert forbidden not in params


def test_no_activation_or_financial_authority_added() -> None:
    source = BRIDGE.read_text(
        encoding="utf-8"
    ).casefold()

    for forbidden in (
        "activate_privilege(",
        "super_admin=*",
        "payment_execution",
        "financial_settlement",
        "break_glass",
    ):
        assert forbidden not in source
