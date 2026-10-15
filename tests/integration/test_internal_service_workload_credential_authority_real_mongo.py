"""Real-Mongo P3-R3G-S6-A1 certificate for verified internal workload proofs.

TITLE: Internal-Service Workload Credential Authority Real-Mongo Certificate
VERSION: v1.0.0-P3-R3G-S6-A1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Disposable-replica-set proof of registry concurrency and verified workload-proof atomicity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_internal_service_workload_credential_authority_real_mongo.py
COLLABORATION / OWNERSHIP: EOS IAM authority and Mongo transaction certification.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-S6-A1 establishes real HMAC, replay, lifecycle, principal, rollback, and concurrency proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated database and synthetic secret; database is destroyed after each test.
TENANT BOUNDARY: Proves workload evidence contains and grants no tenant authority.
AUTHORITY BOUNDARY: Certification only; no provisioning endpoint or privileged activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import hashlib
import hmac
import time
import uuid
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.auth.internal_service_replay_registry import COLLECTION as REPLAY_COLLECTION, InternalServiceReplayRegistry
from tools.eos.auth.internal_service_trust import body_sha3_512, canonical_request
from tools.eos.auth.internal_service_workload_credential_authority import (
    PLATFORM_INTERNAL_SCOPE, InternalServiceWorkloadCredentialAuthority, WorkloadCredentialLifecycleStatus,
)
from tools.eos.auth.internal_service_workload_credential_registry import (
    COLLECTION, POINTER_COLLECTION, InternalServiceWorkloadCredentialConflictError,
    InternalServiceWorkloadCredentialNotCurrentError, InternalServiceWorkloadCredentialPersistedInvalidError,
    InternalServiceWorkloadCredentialTransactionRequiredError,
    InternalServiceWorkloadCredentialRegistry,
)
from tools.eos.auth.internal_service_workload_proof_service import (
    InternalServiceWorkloadProofDeniedError, InternalServiceWorkloadProofService,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import COLLECTION as PRINCIPAL_COLLECTION, PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    COLLECTION as WORKLOAD_COLLECTION, PrivilegedWorkloadTrustCurrentnessRegistry,
)

MONGO_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
SERVICE = "node-authority-bridge"
KEY = "key-current"
SECRET = "certificate-secret-not-persisted"
AUDIENCE = "python-authority"
NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def mongo_context():
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database = client["wilsy_p3_workload_authority_" + uuid.uuid4().hex]
    assert database.name != "wilsy"
    credentials = InternalServiceWorkloadCredentialRegistry(database[COLLECTION], database[POINTER_COLLECTION])
    workloads = PrivilegedWorkloadTrustCurrentnessRegistry(database[WORKLOAD_COLLECTION])
    credentials.ensure_indexes()
    workloads.ensure_indexes()
    InternalServiceReplayRegistry.ensure_indexes(database[REPLAY_COLLECTION])
    PrincipalAuthorityRepository.ensure_indexes(database[PRINCIPAL_COLLECTION])
    try:
        yield client, database, credentials, workloads
    finally:
        client.drop_database(database.name)
        client.close()


def _authority(*, key_id: str = KEY, principal_id: str = "principal-service", revision: int = 1) -> InternalServiceWorkloadCredentialAuthority:
    return InternalServiceWorkloadCredentialAuthority(
        service_id=SERVICE, key_id=key_id, principal_id=principal_id,
        credential_scope=PLATFORM_INTERNAL_SCOPE, credential_revision=revision, lifecycle_revision=1,
        lifecycle_status=WorkloadCredentialLifecycleStatus.CURRENT, status_changed_at=NOW,
    )


def _signed(*, key_id: str = KEY, nonce: str | None = None, audience: str = AUDIENCE, signature_valid: bool = True) -> dict[str, str]:
    stamp = str(int(time.time()))
    body = b'{"policy_id":"audit:read"}'
    request = {
        "version": "v1", "service_id": SERVICE, "audience": audience, "key_id": key_id,
        "method": "POST", "path": "/api/internal/authority/authorize", "timestamp": stamp,
        "nonce": nonce or uuid.uuid4().hex, "body_sha3_512": body_sha3_512(body),
        "correlation_id": "corr-" + uuid.uuid4().hex,
    }
    canonical = canonical_request(
        version=request["version"], service_id=request["service_id"], audience=request["audience"],
        method=request["method"], path=request["path"], timestamp=request["timestamp"], nonce=request["nonce"],
        body_sha3_512_value=request["body_sha3_512"], correlation_id=request["correlation_id"],
    )
    request["signature"] = hmac.new(SECRET.encode(), canonical, hashlib.sha256).hexdigest()
    if not signature_valid:
        request["signature"] = "0" * 64
    return request


def _provision(client: MongoClient[Any], database: Any, credentials: InternalServiceWorkloadCredentialRegistry, *,
               principal_status: PrincipalStatus = PrincipalStatus.ACTIVE, authority: InternalServiceWorkloadCredentialAuthority | None = None) -> None:
    selected = authority or _authority()
    with client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(selected.principal_id, principal_status, 1), database[PRINCIPAL_COLLECTION], session=session,
            )
            credentials.create_or_replay(selected, session=session)


def _service(database: Any, credentials: InternalServiceWorkloadCredentialRegistry,
             workloads: PrivilegedWorkloadTrustCurrentnessRegistry, *, workload_registry: Any | None = None) -> InternalServiceWorkloadProofService:
    return InternalServiceWorkloadProofService(
        replay_collection=database[REPLAY_COLLECTION], credential_registry=credentials,
        principal_collection=database[PRINCIPAL_COLLECTION], workload_registry=workload_registry or workloads,
        clock=lambda: NOW,
    )


def _record(client: MongoClient[Any], service: InternalServiceWorkloadProofService, request: dict[str, str], *,
            keys: dict[str, tuple[str, str]] | None = None, expected_audience: str = AUDIENCE):
    with client.start_session() as session:
        with session.start_transaction():
            return service.verify_and_record(
                request=request, body=b'{"policy_id":"audit:read"}', keys=keys or {KEY: (SERVICE, SECRET)},
                expected_audience=expected_audience, session=session,
            )


def test_valid_hmac_current_binding_and_principal_create_one_server_owned_fact(mongo_context) -> None:
    client, database, credentials, workloads = mongo_context
    _provision(client, database, credentials)
    request = _signed()
    fact = _record(client, _service(database, credentials, workloads), request)
    assert fact.principal_id == "principal-service"
    assert fact.proof_reference.startswith("WILSYWORKLOAD-")
    assert fact.proof_reference not in request.values()
    assert database[WORKLOAD_COLLECTION].count_documents({}) == 1
    persisted = database[WORKLOAD_COLLECTION].find_one({})
    assert persisted is not None
    assert SECRET not in repr(persisted)
    assert request["signature"] not in repr(persisted)
    assert "tenant_id" not in persisted


@pytest.mark.parametrize("case", ["unknown-key", "service-key-mismatch", "revoked", "rotated", "invalidated", "principal-revoked", "signature", "scope"])
def test_denials_create_zero_workload_proof(mongo_context, case: str) -> None:
    client, database, credentials, workloads = mongo_context
    principal_status = PrincipalStatus.REVOKED if case == "principal-revoked" else PrincipalStatus.ACTIVE
    _provision(client, database, credentials, principal_status=principal_status)
    if case in {"revoked", "rotated", "invalidated"}:
        target = WorkloadCredentialLifecycleStatus(case.upper())
        with client.start_session() as session:
            with session.start_transaction():
                credentials.transition(service_id=SERVICE, key_id=KEY, target_status=target, changed_at=NOW, session=session)
    request = _signed(key_id="unknown" if case == "unknown-key" else KEY, signature_valid=case != "signature")
    keys = {"unknown": (SERVICE, SECRET)} if case == "unknown-key" else {KEY: ("different-service" if case == "service-key-mismatch" else SERVICE, SECRET)}
    expected = "different-audience" if case == "scope" else AUDIENCE
    with pytest.raises(InternalServiceWorkloadProofDeniedError):
        _record(client, _service(database, credentials, workloads), request, keys=keys, expected_audience=expected)
    assert database[WORKLOAD_COLLECTION].count_documents({}) == 0
    assert database[REPLAY_COLLECTION].count_documents({}) == 0


def test_replay_denies_second_proof(mongo_context) -> None:
    client, database, credentials, workloads = mongo_context
    _provision(client, database, credentials)
    service = _service(database, credentials, workloads)
    request = _signed(nonce="a" * 32)
    _record(client, service, request)
    with pytest.raises(InternalServiceWorkloadProofDeniedError):
        _record(client, service, request)
    assert database[WORKLOAD_COLLECTION].count_documents({}) == 1
    assert database[REPLAY_COLLECTION].count_documents({}) == 1


def test_rotation_rejects_old_key_and_admits_new_generation(mongo_context) -> None:
    client, database, credentials, workloads = mongo_context
    _provision(client, database, credentials)
    with client.start_session() as session:
        with session.start_transaction():
            new = credentials.rotate(service_id=SERVICE, key_id=KEY, next_key_id="key-next", changed_at=NOW, session=session)
    assert new.credential_revision == 2
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(InternalServiceWorkloadCredentialNotCurrentError):
                credentials.resolve_current(service_id=SERVICE, key_id=KEY, session=session)
    with pytest.raises(InternalServiceWorkloadProofDeniedError):
        _record(client, _service(database, credentials, workloads), _signed())
    fact = _record(
        client, _service(database, credentials, workloads), _signed(key_id="key-next"),
        keys={"key-next": (SERVICE, SECRET)},
    )
    assert fact.credential_or_attestation_reference == new.authority_fingerprint


def test_forced_post_insert_failure_aborts_replay_and_workload_fact(mongo_context) -> None:
    client, database, credentials, workloads = mongo_context
    _provision(client, database, credentials)

    class FailingWorkloads:
        def create_or_replay(self, fact: Any, *, recorded_at: datetime, session: object):
            workloads.create_or_replay(fact, recorded_at=recorded_at, session=session)
            raise RuntimeError("forced-boundary-failure")

    with pytest.raises(InternalServiceWorkloadProofDeniedError):
        _record(client, _service(database, credentials, workloads, workload_registry=FailingWorkloads()), _signed())
    assert database[WORKLOAD_COLLECTION].count_documents({}) == 0
    assert database[REPLAY_COLLECTION].count_documents({}) == 0


def test_indexes_are_explicit_unique_and_never_ttl(mongo_context) -> None:
    _client, database, _credentials, _workloads = mongo_context
    history = {item["name"]: item for item in database[COLLECTION].list_indexes()}
    pointers = {item["name"]: item for item in database[POINTER_COLLECTION].list_indexes()}
    assert history["internal_workload_credential_lifecycle_unique"]["unique"] is True
    assert history["internal_workload_credential_fingerprint_unique"]["unique"] is True
    assert pointers["internal_workload_credential_current_unique"]["unique"] is True
    assert all("expireAfterSeconds" not in item for item in [*history.values(), *pointers.values()])


def test_registry_requires_transaction_replays_exactly_and_rejects_divergence(mongo_context) -> None:
    client, database, credentials, _workloads = mongo_context
    authority = _authority()
    with pytest.raises(InternalServiceWorkloadCredentialTransactionRequiredError):
        credentials.create_or_replay(authority, session=None)
    with client.start_session() as session:
        with session.start_transaction():
            assert credentials.create_or_replay(authority, session=session) == authority
    with client.start_session() as session:
        with session.start_transaction():
            assert credentials.create_or_replay(authority, session=session) == authority
    divergent = _authority(principal_id="different-principal")
    with pytest.raises(InternalServiceWorkloadCredentialConflictError):
        with client.start_session() as session:
            with session.start_transaction():
                credentials.create_or_replay(divergent, session=session)
    assert database[COLLECTION].count_documents({}) == 1


def test_corrupt_current_pointer_is_rejected(mongo_context) -> None:
    client, database, credentials, _workloads = mongo_context
    with client.start_session() as session:
        with session.start_transaction():
            credentials.create_or_replay(_authority(), session=session)
    database[POINTER_COLLECTION].update_one({"service_id": SERVICE, "key_id": KEY}, {"$set": {"principal_id": "corrupt"}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(InternalServiceWorkloadCredentialPersistedInvalidError):
                credentials.resolve_current(service_id=SERVICE, key_id=KEY, session=session)


def test_competing_terminal_mutations_serialize_to_one_winner(mongo_context) -> None:
    client, database, credentials, _workloads = mongo_context
    with client.start_session() as session:
        with session.start_transaction():
            credentials.create_or_replay(_authority(), session=session)
    barrier = Barrier(2)

    def mutate(status: WorkloadCredentialLifecycleStatus) -> str:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait(timeout=5)
                    credentials.transition(service_id=SERVICE, key_id=KEY, target_status=status, changed_at=NOW, session=session)
            return "COMMIT"
        except Exception as error:
            if getattr(error, "has_error_label", lambda _label: False)("TransientTransactionError"):
                return "CONFLICT"
            if isinstance(error, (InternalServiceWorkloadCredentialConflictError, InternalServiceWorkloadCredentialNotCurrentError)):
                return "CONFLICT"
            raise

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(mutate, [WorkloadCredentialLifecycleStatus.REVOKED, WorkloadCredentialLifecycleStatus.INVALIDATED]))
    assert outcomes.count("COMMIT") == 1
    assert outcomes.count("CONFLICT") == 1
    assert database[COLLECTION].count_documents({}) == 2


# ARTIFACT: test_internal_service_workload_credential_authority_real_mongo.py
# VERSION: v1.0.0-P3-R3G-S6-A1
# AUTHORITY BOUNDARY: Real-Mongo certification only; creates no production authority.
# TENANT POSTURE: No tenant authority; disposable database only.
# FAIL-CLOSED POSTURE: Infrastructure absence, skips, denial writes, or partial commits fail certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT



# ============================================================================
# WILSY_P3_R3G_S6_A2_ATOMIC_NONINTERACTIVE_ASSURANCE_CERTIFICATE
# ============================================================================

from tools.eos.auth.internal_service_noninteractive_assurance_service import (
    InternalServiceNoninteractiveAssuranceService,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    COLLECTION as NONINTERACTIVE_PROOF_COLLECTION,
    PrivilegedNoninteractiveSecurityProofRegistry,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as ASSURANCE_EVIDENCE_COLLECTION,
    PrivilegedSecurityAssuranceEvidenceRegistry,
)


S6_A2_BODY = b'{"policy_id":"audit:read"}'


def _s6_a2_service(
    database: Any,
    credentials:
        InternalServiceWorkloadCredentialRegistry,
    workloads:
        PrivilegedWorkloadTrustCurrentnessRegistry,
    *,
    evidence_registry:
        Any | None = None,
) -> (
    InternalServiceNoninteractiveAssuranceService
):
    proof_registry = (
        PrivilegedNoninteractiveSecurityProofRegistry(
            database[
                NONINTERACTIVE_PROOF_COLLECTION
            ]
        )
    )

    assurance_registry = (
        evidence_registry
        if evidence_registry is not None
        else (
            PrivilegedSecurityAssuranceEvidenceRegistry(
                database[
                    ASSURANCE_EVIDENCE_COLLECTION
                ]
            )
        )
    )

    proof_registry.ensure_indexes()

    if evidence_registry is None:
        assurance_registry.ensure_indexes()

    return (
        InternalServiceNoninteractiveAssuranceService(
            workload_source=
                _service(
                    database,
                    credentials,
                    workloads,
                ),
            workload_registry=
                workloads,
            proof_registry=
                proof_registry,
            evidence_registry=
                assurance_registry,
            clock=lambda: NOW,
        )
    )


def _s6_a2_compose(
    client: MongoClient[Any],
    service:
        InternalServiceNoninteractiveAssuranceService,
    request: dict[str, str],
    *,
    idempotency_key: str,
):
    holder: dict[str, Any] = {}

    def callback(
        session,
    ):
        holder["result"] = (
            service.compose(
                request=request,
                body=S6_A2_BODY,
                keys={
                    KEY: (
                        SERVICE,
                        SECRET,
                    )
                },
                expected_audience=
                    AUDIENCE,
                assurance_purpose=(
                    PrivilegedAssurancePurpose
                    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
                ),
                idempotency_key=
                    idempotency_key,
                session=session,
            )
        )

    with client.start_session() as session:
        session.with_transaction(
            callback
        )

    return holder["result"]


def test_s6_a2_valid_hmac_atomically_creates_workload_proof_and_assurance(
    mongo_context,
) -> None:
    client, database, credentials, workloads = (
        mongo_context
    )

    _provision(
        client,
        database,
        credentials,
    )

    request = _signed()

    result = _s6_a2_compose(
        client,
        _s6_a2_service(
            database,
            credentials,
            workloads,
        ),
        request,
        idempotency_key=
            "s6-a2-success",
    )

    assert (
        result.decision.sufficient
        is True
    )

    assert (
        result
        .decision
        .assurance_channel
        is PrivilegedAssuranceChannel
        .NONINTERACTIVE_WORKLOAD_PROOF
    )

    assert (
        result
        .proof_snapshot
        .proof
        .principal_id
        == result
        .workload_fact
        .principal_id
    )

    assert (
        result
        .proof_snapshot
        .proof
        .proof_reference
        == result
        .workload_fact
        .proof_reference
    )

    assert (
        result
        .proof_snapshot
        .proof
        .credential_or_attestation_reference
        == result
        .workload_fact
        .credential_or_attestation_reference
    )

    assert (
        result
        .evidence
        .workload_proof_reference
        == result
        .workload_fact
        .proof_reference
    )

    assert (
        result
        .evidence
        .workload_proof_current
        is True
    )

    assert (
        database[
            WORKLOAD_COLLECTION
        ].count_documents({})
        == 1
    )

    assert (
        database[
            NONINTERACTIVE_PROOF_COLLECTION
        ].count_documents({})
        == 1
    )

    assert (
        database[
            ASSURANCE_EVIDENCE_COLLECTION
        ].count_documents({})
        == 1
    )

    durable = (
        repr(
            database[
                WORKLOAD_COLLECTION
            ].find_one({})
        )
        + repr(
            database[
                NONINTERACTIVE_PROOF_COLLECTION
            ].find_one({})
        )
        + repr(
            database[
                ASSURANCE_EVIDENCE_COLLECTION
            ].find_one({})
        )
    )

    assert SECRET not in durable
    assert (
        request["signature"]
        not in durable
    )


def test_s6_a2_invalid_signature_creates_zero_composed_state(
    mongo_context,
) -> None:
    client, database, credentials, workloads = (
        mongo_context
    )

    _provision(
        client,
        database,
        credentials,
    )

    request = _signed(
        signature_valid=False
    )

    with pytest.raises(
        InternalServiceWorkloadProofDeniedError
    ):
        _s6_a2_compose(
            client,
            _s6_a2_service(
                database,
                credentials,
                workloads,
            ),
            request,
            idempotency_key=
                "s6-a2-invalid-signature",
        )

    assert (
        database[
            WORKLOAD_COLLECTION
        ].count_documents({})
        == 0
    )

    assert (
        database[
            NONINTERACTIVE_PROOF_COLLECTION
        ].count_documents({})
        == 0
    )

    assert (
        database[
            ASSURANCE_EVIDENCE_COLLECTION
        ].count_documents({})
        == 0
    )


class _S6A2FailingEvidenceRegistry:
    def create_or_replay(
        self,
        value,
        *,
        session,
    ):
        raise RuntimeError(
            "FORCED_S6_A2_EVIDENCE_"
            "PERSISTENCE_FAILURE"
        )


def test_s6_a2_post_proof_failure_aborts_all_prior_currentness_writes(
    mongo_context,
) -> None:
    client, database, credentials, workloads = (
        mongo_context
    )

    _provision(
        client,
        database,
        credentials,
    )

    request = _signed()

    service = _s6_a2_service(
        database,
        credentials,
        workloads,
        evidence_registry=
            _S6A2FailingEvidenceRegistry(),
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "FORCED_S6_A2_EVIDENCE_"
            "PERSISTENCE_FAILURE"
        ),
    ):
        _s6_a2_compose(
            client,
            service,
            request,
            idempotency_key=
                "s6-a2-rollback",
        )

    assert (
        database[
            REPLAY_COLLECTION
        ].count_documents({})
        == 0
    )

    assert (
        database[
            WORKLOAD_COLLECTION
        ].count_documents({})
        == 0
    )

    assert (
        database[
            NONINTERACTIVE_PROOF_COLLECTION
        ].count_documents({})
        == 0
    )

    assert (
        database[
            ASSURANCE_EVIDENCE_COLLECTION
        ].count_documents({})
        == 0
    )


def test_s6_a2_caller_cannot_supply_principal_or_proof_reference() -> None:
    import inspect

    parameters = set(
        inspect.signature(
            InternalServiceNoninteractiveAssuranceService
            .compose
        ).parameters
    )

    for forbidden in (
        "principal_id",
        "proof_reference",
        "workload_proof_reference",
        "proof_id",
        "assurance_evidence_id",
    ):
        assert forbidden not in parameters


# S6-A2:
# workload verification != tenant authority
# security assurance != privileged activation
# no role/permission/financial authority
# ============================================================================
