"""TITLE: MW-T12 synthetic Atlas temporary source-IP admission.
VERSION: v1.4.0-SAFE-ADMIN-API-DENIAL-CODES
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Inventory the shared free Atlas test project's network exposure and
         optionally admit exactly one verified ECS task public source IP for
         six hours, or remove only the exact task-owned temporary /32 entry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_atlas_access_admission.py
COLLABORATION / OWNERSHIP: Read-only AWS ECS/EC2 identity via existing MW-T12
         task admission; Atlas Admin API v2 project-scoped network capability.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.4.0-SAFE-ADMIN-API-DENIAL-CODES preserves only status-class
           diagnostics for Atlas API 401/403/429, without exposing body,
           headers, credentials, or mistaking API-key IP allowlists for DB
           network lists. No retries, credential escalation or mutations.
CHANGELOG: v1.3.0-READONLY-ISOLATION-CERT adds an opt-in, mutation-free
           isolation admission that denies global access, duplicate/invalid
           networks and missing consumer ownership without deleting access.
CHANGELOG: v1.2.1-FRESH-REVALIDATION-AND-ACCURATE-AUDIT rechecks the exact Atlas network set immediately
           before any permitted add/revoke, refusing a concurrent change;
           labels baseline inventory truth accurately, and documents the
           narrow owner-only delete boundary.
CHANGELOG: v1.2.0-FORENSIC-BASELINE-OWNED-ROLLBACK adds canonical SHA3-512 Atlas IP/CIDR
           inventory fingerprint, exact task-ID-bound temporary entry receipt
           and explicit owner-only IP revocation with independent readback.
           Never deletes wildcard or unrelated shared Atlas access entries.
CHANGELOG: v1.1.0-SECRET-BACKED-TASK-SOURCE-VERIFICATION admits only task revisions with the exact
           SSM-backed synthetic connection configuration, immutable known
           image digest, execution-role identity and no application task role.
           Denies dormant no-secret revisions; fixes missing-IP exception
           handling and limits mutation attempts to verified ECS source IP.
CHANGELOG: v1.0.0-EXACT-ECS-SOURCE-IP-AND-TEMPORARY-ATLAS-ADMISSION
           provides bounded Atlas entry inventory, public ENI attestation,
           explicit six-hour source-IP mutation gate, and post-write readback.
           Rejects existing global access; never deletes shared entries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: API keys from hidden prompt, no URI or key logs;
                           only owner-bound temporary Atlas /32 add/revoke;
                           no public EOS ingress, NAT, database or IAM writes.
TENANT BOUNDARY: Existing synthetic-only test project; never production.
AUTHORITY BOUNDARY: Atlas IP allowance alone is not authenticated EOS or
                    rollback certification; no automatic compute launch.
FINANCIAL AUTHORITY BOUNDARY: No AWS billing action; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from getpass import getpass
import ipaddress
import re

from tools.eos.ops import mw_t12_task_definition_admission as ecs

VERSION = "v1.4.0-SAFE-ADMIN-API-DENIAL-CODES"
PROJECT = "668cdbbd975c3c0f05fca20c"
ACCOUNT = "121014832643"
REGION = "af-south-1"
CLUSTER = "wilsy-mwt12-nonproduction"
FAMILY = "wilsy-mwt12-eos-nonproduction"
SG = "sg-05bbf379de9a0eee8"
PUBLIC_IP_TTL_HOURS = 6
OWNED_COMMENT_PREFIX = "MW-T12 task "
ATLAS_API = "https://cloud.mongodb.com/api/atlas/v2/groups/" + PROJECT
ATLAS_MEDIA_TYPE = "application/vnd.atlas.2024-08-05+json"
TASK_ARN = re.compile(
    r"arn:aws:ecs:af-south-1:121014832643:task/"
    r"wilsy-mwt12-nonproduction/[0-9a-f]{32}\Z"
)


class NetworkAdmissionError(RuntimeError):
    """Fail-closed public, bounded reason code without secrets or raw responses."""


def require(condition: bool, reason: str) -> None:
    """Refuse unknown ownership, shared-project exposure and mutation state."""
    if not condition:
        raise NetworkAdmissionError(reason)


def atlas_session():
    """Build digest-auth Atlas transport from non-echoing operator inputs only.

    Credentials never pass through command arguments, environment variables,
    logs, exceptions or saved files. Returned session is process-local.
    """
    try:
        import requests
        from requests.auth import HTTPDigestAuth
    except ImportError as exc:
        raise NetworkAdmissionError("ATLAS_REQUESTS_DEPENDENCY_REQUIRED") from exc
    public = getpass("Atlas Admin API public key (hidden): ")
    private = getpass("Atlas Admin API private key (hidden): ")
    require(bool(public and private), "ATLAS_API_CREDENTIALS_REQUIRED")
    client = requests.Session()
    client.auth = HTTPDigestAuth(public, private)
    client.headers.update({"Accept": ATLAS_MEDIA_TYPE})
    return client


def atlas(client, method: str, route: str, *, payload=None, params=None):
    """Execute only enumerated Atlas access-list API routes with bounded reads."""
    require(method in {"GET", "POST", "DELETE"}, "ATLAS_METHOD_NOT_ADMITTED")
    if method == "DELETE":
        require(route.startswith("/accessList/"), "ATLAS_ROUTE_NOT_ADMITTED")
        raw_ip = route.removeprefix("/accessList/")
        try:
            address = ipaddress.ip_address(raw_ip)
        except ValueError as exc:
            raise NetworkAdmissionError("ATLAS_DELETE_IPV4_INVALID") from exc
        require(address.version == 4 and address.is_global
                and str(address) == raw_ip,
                "ATLAS_DELETE_IPV4_INVALID")
    else:
        require(route == "/accessList", "ATLAS_ROUTE_NOT_ADMITTED")
    try:
        response = client.request(
            method, ATLAS_API + route, json=payload, params=params, timeout=20,
        )
        expected = {"GET": {200}, "POST": {200, 201, 202},
                    "DELETE": {200, 202, 204}}
        # Reject unauthenticated or unauthorized requests with distinct
        # *status-only* codes; never log Atlas body, headers, key identifiers,
        # IP addresses, request URLs or the protected authentication context.
        # A 403 may indicate missing project role OR the API credential's
        # separate source-IP allowlist. Neither authorizes access-list changes.
        if response.status_code == 401:
            raise NetworkAdmissionError("ATLAS_ADMIN_API_AUTHENTICATION_DENIED_401")
        if response.status_code == 403:
            raise NetworkAdmissionError("ATLAS_ADMIN_API_ACCESS_DENIED_403")
        if response.status_code == 429:
            raise NetworkAdmissionError("ATLAS_ADMIN_API_RATE_LIMITED_429")
        require(response.status_code in expected[method],
                "ATLAS_API_REQUEST_DENIED")
        require(len(response.content) <= 1048576, "ATLAS_RESPONSE_OVERSIZED")
        data = {} if method == "DELETE" else response.json()
    except NetworkAdmissionError:
        raise
    except Exception as exc:
        raise NetworkAdmissionError("ATLAS_API_UNAVAILABLE_OR_INVALID") from exc
    require(isinstance(data, (dict, list)), "ATLAS_RESPONSE_INVALID")
    return data


def inventory(client) -> list[dict]:
    """Read every access-list page; absence of owner metadata remains unknown."""
    entries: list[dict] = []
    for page in range(1, 11):
        data = atlas(client, "GET", "/accessList",
                     params={"pageNum": page, "itemsPerPage": 100})
        require(isinstance(data, dict)
                and isinstance(data.get("results"), list),
                "ATLAS_ACCESS_LIST_RESPONSE_INVALID")
        rows = data["results"]
        require(all(isinstance(row, dict) for row in rows),
                "ATLAS_ACCESS_ENTRY_INVALID")
        entries.extend(rows)
        require(len(entries) <= 1000, "ATLAS_ACCESS_LIST_TOO_LARGE")
        total = data.get("totalCount")
        require(isinstance(total, int) and total >= len(entries),
                "ATLAS_ACCESS_LIST_COUNT_INVALID")
        if len(entries) == total:
            return entries
        require(len(rows) > 0, "ATLAS_ACCESS_LIST_PAGING_STALLED")
    raise NetworkAdmissionError("ATLAS_ACCESS_LIST_PAGING_EXHAUSTED")


def entry_ip(row: dict) -> str:
    """Normalize the Atlas project's supported IP/CIDR entry representations."""
    value = row.get("cidrBlock") or row.get("ipAddress")
    require(isinstance(value, str), "ATLAS_ENTRY_ADDRESS_INVALID")
    try:
        return str(ipaddress.ip_network(value, strict=False))
    except ValueError as exc:
        raise NetworkAdmissionError("ATLAS_ENTRY_ADDRESS_INVALID") from exc


