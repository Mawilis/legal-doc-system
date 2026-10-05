"""WILSY OS HR Document HTTP Direct Certificate.

TITLE: HR Document HTTP Direct Certificate
VERSION: v1.0.0-P0-C12F7C-B-HR-DOCUMENT-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Freeze the canonical EOS HTTP admission and composition contract for governed
HR document upload, metadata listing, immutable version history and download.

ROUTE CONTRACT:
POST /api/hr/documents/employees/{employee_id}
GET  /api/hr/documents/employees/{employee_id}
GET  /api/hr/documents/employees/{employee_id}/documents/{document_id}/versions
GET  /api/hr/documents/employees/{employee_id}/versions/{document_version_id}/content

TRANSPORT CONTRACT:
Upload uses a raw bounded Request.stream() body. Multipart, UploadFile,
File/Form admission, full request.body() buffering and caller-controlled
provider coordinates are prohibited.

WRITE AUTHORITY:
HrDocumentClass -> sensitivity_for_document_class -> F7B write operation /
permission. IAM admission must occur before provider begin and before F6F.

READ AUTHORITY:
The persisted HrDocument is resolved first through the F4 registry. Its
persisted sensitivity determines the F7B read operation/permission. Provider
coordinates, expected byte length and expected SHA3-512 come only from
persisted metadata.

PROVIDER CONTRACT:
HrDocumentS3StorageAdapter is write-only composition.
HrDocumentS3ReadStorageAdapter is read-only composition.
The HTTP layer does not construct provider object keys from caller input and
does not receive provider coordinates from the caller.

RESULT CONTRACT:
Committed upload -> 201.
Reconciliation required -> 202 and is not equivalent to committed success.
Read/list/version success -> 200.
Authorization denied -> 403.
Missing document -> 404.
Validation failure -> 422.
Authority/persistence/provider/integrity unavailable -> 503.

AUTHORITY BOUNDARY:
No deletion, retention disposal execution, legal-hold release, payroll
payment, billing, settlement or financial execution authority.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_http.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any

from fastapi.routing import APIRoute

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
    HrDocumentSensitivity,
    sensitivity_for_document_class,
)


VERSION = (
    "v1.0.0-P0-C12F7C-B-"
    "HR-DOCUMENT-HTTP-CERT"
)

MODULE_NAME = (
    "tools.eos.api.hr_document_router"
)

ROUTER_PREFIX = (
    "/api/hr/documents"
)

EXPECTED_ROUTES = frozenset({
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

SENSITIVITY_TOKEN = {
    HrDocumentSensitivity.STANDARD_EMPLOYMENT:
        "standard_employment",
    HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED:
        "employee_relations_restricted",
    HrDocumentSensitivity.PERFORMANCE_RESTRICTED:
        "performance_restricted",
    HrDocumentSensitivity.HIGHLY_SENSITIVE_HEALTH:
        "highly_sensitive_health",
    HrDocumentSensitivity.HIGHLY_SENSITIVE_IDENTITY:
        "highly_sensitive_identity",
    HrDocumentSensitivity.SEPARATION_RESTRICTED:
        "separation_restricted",
    HrDocumentSensitivity.GENERAL:
        "general",
}


def load_module() -> ModuleType:
    return importlib.import_module(
        MODULE_NAME
    )


def router_routes(
    module: ModuleType,
) -> list[APIRoute]:
    router = getattr(
        module,
        "router",
        None,
    )

    assert router is not None

    return [
        route
        for route in router.routes
        if isinstance(
            route,
            APIRoute,
        )
    ]


def route_pairs(
    module: ModuleType,
) -> frozenset[
    tuple[
        str,
        str,
    ]
]:
    pairs: set[
        tuple[
            str,
            str,
        ]
    ] = set()

    for route in router_routes(
        module
    ):
        for method in (
            route.methods
            or set()
        ):
            if method in {
                "HEAD",
                "OPTIONS",
            }:
                continue

            pairs.add(
                (
                    method,
                    route.path,
                )
            )

    return frozenset(
        pairs
    )


def source_text(
    module: ModuleType,
) -> str:
    source = inspect.getsource(
        module
    )

    assert isinstance(
        source,
        str,
    )

    return source


def test_canonical_hr_document_router_module_exists() -> None:
    spec = importlib.util.find_spec(
        MODULE_NAME
    )

    assert spec is not None, (
        "P0_C12F7C_EXPECTED_CANONICAL_HR_DOCUMENT_ROUTER_MISSING"
    )


def test_router_exposes_exact_four_route_surface() -> None:
    module = load_module()

    assert route_pairs(
        module
    ) == EXPECTED_ROUTES


def test_router_contains_no_mutating_delete_patch_or_put_surface() -> None:
    module = load_module()

    methods = {
        method
        for method, _
        in route_pairs(
            module
        )
    }

    assert "DELETE" not in methods
    assert "PATCH" not in methods
    assert "PUT" not in methods


def test_upload_route_declares_201_as_committed_default() -> None:
    module = load_module()

    matches = [
        route
        for route in router_routes(
            module
        )
        if (
            route.path
            == (
                "/api/hr/documents/"
                "employees/{employee_id}"
            )
            and "POST"
            in (
                route.methods
                or set()
            )
        )
    ]

    assert len(
        matches
    ) == 1

    assert (
        matches[
            0
        ].status_code
        == 201
    )


def test_upload_uses_raw_stream_not_multipart_or_full_body_buffer() -> None:
    source = source_text(
        load_module()
    )

    assert "request.stream(" in source

    assert "request.body(" not in source

    assert "UploadFile" not in source
    assert "File(" not in source
    assert "Form(" not in source


def test_upload_contract_requires_content_length_and_content_type() -> None:
    source = source_text(
        load_module()
    ).casefold()

    assert "content-length" in source
    assert "content-type" in source


def test_upload_contract_uses_required_hr_metadata_headers() -> None:
    source = source_text(
        load_module()
    ).casefold()

    for header in (
        "x-hr-document-id",
        "x-hr-document-version-id",
        "x-hr-ingestion-reference",
        "x-hr-document-class",
        "x-hr-original-filename",
        "x-tenant-id",
    ):
        assert header in source


def test_caller_cannot_supply_permission_role_sensitivity_or_provider_coordinates() -> None:
    source = source_text(
        load_module()
    ).casefold()

    forbidden_headers = (
        "x-permission-id",
        "x-authorization-role",
        "x-hr-document-sensitivity",
        "x-storage-provider-id",
        "x-storage-object-reference",
        "x-object-version-reference",
    )

    for header in forbidden_headers:
        assert header not in source


def test_write_authority_uses_public_document_class_sensitivity_owner() -> None:
    module = load_module()

    source = source_text(
        module
    )

    assert "HrDocumentClass" in source

    assert (
        "sensitivity_for_document_class"
        in source
    )

    for document_class in HrDocumentClass:
        sensitivity = (
            sensitivity_for_document_class(
                document_class
            )
        )

        assert (
            sensitivity
            in SENSITIVITY_TOKEN
        )


def test_write_and_read_authority_bind_to_f7b_operation_owner() -> None:
    source = source_text(
        load_module()
    )

    assert (
        "permission_for_business_role_operation"
        in source
    )

    assert "hr_document_" in source


def test_write_composition_calls_f6f_and_split_write_adapter() -> None:
    source = source_text(
        load_module()
    )

    assert (
        "orchestrate_hr_document_ingestion"
        in source
    )

    assert (
        "HrDocumentS3StorageAdapter"
        in source
    )


def test_read_composition_uses_registry_and_split_read_adapter() -> None:
    source = source_text(
        load_module()
    )

    assert "get_document_version" in source

    assert "list_employee_documents" in source

    assert "list_document_versions" in source

    assert (
        "HrDocumentS3ReadStorageAdapter"
        in source
    )


def test_download_coordinates_and_integrity_come_from_persisted_document() -> None:
    source = source_text(
        load_module()
    )

    assert "HrDocumentBinaryReadIntent" in source

    for persisted_field in (
        "storage_provider_id",
        "storage_object_reference",
        "object_version_reference",
        "byte_length",
        "content_digest_sha3_512",
    ):
        assert persisted_field in source


def test_http_layer_preserves_reconciliation_required_as_distinct_202() -> None:
    source = source_text(
        load_module()
    )

    assert (
        "RECONCILIATION_REQUIRED"
        in source
    )

    assert "202" in source


def test_expected_fail_closed_http_status_vocabulary_is_present() -> None:
    source = source_text(
        load_module()
    )

    for status_code in (
        "403",
        "404",
        "422",
        "503",
    ):
        assert status_code in source


def test_http_router_has_no_provider_delete_or_financial_execution_surface() -> None:
    source = source_text(
        load_module()
    ).casefold()

    for forbidden in (
        "delete_object(",
        "delete_provider(",
        "execute_payment(",
        "settlement",
        "financial_execution",
    ):
        assert forbidden not in source


def test_router_does_not_reimplement_f6f_reconciliation_resolution() -> None:
    source = source_text(
        load_module()
    )

    assert (
        "reconcile_hr_document_commit_uncertainty("
        not in source
    )


# ARTIFACT: tests/unit/test_hr_document_http.py
# VERSION: v1.0.0-P0-C12F7C-B-HR-DOCUMENT-HTTP-CERT
# ROUTES: exactly four canonical EOS HR document routes
# UPLOAD: raw bounded request stream; no multipart/full-body buffering
# WRITE IAM: canonical class -> sensitivity -> F7B operation/permission
# READ IAM: persisted sensitivity -> F7B operation/permission
# WRITE BUSINESS OWNER: F6F
# READ METADATA OWNER: F4
# READ BYTE CONTRACT: F5C
# WRITE PROVIDER ADAPTER: F5D HrDocumentS3StorageAdapter
# READ PROVIDER ADAPTER: F5D HrDocumentS3ReadStorageAdapter
# CALLER PROVIDER COORDINATES: prohibited
# DELETE / DISPOSAL / HOLD-RELEASE AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
