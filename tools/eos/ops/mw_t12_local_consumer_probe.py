"""TITLE: MW-T12 local Atlas consumer source binding probe.
VERSION: v1.0.0-LOCAL-CONNECTION-OWNERSHIP-EVIDENCE
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Read-only process/credential target evidence that distinguishes
         actual local EOS listener identity from inherited CLI environment.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_local_consumer_probe.py
COLLABORATION / OWNERSHIP: Canonical tools/eos/kernel/db.py MONGODB_URI,
         local EOS 9095 listener and shared Atlas consumer attribution register.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-LOCAL-CONNECTION-OWNERSHIP-EVIDENCE establishes independent
           listener PID check, shell-environment target classification and
           explicit unknown-ownership denials with no credential logging.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No URI, secret, username, environment dump,
                           argv, raw process list or IP addresses printed.
TENANT BOUNDARY: Local operator only; no business record access.
AUTHORITY BOUNDARY: Does not claim the shell environment is the running
                    EOS process environment or authenticate to Atlas.
FINANCIAL AUTHORITY BOUNDARY: No paid resource activation or IAM grant.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
from urllib.parse import parse_qs, unquote, urlsplit

VERSION = "v1.0.0-LOCAL-CONNECTION-OWNERSHIP-EVIDENCE"
ATLAS_CLUSTER_SRV = "legal-doc-test.xmlpwmq.mongodb.net"
ATLAS_SHARDS = frozenset(
    "ac-nagjjuj-shard-00-0" + str(i) + ".xmlpwmq.mongodb.net"
    for i in range(3)
)
LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
MAX_URI_LENGTH = 16384
MAX_PROCESS_OUTPUT = 4096


class ProbeDenied(RuntimeError):
    """Safe error code; never carries a credential, URI or subprocess output."""


def require(ok: bool, code: str) -> None:
    """Deny unknown or unsupported environment/source evidence."""
    if not ok:
        raise ProbeDenied(code)


def classify_uri(raw: str | None) -> dict[str, str]:
    """Classify only a supplied environment value without opening network.

    The URI must be syntactically valid and its host set unambiguous. No
    tokens, usernames or raw hostname values are output. A stable digest of
    host identities can be compared locally but must not be treated as
    evidence that a live service selected that secret.
    """
    require(isinstance(raw, str) and bool(raw.strip()),
            "SHELL_MONGODB_URI_NOT_PRESENT")
    require(len(raw) <= MAX_URI_LENGTH, "SHELL_MONGODB_URI_OVERSIZED")
    require(raw == raw.strip() and "\n" not in raw and "\r" not in raw,
            "SHELL_MONGODB_URI_INVALID")
    require(raw.startswith(("mongodb://", "mongodb+srv://")),
            "SHELL_MONGODB_URI_INVALID")
    scheme, remainder = raw.split("://", 1)
    authority = remainder.split("/", 1)[0].split("?", 1)[0]
    hosts_part = authority.rsplit("@", 1)[-1]
    host_tokens = hosts_part.split(",")
    require(0 < len(host_tokens) <= 10 and all(host_tokens),
            "SHELL_MONGODB_TARGET_INVALID")
    hosts = []
    for token in host_tokens:
        # Most IPv4 and Atlas hostnames; IPv6 loopback is also permitted.
        if token.startswith("["):
            match = re.fullmatch(r"\[([0-9a-fA-F:]+)\](?::\d{1,5})?", token)
            require(match is not None, "SHELL_MONGODB_TARGET_INVALID")
            host = match.group(1).lower()
        else:
            require(token.count(":") <= 1, "SHELL_MONGODB_TARGET_INVALID")
            host = token.split(":", 1)[0].lower()
            if ":" in token:
                port = token.rsplit(":", 1)[1]
                require(port.isdigit() and 1 <= int(port) <= 65535,
                        "SHELL_MONGODB_PORT_INVALID")
        require(bool(re.fullmatch(r"[a-z0-9.-]+|[0-9a-f:]+", host)),
                "SHELL_MONGODB_TARGET_INVALID")
        hosts.append(host)
    if scheme == "mongodb+srv":
        require(len(hosts) == 1 and ":" not in hosts_part,
                "SHELL_MONGODB_SRV_TARGET_INVALID")
    parsed = urlsplit(raw)
    require(parsed.fragment == "", "SHELL_MONGODB_URI_INVALID")
    query = parse_qs(parsed.query, keep_blank_values=True)
    auth_source = query.get("authSource", [])
    require(len(auth_source) <= 1, "SHELL_MONGODB_AUTH_SOURCE_INVALID")
    db = unquote(parsed.path.lstrip("/")).split("/")[0]
    host_set = frozenset(hosts)
    if host_set == {ATLAS_CLUSTER_SRV} or host_set == ATLAS_SHARDS:
        target = "MW_T12_SHARED_TEST_ATLAS"
    elif host_set.issubset(LOCAL_HOSTS):
        target = "LOOPBACK_MONGODB"
    else:
        target = "OTHER_OR_UNVERIFIED"
    digest = hashlib.sha3_512(
        ("|".join(sorted(host_set)) + "/" + db).encode("utf-8")
    ).hexdigest()
    return {
        "target": target,
        "transport": "SRV_TLS" if scheme == "mongodb+srv"
        else "STANDARD_MONGODB",
        "host_count": str(len(host_set)),
        "target_host_db_sha3_512": digest,
    }


def local_listener_pids() -> list[int]:
    """Query only localhost TCP 9095 listener PIDs; never inspect argv/env."""
    try:
        result = subprocess.run(
            ["lsof", "-nP", "-tiTCP:9095", "-sTCP:LISTEN"],
            capture_output=True, timeout=6, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProbeDenied("LOCAL_LISTENER_QUERY_UNAVAILABLE") from exc
    require(result.returncode in {0, 1}
            and len(result.stdout) <= MAX_PROCESS_OUTPUT,
            "LOCAL_LISTENER_QUERY_FAILED")
    raw = result.stdout.decode("ascii", "strict").strip()
    if not raw:
        return []
    pids = raw.splitlines()
    require(len(pids) <= 8 and all(p.isdecimal() and int(p) > 0 for p in pids),
            "LOCAL_LISTENER_PID_INVALID")
    return sorted(set(int(p) for p in pids))


def run() -> None:
    """Emit safe local evidence, explicitly denying runtime/secret inference."""
    pids = local_listener_pids()
    print("MW_T12_LOCAL_EOS_9095_LISTENER=" +
          ("PRESENT" if pids else "ABSENT"))
    print("MW_T12_LOCAL_EOS_LISTENER_COUNT=" + str(len(pids)))
    print("MW_T12_LOCAL_EOS_PID_IDENTITY=NOT_BOUND_TO_SHELL_SECRET")
    try:
        result = classify_uri(os.environ.get("MONGODB_URI"))
    except ProbeDenied as error:
        print("MW_T12_SHELL_MONGODB_URI_CLASSIFICATION=" + str(error))
    else:
        print("MW_T12_SHELL_MONGODB_TARGET=" + result["target"])
        print("MW_T12_SHELL_MONGODB_TRANSPORT=" + result["transport"])
        print("MW_T12_SHELL_MONGODB_HOST_COUNT=" + result["host_count"])
        print("MW_T12_SHELL_HOST_DATABASE_DIGEST=" +
              result["target_host_db_sha3_512"])
    print("MW_T12_LIVE_EOS_RESOLVED_TARGET=NOT_VERIFIED")
    print("MW_T12_ATLAS_SOURCE_IP_OWNER=NOT_VERIFIED")
    print("MW_T12_ATLAS_WILDCARD_RETIREMENT=BLOCKED")
    print("MW_T12_FARGATE_COMPUTE=NOT_LAUNCHED")


def main(argv: list[str] | None = None) -> int:
    """Read local listener and own environment only; no cloud mutations."""
    parser = argparse.ArgumentParser(
        description="MW-T12 secret-free local Mongo consumer preflight")
    parser.parse_args(argv)
    try:
        run()
        return 0
    except (ProbeDenied, UnicodeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, ProbeDenied) else "LOCAL_INPUT_INVALID"
        print("MW_T12_LOCAL_CONSUMER_PROBE=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/mw_t12_local_consumer_probe.py
# VERSION: v1.0.0-LOCAL-CONNECTION-OWNERSHIP-EVIDENCE
# AUTHORITY BOUNDARY: Own shell env + local 9095 listener only, read-only.
# TENANT POSTURE: No tenant reads or credential/identity output.
# FAIL-CLOSED POSTURE: Does not infer runtime ownership from shell URI.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
