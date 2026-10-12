"""Direct certificate for Legal Storefront public-intent HTTP admission.

TITLE: Legal Storefront Public Intent HTTP Direct Certificate
VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify exact anonymous request shape, server-issued
         identity/time, normalized-contact SHA3-512 rate subject, rate-before-
         persistence ordering, caller-owned transaction behavior, bounded HTTP
         projections and strict exclusion of tenant, Legal, AI and financial
         authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_storefront_public_intent_http.py
COLLABORATION / OWNERSHIP: Certifies L8-9C transport/orchestration only.
                            L8-9A owns immutable public intent semantics,
                            L8-9B owns durable persistence, L8-9C0 owns request
                            density, and server mounting is a later gate.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP-CERT
           establishes direct HTTP admission certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic acquisition data only. No live customer,
                             credential, tenant, payment or secret material.
TENANT BOUNDARY: Explicitly pre-tenant; no tenant selector is accepted.
AUTHORITY BOUNDARY: Test evidence only; no production authority.
AI AUTHORITY BOUNDARY: WILSY AI is not invoked or mocked as admission authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from typing import Any, Iterator

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import tools.eos.api.legal_storefront_public_intent_router as subject
from tools.eos.legal_operations.registry.legal_storefront_public_intent_registry import (
    LegalStorefrontPublicIntentRegistryPersistenceError,
    LegalStorefrontPublicIntentRegistryRetryTransactionError,
)
from tools.eos.legal_operations.service.legal_storefront_public_intent_rate_limit import (
    LegalStorefrontPublicIntentRateLimitDependencyError,
    LegalStorefrontPublicIntentRateLimitedError,
)


FIXED_NOW = datetime(
    2026, 10, 12, 14, 30, 0,
    tzinfo=timezone.utc,
)
FIXED_ID = "WILSY-LSI-0123456789abcdef0123456789abcdef"

PAYLOAD = {
    "organization_name": "Wilsy Legal Practice",
    "contact_email": "LEGAL@EXAMPLE.COM",
    "industry": "Legal Services",
    "region": "ZA_GP",
}


class _Persisted:
    intent_id = FIXED_ID


class _Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.started = 0
        self.committed = 0
        self.aborted = 0

    def start_transaction(self) -> None:
        assert self.in_transaction is False
        self.in_transaction = True
        self.started += 1

    def commit_transaction(self) -> None:
        assert self.in_transaction is True
        self.in_transaction = False
        self.committed += 1

    def abort_transaction(self) -> None:
        assert self.in_transaction is True
        self.in_transaction = False
        self.aborted += 1


class _SessionContext:
    def __init__(self, session: _Session) -> None:
        self.session = session

    def __enter__(self) -> _Session:
        return self.session

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        tb: object,
    ) -> None:
        return None


class _Client:
    def __init__(self, session: _Session) -> None:
        self.session = session
        self.start_session_calls = 0

    def start_session(self) -> _SessionContext:
        self.start_session_calls += 1
        return _SessionContext(self.session)


class _Database:
    def __init__(self) -> None:
        self.requested: list[str] = []

    def __getitem__(self, name: str) -> object:
        self.requested.append(name)
        return object()


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(subject.router)
    return app


def _client() -> TestClient:
    return TestClient(_app())


def _install_success(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[_Session, _Client, _Database, list[tuple[str, Any]]]:
    session = _Session()
    client = _Client(session)
    database = _Database()
    calls: list[tuple[str, Any]] = []

    monkeypatch.setattr(subject, "_now", lambda: FIXED_NOW)
    monkeypatch.setattr(subject, "_intent_id", lambda: FIXED_ID)
    monkeypatch.setattr(
        subject,
        "_handles",
        lambda: (client, database),
    )

    def fake_rate(
        *,
        subject_digest: str,
        observed_at: datetime,
    ) -> None:
        calls.append(
            (
                "rate",
                (subject_digest, observed_at),
            )
        )

    class _RateGate:
        def __init__(self, collection: object) -> None:
            calls.append(("rate_collection", collection))

        require_allowed = staticmethod(fake_rate)

    monkeypatch.setattr(
        subject,
        "LegalStorefrontPublicIntentRateLimit",
        _RateGate,
    )

    def fake_admit(
        *,
        database: Any,
        session: Any,
        intent: Any,
    ) -> _Persisted:
        calls.append(
            (
                "persist",
                (database, session, intent),
            )
        )
        assert session.in_transaction is True
        return _Persisted()

    monkeypatch.setattr(
        subject,
        "_admit_in_transaction",
        fake_admit,
    )

    return session, client, database, calls


def test_exact_route_and_method() -> None:
    routes = {
        (
            route.path,
            tuple(sorted(route.methods or set())),
        )
        for route in subject.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/legal-storefront/public-intents"
    }

    assert routes == {
        (
            "/legal-storefront/public-intents",
            ("POST",),
        )
    }


def test_success_is_202_with_bounded_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session, client, _, calls = _install_success(monkeypatch)

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 202
    assert response.json() == {
        "status": "ACCEPTED",
        "intentId": FIXED_ID,
    }

    assert client.start_session_calls == 1
    assert session.started == 1
    assert session.committed == 1
    assert session.aborted == 0

    rate_calls = [
        entry
        for entry in calls
        if entry[0] == "rate"
    ]
    persist_calls = [
        entry
        for entry in calls
        if entry[0] == "persist"
    ]

    assert len(rate_calls) == 1
    assert len(persist_calls) == 1

    expected_digest = hashlib.sha3_512(
        b"legal@example.com"
    ).hexdigest()

    digest, observed_at = rate_calls[0][1]
    assert digest == expected_digest
    assert observed_at == FIXED_NOW

    persisted_intent = persist_calls[0][1][2]
    assert persisted_intent.intent_id == FIXED_ID
    assert persisted_intent.submitted_at == FIXED_NOW
    assert persisted_intent.contact_email == "legal@example.com"


def test_rate_gate_runs_before_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, _, _, calls = _install_success(monkeypatch)

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 202

    ordered = [
        name
        for name, _ in calls
        if name in {"rate", "persist"}
    ]
    assert ordered == ["rate", "persist"]


@pytest.mark.parametrize(
    "extra",
    [
        {"tenant_id": "tenant-forbidden"},
        {"principal_id": "principal-forbidden"},
        {"password": "forbidden"},
        {"plan": "enterprise"},
        {"subscription_id": "sub-forbidden"},
        {"entitlement_id": "ent-forbidden"},
        {"case_matter_id": "matter-forbidden"},
        {"payment_id": "payment-forbidden"},
        {"ai_prompt": "forbidden"},
    ],
)
def test_authority_bearing_extra_fields_are_422(
    extra: dict[str, str],
) -> None:
    response = _client().post(
        "/legal-storefront/public-intents",
        json={**PAYLOAD, **extra},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    [
        "organization_name",
        "contact_email",
        "industry",
        "region",
    ],
)
def test_missing_required_field_is_422(
    field: str,
) -> None:
    payload = dict(PAYLOAD)
    payload.pop(field)

    response = _client().post(
        "/legal-storefront/public-intents",
        json=payload,
    )

    assert response.status_code == 422


def test_domain_validation_failure_is_bounded_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(subject, "_now", lambda: FIXED_NOW)
    monkeypatch.setattr(subject, "_intent_id", lambda: FIXED_ID)

    response = _client().post(
        "/legal-storefront/public-intents",
        json={
            **PAYLOAD,
            "contact_email": "not-an-email",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["code"] == (
        "L8_9A_CONTACT_EMAIL_INVALID"
    )


def test_persistence_unavailable_is_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(subject, "_now", lambda: FIXED_NOW)
    monkeypatch.setattr(subject, "_intent_id", lambda: FIXED_ID)
    monkeypatch.setattr(
        subject,
        "_handles",
        lambda: (None, None),
    )

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "L8_9C_PERSISTENCE_UNAVAILABLE"
        }
    }


def test_rate_limited_is_429_before_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    client = _Client(session)
    database = _Database()

    monkeypatch.setattr(subject, "_now", lambda: FIXED_NOW)
    monkeypatch.setattr(subject, "_intent_id", lambda: FIXED_ID)
    monkeypatch.setattr(
        subject,
        "_handles",
        lambda: (client, database),
    )

    class _RateGate:
        def __init__(self, collection: object) -> None:
            del collection

        @staticmethod
        def require_allowed(
            *,
            subject_digest: str,
            observed_at: datetime,
        ) -> None:
            del subject_digest, observed_at
            raise LegalStorefrontPublicIntentRateLimitedError(
                "L8_9C0_RATE_LIMITED"
            )

    monkeypatch.setattr(
        subject,
        "LegalStorefrontPublicIntentRateLimit",
        _RateGate,
    )

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 429
    assert response.json() == {
        "detail": {
            "code": "L8_9C0_RATE_LIMITED"
        }
    }
    assert client.start_session_calls == 0
    assert session.started == 0


def test_rate_dependency_failure_is_503_before_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    client = _Client(session)
    database = _Database()

    monkeypatch.setattr(subject, "_now", lambda: FIXED_NOW)
    monkeypatch.setattr(subject, "_intent_id", lambda: FIXED_ID)
    monkeypatch.setattr(
        subject,
        "_handles",
        lambda: (client, database),
    )

    class _RateGate:
        def __init__(self, collection: object) -> None:
            del collection

        @staticmethod
        def require_allowed(
            *,
            subject_digest: str,
            observed_at: datetime,
        ) -> None:
            del subject_digest, observed_at
            raise LegalStorefrontPublicIntentRateLimitDependencyError(
                "L8_9C0_WRITE_FAILED"
            )

    monkeypatch.setattr(
        subject,
        "LegalStorefrontPublicIntentRateLimit",
        _RateGate,
    )

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "L8_9C0_WRITE_FAILED"
        }
    }
    assert client.start_session_calls == 0


def test_registry_retry_aborts_and_returns_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session, _, _, _ = _install_success(monkeypatch)

    def fail_admit(
        *,
        database: Any,
        session: Any,
        intent: Any,
    ) -> Any:
        del database, session, intent
        raise LegalStorefrontPublicIntentRegistryRetryTransactionError(
            "L8_9B_RETRY_TRANSACTION"
        )

    monkeypatch.setattr(
        subject,
        "_admit_in_transaction",
        fail_admit,
    )

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "L8_9B_RETRY_TRANSACTION"
        }
    }
    assert session.started == 1
    assert session.committed == 0
    assert session.aborted == 1


def test_registry_failure_aborts_and_returns_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session, _, _, _ = _install_success(monkeypatch)

    def fail_admit(
        *,
        database: Any,
        session: Any,
        intent: Any,
    ) -> Any:
        del database, session, intent
        raise LegalStorefrontPublicIntentRegistryPersistenceError(
            "L8_9B_PERSISTENCE_UNAVAILABLE"
        )

    monkeypatch.setattr(
        subject,
        "_admit_in_transaction",
        fail_admit,
    )

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "L8_9B_PERSISTENCE_UNAVAILABLE"
        }
    }
    assert session.started == 1
    assert session.committed == 0
    assert session.aborted == 1


def test_unexpected_transaction_failure_aborts_and_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session, _, _, _ = _install_success(monkeypatch)

    def fail_admit(
        *,
        database: Any,
        session: Any,
        intent: Any,
    ) -> Any:
        del database, session, intent
        raise RuntimeError("synthetic-secret-detail")

    monkeypatch.setattr(
        subject,
        "_admit_in_transaction",
        fail_admit,
    )

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "L8_9C_PERSISTENCE_UNAVAILABLE"
        }
    }
    assert "synthetic-secret-detail" not in response.text
    assert session.aborted == 1


def test_success_response_contains_no_authority_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_success(monkeypatch)

    response = _client().post(
        "/legal-storefront/public-intents",
        json=PAYLOAD,
    )

    body = response.json()
    assert set(body) == {
        "status",
        "intentId",
    }

    forbidden = {
        "tenantId",
        "tenant_id",
        "principalId",
        "principal_id",
        "role",
        "permissions",
        "plan",
        "subscription",
        "entitlement",
        "instruction",
        "matter",
        "document",
        "invoice",
        "payment",
        "settlement",
        "ai",
        "aiResult",
    }
    assert forbidden.isdisjoint(body)


def test_router_has_no_auth_or_ai_dependency() -> None:
    route = next(
        route
        for route in subject.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/legal-storefront/public-intents"
    )

    dependency_calls = {
        getattr(dep.call, "__name__", repr(dep.call))
        for dep in route.dependant.dependencies
    }

    assert dependency_calls == set()


# ARTIFACT: test_legal_storefront_public_intent_http.py
# VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-HTTP-CERT
# AUTHORITY BOUNDARY: direct HTTP certificate only; no production authority
# TENANT POSTURE: pre-tenant; tenant selectors are rejected
# TRANSACTION POSTURE: rate gate precedes one caller-owned registry transaction
# AI POSTURE: no WILSY AI dependency or invocation
# PRIVACY POSTURE: normalized contact is hashed before entering rate capability
# FAIL-CLOSED POSTURE: validation, throttle and persistence failure never fabricate acceptance
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
