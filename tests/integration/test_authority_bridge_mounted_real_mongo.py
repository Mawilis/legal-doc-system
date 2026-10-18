"""
TITLE:
    WILSY OS P3-R3G-S6-A3 Mounted Authority Bridge Real-Mongo HTTP Certificate

VERSION:
    v1.0.1-P3-R3G-S6-A3-MOUNTED-REAL-MONGO-HTTP

AUTHORITY:
    Wilsy OS Sovereign IAM Certification

EPITOME:
    Certify the actual mounted WilsyAPIServer internal authority bridge against
    UUID-isolated real MongoDB, including canonical trust-denial HTTP mapping.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authority_bridge_mounted_real_mongo.py

COLLABORATION / OWNERSHIP:
    Certificate only. Production runtime remains owned by WilsyAPIServer,
    authority_bridge_router, sovereign IAM repositories, and Kernel DB.

CERTIFICATION / UPDATE DATE:
    2026-10-14

CHANGELOG:
    v1.0.1-P3-R3G-S6-A3-MOUNTED-REAL-MONGO-HTTP
        Corrects the certificate's replay-index contract to preserve the
        canonical expiry TTL while retaining HTTP 401 expectations for genuine
        bad-signature and replay denials.

COMPLIANCE:
    WILSY OS Sovereign Code Governance Contract v1.2.0.

SECURITY / PRIVACY POSTURE:
    Disposable UUID-isolated real Mongo only. No raw workload secret or request
    signature may be durably persisted.

TENANT BOUNDARY:
    Service trust is not tenant authority. Human tenant authorization remains a
    distinct required gate before transaction commit.

AUTHORITY BOUNDARY:
    S6 assurance is security evidence, not role, permission, eligibility, or
    privileged activation authority.

FINANCIAL AUTHORITY BOUNDARY:
    No payment, settlement, paid, released, or financial execution truth is
    created. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

import os
import hashlib
import hmac
import importlib.util
import time
import uuid
from pathlib import Path
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from tools.eos.api import authority_bridge_router as bridge
from tools.eos.api import server as server_module
from tools.eos.api.exceptions import (
    ForbiddenOperationException,
    UnauthorizedAccessException,
)
from tools.eos.auth.internal_service_replay_registry import (
    COLLECTION as REPLAY_COLLECTION,
)
from tools.eos.auth.internal_service_trust import (
    body_sha3_512,
    canonical_request,
)
from tools.eos.auth.internal_service_workload_credential_registry import (
    COLLECTION as CREDENTIAL_COLLECTION,
    POINTER_COLLECTION as CREDENTIAL_POINTER_COLLECTION,
    InternalServiceWorkloadCredentialRegistry,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    COLLECTION as PROOF_COLLECTION,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    COLLECTION as WORKLOAD_COLLECTION,
)
from tools.eos.kernel import db as kernel_db


VERSION = (
    "v1.0.1-P3-R3G-S6-A3-"
    "MOUNTED-REAL-MONGO-HTTP"
)

MONGO_URI_BASE = os.environ["WILSY_VENDOR_CERT_MONGO_URI"]

ROUTE = (
    "/internal/authority/authorize"
)

BODY = (
    b'{"policy_id":"audit:read"}'
)


def _load_module(
    name: str,
    path: Path,
) -> Any:
    """Load one existing certificate helper module without mutating authority."""

    spec = (
        importlib.util
        .spec_from_file_location(
            name,
            path,
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise RuntimeError(
            "CERTIFICATE_HELPER_LOAD_FAILED"
        )

    module = (
        importlib.util
        .module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module


S6 = _load_module(
    "_wilsy_s6_existing_certificate",
    Path(
        "tests/integration/"
        "test_internal_service_workload_credential_authority_real_mongo.py"
    ),
)

MOUNTED = _load_module(
    "_wilsy_mounted_precedent",
    Path(
        "tests/integration/"
        "test_authorization_role_revocation_mounted_runtime_real_mongo.py"
    ),
)

SERVICE = S6.SERVICE
KEY = S6.KEY
SECRET = S6.SECRET
AUDIENCE = S6.AUDIENCE


def _mongo_uri(
    database_name: str,
) -> str:
    """Bind Kernel DB to one UUID-isolated sanctioned replica-set database."""

    base, separator, query = MONGO_URI_BASE.partition("?")
    normalized_base = base.rstrip("/") + "/"
    return (
        normalized_base
        + database_name
        + (
            "?" + query
            if separator
            else ""
        )
    )


@pytest.fixture()
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[
    dict[str, Any]
]:
    """Provide one disposable real-Mongo Kernel database and workload authority."""

    database_name = (
        "wilsy_p3_s6_a3_mounted_"
        + uuid.uuid4().hex
    )

    assert (
        database_name
        != "wilsy"
    )

    probe: MongoClient[Any] = (
        MongoClient(
            MONGO_URI_BASE,
            serverSelectionTimeoutMS=3000,
        )
    )

    hello = (
        probe.admin.command(
            "hello"
        )
    )

    assert (
        hello.get("setName")
        == "wilsyVendorCertRS"
    )

    assert (
        hello.get(
            "isWritablePrimary"
        )
        is True
    )

    database = (
        probe[database_name]
    )

    credentials = (
        InternalServiceWorkloadCredentialRegistry(
            database[
                CREDENTIAL_COLLECTION
            ],
            database[
                CREDENTIAL_POINTER_COLLECTION
            ],
        )
    )

    credentials.ensure_indexes()

    S6._provision(
        probe,
        database,
        credentials,
    )

    monkeypatch.setenv(
        "MONGODB_URI",
        _mongo_uri(
            database_name
        ),
    )

    monkeypatch.setenv(
        "WILSY_KENNEL_DB_TLS",
        "false",
    )

    monkeypatch.setenv(
        "WILSY_DUNNING_SCHEDULER_ENABLED",
        "false",
    )

    monkeypatch.setenv(
        "WILSY_INTERNAL_AUTH_SERVICE_ID",
        SERVICE,
    )

    monkeypatch.setenv(
        "WILSY_INTERNAL_AUTH_AUDIENCE",
        AUDIENCE,
    )

    monkeypatch.setenv(
        "WILSY_INTERNAL_AUTH_KEY_ID",
        KEY,
    )

    monkeypatch.setenv(
        "WILSY_INTERNAL_AUTH_SECRET",
        SECRET,
    )

    kernel_db.disconnect_db()

    try:
        yield {
            "probe": probe,
            "database": database,
            "database_name": database_name,
        }

    finally:
        kernel_db.disconnect_db()

        probe.drop_database(
            database_name
        )

        probe.close()


def _identity() -> Any:
    """Build the same bounded human identity used by the mounted precedent."""

    return MOUNTED._identity(
        "human-principal",
        "tenant-cert",
    )


def _signed_headers(
    *,
    body: bytes = BODY,
    nonce: str | None = None,
    valid_signature: bool = True,
) -> dict[str, str]:
    """Sign exact bytes for the actual mounted route."""

    timestamp = str(
        int(
            time.time()
        )
    )

    selected_nonce = (
        nonce
        or uuid.uuid4().hex
    )

    correlation = (
        "corr-"
        + uuid.uuid4().hex
    )

    digest = body_sha3_512(
        body
    )

    canonical = canonical_request(
        version="v1",
        service_id=SERVICE,
        audience=AUDIENCE,
        method="POST",
        path=ROUTE,
        timestamp=timestamp,
        nonce=selected_nonce,
        body_sha3_512_value=digest,
        correlation_id=correlation,
    )

    signature = hmac.new(
        SECRET.encode(),
        canonical,
        hashlib.sha256,
    ).hexdigest()

    if not valid_signature:
        signature = (
            "0" * 64
        )

    return {
        "X-Wilsy-Auth-Version":
            "v1",
        "X-Wilsy-Service-ID":
            SERVICE,
        "X-Wilsy-Audience":
            AUDIENCE,
        "X-Wilsy-Key-ID":
            KEY,
        "X-Wilsy-Timestamp":
            timestamp,
        "X-Wilsy-Nonce":
            selected_nonce,
        "X-Wilsy-Body-SHA3-512":
            digest,
        "X-Wilsy-Correlation-ID":
            correlation,
        "X-Wilsy-Signature":
            signature,
        "X-Tenant-ID":
            "tenant-cert",
        "Authorization":
            "Bearer certificate-seam",
        "Content-Type":
            "application/json",
    }


def _s6_counts(
    database: Any,
) -> dict[str, int]:
    """Return durable S6 transactional state created by request execution."""

    return {
        "replay":
            database[
                REPLAY_COLLECTION
            ].count_documents({}),
        "workload":
            database[
                WORKLOAD_COLLECTION
            ].count_documents({}),
        "proof":
            database[
                PROOF_COLLECTION
            ].count_documents({}),
        "evidence":
            database[
                EVIDENCE_COLLECTION
            ].count_documents({}),
    }


def _assert_zero_s6(
    database: Any,
) -> None:
    """Prove denial committed no request-scoped S6 state."""

    assert (
        _s6_counts(
            database
        )
        == {
            "replay": 0,
            "workload": 0,
            "proof": 0,
            "evidence": 0,
        }
    )


def _mounted_app(
    monkeypatch: pytest.MonkeyPatch,
    *,
    identity_denied: bool = False,
    tenant_denied: bool = False,
    policy_denied: bool = False,
) -> Any:
    """Build the real WilsyAPIServer while varying downstream authority outcomes."""

    identity = _identity()

    async def current_identity(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if identity_denied:
            raise (
                UnauthorizedAccessException(
                    "Certificate identity denial."
                )
            )

        return identity

    async def current_tenant(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if tenant_denied:
            raise (
                UnauthorizedAccessException(
                    "Certificate tenant denial."
                )
            )

        return identity

    async def authorize_policy(
        value: Any,
        policy_id: str,
    ) -> Any:
        assert (
            policy_id
            == "audit:read"
        )

        if policy_denied:
            raise (
                ForbiddenOperationException(
                    "Certificate policy denial."
                )
            )

        return value

    monkeypatch.setattr(
        bridge,
        "get_current_identity",
        current_identity,
    )

    monkeypatch.setattr(
        bridge,
        "get_current_tenant_identity",
        current_tenant,
    )

    monkeypatch.setattr(
        bridge,
        "_authorize_policy",
        authorize_policy,
    )

    app = (
        server_module
        .WilsyAPIServer(
            reasoning_provider_binding=None,
        )
        .get_app()
    )

    schema = app.openapi()

    assert (
        ROUTE
        in schema["paths"]
    )

    assert set(
        method.lower()
        for method
        in schema["paths"][ROUTE]
        if method.lower()
        in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
        }
    ) == {"post"}

    return app


def test_mounted_valid_signed_request_commits_all_s6_state(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove successful mounted HTTP authorization atomically commits S6."""

    database = (
        mongo_context[
            "database"
        ]
    )

    app = _mounted_app(
        monkeypatch
    )

    with TestClient(
        app
    ) as client:
        response = client.post(
            ROUTE,
            content=BODY,
            headers=
                _signed_headers(),
        )

    assert (
        response.status_code
        == 200
    ), response.text

    payload = (
        response.json()
    )

    assert (
        payload["allowed"]
        is True
    )

    assert (
        payload["tenant_id"]
        == "tenant-cert"
    )

    assert (
        _s6_counts(
            database
        )
        == {
            "replay": 1,
            "workload": 1,
            "proof": 1,
            "evidence": 1,
        }
    )

    rendered = repr(
        [
            database[name]
            .find_one({})
            for name in (
                REPLAY_COLLECTION,
                WORKLOAD_COLLECTION,
                PROOF_COLLECTION,
                EVIDENCE_COLLECTION,
            )
        ]
    )

    assert (
        SECRET
        not in rendered
    )

    assert (
        "X-Wilsy-Signature"
        not in rendered
    )


