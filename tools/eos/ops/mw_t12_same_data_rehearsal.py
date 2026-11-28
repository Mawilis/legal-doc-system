"""TITLE: MW-T12 same-data reversible Python EOS rollback rehearsal.
VERSION: v1.4.0-BOUNDED-FIXTURE-FAILURE-PROVENANCE
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Reuse a single UUID-owned replica database across current, historical,
         and restored-current Python EOS binaries with authenticated readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_same_data_rehearsal.py
COLLABORATION / OWNERSHIP: Existing MW-T12 source staging and owned Mongo
         utilities; existing browser-cert fixture owns seeding, record
         verification, and database cleanup. No extra DB client introduced.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.4.0-BOUNDED-FIXTURE-FAILURE-PROVENANCE
           classifies fixture seed-only errors using a fixed whitelist of
           source-defined verification codes; no raw stderr, URI, principal,
           JWT or record is emitted. All failed fixture actions still deny
           the rehearsal and enforce owned database/process cleanup.
CHANGELOG: v1.3.0-SEEDED-LIFECYCLE-VERIFICATION uses
           the fixture's new read-only verify-seed command before and after
           each staged EOS source switch. The full post-browser verifier
           requires decision and execution events that this rehearsal does
           not create and therefore cannot be claimed here. Existing
           immutable fingerprint, exact-ID HTTP and cleanup gates remain.
CHANGELOG: v1.2.0-EXACT-AUTHENTICATED-SOURCE-RECORD-READBACK
           binds the HTTP SYSTEM incident and responder assignment to the
           same seeded exact IDs after each rollback phase. Nonmatching,
           oversized, unavailable or malformed HTTP records fail closed.
           Source rows and tokens remain unlogged.
CHANGELOG: v1.1.0-SAME-DATA-IMMUTABLE-AUDIT-FINGERPRINT obtains
           the existing source fixture's read-only snapshot digest before
           each Python EOS source switch and rejects mutations of selected
           durable work, entitlement-history and audit evidence. All PASS
           labels are withheld until the single owned database is cleaned
           and stopped. Credentials and source rows remain secret.
CHANGELOG: v1.0.0-THREE-PHASE-SAME-DATA-EOS-REHEARSAL performs a strictly
           opt-in source revision switch on one disposable Mongo replica
           without reseeding or dropping it between versions. An exact
           fixture/tenant session is reused; each revision must pass current
           source-authorized and denied HTTP readback plus independent
           durable fixture verification. No runtime is left running.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Locally random synthetic JWT secret; no token,
         URI, actor, row or full HTTP response is printed.
TENANT BOUNDARY: A new single UUID-scoped local replica database. Canonical
         Founder tenant and remote MongoDB cannot be targeted.
AUTHORITY BOUNDARY: Nonproduction source-version and unchanged-seeded-evidence
         continuity only; not production image rollback, Atlas restoration,
         cross-version write/schema compatibility or release approval.
FINANCIAL AUTHORITY BOUNDARY: No financial authority or execution.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tools.eos.ops.mw_t12_local_eos_recovery import (
    MWRecoveryError,
    SET_NAME,
    _admit_rollback_candidate,
    _certified_source_revision,
    _free_port,
    _guard,
    _stop_owned,
    _wait_primary,
)
from tools.eos.ops.mw_t12_versioned_rehearsal import (
    _link_local_dependencies,
    _stage_revision,
)

VERSION = "v1.4.0-BOUNDED-FIXTURE-FAILURE-PROVENANCE"
FIXTURE = "tests/e2e/browser_cert_fixture.py"
READ_TIMEOUT = 12
# Fixed source-owned diagnostics only. Never print subprocess stderr or secrets.
SEED_FAILURE_CODES = (
    "BROWSER_CERT_SEED_SCOPE_INVALID",
    "BROWSER_CERT_SEED_IDENTIFIER_INVALID",
    "BROWSER_CERT_SEEDED_SOURCE_RECORD_MISSING",
    "BROWSER_CERT_SEEDED_ENTITLEMENT_HISTORY_MISSING",
    "BROWSER_CERT_SEEDED_WORKFLOW_SCOPE_INVALID",
    "BROWSER_CERT_SEEDED_WORKFLOW_TRANSITION_MISSING",
    "BROWSER_CERT_LOCAL_REPLICA_SET_URI_REQUIRED",
    "BROWSER_CERT_DATABASE_NOT_OWNED",
)


def _fixture_failure_code(action: str, stderr: bytes) -> str:
    """Return a literal, allowlisted code—not untrusted exception text."""
    if action == "verify-seed":
        for code in SEED_FAILURE_CODES:
            if code.encode("ascii") in stderr:
                return code
    return "UNCLASSIFIED"


def _run_fixture(script: Path, action: str, state: Path, env: dict[str, str],
                 cwd: Path) -> None:
    arguments = [sys.executable, str(script), action]
    if action != "cleanup":
        arguments.extend(["--state", str(state)])
    try:
        result = subprocess.run(
            arguments, cwd=cwd, env=env, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise MWRecoveryError("SAME_DATA_FIXTURE_COMMAND_UNAVAILABLE") from error
    if result.returncode != 0:
        detail = _fixture_failure_code(action, result.stderr or b"")
        raise MWRecoveryError(
            "SAME_DATA_FIXTURE_" + action.upper().replace("-", "_")
            + "_FAILED_" + detail
        )


def _fingerprint_fixture(script: Path, state: Path, env: dict[str, str],
                         cwd: Path) -> str:
    """Read a canonical, record-based audit digest via the existing fixture."""
    try:
        result = subprocess.run(
            [sys.executable, str(script), "fingerprint", "--state", str(state)],
            cwd=cwd, env=env, check=False, capture_output=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise MWRecoveryError("SAME_DATA_AUDIT_FINGERPRINT_UNAVAILABLE") from error
    digest = result.stdout.decode("ascii", errors="replace").strip()
    if (
        result.returncode != 0
        or len(digest) != 64
        or any(c not in "0123456789abcdef" for c in digest)
    ):
        raise MWRecoveryError("SAME_DATA_AUDIT_FINGERPRINT_INVALID")
    return digest


def _read_authorized(base: str, route: str, token: str,
                     tenant: str | None = None) -> int:
    headers = {"Authorization": "Bearer " + token}
    if tenant is not None:
        headers["X-Tenant-ID"] = tenant
    try:
        with urlopen(
            Request(base + route, headers=headers),
            timeout=READ_TIMEOUT,
        ) as response:
            return response.status
    except HTTPError as error:
        try:
            return error.code
        finally:
            error.close()
    except (OSError, URLError, TimeoutError) as error:
        raise MWRecoveryError("SAME_DATA_HTTP_READ_UNAVAILABLE") from error


def _read_records(base: str, route: str, token: str) -> list[dict[str, object]]:
    """Bounded authenticated source-record readback (no response logging)."""
    try:
        with urlopen(
            Request(base + route, headers={"Authorization": "Bearer " + token}),
            timeout=READ_TIMEOUT,
        ) as response:
            if response.status != 200:
                raise MWRecoveryError("SAME_DATA_SOURCE_RECORD_STATUS_DENIED")
            raw = response.read(65_537)
        if len(raw) > 65_536:
            raise MWRecoveryError("SAME_DATA_SOURCE_RESPONSE_OVERSIZED")
        result = json.loads(raw)
        if not isinstance(result, list) or any(
            not isinstance(item, dict) for item in result
        ):
            raise MWRecoveryError("SAME_DATA_SOURCE_RESPONSE_INVALID")
        return result
    except MWRecoveryError:
        raise
    except (OSError, URLError, TimeoutError, UnicodeError, ValueError) as error:
        raise MWRecoveryError("SAME_DATA_SOURCE_RECORD_UNAVAILABLE") from error


def _health(base: str, process: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise MWRecoveryError("SAME_DATA_EOS_EXITED_DURING_STARTUP")
        try:
            with urlopen(base + "/api/kernel", timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, URLError, TimeoutError):
            time.sleep(0.25)
    raise MWRecoveryError("SAME_DATA_EOS_STARTUP_UNVERIFIED")


def _authenticate_unchanged(base: str, state: dict[str, object]) -> None:
    actors = state.get("actors")
    systems = state.get("system_actors")
    tenant = state.get("tenant_id")
    if not isinstance(actors, dict) or not isinstance(systems, dict) or (
        not isinstance(tenant, str) or not tenant.startswith("browser-tenant-")
    ):
        raise MWRecoveryError("SAME_DATA_FIXTURE_SCOPE_INVALID")
    try:
        partner = actors["partner"]["access_token"]
        owner = actors["tenant_owner"]["access_token"]
        responder = systems["system_responder"]["access_token"]
        triage = systems["system_triage"]["access_token"]
    except (KeyError, TypeError):
        raise MWRecoveryError("SAME_DATA_ACTOR_SESSION_INVALID") from None
    if any(not isinstance(token, str) or not token for token in (
        partner, owner, responder, triage
    )):
        raise MWRecoveryError("SAME_DATA_ACTOR_SESSION_INVALID")
    expected = (
        ("/api/legal-operations/productive-work", partner, tenant, 200),
        ("/api/legal-operations/commercial-context", owner, tenant, 200),
        ("/api/legal-operations/productive-work", owner, tenant, 403),
        ("/api/system-services/workspace-bootstrap", responder, None, 200),
        ("/api/system-services/security-incidents", responder, None, 200),
        ("/api/system-services/security-incident-assignments/mine", responder, None, 200),
        ("/api/system-services/security-incident-assignments/mine", triage, None, 403),
    )
    for route, token, scope, code in expected:
        if _read_authorized(base, route, token, scope) != code:
            raise MWRecoveryError("SAME_DATA_AUTHORIZATION_READBACK_FAILED")
    for route, identifier_key, field in (
        ("/api/system-services/security-incidents", "system_incident_id", "incidentId"),
        ("/api/system-services/security-incident-assignments/mine",
         "system_assignment_id", "assignmentId"),
    ):
        identifier = state.get(identifier_key)
        if not isinstance(identifier, str) or not identifier:
            raise MWRecoveryError("SAME_DATA_SOURCE_RECORD_ID_MISSING")
        records = _read_records(base, route, responder)
        if not any(record.get(field) == identifier for record in records):
            raise MWRecoveryError("SAME_DATA_SOURCE_RECORD_ID_MISMATCH")


def _certify_running_version(
    source: Path, env: dict[str, str], state_file: Path,
    fixture: Path, revision: str, fingerprint: str,
) -> None:
    port = _free_port()
    base = "http://127.0.0.1:" + str(port)
    application = None
    stage_env = dict(env)
    stage_env["PYTHONPATH"] = str(source)
    try:
        application = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "tools.eos.api.server:app",
             "--host", "127.0.0.1", "--port", str(port)],
            cwd=source, env=stage_env, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        _health(base, application)
        state = json.loads(state_file.read_text(encoding="utf-8"))
        if state.get("database_name") != env["BROWSER_CERT_MONGO_DATABASE"]:
            raise MWRecoveryError("SAME_DATA_DATABASE_IDENTITY_MISMATCH")
        _authenticate_unchanged(base, state)
        _run_fixture(fixture, "verify-seed", state_file, env, Path.cwd())
        if _fingerprint_fixture(fixture, state_file, env, Path.cwd()) != fingerprint:
            raise MWRecoveryError("SAME_DATA_AUDIT_EVIDENCE_MUTATED")
        print("MW_T12_SAME_DATA_VERSION_" + revision[:12] + "=PASS", flush=True)
    except (OSError, UnicodeError, ValueError) as error:
        raise MWRecoveryError("SAME_DATA_VERSION_READBACK_FAILED") from error
    finally:
        if application is not None:
            _stop_owned(application)
        print("MW_T12_SAME_DATA_EOS_STOPPED=TRUE", flush=True)


def rehearse_same_data(target: str) -> int:
    binary, _node = _guard()
    current, older = _admit_rollback_candidate(target)
    checkout = Path.cwd().resolve()
    fixture = checkout / FIXTURE
    if not fixture.is_file():
        raise MWRecoveryError("SAME_DATA_FIXTURE_SOURCE_MISSING")
    with tempfile.TemporaryDirectory(prefix="wilsy-mw-t12-same-data-") as tmp:
        root = Path(tmp)
        dbpath = root / "mongo"
        dbpath.mkdir(mode=0o700)
        state_path = root / "state.json"
        database = "wilsy_l8_8m_r3_mwt12_continuity_" + secrets.token_hex(10)
        port = _free_port()
        uri = (
            f"mongodb://127.0.0.1:{port}/{database}"
            f"?replicaSet={SET_NAME}&directConnection=true"
        )
        env = os.environ.copy()
        for key in ("BROWSER_CERT_MONGO_URI", "MONGODB_URI", "MONGO_URI",
                    "MONGO_URL", "WILSY_MONGO_URI", "WILSY_MONGODB_URI"):
            env[key] = uri
        env.update({
            "BROWSER_CERT_MONGO_DATABASE": database,
            "WILSY_JWT_SECRET": secrets.token_hex(32),
            "WILSY_PLATFORM_WORKFORCE_SCOPE_ID": "browser-cert-platform-workforce",
            "ENV": "development",
            "WILSY_ENV": "development",
            "WILSY_KENNEL_DB_TLS": "0",
            "PYTHONPATH": str(checkout),
        })
        mongo = None
        seeded = False
        try:
            mongo = subprocess.Popen(
                [binary, "--dbpath", str(dbpath), "--port", str(port),
                 "--bind_ip", "127.0.0.1", "--replSet", SET_NAME,
                 "--nounixsocket", "--quiet"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, close_fds=True,
            )
            _wait_primary(mongo, port)
            # This one fixture, including issued synthetic sessions, remains
            # unchanged while the active Python EOS source is rolled back.
            seeded = True
            _run_fixture(fixture, "seed", state_path, env, checkout)
            _run_fixture(fixture, "verify-seed", state_path, env, checkout)
            baseline = _fingerprint_fixture(fixture, state_path, env, checkout)
            for label, sha in (("current", current), ("historical", older),
                               ("restored", current)):
                source = root / (label + "-source")
                source.mkdir(mode=0o700)
                _stage_revision(sha, checkout, source)
                _link_local_dependencies(checkout, source)
                _certify_running_version(
                    source, env, state_path, fixture, sha, baseline
                )
                if _certified_source_revision() != current:
                    raise MWRecoveryError("SOURCE_REVISION_CHANGED_DURING_DRILL")
        finally:
            if seeded and mongo is not None and mongo.poll() is None:
                try:
                    _run_fixture(fixture, "cleanup", state_path, env, checkout)
                finally:
                    _stop_owned(mongo)
                print("MW_T12_SAME_DATA_FIXTURE_REMOVED=TRUE", flush=True)
            elif mongo is not None:
                _stop_owned(mongo)
                if seeded:
                    raise MWRecoveryError("SAME_DATA_MONGO_EXITED_BEFORE_CLEANUP")
            print("MW_T12_SAME_DATA_OWNED_MONGO_STOPPED=TRUE", flush=True)
    # Only the verified, cleaned, and stopped case may claim success.
    print("MW_T12_SAME_DATA_THREE_PHASE_READBACK=PASS", flush=True)
    print("MW_T12_SAME_DATA_IMMUTABLE_AUDIT_EVIDENCE=UNCHANGED", flush=True)
    print("MW_T12_SAME_DATA_RECORDS_RESEEDED=FALSE", flush=True)
    print("MW_T12_SAME_DATA_BACKEND_SOURCE_RESTORED=TRUE", flush=True)
    print("MW_T12_VERSIONED_ROLLBACK_CERTIFIED=FALSE", flush=True)
    print("MW_T12_FULL_INFRASTRUCTURE_RECOVERY_CERTIFIED=FALSE", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MW-T12 single disposable database, three Python EOS versions"
    )
    parser.add_argument("--rehearse", required=True, metavar="EXACT_OLDER_COMMIT")
    args = parser.parse_args(argv)
    try:
        return rehearse_same_data(args.rehearse)
    except (MWRecoveryError, KeyboardInterrupt) as error:
        code = error.code if isinstance(error, MWRecoveryError) else "OPERATOR_INTERRUPTED"
        print("MW_T12_SAME_DATA_REHEARSAL=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_VERSIONED_ROLLBACK_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: tools/eos/ops/mw_t12_same_data_rehearsal.py
# VERSION: v1.4.0-BOUNDED-FIXTURE-FAILURE-PROVENANCE
# AUTHORITY BOUNDARY: Only disposable single-database three-phase source test.
# TENANT POSTURE: UUID synthetic local replica; never canonical wilsy or Atlas.
# FAIL-CLOSED POSTURE: Auth, durable fixture or cleanup failure denies success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
