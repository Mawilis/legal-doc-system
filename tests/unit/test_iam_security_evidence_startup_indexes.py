"""TITLE: IAM Security Evidence Startup Index Certificate.
VERSION: v1.0.0-P3-R3G-S5-A2-FACTOR-INDEX-BOOTSTRAP
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies canonical startup ownership of P1 security-evidence and P3
interactive factor-currentness index DDL without issuing security evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_iam_security_evidence_startup_indexes.py
COLLABORATION / OWNERSHIP: WilsyAPIServer startup and IAM registry certificates.
CERTIFICATION/UPDATE DATE: 2026-10-14.
CHANGELOG:
  v1.0.0-P3-R3G-S5-A2-FACTOR-INDEX-BOOTSTRAP: Extends the existing P1 startup
  certificate to the canonical factor-currentness registry and gives the strict
  Mongo collection double only the create_index capability production invokes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Index-only synthetic startup execution; no evidence issuance.
TENANT BOUNDARY: No tenant data is read or written.
AUTHORITY BOUNDARY: Index bootstrap is not authentication or privileged authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.

Certifies that the canonical WilsyAPIServer startup hook initializes both
security-critical P1 evidence registries from the production database before
runtime use.

The certificate never connects to Mongo. It substitutes strict collection and
registry doubles and executes the actual FastAPI startup hook.

No authorization evidence, revocation evidence, role assignment, session,
refresh token, or financial authority is created.
"""

from __future__ import annotations

from typing import Any

import pytest

from tools.eos.api import server as subject


class _Collection:
    def __init__(self) -> None:
        self.index_names: list[str] = []

    def create_index(
        self,
        _keys: object,
        *,
        name: str,
        **_kwargs: object,
    ) -> str:
        self.index_names.append(name)
        return name


class _Database:
    def __init__(self) -> None:
        self.collections: dict[str, _Collection] = {}

    def __getitem__(
        self,
        name: str,
    ) -> _Collection:
        if name not in self.collections:
            self.collections[name] = _Collection()

        return self.collections[name]


class _PrincipalRepository:
    pass


def test_canonical_startup_initializes_both_p1_security_index_registries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _Database()

    principal_repository = (
        _PrincipalRepository()
    )

    calls: list[
        tuple[str, object, object | None]
    ] = []

    class _AuthorizationRegistry:
        def __init__(
            self,
            collection: object,
            *,
            principal_repository: object,
            **_kwargs: object,
        ) -> None:
            self.collection = collection
            self.principal_repository = (
                principal_repository
            )

        def ensure_indexes(
            self,
        ) -> None:
            calls.append(
                (
                    "authorization",
                    self.collection,
                    self.principal_repository,
                )
            )

    class _RevocationRegistry:
        def __init__(
            self,
            collection: object,
        ) -> None:
            self.collection = collection

        def ensure_indexes(
            self,
        ) -> None:
            calls.append(
                (
                    "revocation",
                    self.collection,
                    None,
                )
            )

    class _NoopRegistry:
        @classmethod
        def ensure_indexes(
            cls,
            _collection: object,
        ) -> None:
            return None

    class _NoopRateLimit:
        @classmethod
        def ensure_indexes(
            cls,
            _collection: object,
        ) -> None:
            return None

    monkeypatch.setattr(
        subject,
        "connect_db",
        lambda: (
            True,
            "P1_B5_TEST_CONNECTED",
        ),
    )

    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: database,
    )

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: None,
    )

    monkeypatch.setattr(
        subject,
        "get_principal_authority_repository",
        lambda: principal_repository,
    )

    monkeypatch.setattr(
        subject,
        "TenantAuthorizationDecisionEvidenceRegistry",
        _AuthorizationRegistry,
    )

    monkeypatch.setattr(
        subject,
        "AuthorizationRoleRevocationEvidenceRegistry",
        _RevocationRegistry,
    )

    monkeypatch.setattr(
        subject,
        "DeputyPrincipalBindingRegistry",
        _NoopRegistry,
    )

    monkeypatch.setattr(
        subject,
        "LegalStorefrontPublicIntentRegistry",
        _NoopRegistry,
    )

    monkeypatch.setattr(
        subject,
        "LegalStorefrontPublicIntentRateLimit",
        _NoopRateLimit,
    )

    app = subject.WilsyAPIServer(
        reasoning_provider_binding=None,
    ).get_app()

    startup_handlers = list(
        app.router.on_startup
    )

    assert startup_handlers

    target = None

    for handler in startup_handlers:
        if (
            getattr(
                handler,
                "__name__",
                ""
            )
            == "start_database"
        ):
            target = handler
            break

    assert target is not None

    import asyncio

    asyncio.run(
        target()
    )

    assert calls == [
        (
            "authorization",
            database[
                subject
                .TENANT_AUTHORIZATION_DECISION_EVIDENCE_COLLECTION
            ],
            principal_repository,
        ),
        (
            "revocation",
            database[
                subject
                .AUTHORIZATION_ROLE_REVOCATION_EVIDENCE_COLLECTION
            ],
            None,
        ),
    ]

    factor_collection = database[
        subject.PRIVILEGED_FACTOR_CURRENTNESS_COLLECTION
    ]
    assert factor_collection.index_names == [
        "priv_factor_reference_unique",
        "priv_factor_principal_session_time",
        "priv_factor_status_time",
    ]


def test_startup_source_contains_no_security_evidence_issuance() -> None:
    import inspect

    source = inspect.getsource(
        subject.WilsyAPIServer
    )

    forbidden = (
        ".issue(",
        ".create_or_replay(",
        "session.start_transaction(",
        "role_assignment",
        "refresh_token",
        "financial_execution",
    )

    start = source[
        source.index(
            "async def start_database"
        ):
    ]

    for token in forbidden:
        assert token not in start.split(
            '@app.on_event("startup")',
            1,
        )[0]


def test_startup_bootstrap_uses_canonical_registry_collection_constants() -> None:
    import inspect

    source = inspect.getsource(
        subject
    )

    assert (
        "TENANT_AUTHORIZATION_DECISION_EVIDENCE_COLLECTION"
        in source
    )

    assert (
        "AUTHORIZATION_ROLE_REVOCATION_EVIDENCE_COLLECTION"
        in source
    )

    assert (
        "TenantAuthorizationDecisionEvidenceRegistry("
        in source
    )

    assert (
        "AuthorizationRoleRevocationEvidenceRegistry("
        in source
    )

    assert (
        "PRIVILEGED_FACTOR_CURRENTNESS_COLLECTION"
        in source
    )

    assert (
        "PrivilegedFactorVerificationCurrentnessRegistry("
        in source
    )


def test_otp_request_path_contains_no_factor_index_ddl() -> None:
    """Prove OTP success owns evidence writes but no collection index DDL."""
    import inspect

    from tools.eos.api import auth_router

    source = inspect.getsource(
        auth_router._create_factor_current_session
    )
    assert "ensure_indexes" not in source
    assert "create_index" not in source


# ARTIFACT: test_iam_security_evidence_startup_indexes.py
# VERSION: v1.0.0-P3-R3G-S5-A2-FACTOR-INDEX-BOOTSTRAP
# AUTHORITY BOUNDARY: Startup index observation only; no security evidence or authority issuance.
# TENANT POSTURE: No tenant-scoped mutation occurs.
# FAIL-CLOSED POSTURE: Missing startup DDL or request-path DDL fails certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