def audit_entries(entries: list[dict]) -> None:
    """Report exposure statistics only, never assert consumer ownership."""
    networks = [entry_ip(item) for item in entries]
    global_count = networks.count("0.0.0.0/0")
    owner_unknown = sum(not item.get("comment") for item in entries)
    digest = network_fingerprint(entries)
    print("MW_T12_ATLAS_ACCESS_CIDR_SHA3_512=" + digest)
    print("MW_T12_ATLAS_ACCESS_ENTRIES=" + str(len(entries)))
    print("MW_T12_ATLAS_UNRESTRICTED_ENTRIES=" + str(global_count))
    print("MW_T12_ATLAS_ENTRIES_WITHOUT_OWNER_COMMENT=" + str(owner_unknown))
    print("MW_T12_ATLAS_CONSUMER_DEPENDENCIES=UNVERIFIED")
    print("MW_T12_ATLAS_INITIAL_INVENTORY_READ_ONLY=TRUE")


def certify_isolated_network(entries: list[dict]) -> None:
    """Deny unreviewed shared consumer dependencies without mutating Atlas.

    A restrictive Atlas access list is necessary but never sufficient for
    proving task identity, Fargate connectivity, backup or recovery. Require
    exactly unique global IPv4 /32 entries with explicit nonempty owner
    comments, no wildcard or broader CIDR. Never guess who uses a network.
    """
    networks = [entry_ip(entry) for entry in entries]
    require("0.0.0.0/0" not in networks,
            "ATLAS_PUBLIC_NETWORK_WILDCARD_PRESENT")
    require(len(networks) == len(set(networks)),
            "ATLAS_DUPLICATE_NETWORKS_UNATTRIBUTED")
    for entry, network in zip(entries, networks, strict=True):
        try:
            cidr = ipaddress.ip_network(network, strict=True)
        except ValueError as exc:
            raise NetworkAdmissionError("ATLAS_NETWORK_INVALID") from exc
        require(cidr.version == 4 and cidr.prefixlen == 32
                and cidr.network_address.is_global,
                "ATLAS_NONEXACT_OR_NONGLOBAL_NETWORK")
        comment = entry.get("comment")
        require(isinstance(comment, str) and bool(comment.strip())
                and len(comment) <= 256,
                "ATLAS_NETWORK_CONSUMER_UNATTRIBUTED")
    print("MW_T12_ATLAS_SOURCE_NETWORK_INVENTORY=ISOLATION_ELIGIBLE")
    print("MW_T12_ATLAS_SOURCE_NETWORK_EVIDENCE=READ_ONLY")
    print("MW_T12_ATLAS_ECS_CONNECTIVITY_CERTIFIED=FALSE")
    print("MW_T12_ATLAS_BACKUP_RESTORE_CERTIFIED=FALSE")


