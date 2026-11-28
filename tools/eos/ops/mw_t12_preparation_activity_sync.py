"""TITLE: MW-T12 authenticated preparation milestone EOS activity synchronization.
VERSION: v1.0.0-SOURCE-OWNED-IDEMPOTENT-READBACK
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Append the bounded, separately certified no-cost MW-T12 preparation
         checkpoint once to the original Foundation Projects task and prove
         the exact comment persisted in EOS without changing task lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_preparation_activity_sync.py
COLLABORATION / OWNERSHIP: Existing canonical Projects owner comments route;
         mw_t12_foundation_readback strict local auth, page and tenant guards;
         MW-T12 shared-Atlas consumer attribution register and PR #419.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.0.0-SOURCE-OWNED-IDEMPOTENT-READBACK supports explicit --check
           and --run; exact project/task/status admission, stable idempotency,
           duplicate prevention, receipt verification and independent GET.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Existing EOS bearer via hidden prompt only; no
                           URI, token, principal, comment text or IDs printed.
TENANT BOUNDARY: Only canonical Founder tenant and original Foundation task.
AUTHORITY BOUNDARY: Cannot transition MW-T12, create task/project, authorize
                    Fargate, change Atlas ACL or certify live rollback.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no paid action.
"""
from __future__ import annotations

import argparse
from getpass import getpass
from hashlib import sha3_512
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from tools.eos.ops import mw_t12_foundation_readback as source

VERSION = "v1.0.0-SOURCE-OWNED-IDEMPOTENT-READBACK"
MARKER = "MW-T12 — No-cost engineering preparation closure | 25 November 2026"
BODY = """MW-T12 — No-cost engineering preparation closure | 25 November 2026

Completed at previously verified scope:
• 23/23 exact-head GitHub workflows passed at 6922f9a5d849677302caaf64f598138762e02308.
• Synthetic historical/current immutable-image-backed secure ECS task definitions :3/:4 registered without starting compute.
• Reviewed CloudFormation change-set executed; all three Atlas TCP/27017 egress rules independently verified, with no public ingress or ECS compute.
• Running Python EOS at local port 9095 independently observed connected to all three freshly resolved Wilsy / legalDocSystem Atlas nodes, NOT the separate legal-doc-test recovery cluster.
• Authenticated Strategy M04 client handoff: 49/49 focused tests and production client build passed at b54c2a0c4ed7b5f0579d7df4ac71c2edf750d794.

Outstanding and explicitly NOT certified:
• Shared legal-doc-test 0.0.0.0/0 network entry remains; active/legacy consumer ownership and restricted cutover are incomplete.
• No paid Fargate task launched; no bounded current→historical→current live image rollback or persistent synthetic canary recovery.
• No authenticated EOS runtime database identity/database binding or production release authorization established.

Decision: Close only the zero-cost preparation tranche and resume M04 governed Strategy delivery in parallel. Keep the original MW-T12 task IN_PROGRESS and PR #419 draft. No change of source IAM, tenant, task status or financial authority. GitHub PR comments do not replace this EOS task activity."""
KEY = "mw-t12-preparation-closure-v1-" + sha3_512(BODY.encode("utf-8")).hexdigest()[:32]


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise source.SourceReadbackDenied(reason)


def _locate(client, base: str, token: str) -> tuple[str, str, str]:
    """Find exactly the existing Foundation and MW-T12, not a new project."""
    projects = source._list_all(client, base, token, "/api/projects",
                                "WILSY-PROJECT-LIST/V1", 100)
    project = source._identify_exact(
        projects, "name", source.PROJECT_NAME, "FOUNDATION_PROJECT_NOT_UNIQUE_OR_MISSING")
    project_id = project.get("project_id")
    require(isinstance(project_id, str) and source.PROJECT_ID.fullmatch(project_id)
            and project.get("tenant_id") == source.CANONICAL_TENANT_ID,
            "FOUNDATION_PROJECT_BINDING_INVALID")
    tasks = source._list_all(
        client, base, token, "/api/projects/" + project_id + "/tasks",
        "WILSY-PROJECT-TASK-LIST/V1", 100)
    task = source._identify_exact(
        tasks, "title", source.TASK_NAME, "MW_T12_TASK_NOT_UNIQUE_OR_MISSING")
    task_id = task.get("task_id")
    require(isinstance(task_id, str) and source.TASK_ID.fullmatch(task_id)
            and task.get("tenant_id") == source.CANONICAL_TENANT_ID
            and task.get("project_id") == project_id
            and task.get("status") == "IN_PROGRESS"
            and type(task.get("revision")) is int and task["revision"] >= 1,
            "MW_T12_TASK_STATUS_OR_BINDING_INVALID")
    return project_id, task_id, str(task["revision"])


def _matching_comment(client, base: str, token: str, project: str,
                      task: str) -> dict | None:
    route = "/api/projects/" + project + "/tasks/" + task + "/comments"
    comments = source._list_all(
        client, base, token, route, "WILSY-PROJECT-COMMENT-LIST/V1", 100)
    matches = [item for item in comments
               if isinstance(item.get("body"), str)
               and MARKER in item["body"]]
    require(len(matches) <= 1, "MW_T12_PREPARATION_COMMENT_DUPLICATE")
    if not matches:
        return None
    comment = matches[0]
    require(comment.get("body") == BODY
            and comment.get("tenant_id") == source.CANONICAL_TENANT_ID
            and comment.get("project_id") == project
            and comment.get("task_id") == task
            and isinstance(comment.get("comment_id"), str)
            and bool(comment["comment_id"])
            and isinstance(comment.get("fingerprint"), str)
            and source.HEX_DIGEST.fullmatch(comment["fingerprint"]),
            "MW_T12_PREPARATION_COMMENT_SOURCE_MISMATCH")
    return comment