def test_mounted_second_identical_nonce_is_401_replay_denial_without_extra_state(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove canonical replay denial is HTTP 401 and does not add state."""

    database = (
        mongo_context[
            "database"
        ]
    )

    nonce = (
        uuid.uuid4().hex
    )

    headers = _signed_headers(
        nonce=nonce
    )

    app = _mounted_app(
        monkeypatch
    )

    with TestClient(
        app
    ) as client:
        first = client.post(
            ROUTE,
            content=BODY,
            headers=headers,
        )

        assert (
            first.status_code
            == 200
        ), first.text

        before = (
            _s6_counts(
                database
            )
        )

        second = client.post(
            ROUTE,
            content=BODY,
            headers=headers,
        )

    assert (
        second.status_code
        == 401
    ), second.text

    assert (
        _s6_counts(
            database
        )
        == before
    )


def test_mounted_bad_signature_is_401_and_commits_zero_s6_state(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove canonical bad-HMAC denial is HTTP 401 with zero S6 commit."""

    database = (
        mongo_context[
            "database"
        ]
    )

    app = _mounted_app(
        monkeypatch
    )

    with TestClient(
        app
    ) as client:
        response = client.post(
            ROUTE,
            content=BODY,
            headers=
                _signed_headers(
                    valid_signature=False
                ),
        )

    assert (
        response.status_code
        == 401
    ), response.text

    _assert_zero_s6(
        database
    )


@pytest.mark.parametrize(
    (
        "gate",
        "expected_status",
    ),
    (
        ("identity", 401),
        ("tenant", 401),
        ("policy", 403),
    ),
)
def test_mounted_downstream_denial_aborts_prior_s6_writes(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    gate: str,
    expected_status: int,
) -> None:
    """Prove S6 remains uncommitted through identity, tenant, and policy gates."""

    database = (
        mongo_context[
            "database"
        ]
    )

    app = _mounted_app(
        monkeypatch,
        identity_denied=
            gate == "identity",
        tenant_denied=
            gate == "tenant",
        policy_denied=
            gate == "policy",
    )

    with TestClient(
        app
    ) as client:
        response = client.post(
            ROUTE,
            content=BODY,
            headers=
                _signed_headers(),
        )

    assert (
        response.status_code
        == expected_status
    ), response.text

    _assert_zero_s6(
        database
    )


def test_mounted_request_cannot_assert_principal_or_workload_proof(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove forged principal/proof fields cannot cross the mounted bridge."""

    database = (
        mongo_context[
            "database"
        ]
    )

    forged = (
        b'{"policy_id":"audit:read",'
        b'"principal_id":"forged",'
        b'"proof_reference":"forged"}'
    )

    app = _mounted_app(
        monkeypatch
    )

    with TestClient(
        app
    ) as client:
        response = client.post(
            ROUTE,
            content=forged,
            headers=
                _signed_headers(
                    body=forged
                ),
        )

    assert (
        response.status_code
        == 422
    ), response.text

    _assert_zero_s6(
        database
    )


def test_startup_owns_exact_s6_index_contract(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove startup owns S6 DDL and preserves canonical replay-expiry TTL."""

    database = (
        mongo_context[
            "database"
        ]
    )

    app = _mounted_app(
        monkeypatch
    )

    with TestClient(
        app
    ):
        pass

    replay_indexes = {
        row["name"]:
            row
        for row in (
            database[
                REPLAY_COLLECTION
            ].list_indexes()
        )
    }

    assert (
        replay_indexes[
            "internal_service_replay_identity_unique"
        ]["unique"]
        is True
    )

    assert (
        replay_indexes[
            "internal_service_replay_expiry_ttl"
        ]["expireAfterSeconds"]
        == 0
    )

    for collection_name in (
        CREDENTIAL_COLLECTION,
        CREDENTIAL_POINTER_COLLECTION,
        WORKLOAD_COLLECTION,
        PROOF_COLLECTION,
        EVIDENCE_COLLECTION,
    ):
        indexes = list(
            database[
                collection_name
            ].list_indexes()
        )

        assert (
            len(indexes) >= 1
        ), collection_name

    # Immutable/currentness and assurance evidence are not TTL-deleted.
    for collection_name in (
        WORKLOAD_COLLECTION,
        PROOF_COLLECTION,
        EVIDENCE_COLLECTION,
    ):
        for metadata in (
            database[
                collection_name
            ].list_indexes()
        ):
            assert (
                "expireAfterSeconds"
                not in metadata
            ), (
                collection_name,
                metadata,
            )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_authority_bridge_mounted_real_mongo.py
# VERSION: v1.0.1-P3-R3G-S6-A3-MOUNTED-REAL-MONGO-HTTP
# AUTHORITY BOUNDARY:
#   Certificate only; S6 assurance creates no tenant or privileged authority.
# TENANT POSTURE:
#   Tenant authorization remains a separate gate before transaction commit.
# FAIL-CLOSED POSTURE:
#   Trust, replay, identity, tenant, policy, and persistence failure reject.
# FINANCIAL EXECUTION AUTHORITY:
#   NONE. Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