def public_source_ip(profile: str, task_arn: str) -> str:
    """Resolve precisely one already-running nonproduction Fargate task's ENI.

    An IP from Mac, DNS, unrelated tasks, or the Atlas destination is invalid.
    This read-only task check never requests ECS launch or public ingress.
    """
    require(TASK_ARN.fullmatch(task_arn) is not None,
            "EXACT_NONPRODUCTION_TASK_ARN_REQUIRED")
    caller = ecs.aws(profile, "sts", "get-caller-identity")
    require(caller.get("Account") == ACCOUNT, "AWS_ACCOUNT_MISMATCH")
    result = ecs.aws(profile, "ecs", "describe-tasks",
                     "--cluster", CLUSTER, "--tasks", task_arn)
    tasks = result.get("tasks", [])
    require(not result.get("failures")
            and isinstance(tasks, list) and len(tasks) == 1,
            "EXACT_ECS_TASK_NOT_FOUND")
    task = tasks[0]
    require(task.get("taskArn") == task_arn
            and task.get("launchType") == "FARGATE"
            and task.get("lastStatus") == "RUNNING"
            and task.get("desiredStatus") == "RUNNING",
            "TASK_IDENTITY_OR_STATE_UNVERIFIED")
    definition_arn = task.get("taskDefinitionArn")
    require(isinstance(definition_arn, str)
            and re.fullmatch(
                "arn:aws:ecs:" + REGION + ":" + ACCOUNT +
                ":task-definition/" + FAMILY + r":[1-9][0-9]*",
                definition_arn,
            ) is not None,
            "TASK_DEFINITION_NOT_OWNED")
    definition = ecs.aws(
        profile, "ecs", "describe-task-definition", "--task-definition",
        definition_arn,
    ).get("taskDefinition", {})
    require(isinstance(definition, dict)
            and definition.get("taskDefinitionArn") == definition_arn
            and definition.get("status") == "ACTIVE"
            and definition.get("executionRoleArn") == ecs.ROLE
            and not definition.get("taskRoleArn")
            and definition.get("networkMode") == "awsvpc"
            and "FARGATE" in definition.get("requiresCompatibilities", []),
            "TASK_DEFINITION_AUTHORITY_UNVERIFIED")
    containers = definition.get("containerDefinitions")
    require(isinstance(containers, list) and len(containers) == 1
            and isinstance(containers[0], dict),
            "TASK_DEFINITION_CONTAINER_INVALID")
    container = containers[0]
    expected_images = {
        ecs.source.URI + "@" + ecs.DIGEST_HISTORICAL,
        ecs.source.URI + "@" + ecs.DIGEST_CURRENT,
    }
    require(container.get("image") in expected_images
            and container.get("name") == "python-eos"
            and container.get("readonlyRootFilesystem") is True
            and container.get("user") == "10001:10001"
            and container.get("secrets") == [{
                "name": "MONGODB_URI",
                "valueFrom": ecs.SSM_PARAMETER_ARN,
            }], "TASK_SYNTHETIC_SECRET_OR_IMAGE_UNVERIFIED")
    attachments = task.get("attachments", [])
    details = [
        detail for attachment in attachments if isinstance(attachment, dict)
        and attachment.get("type") == "ElasticNetworkInterface"
        and attachment.get("status") == "ATTACHED"
        for detail in attachment.get("details", [])
        if isinstance(detail, dict) and detail.get("name") == "networkInterfaceId"
    ]
    require(len(details) == 1, "TASK_ENI_AMBIGUOUS")
    interface_id = details[0].get("value")
    require(isinstance(interface_id, str)
            and re.fullmatch(r"eni-[0-9a-f]+", interface_id) is not None,
            "TASK_ENI_INVALID")
    interfaces = ecs.aws(profile, "ec2", "describe-network-interfaces",
                         "--network-interface-ids", interface_id).get(
                             "NetworkInterfaces", [])
    require(isinstance(interfaces, list) and len(interfaces) == 1,
            "TASK_NETWORK_INTERFACE_UNVERIFIED")
    interface = interfaces[0]
    require(interface.get("NetworkInterfaceId") == interface_id
            and interface.get("VpcId") == "vpc-05a3c2c855c4dde26"
            and {g.get("GroupId") for g in interface.get("Groups", [])}
            == {SG}, "TASK_NETWORK_AUTHORITY_MISMATCH")
    address = (interface.get("Association") or {}).get("PublicIp")
    try:
        ip = ipaddress.ip_address(address)
    except (ValueError, TypeError) as exc:
        raise NetworkAdmissionError("TASK_PUBLIC_ADDRESS_MISSING") from exc
    require(ip.version == 4 and ip.is_global,
            "TASK_PUBLIC_ADDRESS_NOT_GLOBAL")
    return str(ip)


