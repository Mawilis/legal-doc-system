"""WILSY OS HR Document Canonical Server Mount Certificate.

TITLE: HR Document HTTP Canonical Server Mount Certificate
VERSION: v1.0.0-P0-C12F7C-C-SERVER-MOUNT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify that the canonical EOS FastAPI application mounts the already-certified
HR document router exactly once and exposes its four routes through the live
application route table.

This certificate grants no HR, storage, provider, billing, payment, settlement
or financial execution authority.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_http_server_mount.py
"""

from __future__ import annotations

from fastapi.routing import APIRoute, _iter_routes_with_context

from tools.eos.api.server import app


VERSION = (
    "v1.0.0-P0-C12F7C-C-"
    "SERVER-MOUNT-CERT"
)


EXPECTED = frozenset({
    (
        "POST",
        "/api/hr/documents/employees/{employee_id}",
    ),
    (
        "GET",
        "/api/hr/documents/employees/{employee_id}",
    ),
    (
        "GET",
        (
            "/api/hr/documents/employees/{employee_id}"
            "/documents/{document_id}/versions"
        ),
    ),
    (
        "GET",
        (
            "/api/hr/documents/employees/{employee_id}"
            "/versions/{document_version_id}/content"
        ),
    ),
})


def _pairs() -> list[
    tuple[
        str,
        str,
    ]
]:
    values: list[
        tuple[
            str,
            str,
        ]
    ] = []

    for route, _context in _iter_routes_with_context(app.routes):
        if not isinstance(
            route,
            APIRoute,
        ):
            continue

        for method in (
            route.methods
            or set()
        ):
            if method in {
                "HEAD",
                "OPTIONS",
            }:
                continue

            values.append(
                (
                    method,
                    route.path,
                )
            )

    return values


def test_canonical_server_mount_exposes_all_four_hr_document_routes() -> None:
    pairs = _pairs()

    missing = (
        EXPECTED
        - set(
            pairs
        )
    )

    assert not missing, (
        "P0_C12F7C_HR_DOCUMENT_SERVER_MOUNT_MISSING:"
        + repr(
            sorted(
                missing
            )
        )
    )


def test_each_hr_document_route_is_mounted_exactly_once() -> None:
    pairs = _pairs()

    for expected in EXPECTED:
        assert pairs.count(
            expected
        ) == 1, (
            "P0_C12F7C_HR_DOCUMENT_SERVER_ROUTE_COUNT_INVALID:"
            + repr(
                expected
            )
        )


def test_server_mount_adds_no_hr_document_delete_patch_or_put_route() -> None:
    hr_document_pairs = [
        pair
        for pair in _pairs()
        if pair[1].startswith(
            "/api/hr/documents"
        )
    ]

    methods = {
        method
        for method, _
        in hr_document_pairs
    }

    assert "DELETE" not in methods
    assert "PATCH" not in methods
    assert "PUT" not in methods


def test_server_mount_has_exact_hr_document_route_surface() -> None:
    hr_document_pairs = frozenset(
        pair
        for pair in _pairs()
        if pair[1].startswith(
            "/api/hr/documents"
        )
    )

    assert hr_document_pairs == EXPECTED


# ARTIFACT: tests/unit/test_hr_document_http_server_mount.py
# VERSION: v1.0.0-P0-C12F7C-C-SERVER-MOUNT-CERT
# CANONICAL APP OWNER: tools/eos/api/server.py
# EXPECTED HR DOCUMENT ROUTES: 4
# DUPLICATE ROUTES: prohibited
# DELETE / PATCH / PUT: prohibited
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