def _post_once(client, base: str, token: str, project: str,
               task: str) -> dict:
    """One authenticated write; never automatic replay after transport error."""
    path = "/api/projects/" + project + "/tasks/" + task + "/comments"
    request = Request(
        base + path, method="POST",
        data=json.dumps({"body": BODY, "mentions": []}).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token,
            "X-Tenant-ID": source.CANONICAL_TENANT_ID,
            "Idempotency-Key": KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cache-Control": "no-store",
        },
    )
    try:
        with client.open(request, timeout=18) as response:
            require(response.status == 201, "MW_T12_COMMENT_POST_NOT_ACCEPTED")
            raw = response.read(65537)
            require(len(raw) <= 65536, "MW_T12_COMMENT_RECEIPT_OVERSIZED")
    except HTTPError as exc:
        code = (
            "EXISTING_EOS_SESSION_AUTHENTICATION_REQUIRED" if exc.code == 401
            else "EXISTING_PROJECTS_UPDATE_PERMISSION_DENIED" if exc.code == 403
            else "MW_T12_COMMENT_SOURCE_CHANGED" if exc.code == 409
            else "EOS_SOURCE_UNAVAILABLE" if exc.code == 503
            else "MW_T12_COMMENT_WRITE_REJECTED"
        )
        raise source.SourceReadbackDenied(code) from None
    except (URLError, TimeoutError):
        raise source.SourceReadbackDenied("MW_T12_COMMENT_WRITE_RESULT_UNKNOWN") from None
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeError):
        raise source.SourceReadbackDenied("MW_T12_COMMENT_RECEIPT_INVALID") from None
    require(isinstance(payload, dict)
            and payload.get("schema") == "WILSY-PROJECT-COMMENT-RESULT/V1"
            and payload.get("tenant_id") == source.CANONICAL_TENANT_ID
            and payload.get("project_id") == project
            and payload.get("task_id") == task
            and isinstance(payload.get("comment"), dict)
            and payload["comment"].get("body") == BODY,
            "MW_T12_COMMENT_RECEIPT_MISMATCH")
    return payload["comment"]


def verify(base: str, token: str, write: bool) -> str:
    """Require existing session/capacity, independent before/after source GETs."""
    client = build_opener(source._NoRedirect)
    source._verify_identity(client, base, token)
    source._verify_workspace_scope(client, base, token)
    project, task, revision = _locate(client, base, token)
    existing = _matching_comment(client, base, token, project, task)
    if existing is None:
        require(write, "MW_T12_PREPARATION_ACTIVITY_NOT_POSTED")
        receipt = _post_once(client, base, token, project, task)
    else:
        receipt = existing
    after = _matching_comment(client, base, token, project, task)
    require(after is not None and after == receipt,
            "MW_T12_PREPARATION_INDEPENDENT_READBACK_MISMATCH")
    # Re-read task after the comment: lifecycle must still be IN_PROGRESS.
    project_now, task_now, revision_now = _locate(client, base, token)
    require((project_now, task_now, revision_now) ==
            (project, task, revision), "MW_T12_TASK_LIFECYCLE_CHANGED")
    return "EXISTING_VERIFIED" if existing is not None else "WRITTEN_AND_VERIFIED"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Append and independently verify original MW-T12 activity")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--base-url", default="http://127.0.0.1:5173")
    args = parser.parse_args(argv)
    try:
        base = source._verify_base(args.base_url)
        if args.check:
            print("MW_T12_PREPARATION_CHECKPOINT=READY")
            print("MW_T12_PREPARATION_COMMENT_POSTED=FALSE")
            return 0
        token = getpass("Existing authenticated EOS access token (hidden): ").strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
        require(bool(token) and len(token) <= 8192
                and not any(c.isspace() for c in token),
                "AUTHENTICATED_SESSION_TOKEN_REQUIRED")
        state = verify(base, token, write=True)
        print("MW_T12_PREPARATION_ACTIVITY=" + state)
        print("MW_T12_PREPARATION_INDEPENDENT_READBACK=VERIFIED")
        print("MW_T12_TASK_STATUS=IN_PROGRESS")
        print("MW_T12_INFRASTRUCTURE_ROLLBACK_CERTIFIED=FALSE")
        print("MW_T12_PRODUCTION_RELEASE_AUTHORIZED=FALSE")
        return 0
    except (source.SourceReadbackDenied, KeyboardInterrupt) as exc:
        code = exc.code if isinstance(exc, source.SourceReadbackDenied) \
            else "OPERATOR_INTERRUPTED"
        print("MW_T12_PREPARATION_ACTIVITY=NOT_VERIFIED")
        print("MW_T12_FAILURE=" + code)
        return 2


if __name__ == "__main__":
    sys.exit(main())

# ARTIFACT: tools/eos/ops/mw_t12_preparation_activity_sync.py
# VERSION: v1.0.0-SOURCE-OWNED-IDEMPOTENT-READBACK
# AUTHORITY BOUNDARY: One existing task comment only, verified via EOS.
# TENANT POSTURE: Exact canonical Founder project, scope and task required.
# FAIL-CLOSED POSTURE: Unknown/partial write never reported as success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