def network_fingerprint(entries: list[dict]) -> str:
    """SHA3-512 stable network-set evidence; no volatile provider metadata.

    The fingerprint enables compare-before-mutate and source/rollback evidence,
    but says nothing about unknown application owners or existing connections.
    """
    return hashlib.sha3_512(json.dumps(
        sorted(entry_ip(item) for item in entries),
        separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()


def owned_comment(task_arn: str) -> str:
    """Bind a temporary Atlas entry to the exact verified task ARN suffix."""
    require(TASK_ARN.fullmatch(task_arn) is not None,
            "EXACT_NONPRODUCTION_TASK_ARN_REQUIRED")
    return OWNED_COMMENT_PREFIX + task_arn.rsplit("/", 1)[-1]


def admit(client, entries: list[dict], task_ip: str,
          task_arn: str) -> None:
    """Add an exact six-hour task-owned /32 and independently read it back.

    Wildcard or existing same-IP entry denies. The comment is bound to one
    exact AWS task identity; no existing shared entry can be overwritten.
    """
    networks = [entry_ip(row) for row in entries]
    require("0.0.0.0/0" not in networks,
            "SHARED_ATLAS_GLOBAL_ACCESS_MUST_BE_REMEDIATED_FIRST")
    cidr = task_ip + "/32"
    require(cidr not in networks, "TASK_IP_ALREADY_ADMITTED_OR_UNOWNED")
    expires = datetime.now(timezone.utc) + timedelta(
        hours=PUBLIC_IP_TTL_HOURS,
    )
    # The initial inventory might have become stale while ECS was checked.
    # Require exact network-set continuity and verify no wildcard appeared.
    latest = inventory(client)
    require(network_fingerprint(latest) == network_fingerprint(entries),
            "ATLAS_ACCESS_LIST_CHANGED_DURING_ADMISSION")
    require("0.0.0.0/0" not in [entry_ip(row) for row in latest],
            "SHARED_ATLAS_GLOBAL_ACCESS_MUST_BE_REMEDIATED_FIRST")
    payload = [{
        "ipAddress": task_ip,
        "comment": owned_comment(task_arn),
        "deleteAfterDate": expires.isoformat(timespec="seconds").replace(
            "+00:00", "Z",
        ),
    }]
    atlas(client, "POST", "/accessList", payload=payload)
    post = inventory(client)
    matching = [row for row in post if entry_ip(row) == cidr]
    require(len(matching) == 1
            and matching[0].get("comment") == payload[0]["comment"]
            and matching[0].get("deleteAfterDate"),
            "ATLAS_TEMPORARY_SOURCE_IP_READBACK_FAILED")
    print("MW_T12_ATLAS_SOURCE_IP_CIDR=" + cidr)
    print("MW_T12_ATLAS_TEMPORARY_ACCESS=VERIFIED_READBACK")
    print("MW_T12_ATLAS_TTL_HOURS=6")
    print("MW_T12_ATLAS_ROLLBACK_CERTIFIED=FALSE")



def revoke_owned(client, entries: list[dict], task_arn: str,
                 task_ip: str) -> None:
    """Remove only one task-identified MW-T12 entry and verify its absence.

    Rollback is allowed after the task stops. It uses exact task ARN binding,
    explicitly supplied IPv4, provider-recorded ownership and a bounded
    expiration interval; never deletes wildcard, external or old entries.
    """
    require(TASK_ARN.fullmatch(task_arn) is not None,
            "EXACT_NONPRODUCTION_TASK_ARN_REQUIRED")
    try:
        address = ipaddress.ip_address(task_ip)
    except ValueError as exc:
        raise NetworkAdmissionError("REVOKE_SOURCE_IPV4_INVALID") from exc
    require(address.version == 4 and address.is_global
            and str(address) == task_ip,
            "REVOKE_SOURCE_IPV4_INVALID")
    network = task_ip + "/32"
    require(network != "0.0.0.0/0", "WILDCARD_REVOCATION_FORBIDDEN")
    matching = [row for row in entries if entry_ip(row) == network]
    require(len(matching) == 1, "OWNED_ATLAS_ENTRY_NOT_UNIQUE")
    entry = matching[0]
    require(entry.get("comment") == owned_comment(task_arn),
            "OWNED_ATLAS_ENTRY_IDENTITY_MISMATCH")
    expires = entry.get("deleteAfterDate")
    require(isinstance(expires, str), "OWNED_ATLAS_EXPIRY_MISSING")
    try:
        expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
    except ValueError as exc:
        raise NetworkAdmissionError("OWNED_ATLAS_EXPIRY_INVALID") from exc
    require(expiry.tzinfo is not None
            and datetime.now(timezone.utc) - timedelta(minutes=15)
            <= expiry <= datetime.now(timezone.utc)
            + timedelta(hours=PUBLIC_IP_TTL_HOURS, minutes=15),
            "OWNED_ATLAS_EXPIRY_OUT_OF_BOUNDS")
    latest = inventory(client)
    require(network_fingerprint(latest) == network_fingerprint(entries),
            "ATLAS_ACCESS_LIST_CHANGED_DURING_REVOKE")
    current_matches = [row for row in latest if entry_ip(row) == network]
    require(len(current_matches) == 1
            and current_matches[0].get("comment") == owned_comment(task_arn)
            and current_matches[0].get("deleteAfterDate") == expires,
            "OWNED_ATLAS_ENTRY_CHANGED_DURING_REVOKE")
    atlas(client, "DELETE", "/accessList/" + task_ip)
    remaining = inventory(client)
    require(all(entry_ip(row) != network for row in remaining),
            "OWNED_ATLAS_ENTRY_DELETE_NOT_VERIFIED")
    print("MW_T12_OWNED_ATLAS_ENTRY_REVOKED=VERIFIED")
    print("MW_T12_SHARED_ATLAS_ENTRIES_DELETED=ZERO")
    print("MW_T12_ROLLBACK_CERTIFIED=FALSE")


def main(argv: list[str] | None = None) -> int:
    """Inventory by default; opt-in changes only exact project network scope."""
    parser = argparse.ArgumentParser(
        description="MW-T12 isolated Atlas source-network admission")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    parser.add_argument("--task-arn", help="Exact running owned Fargate task ARN")
    parser.add_argument("--certify-isolation", action="store_true",
                        help="Read-only deny of unowned or public Atlas access")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--admit-six-hours", action="store_true",
                         help="Explicit Atlas temporary /32 addition")
    actions.add_argument("--revoke-owned", action="store_true",
                         help="Delete only a verified MW-T12 task-owned /32")
    parser.add_argument("--owned-source-ip",
                        help="Exact recorded /32 source IPv4 for owned rollback")
    args = parser.parse_args(argv)
    try:
        require(not args.certify_isolation or not (
            args.admit_six_hours or args.revoke_owned or args.task_arn
            or args.owned_source_ip), "ISOLATION_AUDIT_MUST_BE_READ_ONLY")
        require(not (args.admit_six_hours or args.revoke_owned)
                or bool(args.task_arn),
                "TASK_ARN_REQUIRED_FOR_MUTATION")
        require(not args.revoke_owned or bool(args.owned_source_ip),
                "OWNED_SOURCE_IP_REQUIRED_FOR_ROLLBACK")
        require(not args.owned_source_ip or args.revoke_owned,
                "SOURCE_IP_ONLY_ALLOWED_FOR_ROLLBACK")
        client = atlas_session()
        try:
            entries = inventory(client)
            audit_entries(entries)
            if args.certify_isolation:
                certify_isolated_network(entries)
            if args.revoke_owned:
                revoke_owned(client, entries, args.task_arn,
                             args.owned_source_ip)
            elif args.task_arn:
                task_ip = public_source_ip(args.profile, args.task_arn)
                print("MW_T12_ECS_SOURCE_ADDRESS=INDEPENDENTLY_VERIFIED")
                if args.admit_six_hours:
                    admit(client, entries, task_ip, args.task_arn)
                else:
                    print("MW_T12_ATLAS_SOURCE_ADMISSION=READ_ONLY")
            else:
                print("MW_T12_ATLAS_SOURCE_ADMISSION=INVENTORY_ONLY")
            return 0
        finally:
            client.close()
    except (NetworkAdmissionError, KeyboardInterrupt) as exc:
        code = (str(exc) if isinstance(exc, NetworkAdmissionError)
                else "INTERRUPTED")
        print("MW_T12_ATLAS_ACCESS_ADMISSION=FAIL_CLOSED")
        print("MW_T12_ERROR=" + code)
        print("MW_T12_ATLAS_ROLLBACK_CERTIFIED=FALSE")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/mw_t12_atlas_access_admission.py
# VERSION: v1.4.0-SAFE-ADMIN-API-DENIAL-CODES
# AUTHORITY BOUNDARY: Exact temporary /32 source add/owned delete only.
# TENANT POSTURE: Synthetic test database only; no production read/write.
# FAIL-CLOSED POSTURE: Wildcard add blocked; delete restricted to owned task.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
