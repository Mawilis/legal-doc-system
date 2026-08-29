# -*- coding: utf-8 -*-
"""Governed construction candidate for Wilsy OS authentication outage certification.

TITLE: WILSY OS Authentication Outage Certification Controller
VERSION: v1.0.0-AUTH-OUTAGE-CERTIFICATION
AUTHORITY: Authentication outage certification orchestration, evidence validation, and certification verdict authority only.
EPITOME: A fail-closed EOS controller for deterministic certification of Node authentication behavior across deliberate loss and restoration of the disposable MongoDB certification topology.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/auth_outage_certification.py
COLLABORATION / OWNERSHIP: Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd); AI Collaborator: Core Systems Engineering Agent.
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0-AUTH-OUTAGE-CERTIFICATION establishes the initial governed controller contract for disposable Mongo lifecycle authority, Node runtime observation orchestration, deterministic certification evidence, and fail-closed authentication outage verdict derivation.
COMPLIANCE: Designed under the WILSY OS Sovereign Codex Governance Contract v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION. Certification requires complete runtime and sovereign artifact compliance; missing or malformed evidence must not become certification success.
SECURITY / PRIVACY POSTURE: Fail closed. Synthetic certification data only. Raw credentials, JWTs, authorization headers, passwords, password hashes, complete user documents, and designated-email identifiers are prohibited from canonical evidence.
TENANT BOUNDARY: The controller does not create tenant-membership authority. Any synthetic tenant-shaped fixture data exists only to satisfy real User-model construction requirements and must never be interpreted as governed tenant membership, role assignment, or authorization truth.
AUTHORITY BOUNDARY: Python owns certification lifecycle, Mongo lifecycle, scenario sequencing, raw-observation validation, evidence aggregation, derived authentication verdicts, and final restoration. The Node adapter is a foreign-runtime observation capability only and owns no Wilsy certification verdict.
FINANCIAL AUTHORITY BOUNDARY: None. This controller cannot approve, authorize, request, execute, observe as canonical truth, or settle financial execution. Kennel EOS remains the exclusive financial execution authority.

Public API posture:
    This module is intended to own the complete authentication outage
    certification state machine. It will control only the disposable
    certification MongoDB topology, will own the persistent Node observation
    subprocess, will sequence synthetic fixture operations, and will derive
    authentication certification truth only from validated raw observations.

    The controller must never infer a successful certification from missing
    evidence, infrastructure ambiguity, process failure, malformed protocol
    data, or persistence errors alone. Observation and certification verdict
    are distinct authorities.

Construction status:
    This file is currently a NON-AUTHORITATIVE SCRATCH CANDIDATE located
    outside the repository. The canonical path stated above is its intended
    future governed destination only. This scratch candidate has zero EOS
    authority until complete-file certification and atomic repository install.
"""

from __future__ import annotations

import errno
import json
import math
import os
import queue
import shutil
import socket
import subprocess
import threading
import time
import uuid

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha3_512
from pathlib import Path
from typing import Final, TypeGuard


VERSION: Final[str] = "v1.0.0-AUTH-OUTAGE-CERTIFICATION"
PROTOCOL_VERSION: Final[str] = "1"
EVIDENCE_SCHEMA_VERSION: Final[str] = (
    "WILSY-AUTH-OUTAGE-CERTIFICATION-EVIDENCE/V1"
)

MONGO_HOST: Final[str] = "127.0.0.1"
MONGO_PORT: Final[int] = 27027
MONGO_REPLICA_SET: Final[str] = "wilsyVendorCertRS"
MONGO_DB_PATH: Final[Path] = Path("/private/tmp/wilsy-node-auth-mongo-27027")
MONGO_LOG_PATH: Final[Path] = MONGO_DB_PATH / "mongod.log"
CERTIFICATION_DATABASE: Final[str] = "wilsy_node_auth_cert"

MONGOD_BINARY: Final[Path] = Path("/opt/homebrew/bin/mongod")
MONGOSH_BINARY: Final[Path] = Path("/opt/homebrew/bin/mongosh")

READINESS_DEADLINE_SECONDS: Final[float] = 30.0
POLL_INTERVAL_SECONDS: Final[float] = 0.25
LISTENER_PROBE_TIMEOUT_SECONDS: Final[float] = 0.5
MONGO_COMMAND_TIMEOUT_SECONDS: Final[float] = 5.0
NODE_VERSION_TIMEOUT_SECONDS: Final[float] = 5.0
ADAPTER_RESPONSE_TIMEOUT_SECONDS: Final[float] = 20.0
ADAPTER_PROCESS_EXIT_TIMEOUT_SECONDS: Final[float] = 5.0
ADAPTER_READER_QUEUE_CAPACITY: Final[int] = 32
ADAPTER_READER_POLL_SECONDS: Final[float] = 0.25
JSON_PROTOCOL_MAX_DEPTH: Final[int] = 32
NODE_SELECTION_TIMEOUT_MS: Final[int] = 1500
NODE_HEARTBEAT_FREQUENCY_MS: Final[int] = 500

CANONICAL_REPOSITORY_ROOT: Final[Path] = Path(
    "/Users/wilsonkhanyezi/legal-doc-system"
)
NODE_ADAPTER_RELATIVE_PATH: Final[Path] = Path(
    "server/tests/security/helpers/authPersistenceOutage.child.mjs"
)

PROTOCOL_COMMANDS: Final[tuple[str, ...]] = (
    "INITIALIZE_RUNTIME",
    "PROVISION_FIXTURE",
    "LOOKUP_FIXTURE",
    "DELETE_FIXTURE",
    "RUN_SCENARIO",
    "CLOSE_RUNTIME",
)

FORBIDDEN_EVIDENCE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "authorization",
        "designated_email",
        "full_user",
        "jwt",
        "jwt_secret",
        "password",
        "password_hash",
        "passwordhash",
        "raw_user",
        "token",
    }
)


AUTH_SCENARIO_CANONICAL_ORDER: Final[tuple[str, ...]] = (
    "PRIMARY_USER_FOUND",
    "PRIMARY_SOVEREIGN_USER_FOUND",
    "SECONDARY_USER_FOUND",
    "PRIMARY_DB_FAILURE",
    "PRIMARY_PRIVILEGED_ROLE_DB_FAILURE",
    "PRIMARY_SECURITY_CLEARANCE_DB_FAILURE",
    "PRIMARY_TENANT_DB_FAILURE",
    "PRIMARY_SOVEREIGN_DB_FAILURE",
    "SECONDARY_DB_FAILURE",
    "SECONDARY_PRIVILEGED_ROLE_DB_FAILURE",
    "DESIGNATED_EMAIL_DB_FAILURE",
    "SECONDARY_SECURITY_CLEARANCE_DB_FAILURE",
    "SECONDARY_TENANT_DB_FAILURE",
)

POSITIVE_SCENARIO_IDS: Final[frozenset[str]] = frozenset(
    AUTH_SCENARIO_CANONICAL_ORDER[:3]
)

OUTAGE_SCENARIO_IDS: Final[frozenset[str]] = frozenset(
    AUTH_SCENARIO_CANONICAL_ORDER[3:]
)

ALL_AUTH_SCENARIO_IDS: Final[frozenset[str]] = frozenset(
    AUTH_SCENARIO_CANONICAL_ORDER
)

PERSISTENCE_DIAGNOSTIC_MAX_LENGTH: Final[int] = 240


class MongoLifecycleState(StrEnum):
    """Closed lifecycle vocabulary for the disposable certification Mongo topology.

    Authority:
        Identifies controller-observed certification Mongo lifecycle state only.

    Tenant scope:
        None. The state describes host certification infrastructure and cannot
        establish tenant identity or membership.

    Mutation semantics:
        This enum performs no mutation. Lifecycle transition authority belongs
        to the certification controller.

    Fail-closed behavior:
        Unknown lifecycle values must not be accepted as valid lifecycle truth.

    Financial boundary:
        None. Mongo lifecycle state conveys no financial execution authority.
    """

    UNKNOWN = "UNKNOWN"
    STARTING = "STARTING"
    PRIMARY_READY = "PRIMARY_READY"
    STOPPING = "STOPPING"
    DOWN = "DOWN"
    RESTARTING = "RESTARTING"
    RECOVERING = "RECOVERING"
    RESTORED = "RESTORED"
    RESTORATION_FAILED = "RESTORATION_FAILED"


class ReadinessPhase(StrEnum):
    """Closed lifecycle phase vocabulary for bounded Mongo readiness.

    The phase determines timeout classification and final lifecycle identity.
    It does not modify Mongo and does not establish tenant, authentication, or
    financial authority.
    """

    STARTUP = "STARTUP"
    RECOVERY = "RECOVERY"
    RESTORATION = "RESTORATION"


class CertificationStatus(StrEnum):
    """Closed final certification status vocabulary.

    CERTIFIED requires complete admissible evidence plus successful cleanup and
    final restoration. FAILED is reserved for an admissible proven security
    failure such as authenticated continuation during a denial-required outage.
    BLOCKED represents an environment, protocol, fixture, observation, cleanup,
    or restoration blocker. NOT_READY represents structural/governance
    preconditions that prevent runtime certification from beginning.
    """

    CERTIFIED = "CERTIFIED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"


class AdapterResponseType(StrEnum):
    """Closed foreign-runtime response vocabulary for the JSONL protocol.

    These values classify protocol message shape only. They carry no
    authentication, tenant, financial, or certification verdict authority.
    """

    READY = "READY"
    RESULT = "RESULT"
    ERROR = "ERROR"
    SHUTDOWN_COMPLETE = "SHUTDOWN_COMPLETE"


class AdapterReaderEventKind(StrEnum):
    """Closed transport-event vocabulary emitted by the stdout reader thread."""

    LINE = "LINE"
    EOF = "EOF"
    ERROR = "ERROR"


class ScenarioClass(StrEnum):
    """Closed semantic class for authentication certification scenarios."""

    POSITIVE = "POSITIVE"
    OUTAGE = "OUTAGE"


class PersistenceEvidenceState(StrEnum):
    """Whether raw persistence evidence is absent, recognized, or unknown."""

    NONE = "NONE"
    RECOGNIZED = "RECOGNIZED"
    UNRECOGNIZED = "UNRECOGNIZED"


class PositiveControlStatus(StrEnum):
    """Python-derived positive-control result vocabulary."""

    PASS = "PASS"
    FAIL = "FAIL"
    EVIDENCE_INCOMPLETE = "EVIDENCE_INCOMPLETE"


class OutageScenarioStatus(StrEnum):
    """Python-derived outage result vocabulary."""

    FAIL_OPEN = "FAIL_OPEN"
    FAIL_CLOSED = "FAIL_CLOSED"
    EVIDENCE_INCOMPLETE = "EVIDENCE_INCOMPLETE"


class PersistenceFailureCategory(StrEnum):
    """Normalized persistence-unavailability evidence categories.

    These values describe the database condition observed by the Node runtime.
    They do not independently establish an authentication verdict.
    """

    SERVER_SELECTION_UNAVAILABLE = "SERVER_SELECTION_UNAVAILABLE"
    TOPOLOGY_UNAVAILABLE = "TOPOLOGY_UNAVAILABLE"
    CONNECTION_REFUSED = "CONNECTION_REFUSED"


class AuthOutageCertificationError(RuntimeError):
    """Base structured failure for the authentication outage controller.

    Exceptions under this boundary represent certification machinery failure or
    incomplete authority evidence. They do not implicitly mean authentication
    FAIL_OPEN or FAIL_CLOSED.
    """


class ConfigurationError(AuthOutageCertificationError):
    """Raised when immutable certification configuration is invalid or unsafe."""


class ExecutableUnavailableError(AuthOutageCertificationError):
    """Raised when a required governed host executable cannot be resolved."""


class WrongReplicaSetError(AuthOutageCertificationError):
    """Raised when the observed Mongo listener belongs to an unexpected replica set."""


class StartupPrimaryTimeoutError(AuthOutageCertificationError):
    """Raised when initial certification Mongo readiness misses its bounded deadline."""


class ShutdownError(AuthOutageCertificationError):
    """Raised when the exact disposable Mongo topology cannot be safely stopped."""


class RestartError(AuthOutageCertificationError):
    """Raised when the exact disposable Mongo topology cannot be restarted."""


class RecoveryPrimaryTimeoutError(AuthOutageCertificationError):
    """Raised when recovery cannot establish the expected writable primary in time."""


class RestorationError(AuthOutageCertificationError):
    """Raised when final environment restoration cannot prove a healthy primary."""


class AdapterStartError(AuthOutageCertificationError):
    """Raised when the foreign-runtime Node observation adapter cannot start safely."""


class AdapterProtocolError(AuthOutageCertificationError):
    """Raised for malformed, mismatched, unsafe, or unsupported adapter protocol data."""


class AdapterRuntimeError(AuthOutageCertificationError):
    """Raised when the Node adapter reports a bounded runtime failure."""


class AdapterExitError(AuthOutageCertificationError):
    """Raised when the Node adapter exits outside an authorized shutdown transition."""


class ObservationTimeoutError(AuthOutageCertificationError):
    """Raised when a bounded adapter observation is not received before its deadline."""


class FixtureProvisionError(AuthOutageCertificationError):
    """Raised when the real User-model synthetic fixture cannot be durably provisioned."""


class FixtureLookupError(AuthOutageCertificationError):
    """Raised when fixture lookup cannot produce admissible real User-model evidence."""


class FixtureCleanupError(AuthOutageCertificationError):
    """Raised when the exact owned synthetic fixture cannot be deleted and proven absent."""


class EvidenceIncompleteError(AuthOutageCertificationError):
    """Raised when mandatory raw certification evidence is absent or incoherent."""


@dataclass(frozen=True, slots=True)
class MongoTopology:
    """Immutable identity of the disposable Mongo certification topology.

    Authority:
        Defines exactly which local topology this controller is permitted to
        inspect, start, stop, recover, and restore.

    Tenant scope:
        None.

    Mutation semantics:
        Immutable value object; process mutation is performed only by lifecycle
        functions that consume this identity.

    Fail-closed behavior:
        Runtime observations inconsistent with this identity must block
        certification.

    Financial boundary:
        None.
    """

    host: str
    port: int
    replica_set: str
    db_path: Path
    log_path: Path


@dataclass(frozen=True, slots=True)
class ReadinessObservation:
    """Immutable raw observation of certification Mongo readiness.

    The object records infrastructure facts only. Listener presence does not
    imply writable-primary authority, and writable-primary status is admissible
    only when replica-set identity also matches the governed topology.
    """

    lifecycle_state: MongoLifecycleState
    listener_present: bool
    set_name: str | None
    writable_primary: bool
    member_health: int | None
    elapsed_ms: int
    sanitized_error: str | None


@dataclass(frozen=True, slots=True)
class FixtureIdentity:
    """Minimal immutable identity of the transaction-owned synthetic User fixture.

    Canonical evidence retains only the durable identifier and certification
    database identity. Synthetic construction email and tenant-shaped fixture
    inputs are operational details and are not tenant or identity authority.
    """

    durable_user_id: str
    database_name: str


@dataclass(frozen=True, slots=True)
class AdapterObservation:
    """Validated raw observation returned by the foreign-runtime Node adapter.

    This object contains observed facts only. It cannot carry or establish a
    final Wilsy authentication certification verdict.
    """

    protocol_version: str
    scenario_id: str
    middleware_completed: bool
    next_count: int
    has_authenticated_user: bool
    http_status: int | None
    elapsed_ms: int
    response_code: str | None
    persistence_error_name: str | None
    persistence_error_category: str | None
    persistence_error_message_sanitized: str | None


@dataclass(frozen=True, slots=True)
class ScenarioObservation:
    """Immutable scenario evidence combining validated raw facts and persistence class.

    The persistence category is observational evidence about the intended input
    condition. Authentication truth remains a separately derived authority.
    """

    scenario_id: str
    adapter_observation: AdapterObservation
    persistence_category: PersistenceFailureCategory | None


@dataclass(frozen=True, slots=True)
class RestorationResult:
    """Immutable evidence that final certification infrastructure was restored.

    A successful result requires the expected listener, writable-primary state,
    and replica-set identity. Restoration failure prevents overall
    certification even if earlier authentication observations were otherwise
    admissible.
    """

    listener_present: bool
    writable_primary: bool
    set_name: str | None
    member_health: int | None
    healthy: bool
    elapsed_ms: int



