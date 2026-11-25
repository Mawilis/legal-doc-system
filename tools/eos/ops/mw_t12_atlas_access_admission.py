"""TITLE: MW-T12 synthetic Atlas temporary source-IP admission.
VERSION: v1.0.0-EXACT-ECS-SOURCE-IP-AND-TEMPORARY-ATLAS-ADMISSION
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Inventory the shared free Atlas test project's network exposure and
         optionally admit exactly one verified ECS task public source IP for
         six hours; never broaden, delete, or change existing Atlas entries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_atlas_access_admission.py
COLLABORATION / OWNERSHIP: Read-only AWS ECS/EC2 identity via existing MW-T12
         task admission; Atlas Admin API v2 project-scoped network capability.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-EXACT-ECS-SOURCE-IP-AND-TEMPORARY-ATLAS-ADMISSION
           provides bounded Atlas entry inventory, public ENI attestation,
           explicit six-hour source-IP mutation gate, and post-write readback.
           Rejects existing global access; never deletes shared entries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: API keys from hidden prompt, no URI or key logs;
                           no public EOS ingress, NAT, database or IAM writes.
TENANT BOUNDARY: Existing synthetic-only test project; never production.
AUTHORITY BOUNDARY: Atlas IP allowance alone is not authenticated EOS or
                    rollback certification; no automatic compute launch.
FINANCIAL AUTHORITY BOUNDARY: No AWS billing action; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from getpass import getpass
import ipaddress
import re

from tools.eos.ops import mw_t12_task_definition_admission as ecs

VERSION = "v1.0.0-EXACT-ECS-SOURCE-IP-AND-TEMPORARY-ATLAS-ADMISSION"
PROJECT = "668cdbbd975c3c0f05fca20c"
ACCOUNT = "121014832643"
REGION = "af-south-1"
CLUSTER = "wilsy-mwt12-nonproduction"
FAMILY = "wilsy-mwt12-eos-nonproduction"
SG = "sg-05bbf379de9a0eee8"
PUBLIC_IP_TTL_HOURS = 6
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
    require(method in {"GET", "POST"}, "ATLAS_METHOD_NOT_ADMITTED")
    require(route == "/accessList", "ATLAS_ROUTE_NOT_ADMITTED")
    try:
        response = client.request(
            method, ATLAS_API + route, json=payload, params=params, timeout=20,
        )
        require(response.status_code in ({200} if method == "GET"
                                         else {200, 201, 202}),
                "ATLAS_API_REQUEST_DENIED")
        require(len(response.content) <= 1048576, "ATLAS_RESPONSE_OVERSIZED")
        data = response.json()
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
    print("MW_T12_ATLAS_ACCESS_ENTRIES=" + str(len(entries)))
    print("MW_T12_ATLAS_UNRESTRICTED_ENTRIES=" + str(global_count))
    print("MW_T12_ATLAS_ENTRIES_WITHOUT_OWNER_COMMENT=" + str(owner_unknown))
    print("MW_T12_ATLAS_CONSUMER_DEPENDENCIES=UNVERIFIED")
    print("MW_T12_ATLAS_ACCESS_LIST_MUTATED=FALSE")


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
            and task.get("desiredStatus") == "RUNNING"
            and task.get("taskDefinitionArn") in {
                "arn:aws:ecs:" + REGION + ":" + ACCOUNT +
                ":task-definition/" + FAMILY + ":1",
                "arn:aws:ecs:" + REGION + ":" + ACCOUNT +
                ":task-definition/" + FAMILY + ":2",
            }, "TASK_IDENTITY_OR_STATE_UNVERIFIED")
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
    except ValueError as exc:
        raise NetworkAdmissionError("TASK_PUBLIC_ADDRESS_MISSING") from exc
    require(ip.version == 4 and ip.is_global,
            "TASK_PUBLIC_ADDRESS_NOT_GLOBAL")
    return str(ip)


def admit(client, entries: list[dict], task_ip: str) -> None:
    """Add six-hour, exactly-scoped source /32 with independent API readback.

    Existing broad project entries or pre-existing same-IP entries deny; never
    infer an added /32 mitigates a wildcard. No deletion or renewal included.
    """
    networks = [entry_ip(row) for row in entries]
    require("0.0.0.0/0" not in networks,
            "SHARED_ATLAS_GLOBAL_ACCESS_MUST_BE_REMEDIATED_FIRST")
    cidr = task_ip + "/32"
    require(cidr not in networks, "TASK_IP_ALREADY_ADMITTED_OR_UNOWNED")
    expires = datetime.now(timezone.utc) + timedelta(
        hours=PUBLIC_IP_TTL_HOURS,
    )
    payload = [{
        "ipAddress": task_ip,
        "comment": "MW-T12 ECS temporary synthetic recovery source only",
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


def main(argv: list[str] | None = None) -> int:
    """Inventory by default; opt-in changes only exact project network scope."""
    parser = argparse.ArgumentParser(
        description="MW-T12 isolated Atlas source-network admission")
    parser.add_argument("--profile", default="wilsy-legal-cert")
    parser.add_argument("--task-arn", help="Exact running owned Fargate task ARN")
    parser.add_argument("--admit-six-hours", action="store_true",
                        help="Explicit Atlas temporary /32 mutation, no compute")
    args = parser.parse_args(argv)
    try:
        require(not args.admit_six_hours or bool(args.task_arn),
                "TASK_ARN_REQUIRED_FOR_MUTATION")
        client = atlas_session()
        try:
            entries = inventory(client)
            audit_entries(entries)
            if args.task_arn:
                task_ip = public_source_ip(args.profile, args.task_arn)
                print("MW_T12_ECS_SOURCE_ADDRESS=INDEPENDENTLY_VERIFIED")
                if args.admit_six_hours:
                    admit(client, entries, task_ip)
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
# VERSION: v1.0.0-EXACT-ECS-SOURCE-IP-AND-TEMPORARY-ATLAS-ADMISSION
# AUTHORITY BOUNDARY: Only exact Atlas project temporary /32 source mutation.
# TENANT POSTURE: Synthetic test database only; no production read/write.
# FAIL-CLOSED POSTURE: Wildcard or missing task identity denies all mutations.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