@dataclass(frozen=True, slots=True)
class NodeRuntimeIdentity:
    """Immutable identity of the exact Node runtime used by certification.

    Authority:
        Records executable, runtime version, and foreign-runtime adapter path.

    Mutation semantics:
        None.

    Fail-closed behavior:
        Missing, non-executable, relative, or malformed runtime identity blocks
        adapter startup.

    Tenant and financial boundary:
        None.
    """

    executable: Path
    version: str
    adapter_path: Path

    def __post_init__(self) -> None:
        """Reject malformed runtime identity rather than inventing defaults."""

        if not self.executable.is_absolute():
            raise ConfigurationError("Node executable path must be absolute")
        if not self.adapter_path.is_absolute():
            raise ConfigurationError("Node adapter path must be absolute")
        if not self.version or self.version != self.version.strip():
            raise ConfigurationError(
                "Node runtime version must be a non-empty trimmed string"
            )


@dataclass(frozen=True, slots=True)
class AdapterProtocolResponse:
    """Validated transport response from the foreign-runtime adapter.

    The payload remains observational protocol data. This type does not derive
    or store Wilsy authentication certification truth.
    """

    protocol_version: str
    operation_id: str
    response_type: AdapterResponseType
    payload: object


@dataclass(frozen=True, slots=True)
class AdapterReaderEvent:
    """Immutable stdout-reader transport event.

    A reader event records one line, EOF, or one bounded reader failure.
    Reader-thread events contain no certification verdict.
    """

    kind: AdapterReaderEventKind
    line: str | None
    error_type: str | None
    error_message: str | None




@dataclass(frozen=True, slots=True)
class FixtureProvisionRequest:
    """Operational input for one transaction-owned synthetic User fixture.

    Authority:
        Construction input only. This object is not principal, tenant,
        membership, role, or authorization authority.

    Privacy posture:
        Synthetic values only. The synthetic email is operational input and
        must not enter canonical certification evidence.

    Financial boundary:
        None.
    """

    synthetic_email: str
    synthetic_tenant_value: str | None

    def __post_init__(self) -> None:
        """Reject malformed fixture construction values."""

        if (
            not self.synthetic_email
            or self.synthetic_email != self.synthetic_email.strip()
        ):
            raise FixtureProvisionError(
                "synthetic fixture email must be a non-empty trimmed string"
            )

        if self.synthetic_tenant_value is not None and (
            not self.synthetic_tenant_value
            or self.synthetic_tenant_value
            != self.synthetic_tenant_value.strip()
        ):
            raise FixtureProvisionError(
                "synthetic tenant-shaped fixture value must be trimmed and non-empty"
            )


@dataclass(frozen=True, slots=True)
class FixtureLookupResult:
    """Bounded result of one real User-model fixture lookup.

    The result records only exact fixture identity visibility. It does not carry
    a complete user document, authentication projection, membership authority,
    role assignment, or authorization truth.
    """

    requested_durable_user_id: str
    operation_succeeded: bool
    found: bool
    observed_durable_user_id: str | None
    database_name: str


@dataclass(frozen=True, slots=True)
class FixtureDeleteResult:
    """Bounded result of deleting one exact transaction-owned fixture."""

    durable_user_id: str
    operation_succeeded: bool
    deleted: bool
    database_name: str


@dataclass(frozen=True, slots=True)
class AdapterRuntimeReadiness:
    """Raw Node/Mongoose initialization facts for fixture-capable runtime use.

    These are runtime observations only. They do not establish authentication
    or certification verdicts.
    """

    node_version: str
    server_mongoose_ready_state: int
    user_db_ready_state: int
    same_mongoose_base: bool
    database_name: str




@dataclass(frozen=True, slots=True)
class PersistenceClassification:
    """Python-owned interpretation of raw persistence failure evidence."""

    state: PersistenceEvidenceState
    category: PersistenceFailureCategory | None
    reason: str


@dataclass(frozen=True, slots=True)
class PositiveControlResult:
    """Python-derived result for one healthy positive authentication control."""

    scenario_id: str
    status: PositiveControlStatus
    reason: str


@dataclass(frozen=True, slots=True)
class OutageScenarioResult:
    """Python-derived result for one persistence-outage authentication scenario."""

    scenario_id: str
    status: OutageScenarioStatus
    reason: str



@dataclass(frozen=True, slots=True)
class CertificationEvidence:
    """Digest-free semantic evidence owned by the Python controller.

    Canonical evidence preserves positive-control results and outage results as
    separate authorities. The SHA3-512 digest is intentionally excluded from
    this object and is computed over its explicit canonical semantic payload.

    Volatile elapsed timings, process IDs, operation IDs, timestamps, and
    scratch-path metadata are deliberately excluded from canonical digest
    material even when corresponding runtime observation objects retain some
    of those diagnostics.

    Tenant authority:
        None. Synthetic fixture tenant-shaped inputs are excluded.

    Financial authority:
        None.
    """

    schema_version: str
    controller_version: str
    protocol_version: str
    topology: MongoTopology
    fixture: FixtureIdentity | None
    lifecycle: tuple[ReadinessObservation, ...]
    observations: tuple[ScenarioObservation, ...]
    positive_controls: tuple[PositiveControlResult, ...]
    outage_results: tuple[OutageScenarioResult, ...]
    fixture_absence_proven: bool
    adapter_shutdown_proven: bool
    restoration: RestorationResult | None


@dataclass(frozen=True, slots=True)
class StructuredFailure:
    """Immutable bounded failure representation for compound certification outcomes.

    Separate instances preserve primary, fixture-cleanup, adapter-shutdown, and
    restoration failures without overwriting one another or collapsing them
    into an opaque concatenated string.
    """

    category: str
    error_type: str
    message: str


@dataclass(frozen=True, slots=True)
class CertificationResult:
    """Immutable outer certification result and provenance envelope.

    The result owns final status, the SHA3-512 digest of the digest-free
    canonical evidence payload, and separate structured failures. Positive
    control and outage-result authorities remain separately represented inside
    CertificationEvidence. Volatile execution metadata remains outside the
    canonical digest payload.
    """

    status: CertificationStatus
    evidence: CertificationEvidence
    evidence_sha3_512: str
    primary_failure: StructuredFailure | None
    fixture_cleanup_failure: StructuredFailure | None
    adapter_shutdown_failure: StructuredFailure | None
    restoration_failure: StructuredFailure | None


DEFAULT_TOPOLOGY: Final[MongoTopology] = MongoTopology(
    host=MONGO_HOST,
    port=MONGO_PORT,
    replica_set=MONGO_REPLICA_SET,
    db_path=MONGO_DB_PATH,
    log_path=MONGO_LOG_PATH,
)



def _sanitize_diagnostic(value: str | None, *, limit: int = 240) -> str | None:
    """Return a bounded single-line diagnostic without creating authority.

    The helper is intentionally conservative: diagnostics are evidence support,
    not business truth, and are bounded to prevent accidental unstructured
    disclosure in later certification output.
    """

    if value is None:
        return None

    normalized = " ".join(value.replace("\x00", "").split())
    if not normalized:
        return None
    return normalized[:limit]


def _require_executable(path: Path, *, label: str) -> None:
    """Fail closed unless an exact governed host executable is available.

    This function performs validation only. It does not search for or silently
    substitute a different binary.
    """

    if not path.is_file():
        raise ExecutableUnavailableError(
            f"{label} executable is unavailable at governed path: {path}"
        )
    if not os.access(path, os.X_OK):
        raise ExecutableUnavailableError(
            f"{label} executable is not executable at governed path: {path}"
        )


def validate_certification_configuration(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
) -> None:
    """Validate immutable host configuration before lifecycle mutation.

    Authority:
        Validates that the caller is targeting only the disposable Wilsy auth
        certification topology.

    Mutation semantics:
        None.

    Fail-closed behavior:
        Any topology drift, missing data directory, or unavailable governed
        executable blocks lifecycle mutation.

    Tenant and financial boundary:
        None. This validates local certification infrastructure only.
    """

    if topology != DEFAULT_TOPOLOGY:
        raise ConfigurationError(
            "certification topology does not equal the governed disposable topology"
        )

    if topology.host != MONGO_HOST:
        raise ConfigurationError("certification Mongo host is not governed")
    if topology.port != MONGO_PORT:
        raise ConfigurationError("certification Mongo port is not governed")
    if topology.replica_set != MONGO_REPLICA_SET:
        raise ConfigurationError("certification Mongo replica set is not governed")
    if topology.db_path != MONGO_DB_PATH:
        raise ConfigurationError("certification Mongo db path is not governed")
    if topology.log_path != MONGO_LOG_PATH:
        raise ConfigurationError("certification Mongo log path is not governed")

    if not topology.db_path.is_dir():
        raise ConfigurationError(
            f"certification Mongo db path does not exist: {topology.db_path}"
        )

    _require_executable(MONGOD_BINARY, label="mongod")
    _require_executable(MONGOSH_BINARY, label="mongosh")


def probe_listener(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
    *,
    timeout_seconds: float = LISTENER_PROBE_TIMEOUT_SECONDS,
) -> bool:
    """Observe whether the exact certification host/port accepts TCP.

    Listener presence is infrastructure evidence only and never implies Mongo
    identity, writable-primary authority, authentication truth, tenant truth,
    or certification success.
    """

    if timeout_seconds <= 0:
        raise ConfigurationError("listener probe timeout must be positive")

    try:
        with socket.create_connection(
            (topology.host, topology.port),
            timeout=timeout_seconds,
        ):
            return True
    except TimeoutError:
        return False
    except ConnectionRefusedError:
        return False
    except OSError as exc:
        if exc.errno in {errno.ECONNREFUSED, errno.ETIMEDOUT}:
            return False
        raise AuthOutageCertificationError(
            "unexpected listener probe failure: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc


def _mongo_uri(topology: MongoTopology, *, database: str = "admin") -> str:
    """Build the exact direct-connection URI for certification probes."""

    if not database or database != database.strip():
        raise ConfigurationError("Mongo probe database must be a trimmed value")

    return (
        f"mongodb://{topology.host}:{topology.port}/{database}"
        "?directConnection=true"
        "&serverSelectionTimeoutMS=1000"
    )


def _is_expected_transient_mongo_probe_failure(message: str) -> bool:
    """Classify only known readiness-time persistence transport failures.

    This is deliberately narrow. Unknown command, permission, parse, and
    executable failures are not converted into retryable readiness conditions.
    """

    lowered = message.casefold()
    signatures = (
        "econnrefused",
        "connection refused",
        "server selection timed out",
        "serverselectiontimeout",
        "mongoserverselectionerror",
        "replicasetnoprimary",
        "no primary",
        "connection closed",
        "socket exception",
        "network error",
    )
    return any(signature in lowered for signature in signatures)


def observe_mongo_readiness(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
    *,
    lifecycle_state: MongoLifecycleState = MongoLifecycleState.UNKNOWN,
) -> ReadinessObservation:
    """Observe listener, replica-set identity, writable-primary state, and health.

    The probe uses the governed ``mongosh`` binary and queries both ``hello()``
    and replica-set status. A wrong replica-set name is an authority mismatch
    and fails immediately. Expected startup/recovery transport failures are
    returned as non-ready observations; unexpected command failures propagate.
    """

    started = time.monotonic()

    if not probe_listener(topology):
        return ReadinessObservation(
            lifecycle_state=lifecycle_state,
            listener_present=False,
            set_name=None,
            writable_primary=False,
            member_health=None,
            elapsed_ms=int((time.monotonic() - started) * 1000),
            sanitized_error="listener unavailable",
        )

    javascript = (
        "const h=db.hello();"
        "const s=db.adminCommand({replSetGetStatus:1});"
        "const selfMember=Array.isArray(s.members)"
        "?s.members.find((m)=>m.self===true):null;"
        "print(JSON.stringify({"
        "setName:(h.setName??null),"
        "isWritablePrimary:(h.isWritablePrimary===true),"
        "memberHealth:(selfMember?.health??null)"
        "}));"
    )

    command = [
        str(MONGOSH_BINARY),
        _mongo_uri(topology),
        "--quiet",
        "--eval",
        javascript,
    ]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=MONGO_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        diagnostic = _sanitize_diagnostic(
            (exc.stderr or "") if isinstance(exc.stderr, str) else str(exc)
        )
        return ReadinessObservation(
            lifecycle_state=lifecycle_state,
            listener_present=True,
            set_name=None,
            writable_primary=False,
            member_health=None,
            elapsed_ms=int((time.monotonic() - started) * 1000),
            sanitized_error=diagnostic or "mongosh readiness probe timed out",
        )
    except OSError as exc:
        raise AuthOutageCertificationError(
            "mongosh readiness probe could not execute: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc

    if completed.returncode != 0:
        diagnostic = _sanitize_diagnostic(
            "\n".join(
                part
                for part in (completed.stdout, completed.stderr)
                if part and part.strip()
            )
        )
        message = diagnostic or f"mongosh exited {completed.returncode}"

        if _is_expected_transient_mongo_probe_failure(message):
            return ReadinessObservation(
                lifecycle_state=lifecycle_state,
                listener_present=True,
                set_name=None,
                writable_primary=False,
                member_health=None,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                sanitized_error=message,
            )

        raise AuthOutageCertificationError(
            f"unexpected mongosh readiness failure: {message}"
        )

    raw = completed.stdout.strip()
    if not raw:
        raise AuthOutageCertificationError(
            "mongosh readiness probe returned empty machine output"
        )

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuthOutageCertificationError(
            "mongosh readiness probe returned malformed JSON"
        ) from exc

    if not isinstance(parsed, dict):
        raise AuthOutageCertificationError(
            "mongosh readiness probe returned non-object JSON"
        )

    set_name_value = parsed.get("setName")
    writable_value = parsed.get("isWritablePrimary")
    health_value = parsed.get("memberHealth")

    if set_name_value is not None and not isinstance(set_name_value, str):
        raise AuthOutageCertificationError(
            "mongosh readiness setName has invalid type"
        )

    if not isinstance(writable_value, bool):
        raise AuthOutageCertificationError(
            "mongosh readiness writable-primary flag has invalid type"
        )

    if health_value is not None and (
        isinstance(health_value, bool) or not isinstance(health_value, int)
    ):
        raise AuthOutageCertificationError(
            "mongosh readiness member health has invalid type"
        )

    if set_name_value is not None and set_name_value != topology.replica_set:
        raise WrongReplicaSetError(
            "Mongo listener belongs to unexpected replica set: "
            f"{set_name_value!r}"
        )

    return ReadinessObservation(
        lifecycle_state=lifecycle_state,
        listener_present=True,
        set_name=set_name_value,
        writable_primary=writable_value,
        member_health=health_value,
        elapsed_ms=int((time.monotonic() - started) * 1000),
        sanitized_error=None,
    )


def _phase_probe_state(phase: ReadinessPhase) -> MongoLifecycleState:
    """Return the lifecycle state used while polling the requested phase."""

    if phase is ReadinessPhase.STARTUP:
        return MongoLifecycleState.STARTING
    if phase is ReadinessPhase.RECOVERY:
        return MongoLifecycleState.RECOVERING
    return MongoLifecycleState.RECOVERING


def _phase_ready_state(phase: ReadinessPhase) -> MongoLifecycleState:
    """Return the lifecycle state emitted once the requested phase is ready."""

    if phase is ReadinessPhase.STARTUP:
        return MongoLifecycleState.PRIMARY_READY
    return MongoLifecycleState.RESTORED


def wait_for_writable_primary(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
    *,
    phase: ReadinessPhase,
    deadline_seconds: float = READINESS_DEADLINE_SECONDS,
) -> ReadinessObservation:
    """Wait for the exact certification replica set to become healthy PRIMARY.

    Readiness requires all of:

    - listener present;
    - expected replica-set identity;
    - ``isWritablePrimary is True``;
    - local replica-set member health equal to ``1``.

    Timeout classification is phase-aware. No fixed delay is interpreted as
    readiness.
    """

    if deadline_seconds <= 0:
        raise ConfigurationError("readiness deadline must be positive")

    started = time.monotonic()
    last_observation: ReadinessObservation | None = None

    while True:
        elapsed = time.monotonic() - started
        if elapsed >= deadline_seconds:
            detail = (
                last_observation.sanitized_error
                if last_observation is not None
                else None
            )
            suffix = f": {detail}" if detail else ""

            if phase is ReadinessPhase.STARTUP:
                raise StartupPrimaryTimeoutError(
                    f"startup writable-primary deadline exceeded{suffix}"
                )
            if phase is ReadinessPhase.RECOVERY:
                raise RecoveryPrimaryTimeoutError(
                    f"recovery writable-primary deadline exceeded{suffix}"
                )
            raise RestorationError(
                f"final restoration writable-primary deadline exceeded{suffix}"
            )

        last_observation = observe_mongo_readiness(
            topology,
            lifecycle_state=_phase_probe_state(phase),
        )

        if (
            last_observation.listener_present
            and last_observation.set_name == topology.replica_set
            and last_observation.writable_primary
            and last_observation.member_health == 1
        ):
            return ReadinessObservation(
                lifecycle_state=_phase_ready_state(phase),
                listener_present=True,
                set_name=last_observation.set_name,
                writable_primary=True,
                member_health=1,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                sanitized_error=None,
            )

        remaining = deadline_seconds - (time.monotonic() - started)
        if remaining <= 0:
            continue
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))


def start_certification_mongo(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
    *,
    phase: ReadinessPhase = ReadinessPhase.STARTUP,
) -> ReadinessObservation:
    """Ensure the exact disposable Mongo topology is running and writable.

    The function does not restart an already healthy governed topology. If a
    listener exists, its Mongo identity must be established before any start
    operation is attempted. Only the exact certified ``mongod`` command may be
    launched.
    """

    validate_certification_configuration(topology)

    if probe_listener(topology):
        current = observe_mongo_readiness(
            topology,
            lifecycle_state=_phase_probe_state(phase),
        )
        if (
            current.set_name == topology.replica_set
            and current.writable_primary
            and current.member_health == 1
        ):
            return ReadinessObservation(
                lifecycle_state=_phase_ready_state(phase),
                listener_present=True,
                set_name=current.set_name,
                writable_primary=True,
                member_health=1,
                elapsed_ms=current.elapsed_ms,
                sanitized_error=None,
            )

        if current.set_name in {None, topology.replica_set}:
            return wait_for_writable_primary(
                topology,
                phase=phase,
            )

        raise WrongReplicaSetError(
            "listener exists but does not belong to the governed replica set"
        )

    command = [
        str(MONGOD_BINARY),
        "--dbpath",
        str(topology.db_path),
        "--port",
        str(topology.port),
        "--bind_ip",
        topology.host,
        "--replSet",
        topology.replica_set,
        "--logpath",
        str(topology.log_path),
        "--fork",
    ]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=MONGO_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RestartError(
            "governed mongod start command exceeded its bounded command timeout"
        ) from exc
    except OSError as exc:
        raise RestartError(
            "governed mongod start command could not execute: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc

    if completed.returncode != 0:
        diagnostic = _sanitize_diagnostic(
            "\n".join(
                part
                for part in (completed.stdout, completed.stderr)
                if part and part.strip()
            )
        )
        raise RestartError(
            "governed mongod start command failed"
            + (f": {diagnostic}" if diagnostic else "")
        )

    return wait_for_writable_primary(
        topology,
        phase=phase,
    )


def wait_for_listener_state(
    topology: MongoTopology,
    *,
    wanted: bool,
    deadline_seconds: float = READINESS_DEADLINE_SECONDS,
) -> int:
    """Wait until listener presence matches the requested infrastructure state.

    Returns elapsed milliseconds. This function proves port reachability only;
    it does not establish replica-set or writable-primary authority.
    """

    if deadline_seconds <= 0:
        raise ConfigurationError("listener-state deadline must be positive")

    started = time.monotonic()

    while True:
        if probe_listener(topology) is wanted:
            return int((time.monotonic() - started) * 1000)

        elapsed = time.monotonic() - started
        if elapsed >= deadline_seconds:
            state = "present" if wanted else "absent"
            raise ShutdownError(
                f"listener did not become {state} within bounded deadline"
            )

        remaining = deadline_seconds - elapsed
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))


def stop_certification_mongo(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
) -> ReadinessObservation:
    """Gracefully stop only the exact disposable certification Mongo topology.

    Before mutation, the function requires observable membership in the
    governed replica set. A shutdown command may close its own client
    connection; success is therefore determined by the subsequent bounded
    no-listener proof rather than by blindly accepting a command exception.
    """

    validate_certification_configuration(topology)
    started = time.monotonic()

    if not probe_listener(topology):
        return ReadinessObservation(
            lifecycle_state=MongoLifecycleState.DOWN,
            listener_present=False,
            set_name=None,
            writable_primary=False,
            member_health=None,
            elapsed_ms=int((time.monotonic() - started) * 1000),
            sanitized_error=None,
        )

    current = observe_mongo_readiness(
        topology,
        lifecycle_state=MongoLifecycleState.STOPPING,
    )

    if current.set_name != topology.replica_set:
        raise ShutdownError(
            "refusing shutdown because governed replica-set identity "
            "was not established"
        )

    command = [
        str(MONGOSH_BINARY),
        _mongo_uri(topology),
        "--quiet",
        "--eval",
        "db.adminCommand({shutdown:1})",
    ]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=MONGO_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        completed = None
        command_error = _sanitize_diagnostic(str(exc))
    except OSError as exc:
        raise ShutdownError(
            "governed Mongo shutdown command could not execute: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc
    else:
        command_error = _sanitize_diagnostic(
            "\n".join(
                part
                for part in (completed.stdout, completed.stderr)
                if part and part.strip()
            )
        )

    try:
        wait_for_listener_state(
            topology,
            wanted=False,
            deadline_seconds=READINESS_DEADLINE_SECONDS,
        )
    except ShutdownError as exc:
        command_status = (
            f"returncode={completed.returncode}"
            if completed is not None
            else "command-timeout"
        )
        detail = f"; diagnostic={command_error}" if command_error else ""
        raise ShutdownError(
            "Mongo shutdown did not produce bounded no-listener proof; "
            f"{command_status}{detail}"
        ) from exc

    return ReadinessObservation(
        lifecycle_state=MongoLifecycleState.DOWN,
        listener_present=False,
        set_name=topology.replica_set,
        writable_primary=False,
        member_health=None,
        elapsed_ms=int((time.monotonic() - started) * 1000),
        sanitized_error=command_error,
    )


def ensure_certification_mongo_restored(
    topology: MongoTopology = DEFAULT_TOPOLOGY,
) -> RestorationResult:
    """Idempotently restore and prove the disposable certification Mongo PRIMARY.

    This is the authoritative final infrastructure-restoration primitive.
    Correct already-healthy topology is preserved. A down topology is started
    with the exact governed command. A correct but non-primary topology is
    awaited. Wrong replica-set identity fails closed.

    Financial and tenant authority:
        None. Restoration concerns certification infrastructure only.
    """

    started = time.monotonic()
    validate_certification_configuration(topology)

    try:
        if not probe_listener(topology):
            readiness = start_certification_mongo(
                topology,
                phase=ReadinessPhase.RESTORATION,
            )
        else:
            readiness = observe_mongo_readiness(
                topology,
                lifecycle_state=MongoLifecycleState.RECOVERING,
            )

            if readiness.set_name not in {None, topology.replica_set}:
                raise WrongReplicaSetError(
                    "final restoration observed unexpected replica-set identity"
                )

            if not (
                readiness.set_name == topology.replica_set
                and readiness.writable_primary
                and readiness.member_health == 1
            ):
                readiness = wait_for_writable_primary(
                    topology,
                    phase=ReadinessPhase.RESTORATION,
                )
    except (WrongReplicaSetError, RestorationError):
        raise
    except (
        AuthOutageCertificationError,
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        raise RestorationError(
            "final certification Mongo restoration failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc

    healthy = (
        readiness.listener_present
        and readiness.set_name == topology.replica_set
        and readiness.writable_primary
        and readiness.member_health == 1
    )

    if not healthy:
        raise RestorationError(
            "final certification Mongo restoration did not prove healthy PRIMARY"
        )

    return RestorationResult(
        listener_present=True,
        writable_primary=True,
        set_name=readiness.set_name,
        member_health=readiness.member_health,
        healthy=True,
        elapsed_ms=int((time.monotonic() - started) * 1000),
    )




def resolve_repository_root() -> Path:
    """Resolve and validate the one governed repository root.

    The controller does not derive authority from the caller's working
    directory. The canonical repository identity is explicit and must contain
    the expected Wilsy governance and adapter surfaces before Node execution is
    permitted.
    """

    root = CANONICAL_REPOSITORY_ROOT.resolve()

    if root != CANONICAL_REPOSITORY_ROOT:
        raise ConfigurationError(
            "canonical repository root resolves through an unexpected alias"
        )
    if not root.is_dir():
        raise ConfigurationError(
            f"canonical repository root does not exist: {root}"
        )
    if not (root / "AGENTS.md").is_file():
        raise ConfigurationError(
            "canonical repository root does not contain AGENTS.md"
        )

    return root


def resolve_node_adapter_path() -> Path:
    """Resolve the foreign-runtime adapter from the governed repository root."""

    root = resolve_repository_root()
    adapter = (root / NODE_ADAPTER_RELATIVE_PATH).resolve()

    try:
        adapter.relative_to(root)
    except ValueError as exc:
        raise ConfigurationError(
            "Node adapter path escapes the canonical repository root"
        ) from exc

    expected = root / NODE_ADAPTER_RELATIVE_PATH
    if adapter != expected:
        raise ConfigurationError(
            "Node adapter resolves through an unexpected filesystem alias"
        )
    if not adapter.is_file():
        raise ConfigurationError(
            f"Node adapter is unavailable at governed path: {adapter}"
        )

    return adapter


def resolve_node_runtime_identity() -> NodeRuntimeIdentity:
    """Resolve and observe the exact Node executable used for adapter execution.

    The executable is resolved from PATH once, normalized to an absolute path,
    checked for executability, and queried with a bounded ``--version`` call.
    Shell aliases, npm, npx, and implicit runtime substitution are not used.
    """

    discovered = shutil.which("node")
    if discovered is None:
        raise ExecutableUnavailableError(
            "Node executable could not be resolved from PATH"
        )

    executable = Path(discovered).resolve()
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ExecutableUnavailableError(
            f"resolved Node executable is unavailable: {executable}"
        )

    try:
        completed = subprocess.run(
            [str(executable), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=NODE_VERSION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ExecutableUnavailableError(
            "Node version observation exceeded its bounded deadline"
        ) from exc
    except OSError as exc:
        raise ExecutableUnavailableError(
            "Node version observation could not execute: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc

    if completed.returncode != 0:
        diagnostic = _sanitize_diagnostic(
            "\n".join(
                part
                for part in (completed.stdout, completed.stderr)
                if part and part.strip()
            )
        )
        raise ExecutableUnavailableError(
            "Node version observation failed"
            + (f": {diagnostic}" if diagnostic else "")
        )

    version = completed.stdout.strip()
    if not version:
        raise ExecutableUnavailableError(
            "Node version observation returned an empty version"
        )

    return NodeRuntimeIdentity(
        executable=executable,
        version=version,
        adapter_path=resolve_node_adapter_path(),
    )


def _normalize_sensitive_key(key: str) -> str:
    """Normalize a protocol key for recursive sensitive-field comparison."""

    return "".join(character for character in key.casefold() if character.isalnum())


NORMALIZED_FORBIDDEN_EVIDENCE_KEYS: Final[frozenset[str]] = frozenset(
    _normalize_sensitive_key(key) for key in FORBIDDEN_EVIDENCE_KEYS
)


def _is_string_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    """Narrow an object to a dictionary whose keys are all strings."""

    if not isinstance(value, dict):
        return False
    return all(isinstance(key, str) for key in value)


def validate_json_protocol_value(
    value: object,
    *,
    path: str = "$",
    depth: int = 0,
    active_container_ids: frozenset[int] = frozenset(),
) -> None:
    """Validate JSON compatibility and recursively reject sensitive fields.

    The validator accepts only JSON primitives, lists, and string-keyed
    dictionaries. Non-finite floats, excessive depth, cyclic containers, and
    normalized forbidden keys fail closed before transport or evidence use.

    This function validates structure only; it does not derive authentication
    or certification truth.
    """

    if depth > JSON_PROTOCOL_MAX_DEPTH:
        raise AdapterProtocolError(
            f"JSON protocol value exceeds maximum depth at {path}"
        )

    if value is None or isinstance(value, (str, bool, int)):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise AdapterProtocolError(
                f"JSON protocol contains non-finite float at {path}"
            )
        return

    if isinstance(value, list):
        identity = id(value)
        if identity in active_container_ids:
            raise AdapterProtocolError(
                f"JSON protocol contains cyclic list at {path}"
            )

        next_active = active_container_ids | {identity}
        for index, item in enumerate(value):
            validate_json_protocol_value(
                item,
                path=f"{path}[{index}]",
                depth=depth + 1,
                active_container_ids=next_active,
            )
        return

    if _is_string_object_dict(value):
        identity = id(value)
        if identity in active_container_ids:
            raise AdapterProtocolError(
                f"JSON protocol contains cyclic object at {path}"
            )

        next_active = active_container_ids | {identity}

        for key, item in value.items():
            normalized_key = _normalize_sensitive_key(key)
            if normalized_key in NORMALIZED_FORBIDDEN_EVIDENCE_KEYS:
                raise AdapterProtocolError(
                    f"JSON protocol contains forbidden sensitive key at "
                    f"{path}.{key}"
                )

            validate_json_protocol_value(
                item,
                path=f"{path}.{key}",
                depth=depth + 1,
                active_container_ids=next_active,
            )
        return

    raise AdapterProtocolError(
        f"JSON protocol contains unsupported value type at {path}: "
        f"{type(value).__name__}"
    )


def _require_protocol_object(value: object, *, context: str) -> dict[str, object]:
    """Require a validated string-keyed protocol object."""

    if not _is_string_object_dict(value):
        raise AdapterProtocolError(f"{context} must be a JSON object")
    validate_json_protocol_value(value)
    return value


def _require_string_field(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
) -> str:
    """Require one non-empty trimmed string field without default invention."""

    if field not in mapping:
        raise AdapterProtocolError(
            f"{context} is missing required field {field!r}"
        )

    value = mapping[field]
    if not isinstance(value, str) or not value or value != value.strip():
        raise AdapterProtocolError(
            f"{context} field {field!r} must be a non-empty trimmed string"
        )

    return value


def _adapter_environment() -> dict[str, str]:
    """Build the child environment without mutating global process state.

    The environment supplies only certification topology/protocol parameters.
    It deliberately does not introduce a production JWT secret or other
    credential authority.
    """

    environment = os.environ.copy()
    environment.update(
        {
            "WILSY_AUTH_CERT_PROTOCOL_VERSION": PROTOCOL_VERSION,
            "WILSY_AUTH_CERT_MONGO_HOST": MONGO_HOST,
            "WILSY_AUTH_CERT_MONGO_PORT": str(MONGO_PORT),
            "WILSY_AUTH_CERT_REPLICA_SET": MONGO_REPLICA_SET,
            "WILSY_AUTH_CERT_DATABASE": CERTIFICATION_DATABASE,
            "WILSY_AUTH_CERT_NODE_SELECTION_TIMEOUT_MS": str(
                NODE_SELECTION_TIMEOUT_MS
            ),
            "WILSY_AUTH_CERT_NODE_HEARTBEAT_FREQUENCY_MS": str(
                NODE_HEARTBEAT_FREQUENCY_MS
            ),
        }
    )
    return environment


def _expected_response_type(command: str) -> AdapterResponseType:
    """Return the one admissible response type for a protocol command."""

    mapping: dict[str, AdapterResponseType] = {
        "INITIALIZE_RUNTIME": AdapterResponseType.READY,
        "PROVISION_FIXTURE": AdapterResponseType.RESULT,
        "LOOKUP_FIXTURE": AdapterResponseType.RESULT,
        "DELETE_FIXTURE": AdapterResponseType.RESULT,
        "RUN_SCENARIO": AdapterResponseType.RESULT,
        "CLOSE_RUNTIME": AdapterResponseType.SHUTDOWN_COMPLETE,
    }

    if command not in mapping:
        raise AdapterProtocolError(
            f"unsupported adapter protocol command: {command!r}"
        )

    return mapping[command]


def _parse_protocol_response(line: str) -> AdapterProtocolResponse:
    """Parse and validate one complete inbound adapter JSONL message."""

    if not line or not line.strip():
        raise AdapterProtocolError("adapter returned an empty protocol line")

    try:
        parsed: object = json.loads(line)
    except json.JSONDecodeError as exc:
        raise AdapterProtocolError(
            "adapter returned malformed JSONL protocol data"
        ) from exc

    message = _require_protocol_object(
        parsed,
        context="adapter response",
    )

    required_fields = {
        "protocol_version",
        "operation_id",
        "type",
        "payload",
    }
    actual_fields = set(message)

    if actual_fields != required_fields:
        missing = sorted(required_fields - actual_fields)
        unexpected = sorted(actual_fields - required_fields)
        raise AdapterProtocolError(
            "adapter response field contract mismatch; "
            f"missing={missing}; unexpected={unexpected}"
        )

    protocol_version = _require_string_field(
        message,
        field="protocol_version",
        context="adapter response",
    )
    operation_id = _require_string_field(
        message,
        field="operation_id",
        context="adapter response",
    )
    response_type_raw = _require_string_field(
        message,
        field="type",
        context="adapter response",
    )

    if protocol_version != PROTOCOL_VERSION:
        raise AdapterProtocolError(
            "adapter response protocol version mismatch"
        )

    try:
        response_type = AdapterResponseType(response_type_raw)
    except ValueError as exc:
        raise AdapterProtocolError(
            f"unsupported adapter response type: {response_type_raw!r}"
        ) from exc

    payload = message["payload"]
    validate_json_protocol_value(
        payload,
        path="$.payload",
    )

    return AdapterProtocolResponse(
        protocol_version=protocol_version,
        operation_id=operation_id,
        response_type=response_type,
        payload=payload,
    )


def _runtime_error_from_payload(payload: object) -> AdapterRuntimeError:
    """Create a bounded runtime error from an exact foreign error contract.

    ERROR is a protocol response type, so malformed ERROR payloads are protocol
    defects rather than permission to invent diagnostic defaults.
    """

    error_payload = _require_protocol_object(
        payload,
        context="adapter ERROR payload",
    )

    required_fields = {"error_type", "message"}
    actual_fields = set(error_payload)

    if actual_fields != required_fields:
        missing = sorted(required_fields - actual_fields)
        unexpected = sorted(actual_fields - required_fields)
        raise AdapterProtocolError(
            "adapter ERROR payload field contract mismatch; "
            f"missing={missing}; unexpected={unexpected}"
        )

    error_type = _require_string_field(
        error_payload,
        field="error_type",
        context="adapter ERROR payload",
    )
    raw_message = _require_string_field(
        error_payload,
        field="message",
        context="adapter ERROR payload",
    )
    message = _sanitize_diagnostic(raw_message)

    if message is None:
        raise AdapterProtocolError(
            "adapter ERROR payload message became empty after sanitization"
        )

    return AdapterRuntimeError(f"{error_type}: {message}")


class NodeAdapterProcess:
    """Python-owned lifecycle boundary for the persistent Node observation adapter.

    Authority:
        Owns subprocess creation, JSONL transport, operation correlation,
        bounded response waiting, graceful runtime closure, and forced process
        cleanup.

    Tenant scope:
        None at transport level. Tenant-shaped fixture/scenario payload authority
        belongs to later controller layers.

    Mutation semantics:
        Mutates only the child process it creates and its stdin/stdout transport.
        It does not start, stop, or restore Mongo.

    Fail-closed behavior:
        Protocol mismatch, sensitive data, malformed JSON, unexpected response,
        reader failure, timeout, or process exit blocks the operation.

    Financial boundary:
        None. This class has no financial execution authority.
    """

    def __init__(
        self,
        *,
        runtime: NodeRuntimeIdentity,
        process: subprocess.Popen[str],
        response_queue: queue.Queue[AdapterReaderEvent],
        reader_thread: threading.Thread,
    ) -> None:
        """Initialize one already-started adapter process owner."""

        self._runtime = runtime
        self._process = process
        self._response_queue = response_queue
        self._reader_thread = reader_thread
        self._reader_failure_lock = threading.Lock()
        self._reader_failure: AdapterReaderEvent | None = None
        self._closed = False

    @property
    def runtime(self) -> NodeRuntimeIdentity:
        """Return immutable observed Node runtime identity."""

        return self._runtime

    @property
    def process_id(self) -> int:
        """Return child process ID for volatile diagnostics only."""

        return self._process.pid

    @classmethod
    def start(
        cls,
        runtime: NodeRuntimeIdentity | None = None,
    ) -> "NodeAdapterProcess":
        """Start the persistent Node adapter transport without claiming readiness.

        Process creation proves only that Python obtained a child-process handle.
        Runtime readiness is established later by sending INITIALIZE_RUNTIME and
        validating its READY response.
        """

        resolved_runtime = runtime or resolve_node_runtime_identity()

        response_queue: queue.Queue[AdapterReaderEvent] = queue.Queue(
            maxsize=ADAPTER_READER_QUEUE_CAPACITY
        )

        try:
            process = subprocess.Popen(
                [
                    str(resolved_runtime.executable),
                    str(resolved_runtime.adapter_path),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=None,
                text=True,
                encoding="utf-8",
                bufsize=1,
                cwd=str(CANONICAL_REPOSITORY_ROOT),
                env=_adapter_environment(),
            )
        except OSError as exc:
            raise AdapterStartError(
                "Node adapter process could not start: "
                f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
            ) from exc

        if process.stdin is None or process.stdout is None:
            cls._terminate_unowned_process(process)
            raise AdapterStartError(
                "Node adapter process did not expose required stdin/stdout pipes"
            )

        owner_holder: list[NodeAdapterProcess] = []

        def reader_target() -> None:
            owner = owner_holder[0]
            owner._stdout_reader_loop()

        reader_thread = threading.Thread(
            target=reader_target,
            name="wilsy-auth-cert-node-stdout",
            daemon=True,
        )

        owner = cls(
            runtime=resolved_runtime,
            process=process,
            response_queue=response_queue,
            reader_thread=reader_thread,
        )
        owner_holder.append(owner)
        reader_thread.start()

        if process.poll() is not None:
            owner.terminate()
            raise AdapterStartError(
                "Node adapter exited immediately after process creation"
            )

        return owner

    @staticmethod
    def _terminate_unowned_process(process: subprocess.Popen[str]) -> None:
        """Best-effort bounded cleanup before process ownership is established."""

        if process.poll() is not None:
            return

        process.terminate()
        try:
            process.wait(timeout=ADAPTER_PROCESS_EXIT_TIMEOUT_SECONDS)
            return
        except subprocess.TimeoutExpired:
            process.kill()

        try:
            process.wait(timeout=ADAPTER_PROCESS_EXIT_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as exc:
            raise AdapterExitError(
                "unowned Node adapter could not be terminated after spawn failure"
            ) from exc

    def _set_reader_failure(self, event: AdapterReaderEvent) -> None:
        """Record the first reader failure without silently overwriting it."""

        with self._reader_failure_lock:
            if self._reader_failure is None:
                self._reader_failure = event

    def _get_reader_failure(self) -> AdapterReaderEvent | None:
        """Return the first recorded reader failure, if one exists."""

        with self._reader_failure_lock:
            return self._reader_failure

    def _enqueue_reader_event(self, event: AdapterReaderEvent) -> bool:
        """Enqueue one reader event or record bounded queue-overflow failure."""

        try:
            self._response_queue.put_nowait(event)
            return True
        except queue.Full:
            self._set_reader_failure(
                AdapterReaderEvent(
                    kind=AdapterReaderEventKind.ERROR,
                    line=None,
                    error_type="AdapterReaderQueueFull",
                    error_message=(
                        "adapter stdout reader queue exceeded bounded capacity"
                    ),
                )
            )
            return False

    def _stdout_reader_loop(self) -> None:
        """Continuously move child stdout lines into the bounded transport queue."""

        stdout = self._process.stdout
        if stdout is None:
            self._set_reader_failure(
                AdapterReaderEvent(
                    kind=AdapterReaderEventKind.ERROR,
                    line=None,
                    error_type="AdapterStdoutUnavailable",
                    error_message="Node adapter stdout pipe is unavailable",
                )
            )
            return

        try:
            while True:
                line = stdout.readline()
                if line == "":
                    self._enqueue_reader_event(
                        AdapterReaderEvent(
                            kind=AdapterReaderEventKind.EOF,
                            line=None,
                            error_type=None,
                            error_message=None,
                        )
                    )
                    return

                if not self._enqueue_reader_event(
                    AdapterReaderEvent(
                        kind=AdapterReaderEventKind.LINE,
                        line=line,
                        error_type=None,
                        error_message=None,
                    )
                ):
                    return
        except (OSError, UnicodeError, ValueError) as exc:
            event = AdapterReaderEvent(
                kind=AdapterReaderEventKind.ERROR,
                line=None,
                error_type=type(exc).__name__,
                error_message=_sanitize_diagnostic(str(exc)),
            )
            if not self._enqueue_reader_event(event):
                self._set_reader_failure(event)

    def ensure_alive(self) -> None:
        """Fail closed unless the owned Node child is still running."""

        return_code = self._process.poll()
        if return_code is not None:
            raise AdapterExitError(
                f"Node adapter exited unexpectedly with return code {return_code}"
            )

    def ensure_transport_usable(self) -> None:
        """Fail closed unless process and JSONL transport remain usable.

        Process liveness alone is insufficient. A persistent child with a
        failed reader or closed protocol stream cannot be treated as an active
        cleanup capability.
        """

        self.ensure_alive()

        reader_failure = self._get_reader_failure()
        if reader_failure is not None:
            raise AdapterRuntimeError(
                f"{reader_failure.error_type or 'AdapterReaderFailure'}: "
                f"{reader_failure.error_message or 'stdout reader failed'}"
            )

        stdin = self._process.stdin
        stdout = self._process.stdout

        if stdin is None or stdin.closed:
            raise AdapterRuntimeError(
                "Node adapter stdin transport is unavailable"
            )
        if stdout is None or stdout.closed:
            raise AdapterRuntimeError(
                "Node adapter stdout transport is unavailable"
            )

    def _write_request(
        self,
        *,
        operation_id: str,
        command: str,
        payload: dict[str, object],
    ) -> None:
        """Write and flush one deterministic JSONL request envelope."""

        self.ensure_alive()

        stdin = self._process.stdin
        if stdin is None or stdin.closed:
            raise AdapterRuntimeError(
                "Node adapter stdin is unavailable for protocol request"
            )

        envelope: dict[str, object] = {
            "protocol_version": PROTOCOL_VERSION,
            "operation_id": operation_id,
            "command": command,
            "payload": payload,
        }
        validate_json_protocol_value(envelope)

        encoded = json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

        try:
            stdin.write(encoded + "\n")
            stdin.flush()
        except (BrokenPipeError, OSError, ValueError) as exc:
            raise AdapterRuntimeError(
                "Node adapter request write failed: "
                f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
            ) from exc

    def _next_reader_event(
        self,
        *,
        deadline: float,
    ) -> AdapterReaderEvent:
        """Return the next queued reader event before a monotonic deadline.

        Already-queued transport evidence is consumed before process-exit
        classification. This preserves a valid final response that was written
        and observed immediately before the Node child exited.
        """

        while True:
            reader_failure = self._get_reader_failure()
            if reader_failure is not None:
                raise AdapterRuntimeError(
                    f"{reader_failure.error_type or 'AdapterReaderFailure'}: "
                    f"{reader_failure.error_message or 'stdout reader failed'}"
                )

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ObservationTimeoutError(
                    "bounded adapter response deadline exceeded"
                )

            try:
                return self._response_queue.get(
                    timeout=min(
                        ADAPTER_READER_POLL_SECONDS,
                        remaining,
                    )
                )
            except queue.Empty:
                reader_failure = self._get_reader_failure()
                if reader_failure is not None:
                    raise AdapterRuntimeError(
                        f"{reader_failure.error_type or 'AdapterReaderFailure'}: "
                        f"{reader_failure.error_message or 'stdout reader failed'}"
                    )

                return_code = self._process.poll()
                if return_code is not None:
                    raise AdapterExitError(
                        "Node adapter exited before the expected queued response; "
                        f"return_code={return_code}"
                    )

    def request(
        self,
        command: str,
        payload: dict[str, object],
        *,
        timeout_seconds: float = ADAPTER_RESPONSE_TIMEOUT_SECONDS,
    ) -> AdapterProtocolResponse:
        """Send one sequential correlated request and return its validated response.

        Only one response for the exact generated operation ID is admissible.
        Unexpected correlation IDs are protocol defects rather than evidence to
        reorder or reinterpret.

        This transport method does not interpret fixture, middleware, tenant, or
        authentication semantics.
        """

        if self._closed:
            raise AdapterRuntimeError(
                "Node adapter process owner is already closed"
            )
        if command not in PROTOCOL_COMMANDS:
            raise AdapterProtocolError(
                f"unsupported adapter protocol command: {command!r}"
            )
        if timeout_seconds <= 0:
            raise ConfigurationError(
                "adapter response timeout must be positive"
            )

        validate_json_protocol_value(
            payload,
            path="$.payload",
        )

        operation_id = str(uuid.uuid4())
        expected_response = _expected_response_type(command)

        self._write_request(
            operation_id=operation_id,
            command=command,
            payload=payload,
        )

        deadline = time.monotonic() + timeout_seconds

        while True:
            event = self._next_reader_event(deadline=deadline)

            if event.kind is AdapterReaderEventKind.EOF:
                return_code = self._process.poll()
                raise AdapterExitError(
                    "Node adapter stdout closed before expected response; "
                    f"return_code={return_code}"
                )

            if event.kind is AdapterReaderEventKind.ERROR:
                raise AdapterRuntimeError(
                    f"{event.error_type or 'AdapterReaderFailure'}: "
                    f"{event.error_message or 'stdout reader failed'}"
                )

            if event.kind is not AdapterReaderEventKind.LINE or event.line is None:
                raise AdapterProtocolError(
                    "Node adapter reader emitted an incoherent transport event"
                )

            response = _parse_protocol_response(event.line)

            if response.operation_id != operation_id:
                raise AdapterProtocolError(
                    "Node adapter response operation ID does not match "
                    "the sequential request"
                )

            if response.response_type is AdapterResponseType.ERROR:
                raise _runtime_error_from_payload(response.payload)

            if response.response_type is not expected_response:
                raise AdapterProtocolError(
                    "Node adapter response type does not match command contract; "
                    f"command={command}; "
                    f"expected={expected_response.value}; "
                    f"actual={response.response_type.value}"
                )

            return response

    def close_runtime(self) -> None:
        """Gracefully close Node-owned runtime resources and child process.

        CLOSE_RUNTIME has no Mongo lifecycle authority. If graceful protocol
        shutdown or bounded process exit fails, Python terminates only the child
        process it owns.
        """

        if self._closed:
            return

        if self._process.poll() is None:
            try:
                self.request(
                    "CLOSE_RUNTIME",
                    {},
                    timeout_seconds=ADAPTER_RESPONSE_TIMEOUT_SECONDS,
                )
            except (
                AdapterExitError,
                AdapterProtocolError,
                AdapterRuntimeError,
                ObservationTimeoutError,
            ):
                self.terminate()
                raise

        stdin = self._process.stdin
        if stdin is not None and not stdin.closed:
            try:
                stdin.close()
            except OSError as exc:
                self.terminate()
                raise AdapterRuntimeError(
                    "Node adapter stdin close failed: "
                    f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
                ) from exc

        try:
            self._process.wait(
                timeout=ADAPTER_PROCESS_EXIT_TIMEOUT_SECONDS
            )
        except subprocess.TimeoutExpired:
            self.terminate()
            return

        self._closed = True

    def terminate(self) -> None:
        """Idempotently terminate only the Node child process owned by Python.

        Process termination is attempted before parent-stream cleanup so a
        stream-close defect cannot prevent child cleanup. Once process exit is
        proven, any parent stdin close failure is surfaced explicitly.

        This method never starts, stops, restarts, or restores Mongo.
        """

        if self._closed and self._process.poll() is not None:
            return

        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(
                    timeout=ADAPTER_PROCESS_EXIT_TIMEOUT_SECONDS
                )
            except subprocess.TimeoutExpired:
                self._process.kill()
                try:
                    self._process.wait(
                        timeout=ADAPTER_PROCESS_EXIT_TIMEOUT_SECONDS
                    )
                except subprocess.TimeoutExpired as exc:
                    raise AdapterExitError(
                        "Node adapter remained alive after terminate and kill"
                    ) from exc

        self._closed = True

        stdin = self._process.stdin
        if stdin is not None and not stdin.closed:
            try:
                stdin.close()
            except OSError as exc:
                raise AdapterRuntimeError(
                    "Node adapter process exited but parent stdin close failed: "
                    f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
                ) from exc



def _require_bool_field(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
) -> bool:
    """Require one exact boolean field without truthy coercion."""

    if field not in mapping:
        raise AdapterProtocolError(
            f"{context} is missing required field {field!r}"
        )

    value = mapping[field]
    if not isinstance(value, bool):
        raise AdapterProtocolError(
            f"{context} field {field!r} must be boolean"
        )

    return value


def _require_int_field(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
) -> int:
    """Require one integer field while rejecting booleans."""

    if field not in mapping:
        raise AdapterProtocolError(
            f"{context} is missing required field {field!r}"
        )

    value = mapping[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdapterProtocolError(
            f"{context} field {field!r} must be integer"
        )

    return value


def _require_nullable_string_field(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
) -> str | None:
    """Require one nullable trimmed-string protocol field."""

    if field not in mapping:
        raise AdapterProtocolError(
            f"{context} is missing required field {field!r}"
        )

    value = mapping[field]
    if value is None:
        return None

    if not isinstance(value, str) or not value or value != value.strip():
        raise AdapterProtocolError(
            f"{context} field {field!r} must be null or a trimmed string"
        )

    return value


def _require_exact_fields(
    mapping: dict[str, object],
    *,
    required_fields: frozenset[str],
    context: str,
) -> None:
    """Require exact protocol payload fields with no authority-bearing extras."""

    actual_fields = frozenset(mapping)

    if actual_fields != required_fields:
        missing = sorted(required_fields - actual_fields)
        unexpected = sorted(actual_fields - required_fields)
        raise AdapterProtocolError(
            f"{context} field contract mismatch; "
            f"missing={missing}; unexpected={unexpected}"
        )


def _validate_opaque_durable_user_id(
    durable_user_id: object,
    *,
    context: str,
) -> str:
    """Validate a Node/Mongoose-created durable User identifier as opaque text.

    Python does not generate or infer Mongo ObjectId syntax. It accepts only a
    non-empty trimmed identifier returned by the real foreign-runtime model.
    """

    if (
        not isinstance(durable_user_id, str)
        or not durable_user_id
        or durable_user_id != durable_user_id.strip()
    ):
        raise EvidenceIncompleteError(
            f"{context} durable user ID must be a non-empty trimmed string"
        )

    return durable_user_id


def _require_certification_database(
    database_name: object,
    *,
    context: str,
) -> str:
    """Require exact certification database identity."""

    if not isinstance(database_name, str):
        raise AdapterProtocolError(
            f"{context} database_name must be a string"
        )

    if database_name != CERTIFICATION_DATABASE:
        raise AdapterProtocolError(
            f"{context} database identity mismatch"
        )

    return database_name


def parse_adapter_runtime_readiness(
    response: AdapterProtocolResponse,
) -> AdapterRuntimeReadiness:
    """Validate raw INITIALIZE_RUNTIME READY facts for fixture operations.

    This parser validates only runtime identity observations required to safely
    use the real User model. Authentication success and certification truth are
    outside this function's authority.
    """

    if response.response_type is not AdapterResponseType.READY:
        raise AdapterProtocolError(
            "INITIALIZE_RUNTIME did not return READY"
        )

    payload = _require_protocol_object(
        response.payload,
        context="INITIALIZE_RUNTIME READY payload",
    )

    _require_exact_fields(
        payload,
        required_fields=frozenset(
            {
                "node_version",
                "server_mongoose_ready_state",
                "user_db_ready_state",
                "same_mongoose_base",
                "database_name",
            }
        ),
        context="INITIALIZE_RUNTIME READY payload",
    )

    node_version = _require_string_field(
        payload,
        field="node_version",
        context="INITIALIZE_RUNTIME READY payload",
    )
    server_ready_state = _require_int_field(
        payload,
        field="server_mongoose_ready_state",
        context="INITIALIZE_RUNTIME READY payload",
    )
    user_ready_state = _require_int_field(
        payload,
        field="user_db_ready_state",
        context="INITIALIZE_RUNTIME READY payload",
    )
    same_base = _require_bool_field(
        payload,
        field="same_mongoose_base",
        context="INITIALIZE_RUNTIME READY payload",
    )
    database_name = _require_certification_database(
        payload["database_name"],
        context="INITIALIZE_RUNTIME READY payload",
    )

    return AdapterRuntimeReadiness(
        node_version=node_version,
        server_mongoose_ready_state=server_ready_state,
        user_db_ready_state=user_ready_state,
        same_mongoose_base=same_base,
        database_name=database_name,
    )


def initialize_adapter_runtime(
    adapter: NodeAdapterProcess,
) -> AdapterRuntimeReadiness:
    """Initialize and prove the closed real Node/Mongoose fixture runtime.

    Required facts are:

    - Node-reported version equals Python's resolved executable version;
    - server Mongoose ready state is exactly connected state ``1``;
    - User-model database ready state is exactly connected state ``1``;
    - User model and server runtime report the same Mongoose base;
    - database identity is exactly the certification database.

    These remain runtime facts only and establish no authentication verdict.
    """

    try:
        response = adapter.request(
            "INITIALIZE_RUNTIME",
            {},
        )
        readiness = parse_adapter_runtime_readiness(response)

        if readiness.node_version != adapter.runtime.version:
            raise AdapterRuntimeError(
                "Node adapter runtime version does not match resolved executable"
            )

        if readiness.server_mongoose_ready_state != 1:
            raise AdapterRuntimeError(
                "server Mongoose is not in connected ready state"
            )

        if readiness.user_db_ready_state != 1:
            raise AdapterRuntimeError(
                "User-model database is not in connected ready state"
            )

        if not readiness.same_mongoose_base:
            raise AdapterRuntimeError(
                "User model and server runtime do not share Mongoose base"
            )

        if readiness.database_name != CERTIFICATION_DATABASE:
            raise AdapterRuntimeError(
                "Node adapter initialized against unexpected database"
            )

        return readiness
    except AdapterProtocolError:
        raise
    except (
        AdapterRuntimeError,
        AdapterExitError,
        ObservationTimeoutError,
    ) as exc:
        raise AdapterRuntimeError(
            "Node adapter runtime initialization failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc


def _fixture_provision_payload(
    request: FixtureProvisionRequest,
) -> dict[str, object]:
    """Build the minimum operational fixture-provision payload."""

    payload: dict[str, object] = {
        "synthetic_email": request.synthetic_email,
        "synthetic_tenant_value": request.synthetic_tenant_value,
    }
    validate_json_protocol_value(payload)
    return payload


def provision_fixture(
    adapter: NodeAdapterProcess,
    request: FixtureProvisionRequest,
) -> FixtureIdentity:
    """Provision one real User-model synthetic fixture through the Node adapter.

    Python owns sequencing and validates the returned durable identity. Node
    owns actual Mongoose/User creation. Provision success is not authentication
    success and is not tenant-membership authority.
    """

    try:
        response = adapter.request(
            "PROVISION_FIXTURE",
            _fixture_provision_payload(request),
        )
        payload = _require_protocol_object(
            response.payload,
            context="PROVISION_FIXTURE RESULT payload",
        )

        _require_exact_fields(
            payload,
            required_fields=frozenset(
                {
                    "operation_succeeded",
                    "durable_user_id",
                    "database_name",
                }
            ),
            context="PROVISION_FIXTURE RESULT payload",
        )

        operation_succeeded = _require_bool_field(
            payload,
            field="operation_succeeded",
            context="PROVISION_FIXTURE RESULT payload",
        )

        if not operation_succeeded:
            raise FixtureProvisionError(
                "Node adapter reported unsuccessful fixture provision"
            )

        durable_user_id = _validate_opaque_durable_user_id(
            payload["durable_user_id"],
            context="PROVISION_FIXTURE RESULT payload",
        )
        database_name = _require_certification_database(
            payload["database_name"],
            context="PROVISION_FIXTURE RESULT payload",
        )

        return FixtureIdentity(
            durable_user_id=durable_user_id,
            database_name=database_name,
        )
    except FixtureProvisionError:
        raise
    except (
        AdapterProtocolError,
        AdapterRuntimeError,
        AdapterExitError,
        ObservationTimeoutError,
        EvidenceIncompleteError,
    ) as exc:
        raise FixtureProvisionError(
            "fixture provisioning failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc


def lookup_fixture(
    adapter: NodeAdapterProcess,
    durable_user_id: str,
) -> FixtureLookupResult:
    """Look up one exact fixture by its opaque durable User identifier.

    Lookup failure is not equivalent to fixture absence. The result is accepted
    only when the adapter reports an internally coherent found/not-found state
    for the exact certification database.
    """

    requested_id = _validate_opaque_durable_user_id(
        durable_user_id,
        context="LOOKUP_FIXTURE request",
    )

    request_payload: dict[str, object] = {
        "durable_user_id": requested_id,
    }

    try:
        response = adapter.request(
            "LOOKUP_FIXTURE",
            request_payload,
        )
        payload = _require_protocol_object(
            response.payload,
            context="LOOKUP_FIXTURE RESULT payload",
        )

        _require_exact_fields(
            payload,
            required_fields=frozenset(
                {
                    "lookup_succeeded",
                    "found",
                    "durable_user_id",
                    "database_name",
                }
            ),
            context="LOOKUP_FIXTURE RESULT payload",
        )

        lookup_succeeded = _require_bool_field(
            payload,
            field="lookup_succeeded",
            context="LOOKUP_FIXTURE RESULT payload",
        )
        found = _require_bool_field(
            payload,
            field="found",
            context="LOOKUP_FIXTURE RESULT payload",
        )
        observed_id = _require_nullable_string_field(
            payload,
            field="durable_user_id",
            context="LOOKUP_FIXTURE RESULT payload",
        )
        database_name = _require_certification_database(
            payload["database_name"],
            context="LOOKUP_FIXTURE RESULT payload",
        )

        if not lookup_succeeded:
            raise FixtureLookupError(
                "Node adapter reported unsuccessful fixture lookup"
            )

        if found:
            if observed_id is None:
                raise FixtureLookupError(
                    "fixture lookup reports found without durable ID"
                )
            if observed_id != requested_id:
                raise FixtureLookupError(
                    "fixture lookup returned a different durable ID"
                )
        elif observed_id is not None:
            raise FixtureLookupError(
                "fixture lookup reports absent while returning a durable ID"
            )

        return FixtureLookupResult(
            requested_durable_user_id=requested_id,
            operation_succeeded=True,
            found=found,
            observed_durable_user_id=observed_id,
            database_name=database_name,
        )
    except FixtureLookupError:
        raise
    except (
        AdapterProtocolError,
        AdapterRuntimeError,
        AdapterExitError,
        ObservationTimeoutError,
        EvidenceIncompleteError,
    ) as exc:
        raise FixtureLookupError(
            "fixture lookup failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc


def verify_fixture_present(
    adapter: NodeAdapterProcess,
    fixture: FixtureIdentity,
) -> FixtureLookupResult:
    """Prove the provisioned fixture is observable under the same durable ID."""

    if fixture.database_name != CERTIFICATION_DATABASE:
        raise FixtureLookupError(
            "fixture identity does not belong to certification database"
        )

    result = lookup_fixture(
        adapter,
        fixture.durable_user_id,
    )

    if not result.found:
        raise FixtureLookupError(
            "provisioned fixture is not observable by real User-model lookup"
        )

    if result.observed_durable_user_id != fixture.durable_user_id:
        raise FixtureLookupError(
            "provisioned fixture lookup did not preserve durable identity"
        )

    return result


def delete_fixture(
    adapter: NodeAdapterProcess,
    fixture: FixtureIdentity,
) -> FixtureDeleteResult:
    """Delete exactly one transaction-owned fixture by durable identity.

    No collection-wide deletion, database drop, or inferred fixture ownership is
    permitted.
    """

    if fixture.database_name != CERTIFICATION_DATABASE:
        raise FixtureCleanupError(
            "refusing fixture cleanup outside certification database"
        )

    request_payload: dict[str, object] = {
        "durable_user_id": fixture.durable_user_id,
    }

    try:
        response = adapter.request(
            "DELETE_FIXTURE",
            request_payload,
        )
        payload = _require_protocol_object(
            response.payload,
            context="DELETE_FIXTURE RESULT payload",
        )

        _require_exact_fields(
            payload,
            required_fields=frozenset(
                {
                    "delete_succeeded",
                    "deleted",
                    "durable_user_id",
                    "database_name",
                }
            ),
            context="DELETE_FIXTURE RESULT payload",
        )

        delete_succeeded = _require_bool_field(
            payload,
            field="delete_succeeded",
            context="DELETE_FIXTURE RESULT payload",
        )
        deleted = _require_bool_field(
            payload,
            field="deleted",
            context="DELETE_FIXTURE RESULT payload",
        )
        durable_user_id = _validate_opaque_durable_user_id(
            payload["durable_user_id"],
            context="DELETE_FIXTURE RESULT payload",
        )
        database_name = _require_certification_database(
            payload["database_name"],
            context="DELETE_FIXTURE RESULT payload",
        )

        if not delete_succeeded:
            raise FixtureCleanupError(
                "Node adapter reported unsuccessful fixture delete"
            )

        if durable_user_id != fixture.durable_user_id:
            raise FixtureCleanupError(
                "fixture delete result returned a different durable ID"
            )

        return FixtureDeleteResult(
            durable_user_id=durable_user_id,
            operation_succeeded=True,
            deleted=deleted,
            database_name=database_name,
        )
    except FixtureCleanupError:
        raise
    except (
        AdapterProtocolError,
        AdapterRuntimeError,
        AdapterExitError,
        ObservationTimeoutError,
        EvidenceIncompleteError,
    ) as exc:
        raise FixtureCleanupError(
            "fixture delete failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc


def prove_fixture_absent(
    adapter: NodeAdapterProcess,
    fixture: FixtureIdentity,
) -> FixtureLookupResult:
    """Prove exact fixture absence through a separate real User-model lookup."""

    result = lookup_fixture(
        adapter,
        fixture.durable_user_id,
    )

    if result.found:
        raise FixtureCleanupError(
            "fixture remains observable after cleanup"
        )

    if result.observed_durable_user_id is not None:
        raise FixtureCleanupError(
            "absent fixture proof returned an unexpected durable ID"
        )

    return result


def cleanup_fixture_with_active_adapter(
    adapter: NodeAdapterProcess,
    fixture: FixtureIdentity,
) -> None:
    """Idempotently clean one owned fixture through an active adapter.

    Already-absent fixture state is accepted only after a successful real lookup.
    Lookup failure is never converted into absence.
    """

    try:
        adapter.ensure_alive()
        initial = lookup_fixture(
            adapter,
            fixture.durable_user_id,
        )

        if not initial.found:
            return

        delete_fixture(
            adapter,
            fixture,
        )

        prove_fixture_absent(
            adapter,
            fixture,
        )
    except FixtureCleanupError:
        raise
    except (
        AdapterProtocolError,
        AdapterRuntimeError,
        AdapterExitError,
        ObservationTimeoutError,
        FixtureLookupError,
    ) as exc:
        raise FixtureCleanupError(
            "active-adapter fixture cleanup failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        ) from exc


def cleanup_fixture_with_fresh_adapter(
    fixture: FixtureIdentity,
    *,
    runtime: NodeRuntimeIdentity | None = None,
) -> None:
    """Clean one fixture using a fresh scenario-incapable adapter path.

    The function exposes only runtime initialization plus exact lookup/delete/
    lookup cleanup sequencing. It cannot execute RUN_SCENARIO and has no auth
    verdict authority.

    Preconditions:
        Mongo restoration belongs to the caller and must already be complete.
    """

    cleanup_adapter: NodeAdapterProcess | None = None
    primary_error: FixtureCleanupError | None = None

    try:
        cleanup_adapter = NodeAdapterProcess.start(runtime)
        readiness = initialize_adapter_runtime(cleanup_adapter)

        if readiness.database_name != CERTIFICATION_DATABASE:
            raise FixtureCleanupError(
                "cleanup adapter initialized against wrong database"
            )

        cleanup_fixture_with_active_adapter(
            cleanup_adapter,
            fixture,
        )
    except FixtureCleanupError as exc:
        primary_error = exc
    except (
        AdapterProtocolError,
        AdapterRuntimeError,
        AdapterExitError,
        AdapterStartError,
        ObservationTimeoutError,
    ) as exc:
        primary_error = FixtureCleanupError(
            "fresh-adapter fixture cleanup failed: "
            f"{_sanitize_diagnostic(str(exc)) or type(exc).__name__}"
        )
        primary_error.__cause__ = exc
    finally:
        shutdown_error: AuthOutageCertificationError | None = None

        if cleanup_adapter is not None:
            try:
                cleanup_adapter.close_runtime()
            except (
                AdapterProtocolError,
                AdapterRuntimeError,
                AdapterExitError,
                ObservationTimeoutError,
            ) as exc:
                shutdown_error = exc
                try:
                    cleanup_adapter.terminate()
                except (
                    AdapterRuntimeError,
                    AdapterExitError,
                ) as termination_exc:
                    shutdown_error = AdapterExitError(
                        "cleanup adapter graceful shutdown and termination "
                        "both failed: "
                        f"{_sanitize_diagnostic(str(termination_exc)) or type(termination_exc).__name__}"
                    )

        if primary_error is not None:
            if shutdown_error is not None:
                raise FixtureCleanupError(
                    "fixture cleanup failed and cleanup adapter shutdown also failed; "
                    f"cleanup={_sanitize_diagnostic(str(primary_error)) or type(primary_error).__name__}; "
                    f"shutdown={_sanitize_diagnostic(str(shutdown_error)) or type(shutdown_error).__name__}"
                ) from primary_error
            raise primary_error

        if shutdown_error is not None:
            raise FixtureCleanupError(
                "fixture cleanup succeeded but cleanup adapter shutdown failed: "
                f"{_sanitize_diagnostic(str(shutdown_error)) or type(shutdown_error).__name__}"
            ) from shutdown_error


def cleanup_owned_fixture(
    fixture: FixtureIdentity,
    *,
    active_adapter: NodeAdapterProcess | None,
    runtime: NodeRuntimeIdentity | None = None,
) -> None:
    """Clean one exact transaction-owned fixture through a bounded authority path.

    If an active adapter is genuinely alive, it is used. Otherwise a fresh
    cleanup-only adapter is created. Failure of the active adapter is never
    interpreted as fixture absence.

    This function does not restore Mongo; restoration remains a distinct
    lifecycle authority owned by Phase B and composed later by the controller
    finalizer.
    """

    if fixture.database_name != CERTIFICATION_DATABASE:
        raise FixtureCleanupError(
            "owned fixture does not belong to certification database"
        )

    if active_adapter is not None:
        try:
            active_adapter.ensure_transport_usable()
        except (
            AdapterExitError,
            AdapterRuntimeError,
        ):
            cleanup_fixture_with_fresh_adapter(
                fixture,
                runtime=runtime,
            )
            return

        cleanup_fixture_with_active_adapter(
            active_adapter,
            fixture,
        )
        return

    cleanup_fixture_with_fresh_adapter(
        fixture,
        runtime=runtime,
    )



def classify_scenario(scenario_id: str) -> ScenarioClass:
    """Classify only explicitly governed authentication scenario IDs."""

    if scenario_id in POSITIVE_SCENARIO_IDS:
        return ScenarioClass.POSITIVE
    if scenario_id in OUTAGE_SCENARIO_IDS:
        return ScenarioClass.OUTAGE

    raise EvidenceIncompleteError(
        f"unsupported authentication scenario ID: {scenario_id!r}"
    )


def _require_nonnegative_int_field(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
) -> int:
    """Require one exact non-negative integer without boolean coercion."""

    value = _require_int_field(
        mapping,
        field=field,
        context=context,
    )

    if value < 0:
        raise AdapterProtocolError(
            f"{context} field {field!r} must be non-negative"
        )

    return value


def _require_nullable_http_status(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
) -> int | None:
    """Require null or one syntactically valid HTTP status code."""

    if field not in mapping:
        raise AdapterProtocolError(
            f"{context} is missing required field {field!r}"
        )

    value = mapping[field]

    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, int):
        raise AdapterProtocolError(
            f"{context} field {field!r} must be null or integer"
        )

    if value < 100 or value > 599:
        raise AdapterProtocolError(
            f"{context} field {field!r} is outside HTTP status range"
        )

    return value


def _require_nullable_bounded_string_field(
    mapping: dict[str, object],
    *,
    field: str,
    context: str,
    max_length: int,
) -> str | None:
    """Require a null or bounded non-empty trimmed diagnostic string."""

    value = _require_nullable_string_field(
        mapping,
        field=field,
        context=context,
    )

    if value is not None and len(value) > max_length:
        raise AdapterProtocolError(
            f"{context} field {field!r} exceeds bounded length"
        )

    return value


def parse_adapter_observation(
    response: AdapterProtocolResponse,
    *,
    expected_scenario_id: str,
) -> AdapterObservation:
    """Validate one RUN_SCENARIO RESULT without deriving authentication truth.

    All raw facts are explicit. Missing booleans, counters, statuses, and
    persistence evidence are never replaced by safe defaults.
    """

    classify_scenario(expected_scenario_id)

    if response.response_type is not AdapterResponseType.RESULT:
        raise AdapterProtocolError(
            "RUN_SCENARIO did not return RESULT"
        )

    payload = _require_protocol_object(
        response.payload,
        context="RUN_SCENARIO RESULT payload",
    )

    _require_exact_fields(
        payload,
        required_fields=frozenset(
            {
                "protocol_version",
                "scenario_id",
                "middleware_completed",
                "next_count",
                "has_authenticated_user",
                "http_status",
                "elapsed_ms",
                "response_code",
                "persistence_error_name",
                "persistence_error_category",
                "persistence_error_message_sanitized",
            }
        ),
        context="RUN_SCENARIO RESULT payload",
    )

    protocol_version = _require_string_field(
        payload,
        field="protocol_version",
        context="RUN_SCENARIO RESULT payload",
    )

    if protocol_version != PROTOCOL_VERSION:
        raise AdapterProtocolError(
            "RUN_SCENARIO observation protocol version mismatch"
        )

    scenario_id = _require_string_field(
        payload,
        field="scenario_id",
        context="RUN_SCENARIO RESULT payload",
    )

    if scenario_id != expected_scenario_id:
        raise AdapterProtocolError(
            "RUN_SCENARIO observation scenario ID mismatch"
        )

    middleware_completed = _require_bool_field(
        payload,
        field="middleware_completed",
        context="RUN_SCENARIO RESULT payload",
    )
    next_count = _require_nonnegative_int_field(
        payload,
        field="next_count",
        context="RUN_SCENARIO RESULT payload",
    )
    has_authenticated_user = _require_bool_field(
        payload,
        field="has_authenticated_user",
        context="RUN_SCENARIO RESULT payload",
    )
    http_status = _require_nullable_http_status(
        payload,
        field="http_status",
        context="RUN_SCENARIO RESULT payload",
    )
    elapsed_ms = _require_nonnegative_int_field(
        payload,
        field="elapsed_ms",
        context="RUN_SCENARIO RESULT payload",
    )
    response_code = _require_nullable_bounded_string_field(
        payload,
        field="response_code",
        context="RUN_SCENARIO RESULT payload",
        max_length=120,
    )
    persistence_error_name = _require_nullable_bounded_string_field(
        payload,
        field="persistence_error_name",
        context="RUN_SCENARIO RESULT payload",
        max_length=120,
    )
    persistence_error_category = _require_nullable_bounded_string_field(
        payload,
        field="persistence_error_category",
        context="RUN_SCENARIO RESULT payload",
        max_length=120,
    )
    persistence_error_message = _require_nullable_bounded_string_field(
        payload,
        field="persistence_error_message_sanitized",
        context="RUN_SCENARIO RESULT payload",
        max_length=PERSISTENCE_DIAGNOSTIC_MAX_LENGTH,
    )

    return AdapterObservation(
        protocol_version=protocol_version,
        scenario_id=scenario_id,
        middleware_completed=middleware_completed,
        next_count=next_count,
        has_authenticated_user=has_authenticated_user,
        http_status=http_status,
        elapsed_ms=elapsed_ms,
        response_code=response_code,
        persistence_error_name=persistence_error_name,
        persistence_error_category=persistence_error_category,
        persistence_error_message_sanitized=persistence_error_message,
    )


def _normalize_persistence_token(value: str) -> str:
    """Normalize persistence classifier input without preserving punctuation."""

    return "".join(
        character
        for character in value.casefold()
        if character.isalnum()
    )


def classify_persistence_evidence(
    observation: AdapterObservation,
) -> PersistenceClassification:
    """Normalize raw persistence evidence while preserving unknown-vs-absent.

    Error name/category tokens are primary classifier inputs. Sanitized message
    text is used only as a narrowly bounded fallback for known transport
    signatures.
    """

    raw_values = (
        observation.persistence_error_category,
        observation.persistence_error_name,
        observation.persistence_error_message_sanitized,
    )

    if all(value is None for value in raw_values):
        return PersistenceClassification(
            state=PersistenceEvidenceState.NONE,
            category=None,
            reason="no persistence failure evidence reported",
        )

    category_token = (
        _normalize_persistence_token(
            observation.persistence_error_category
        )
        if observation.persistence_error_category is not None
        else ""
    )
    name_token = (
        _normalize_persistence_token(
            observation.persistence_error_name
        )
        if observation.persistence_error_name is not None
        else ""
    )
    message_token = (
        _normalize_persistence_token(
            observation.persistence_error_message_sanitized
        )
        if observation.persistence_error_message_sanitized is not None
        else ""
    )

    connection_refused_tokens = frozenset(
        {
            "connectionrefused",
            "econnrefused",
        }
    )
    topology_tokens = frozenset(
        {
            "replicasetnoprimary",
            "noprimary",
            "topologyunavailable",
            "mongotopologyclosederror",
        }
    )
    server_selection_tokens = frozenset(
        {
            "mongooseserverselectionerror",
            "mongoserverselectionerror",
            "serverselectionunavailable",
            "serverselectiontimeout",
            "serverselectiontimedout",
        }
    )

    structured_tokens = frozenset(
        token
        for token in (category_token, name_token)
        if token
    )

    if structured_tokens & connection_refused_tokens:
        return PersistenceClassification(
            state=PersistenceEvidenceState.RECOGNIZED,
            category=PersistenceFailureCategory.CONNECTION_REFUSED,
            reason="recognized connection-refused persistence failure",
        )

    if structured_tokens & topology_tokens:
        return PersistenceClassification(
            state=PersistenceEvidenceState.RECOGNIZED,
            category=PersistenceFailureCategory.TOPOLOGY_UNAVAILABLE,
            reason="recognized topology-unavailable persistence failure",
        )

    if structured_tokens & server_selection_tokens:
        return PersistenceClassification(
            state=PersistenceEvidenceState.RECOGNIZED,
            category=PersistenceFailureCategory.SERVER_SELECTION_UNAVAILABLE,
            reason="recognized server-selection persistence failure",
        )

    message_signatures: tuple[
        tuple[str, PersistenceFailureCategory, str],
        ...,
    ] = (
        (
            "econnrefused",
            PersistenceFailureCategory.CONNECTION_REFUSED,
            "recognized connection-refused diagnostic signature",
        ),
        (
            "connectionrefused",
            PersistenceFailureCategory.CONNECTION_REFUSED,
            "recognized connection-refused diagnostic signature",
        ),
        (
            "replicasetnoprimary",
            PersistenceFailureCategory.TOPOLOGY_UNAVAILABLE,
            "recognized no-primary diagnostic signature",
        ),
        (
            "topologyunavailable",
            PersistenceFailureCategory.TOPOLOGY_UNAVAILABLE,
            "recognized topology-unavailable diagnostic signature",
        ),
        (
            "serverselectiontimedout",
            PersistenceFailureCategory.SERVER_SELECTION_UNAVAILABLE,
            "recognized server-selection timeout diagnostic signature",
        ),
        (
            "serverselectionerror",
            PersistenceFailureCategory.SERVER_SELECTION_UNAVAILABLE,
            "recognized server-selection diagnostic signature",
        ),
    )

    for signature, category, reason in message_signatures:
        if signature in message_token:
            return PersistenceClassification(
                state=PersistenceEvidenceState.RECOGNIZED,
                category=category,
                reason=reason,
            )

    return PersistenceClassification(
        state=PersistenceEvidenceState.UNRECOGNIZED,
        category=None,
        reason="persistence failure evidence is present but unrecognized",
    )


def normalize_persistence_failure(
    observation: AdapterObservation,
) -> PersistenceFailureCategory | None:
    """Return a recognized normalized persistence category, if one exists.

    Callers that need to distinguish no-error from unrecognized-error must use
    ``classify_persistence_evidence`` instead.
    """

    classification = classify_persistence_evidence(observation)

    if classification.state is PersistenceEvidenceState.RECOGNIZED:
        return classification.category

    return None


def build_scenario_observation(
    observation: AdapterObservation,
) -> ScenarioObservation:
    """Attach recognized persistence classification to validated raw facts."""

    classify_scenario(observation.scenario_id)
    classification = classify_persistence_evidence(observation)

    return ScenarioObservation(
        scenario_id=observation.scenario_id,
        adapter_observation=observation,
        persistence_category=(
            classification.category
            if classification.state is PersistenceEvidenceState.RECOGNIZED
            else None
        ),
    )


def derive_positive_control(
    scenario: ScenarioObservation,
) -> PositiveControlResult:
    """Derive one positive-control result from complete validated raw facts.

    Positive success has distinct vocabulary and is never represented as
    FAIL_OPEN or FAIL_CLOSED.
    """

    if classify_scenario(scenario.scenario_id) is not ScenarioClass.POSITIVE:
        raise EvidenceIncompleteError(
            "positive-control derivation requires a positive scenario"
        )

    observation = scenario.adapter_observation
    persistence = classify_persistence_evidence(observation)

    if not observation.middleware_completed:
        return PositiveControlResult(
            scenario_id=scenario.scenario_id,
            status=PositiveControlStatus.EVIDENCE_INCOMPLETE,
            reason="middleware invocation did not complete",
        )

    if observation.next_count > 1:
        return PositiveControlResult(
            scenario_id=scenario.scenario_id,
            status=PositiveControlStatus.EVIDENCE_INCOMPLETE,
            reason="middleware invoked next more than once",
        )

    if persistence.state is not PersistenceEvidenceState.NONE:
        return PositiveControlResult(
            scenario_id=scenario.scenario_id,
            status=PositiveControlStatus.FAIL,
            reason=(
                "healthy positive control reported persistence failure evidence"
            ),
        )

    if (
        observation.next_count == 1
        and observation.has_authenticated_user
    ):
        return PositiveControlResult(
            scenario_id=scenario.scenario_id,
            status=PositiveControlStatus.PASS,
            reason=(
                "middleware completed with one continuation and authenticated "
                "user projection"
            ),
        )

    return PositiveControlResult(
        scenario_id=scenario.scenario_id,
        status=PositiveControlStatus.FAIL,
        reason=(
            "complete healthy control did not produce the required authenticated "
            "continuation"
        ),
    )


def derive_outage_verdict(
    scenario: ScenarioObservation,
) -> OutageScenarioResult:
    """Derive fail-open/fail-closed truth only after proving outage input.

    HTTP response status is supporting evidence only. It cannot independently
    establish authentication denial.
    """

    if classify_scenario(scenario.scenario_id) is not ScenarioClass.OUTAGE:
        raise EvidenceIncompleteError(
            "outage derivation requires a governed outage scenario"
        )

    observation = scenario.adapter_observation
    persistence = classify_persistence_evidence(observation)

    if not observation.middleware_completed:
        return OutageScenarioResult(
            scenario_id=scenario.scenario_id,
            status=OutageScenarioStatus.EVIDENCE_INCOMPLETE,
            reason="middleware invocation did not complete",
        )

    if observation.next_count > 1:
        return OutageScenarioResult(
            scenario_id=scenario.scenario_id,
            status=OutageScenarioStatus.EVIDENCE_INCOMPLETE,
            reason="middleware invoked next more than once",
        )

    if persistence.state is not PersistenceEvidenceState.RECOGNIZED:
        return OutageScenarioResult(
            scenario_id=scenario.scenario_id,
            status=OutageScenarioStatus.EVIDENCE_INCOMPLETE,
            reason=(
                "intended persistence outage was not established by recognized "
                "persistence failure evidence"
            ),
        )

    if (
        observation.next_count > 0
        or observation.has_authenticated_user
    ):
        return OutageScenarioResult(
            scenario_id=scenario.scenario_id,
            status=OutageScenarioStatus.FAIL_OPEN,
            reason=(
                "recognized persistence outage coincided with authentication "
                "continuation or authenticated user projection"
            ),
        )

    if (
        observation.next_count == 0
        and not observation.has_authenticated_user
    ):
        return OutageScenarioResult(
            scenario_id=scenario.scenario_id,
            status=OutageScenarioStatus.FAIL_CLOSED,
            reason=(
                "recognized persistence outage completed without continuation "
                "and without authenticated user projection"
            ),
        )

    return OutageScenarioResult(
        scenario_id=scenario.scenario_id,
        status=OutageScenarioStatus.EVIDENCE_INCOMPLETE,
        reason="outage observation could not be coherently derived",
    )


def execute_scenario(
    adapter: NodeAdapterProcess,
    *,
    scenario_id: str,
    parameters: dict[str, object],
) -> ScenarioObservation:
    """Execute one named scenario transport request and validate raw Node facts.

    This helper is defined for the future cross-certified adapter. The scratch
    build does not invoke it. Sensitive credentials are not accepted through
    the evidence-safe scenario parameters because recursive protocol validation
    rejects forbidden keys.
    """

    classify_scenario(scenario_id)
    validate_json_protocol_value(
        parameters,
        path="$.scenario_parameters",
    )

    request_payload: dict[str, object] = {
        "scenario_id": scenario_id,
        "parameters": parameters,
    }

    response = adapter.request(
        "RUN_SCENARIO",
        request_payload,
    )

    observation = parse_adapter_observation(
        response,
        expected_scenario_id=scenario_id,
    )

    return build_scenario_observation(observation)




def _canonical_scenario_rank(scenario_id: str) -> int:
    """Return deterministic governed order for one known auth scenario."""

    try:
        return AUTH_SCENARIO_CANONICAL_ORDER.index(scenario_id)
    except ValueError as exc:
        raise EvidenceIncompleteError(
            f"scenario is absent from canonical evidence order: {scenario_id!r}"
        ) from exc


def _canonical_topology_payload(
    topology: MongoTopology,
) -> dict[str, object]:
    """Serialize governed Mongo topology into explicit semantic JSON data."""

    return {
        "host": topology.host,
        "port": topology.port,
        "replica_set": topology.replica_set,
        "db_path": str(topology.db_path),
        "log_path": str(topology.log_path),
    }


def _canonical_fixture_payload(
    fixture: FixtureIdentity | None,
) -> dict[str, object] | None:
    """Serialize only durable fixture identity retained as evidence."""

    if fixture is None:
        return None

    if fixture.database_name != CERTIFICATION_DATABASE:
        raise EvidenceIncompleteError(
            "canonical fixture belongs to unexpected database"
        )

    durable_id = _validate_opaque_durable_user_id(
        fixture.durable_user_id,
        context="canonical fixture evidence",
    )

    return {
        "durable_user_id": durable_id,
        "database_name": fixture.database_name,
    }


def _canonical_readiness_payload(
    observation: ReadinessObservation,
) -> dict[str, object]:
    """Serialize semantic Mongo readiness facts while excluding elapsed timing."""

    sanitized_error = observation.sanitized_error
    if sanitized_error is not None:
        if (
            not sanitized_error
            or sanitized_error != sanitized_error.strip()
            or len(sanitized_error) > PERSISTENCE_DIAGNOSTIC_MAX_LENGTH
        ):
            raise EvidenceIncompleteError(
                "readiness diagnostic is malformed or unbounded"
            )

    return {
        "lifecycle_state": observation.lifecycle_state.value,
        "listener_present": observation.listener_present,
        "set_name": observation.set_name,
        "writable_primary": observation.writable_primary,
        "member_health": observation.member_health,
        "sanitized_error": sanitized_error,
    }


def _canonical_adapter_observation_payload(
    observation: AdapterObservation,
) -> dict[str, object]:
    """Serialize validated raw Node facts while excluding elapsed timing."""

    if observation.protocol_version != PROTOCOL_VERSION:
        raise EvidenceIncompleteError(
            "adapter observation protocol version mismatch in canonical evidence"
        )

    classify_scenario(observation.scenario_id)

    if observation.next_count < 0 or observation.next_count > 1:
        raise EvidenceIncompleteError(
            "adapter observation next_count is incoherent"
        )

    if observation.http_status is not None and (
        observation.http_status < 100
        or observation.http_status > 599
    ):
        raise EvidenceIncompleteError(
            "adapter observation HTTP status is malformed"
        )

    for label, value, limit in (
        ("response_code", observation.response_code, 120),
        (
            "persistence_error_name",
            observation.persistence_error_name,
            120,
        ),
        (
            "persistence_error_category",
            observation.persistence_error_category,
            120,
        ),
        (
            "persistence_error_message_sanitized",
            observation.persistence_error_message_sanitized,
            PERSISTENCE_DIAGNOSTIC_MAX_LENGTH,
        ),
    ):
        if value is not None and (
            not value
            or value != value.strip()
            or len(value) > limit
        ):
            raise EvidenceIncompleteError(
                f"canonical adapter field {label!r} is malformed"
            )

    return {
        "protocol_version": observation.protocol_version,
        "scenario_id": observation.scenario_id,
        "middleware_completed": observation.middleware_completed,
        "next_count": observation.next_count,
        "has_authenticated_user": observation.has_authenticated_user,
        "http_status": observation.http_status,
        "response_code": observation.response_code,
        "persistence_error_name": observation.persistence_error_name,
        "persistence_error_category": (
            observation.persistence_error_category
        ),
        "persistence_error_message_sanitized": (
            observation.persistence_error_message_sanitized
        ),
    }


def _canonical_scenario_observation_payload(
    scenario: ScenarioObservation,
) -> dict[str, object]:
    """Serialize one coherent scenario observation and persistence class."""

    if scenario.scenario_id != scenario.adapter_observation.scenario_id:
        raise EvidenceIncompleteError(
            "scenario and adapter observation identities disagree"
        )

    classification = classify_persistence_evidence(
        scenario.adapter_observation
    )

    expected_category = (
        classification.category
        if classification.state is PersistenceEvidenceState.RECOGNIZED
        else None
    )

    if scenario.persistence_category is not expected_category:
        raise EvidenceIncompleteError(
            "scenario persistence category disagrees with Python classifier"
        )

    return {
        "scenario_id": scenario.scenario_id,
        "adapter_observation": _canonical_adapter_observation_payload(
            scenario.adapter_observation
        ),
        "persistence_category": (
            scenario.persistence_category.value
            if scenario.persistence_category is not None
            else None
        ),
        "persistence_evidence_state": classification.state.value,
    }


def _canonical_positive_result_payload(
    result: PositiveControlResult,
) -> dict[str, object]:
    """Serialize one Python-derived positive-control authority result."""

    if classify_scenario(result.scenario_id) is not ScenarioClass.POSITIVE:
        raise EvidenceIncompleteError(
            "positive-control result has non-positive scenario ID"
        )

    if not result.reason or result.reason != result.reason.strip():
        raise EvidenceIncompleteError(
            "positive-control reason must be non-empty and trimmed"
        )

    return {
        "scenario_id": result.scenario_id,
        "status": result.status.value,
        "reason": result.reason,
    }


def _canonical_outage_result_payload(
    result: OutageScenarioResult,
) -> dict[str, object]:
    """Serialize one Python-derived persistence-outage authority result."""

    if classify_scenario(result.scenario_id) is not ScenarioClass.OUTAGE:
        raise EvidenceIncompleteError(
            "outage result has non-outage scenario ID"
        )

    if not result.reason or result.reason != result.reason.strip():
        raise EvidenceIncompleteError(
            "outage-result reason must be non-empty and trimmed"
        )

    return {
        "scenario_id": result.scenario_id,
        "status": result.status.value,
        "reason": result.reason,
    }


def _canonical_restoration_payload(
    restoration: RestorationResult | None,
) -> dict[str, object] | None:
    """Serialize final restoration facts while excluding elapsed timing."""

    if restoration is None:
        return None

    return {
        "listener_present": restoration.listener_present,
        "writable_primary": restoration.writable_primary,
        "set_name": restoration.set_name,
        "member_health": restoration.member_health,
        "healthy": restoration.healthy,
    }


def _validate_evidence_derivation_coherence(
    evidence: CertificationEvidence,
) -> None:
    """Prove canonical derived results equal current Python derivation authority.

    This prevents hand-constructed or stale derived results from being hashed as
    valid certification evidence.
    """

    observations_by_id: dict[str, ScenarioObservation] = {}

    for scenario in evidence.observations:
        if scenario.scenario_id in observations_by_id:
            raise EvidenceIncompleteError(
                f"duplicate scenario observation: {scenario.scenario_id}"
            )

        classify_scenario(scenario.scenario_id)
        observations_by_id[scenario.scenario_id] = scenario

    positive_ids: set[str] = set()

    for result in evidence.positive_controls:
        if result.scenario_id in positive_ids:
            raise EvidenceIncompleteError(
                f"duplicate positive-control result: {result.scenario_id}"
            )

        positive_ids.add(result.scenario_id)

        scenario = observations_by_id.get(result.scenario_id)
        if scenario is None:
            raise EvidenceIncompleteError(
                "positive-control result has no corresponding observation: "
                f"{result.scenario_id}"
            )

        expected = derive_positive_control(scenario)
        if expected != result:
            raise EvidenceIncompleteError(
                "positive-control result disagrees with Python derivation: "
                f"{result.scenario_id}"
            )

    outage_ids: set[str] = set()

    for result in evidence.outage_results:
        if result.scenario_id in outage_ids:
            raise EvidenceIncompleteError(
                f"duplicate outage result: {result.scenario_id}"
            )

        outage_ids.add(result.scenario_id)

        scenario = observations_by_id.get(result.scenario_id)
        if scenario is None:
            raise EvidenceIncompleteError(
                "outage result has no corresponding observation: "
                f"{result.scenario_id}"
            )

        expected = derive_outage_verdict(scenario)
        if expected != result:
            raise EvidenceIncompleteError(
                "outage result disagrees with Python derivation: "
                f"{result.scenario_id}"
            )


def canonical_certification_evidence_payload(
    evidence: CertificationEvidence,
) -> dict[str, object]:
    """Build the explicit digest-free semantic certification payload.

    Determinism:
        Scenario observations and derived results are ordered by the governed
        canonical scenario order, independent of tuple construction order.

    Excluded volatile metadata:
        elapsed milliseconds, timestamps, process IDs, operation IDs, runtime
        random UUIDs, and scratch paths.

    Cryptographic boundary:
        No digest field is present in this payload. SHA3-512 is computed only
        after this complete semantic payload has been validated.

    Tenant and financial authority:
        None.
    """

    if evidence.schema_version != EVIDENCE_SCHEMA_VERSION:
        raise EvidenceIncompleteError(
            "certification evidence schema version mismatch"
        )
    if evidence.controller_version != VERSION:
        raise EvidenceIncompleteError(
            "certification evidence controller version mismatch"
        )
    if evidence.protocol_version != PROTOCOL_VERSION:
        raise EvidenceIncompleteError(
            "certification evidence protocol version mismatch"
        )
    if evidence.topology != DEFAULT_TOPOLOGY:
        raise EvidenceIncompleteError(
            "certification evidence topology differs from governed topology"
        )

    _validate_evidence_derivation_coherence(evidence)

    lifecycle_payload = [
        _canonical_readiness_payload(item)
        for item in evidence.lifecycle
    ]

    observations = sorted(
        evidence.observations,
        key=lambda item: _canonical_scenario_rank(item.scenario_id),
    )
    positive_controls = sorted(
        evidence.positive_controls,
        key=lambda item: _canonical_scenario_rank(item.scenario_id),
    )
    outage_results = sorted(
        evidence.outage_results,
        key=lambda item: _canonical_scenario_rank(item.scenario_id),
    )

    payload: dict[str, object] = {
        "schema_version": evidence.schema_version,
        "controller_version": evidence.controller_version,
        "protocol_version": evidence.protocol_version,
        "topology": _canonical_topology_payload(evidence.topology),
        "fixture": _canonical_fixture_payload(evidence.fixture),
        "lifecycle": [
            item
            for item in lifecycle_payload
        ],
        "observations": [
            _canonical_scenario_observation_payload(item)
            for item in observations
        ],
        "positive_controls": [
            _canonical_positive_result_payload(item)
            for item in positive_controls
        ],
        "outage_results": [
            _canonical_outage_result_payload(item)
            for item in outage_results
        ],
        "fixture_absence_proven": evidence.fixture_absence_proven,
        "adapter_shutdown_proven": evidence.adapter_shutdown_proven,
        "restoration": _canonical_restoration_payload(
            evidence.restoration
        ),
    }

    validate_json_protocol_value(
        payload,
        path="$.certification_evidence",
    )

    forbidden_canonical_keys = {
        "digest",
        "evidence_sha3_512",
        "timestamp",
        "pid",
        "process_id",
        "operation_id",
        "scratch_path",
        "elapsed_ms",
    }

    def inspect_keys(value: object, *, location: str) -> None:
        if isinstance(value, list):
            for index, item in enumerate(value):
                inspect_keys(
                    item,
                    location=f"{location}[{index}]",
                )
            return

        if _is_string_object_dict(value):
            for key, item in value.items():
                if key in forbidden_canonical_keys:
                    raise EvidenceIncompleteError(
                        "volatile or recursive field entered canonical evidence: "
                        f"{location}.{key}"
                    )
                inspect_keys(
                    item,
                    location=f"{location}.{key}",
                )

    inspect_keys(
        payload,
        location="$",
    )

    return payload


def canonical_certification_evidence_bytes(
    evidence: CertificationEvidence,
) -> bytes:
    """Serialize validated canonical evidence into deterministic UTF-8 JSON."""

    payload = canonical_certification_evidence_payload(evidence)

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    return encoded.encode("utf-8")


def certification_evidence_sha3_512(
    evidence: CertificationEvidence,
) -> str:
    """Return lowercase SHA3-512 over digest-free canonical evidence bytes."""

    return sha3_512(
        canonical_certification_evidence_bytes(evidence)
    ).hexdigest()


def build_certification_result(
    *,
    status: CertificationStatus,
    evidence: CertificationEvidence,
    primary_failure: StructuredFailure | None = None,
    fixture_cleanup_failure: StructuredFailure | None = None,
    adapter_shutdown_failure: StructuredFailure | None = None,
    restoration_failure: StructuredFailure | None = None,
) -> CertificationResult:
    """Construct the outer result envelope around canonical evidence.

    Final-status derivation is intentionally NOT owned here; Phase G supplies
    the already-derived status. This function owns only digest construction and
    immutable result assembly.
    """

    digest = certification_evidence_sha3_512(evidence)

    return CertificationResult(
        status=status,
        evidence=evidence,
        evidence_sha3_512=digest,
        primary_failure=primary_failure,
        fixture_cleanup_failure=fixture_cleanup_failure,
        adapter_shutdown_failure=adapter_shutdown_failure,
        restoration_failure=restoration_failure,
    )




def _structured_failure(
    category: str,
    exc: BaseException,
) -> StructuredFailure:
    """Convert one bounded controller failure into immutable evidence."""

    if not category or category != category.strip():
        raise EvidenceIncompleteError(
            "structured failure category must be non-empty and trimmed"
        )

    message = _sanitize_diagnostic(str(exc))

    return StructuredFailure(
        category=category,
        error_type=type(exc).__name__,
        message=message or type(exc).__name__,
    )


def _controller_evidence(
    *,
    fixture: FixtureIdentity | None,
    lifecycle: list[ReadinessObservation],
    observations: list[ScenarioObservation],
    positive_controls: list[PositiveControlResult],
    outage_results: list[OutageScenarioResult],
    fixture_absence_proven: bool,
    adapter_shutdown_proven: bool,
    restoration: RestorationResult | None,
) -> CertificationEvidence:
    """Build immutable evidence from accumulated controller state."""

    return CertificationEvidence(
        schema_version=EVIDENCE_SCHEMA_VERSION,
        controller_version=VERSION,
        protocol_version=PROTOCOL_VERSION,
        topology=DEFAULT_TOPOLOGY,
        fixture=fixture,
        lifecycle=tuple(lifecycle),
        observations=tuple(observations),
        positive_controls=tuple(positive_controls),
        outage_results=tuple(outage_results),
        fixture_absence_proven=fixture_absence_proven,
        adapter_shutdown_proven=adapter_shutdown_proven,
        restoration=restoration,
    )


def _scenario_ids_exact_once(
    values: tuple[str, ...],
    *,
    expected: frozenset[str],
) -> bool:
    """Return whether each expected scenario ID occurs exactly once."""

    return (
        len(values) == len(expected)
        and len(set(values)) == len(values)
        and set(values) == expected
    )


def derive_certification_status(
    evidence: CertificationEvidence,
    *,
    primary_failure: StructuredFailure | None,
    fixture_cleanup_failure: StructuredFailure | None,
    adapter_shutdown_failure: StructuredFailure | None,
    restoration_failure: StructuredFailure | None,
) -> CertificationStatus:
    """Derive final certification status from complete accumulated evidence."""

    if any(
        failure is not None
        for failure in (
            primary_failure,
            fixture_cleanup_failure,
            adapter_shutdown_failure,
            restoration_failure,
        )
    ):
        return CertificationStatus.BLOCKED

    observation_ids = tuple(
        item.scenario_id for item in evidence.observations
    )
    positive_ids = tuple(
        item.scenario_id for item in evidence.positive_controls
    )
    outage_ids = tuple(
        item.scenario_id for item in evidence.outage_results
    )

    if not _scenario_ids_exact_once(
        observation_ids,
        expected=ALL_AUTH_SCENARIO_IDS,
    ):
        return CertificationStatus.BLOCKED

    if not _scenario_ids_exact_once(
        positive_ids,
        expected=POSITIVE_SCENARIO_IDS,
    ):
        return CertificationStatus.BLOCKED

    if not _scenario_ids_exact_once(
        outage_ids,
        expected=OUTAGE_SCENARIO_IDS,
    ):
        return CertificationStatus.BLOCKED

    if evidence.fixture is None:
        return CertificationStatus.BLOCKED

    if not evidence.fixture_absence_proven:
        return CertificationStatus.BLOCKED

    if not evidence.adapter_shutdown_proven:
        return CertificationStatus.BLOCKED

    restoration = evidence.restoration
    if restoration is None:
        return CertificationStatus.BLOCKED

    if not (
        restoration.healthy
        and restoration.listener_present
        and restoration.writable_primary
        and restoration.set_name == MONGO_REPLICA_SET
        and restoration.member_health == 1
    ):
        return CertificationStatus.BLOCKED

    if any(
        result.status is not PositiveControlStatus.PASS
        for result in evidence.positive_controls
    ):
        return CertificationStatus.BLOCKED

    if any(
        result.status is OutageScenarioStatus.EVIDENCE_INCOMPLETE
        for result in evidence.outage_results
    ):
        return CertificationStatus.BLOCKED

    if any(
        result.status is OutageScenarioStatus.FAIL_OPEN
        for result in evidence.outage_results
    ):
        return CertificationStatus.FAILED

    if not all(
        result.status is OutageScenarioStatus.FAIL_CLOSED
        for result in evidence.outage_results
    ):
        return CertificationStatus.BLOCKED

    return CertificationStatus.CERTIFIED




def _not_ready_result(
    exc: AuthOutageCertificationError,
) -> CertificationResult:
    """Return a digest-bearing NOT_READY result before runtime execution begins."""

    evidence = _controller_evidence(
        fixture=None,
        lifecycle=[],
        observations=[],
        positive_controls=[],
        outage_results=[],
        fixture_absence_proven=False,
        adapter_shutdown_proven=False,
        restoration=None,
    )

    return build_certification_result(
        status=CertificationStatus.NOT_READY,
        evidence=evidence,
        primary_failure=_structured_failure(
            "precondition",
            exc,
        ),
    )


def _synthetic_fixture_request() -> FixtureProvisionRequest:
    """Create transaction-local synthetic fixture construction input only."""

    transaction_id = uuid.uuid4().hex

    return FixtureProvisionRequest(
        synthetic_email=(
            f"wilsy-auth-outage-cert-{transaction_id}@example.invalid"
        ),
        synthetic_tenant_value=(
            f"synthetic-cert-tenant-{transaction_id}"
        ),
    )


def _scenario_parameters(
    fixture: FixtureIdentity,
) -> dict[str, object]:
    """Return the minimum non-sensitive scenario construction parameters."""

    return {
        "durable_user_id": fixture.durable_user_id,
    }


def run_auth_outage_certification() -> CertificationResult:
    """Run the governed authentication persistence-outage certification.

    Python owns lifecycle mutation, scenario sequencing, raw-observation
    validation, verdict derivation, finalization, final status, and evidence
    hashing. The Node adapter remains a foreign-runtime observation capability
    only and cannot establish Wilsy certification truth.

    A proven FAIL_OPEN remains ordinary evidence so cleanup, adapter shutdown,
    and final Mongo restoration still execute. Machinery ambiguity or incomplete
    evidence produces BLOCKED rather than invented security truth.

    Tenant authority:
        None.

    Financial authority:
        None.
    """

    try:
        validate_certification_configuration(DEFAULT_TOPOLOGY)
        runtime = resolve_node_runtime_identity()
    except (
        ConfigurationError,
        ExecutableUnavailableError,
    ) as exc:
        return _not_ready_result(exc)

    lifecycle: list[ReadinessObservation] = []
    observations: list[ScenarioObservation] = []
    positive_controls: list[PositiveControlResult] = []
    outage_results: list[OutageScenarioResult] = []

    adapter: NodeAdapterProcess | None = None
    fixture: FixtureIdentity | None = None

    fixture_provision_attempted = False
    fixture_absence_proven = False
    adapter_shutdown_proven = False

    primary_failure: StructuredFailure | None = None
    fixture_cleanup_failure: StructuredFailure | None = None
    adapter_shutdown_failure: StructuredFailure | None = None
    restoration_failure: StructuredFailure | None = None

    final_restoration: RestorationResult | None = None
    restoration_ready_for_cleanup = False

    # ------------------------------------------------------------------
    # Primary execution.
    # ------------------------------------------------------------------

    try:
        startup = start_certification_mongo(
            DEFAULT_TOPOLOGY,
            phase=ReadinessPhase.STARTUP,
        )
        lifecycle.append(startup)

        adapter = NodeAdapterProcess.start(runtime)
        initialize_adapter_runtime(adapter)

        fixture_provision_attempted = True
        fixture = provision_fixture(
            adapter,
            _synthetic_fixture_request(),
        )
        verify_fixture_present(
            adapter,
            fixture,
        )

        parameters = _scenario_parameters(fixture)

        for scenario_id in AUTH_SCENARIO_CANONICAL_ORDER[:3]:
            scenario = execute_scenario(
                adapter,
                scenario_id=scenario_id,
                parameters=parameters,
            )
            observations.append(scenario)

            result = derive_positive_control(scenario)
            positive_controls.append(result)

            if result.status is not PositiveControlStatus.PASS:
                raise EvidenceIncompleteError(
                    "healthy positive control did not establish required "
                    f"authenticated continuation: {scenario_id}"
                )

        stopped = stop_certification_mongo(
            DEFAULT_TOPOLOGY
        )
        lifecycle.append(stopped)

        if (
            stopped.listener_present
            or stopped.lifecycle_state is not MongoLifecycleState.DOWN
        ):
            raise ShutdownError(
                "outage phase began without proven Mongo DOWN state"
            )

        for scenario_id in AUTH_SCENARIO_CANONICAL_ORDER[3:]:
            scenario = execute_scenario(
                adapter,
                scenario_id=scenario_id,
                parameters=parameters,
            )
            observations.append(scenario)
            outage_results.append(
                derive_outage_verdict(scenario)
            )

        incomplete_outage_ids = tuple(
            result.scenario_id
            for result in outage_results
            if result.status
            is OutageScenarioStatus.EVIDENCE_INCOMPLETE
        )

        if incomplete_outage_ids:
            raise EvidenceIncompleteError(
                "one or more outage scenarios lacked admissible evidence: "
                + ",".join(incomplete_outage_ids)
            )

    except (
        WrongReplicaSetError,
        StartupPrimaryTimeoutError,
        ShutdownError,
        RestartError,
        RecoveryPrimaryTimeoutError,
        RestorationError,
        AdapterStartError,
        AdapterProtocolError,
        AdapterRuntimeError,
        AdapterExitError,
        ObservationTimeoutError,
        FixtureProvisionError,
        FixtureLookupError,
        FixtureCleanupError,
        EvidenceIncompleteError,
        ConfigurationError,
        ExecutableUnavailableError,
    ) as exc:
        primary_failure = _structured_failure(
            "primary",
            exc,
        )

    # ------------------------------------------------------------------
    # Finalizer 1: restore Mongo before exact fixture cleanup.
    # ------------------------------------------------------------------

    try:
        ensure_certification_mongo_restored(
            DEFAULT_TOPOLOGY
        )
        restoration_ready_for_cleanup = True
    except (
        WrongReplicaSetError,
        RestorationError,
        RestartError,
        RecoveryPrimaryTimeoutError,
        ConfigurationError,
        ExecutableUnavailableError,
    ) as exc:
        restoration_failure = _structured_failure(
            "restoration",
            exc,
        )

    # ------------------------------------------------------------------
    # Finalizer 2: exact owned-fixture cleanup only.
    # ------------------------------------------------------------------

    if fixture is not None and restoration_ready_for_cleanup:
        try:
            cleanup_owned_fixture(
                fixture,
                active_adapter=adapter,
                runtime=runtime,
            )
            fixture_absence_proven = True
        except (
            FixtureCleanupError,
            FixtureLookupError,
            AdapterProtocolError,
            AdapterRuntimeError,
            AdapterExitError,
            ObservationTimeoutError,
        ) as exc:
            fixture_cleanup_failure = _structured_failure(
                "fixture_cleanup",
                exc,
            )
    elif fixture is not None:
        fixture_cleanup_failure = StructuredFailure(
            category="fixture_cleanup",
            error_type="RestorationPrerequisiteUnavailable",
            message=(
                "exact fixture cleanup was not attempted because restored "
                "certification Mongo PRIMARY was not proven"
            ),
        )
    elif fixture_provision_attempted:
        fixture_cleanup_failure = StructuredFailure(
            category="fixture_cleanup",
            error_type="FixtureIdentityUnavailable",
            message=(
                "fixture provisioning was attempted but no durable fixture "
                "identity was available for exact cleanup proof"
            ),
        )
    else:
        fixture_absence_proven = True

    # ------------------------------------------------------------------
    # Finalizer 3: close or force-terminate only Python's Node child.
    # ------------------------------------------------------------------

    if adapter is not None:
        try:
            adapter.close_runtime()
            adapter_shutdown_proven = True
        except (
            AdapterProtocolError,
            AdapterRuntimeError,
            AdapterExitError,
            ObservationTimeoutError,
        ) as exc:
            adapter_shutdown_failure = _structured_failure(
                "adapter_shutdown",
                exc,
            )

            try:
                adapter.terminate()
            except (
                AdapterRuntimeError,
                AdapterExitError,
            ):
                adapter_shutdown_failure = StructuredFailure(
                    category="adapter_shutdown",
                    error_type="CompoundAdapterShutdownFailure",
                    message=(
                        "graceful adapter shutdown failed and forced "
                        "termination also failed"
                    ),
                )

    # ------------------------------------------------------------------
    # Finalizer 4: independent final Mongo PRIMARY proof.
    # ------------------------------------------------------------------

    try:
        final_restoration = ensure_certification_mongo_restored(
            DEFAULT_TOPOLOGY
        )
    except (
        WrongReplicaSetError,
        RestorationError,
        RestartError,
        RecoveryPrimaryTimeoutError,
        ConfigurationError,
        ExecutableUnavailableError,
    ) as exc:
        if restoration_failure is None:
            restoration_failure = _structured_failure(
                "restoration",
                exc,
            )
        else:
            restoration_failure = StructuredFailure(
                category="restoration",
                error_type="CompoundRestorationFailure",
                message=(
                    "initial finalizer restoration and final restoration "
                    "proof both encountered failure"
                ),
            )

    # ------------------------------------------------------------------
    # Final immutable evidence, status, and digest envelope.
    # ------------------------------------------------------------------

    evidence = _controller_evidence(
        fixture=fixture,
        lifecycle=lifecycle,
        observations=observations,
        positive_controls=positive_controls,
        outage_results=outage_results,
        fixture_absence_proven=fixture_absence_proven,
        adapter_shutdown_proven=adapter_shutdown_proven,
        restoration=final_restoration,
    )

    status = derive_certification_status(
        evidence,
        primary_failure=primary_failure,
        fixture_cleanup_failure=fixture_cleanup_failure,
        adapter_shutdown_failure=adapter_shutdown_failure,
        restoration_failure=restoration_failure,
    )

    return build_certification_result(
        status=status,
        evidence=evidence,
        primary_failure=primary_failure,
        fixture_cleanup_failure=fixture_cleanup_failure,
        adapter_shutdown_failure=adapter_shutdown_failure,
        restoration_failure=restoration_failure,
    )



__all__ = [
    "AdapterExitError",
    "AdapterProtocolResponse",
    "AdapterReaderEvent",
    "AdapterReaderEventKind",
    "AdapterResponseType",
    "AdapterObservation",
    "AdapterProtocolError",
    "AdapterRuntimeError",
    "AdapterStartError",
    "AuthOutageCertificationError",
    "ALL_AUTH_SCENARIO_IDS",
    "CertificationEvidence",
    "CertificationResult",
    "CertificationStatus",
    "ConfigurationError",
    "DEFAULT_TOPOLOGY",
    "EvidenceIncompleteError",
    "EVIDENCE_SCHEMA_VERSION",
    "ExecutableUnavailableError",
    "FixtureCleanupError",
    "FixtureDeleteResult",
    "FixtureLookupResult",
    "FixtureProvisionRequest",
    "FixtureIdentity",
    "FixtureLookupError",
    "FixtureProvisionError",
    "MongoLifecycleState",
    "NodeAdapterProcess",
    "AdapterRuntimeReadiness",
    "NodeRuntimeIdentity",
    "MongoTopology",
    "ObservationTimeoutError",
    "PersistenceFailureCategory",
    "PersistenceClassification",
    "PersistenceEvidenceState",
    "PositiveControlResult",
    "PositiveControlStatus",
    "ReadinessObservation",
    "ReadinessPhase",
    "RecoveryPrimaryTimeoutError",
    "RestartError",
    "RestorationError",
    "RestorationResult",
    "ScenarioObservation",
    "ScenarioClass",
    "OutageScenarioResult",
    "OutageScenarioStatus",
    "ShutdownError",
    "StartupPrimaryTimeoutError",
    "StructuredFailure",
    "VERSION",
    "WrongReplicaSetError",
    "build_scenario_observation",
    "build_certification_result",
    "canonical_certification_evidence_bytes",
    "canonical_certification_evidence_payload",
    "certification_evidence_sha3_512",
    "classify_persistence_evidence",
    "classify_scenario",
    "derive_outage_verdict",
    "derive_positive_control",
    "derive_certification_status",
    "execute_scenario",
    "normalize_persistence_failure",
    "parse_adapter_observation",
    "cleanup_fixture_with_active_adapter",
    "cleanup_fixture_with_fresh_adapter",
    "cleanup_owned_fixture",
    "delete_fixture",
    "initialize_adapter_runtime",
    "lookup_fixture",
    "parse_adapter_runtime_readiness",
    "prove_fixture_absent",
    "provision_fixture",
    "verify_fixture_present",
    "resolve_node_adapter_path",
    "resolve_node_runtime_identity",
    "resolve_repository_root",
    "run_auth_outage_certification",
    "validate_json_protocol_value",
    "ensure_certification_mongo_restored",
    "observe_mongo_readiness",
    "probe_listener",
    "start_certification_mongo",
    "stop_certification_mongo",
    "validate_certification_configuration",
    "wait_for_listener_state",
    "wait_for_writable_primary",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
#
# ARTIFACT:
#     WILSY OS Authentication Outage Certification Controller
#
# VERSION:
#     v1.0.0-AUTH-OUTAGE-CERTIFICATION
#
# AUTHORITY BOUNDARY:
#     Python owns authentication-outage certification orchestration, disposable
#     Mongo lifecycle control, scenario sequencing, raw-observation validation,
#     evidence aggregation, derived certification verdicts, finalization, and
#     SHA3-512 certification-evidence authority. The Node adapter is a
#     foreign-runtime observation capability only and owns no Wilsy
#     certification verdict or business truth.
#
# TENANT POSTURE:
#     This artifact creates no tenant-membership, tenant-role, tenant-access, or
#     tenant-authorization authority. Synthetic tenant-shaped fixture data may
#     exist only to satisfy real User-model construction requirements and must
#     never be interpreted as governed tenant authority.
#
# FAIL-CLOSED POSTURE:
#     Missing, malformed, incomplete, ambiguous, duplicated, cleanup-defective,
#     adapter-shutdown-defective, restoration-defective, or otherwise
#     inadmissible certification evidence cannot become CERTIFIED.
#     Proven authentication FAIL_OPEN remains ordinary evidence and yields
#     FAILED only when the certification transaction itself remains complete;
#     machinery or finalizer defects yield BLOCKED.
#
# FINANCIAL EXECUTION AUTHORITY:
#     None. This artifact cannot approve, authorize, request, execute, observe
#     as canonical truth, or settle financial execution. Kennel EOS remains the
#     exclusive financial execution authority.
#
# SCRATCH AUTHORITY POSTURE:
#     This complete-file candidate remains NON-AUTHORITATIVE while located
#     outside the governed repository. Sovereign EOS authority begins only
#     after complete-file certification and atomic installation at the canonical
#     repository path stated in the module header.
#
# END OF WILSY OS SOVEREIGN ARTIFACT
# =============================================================================
