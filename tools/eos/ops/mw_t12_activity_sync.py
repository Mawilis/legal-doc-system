"""TITLE: MW-T12 source-owned EOS project activity synchronization.
VERSION: v1.1.0-BROWSER-SESSION-ACTIVITY-FALLBACK
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Append one verified milestone to the existing Foundation MW-T12 task.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_activity_sync.py
COLLABORATION / OWNERSHIP: Canonical projects_router.py task-comment POST/GET;
    ProjectCommentRegistry owns tenant transaction and immutable event replay.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.1.0-BROWSER-SESSION-ACTIVITY-FALLBACK supplies a safe,
    token-free browser publication path for an existing authorized EOS
    session, and distinguishes absent from unsupported bearer input.
    Does not read browser storage or bypass current IAM authority.
CHANGELOG: v1.0.0-AUTHORIZED-HTTP-IDEMPOTENT-READBACK performs bounded
    authorized project/task discovery and deduplicated write/readback.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Browser-mode milestone text requires no token;
    optional API-mode hidden bearer prompt; localhost-only EOS HTTP;
    never log credentials, response bodies, opaque principal or source rows.
TENANT BOUNDARY: Canonical Founder tenant; server rechecks current IAM.
AUTHORITY BOUNDARY: Existing task comment only; no fabricated completion.
FINANCIAL AUTHORITY BOUNDARY: No finance, cloud or payment writes.
"""
from __future__ import annotations

import argparse
from getpass import getpass
from hashlib import sha3_512
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VERSION = "v1.1.0-BROWSER-SESSION-ACTIVITY-FALLBACK"
BASE = "http://127.0.0.1:9095/api/projects"
TENANT = "WILSYTENANT-4CD2FZ4O"
FOUNDATION = "WILSY OS — Unified Operating Platform Foundation"
MILESTONE = (
    "MW-T12 — Durable Atlas recovery admission | 25 November 2026\n"
    "Commit df95ef588e13359e7554455b1120182f14d181d1.\n"
    "Mac exact-head syntax PASS, sovereign governance 8/8 PASS.\n"
    "Scoped synthetic Atlas credential: verified readWrite-only on test DB; "
    "identical durable recovery canary verified in three new TLS sessions.\n"
    "ECS task definitions :1 and :2 registered. Running Fargate: zero.\n"
    "Pending: rotated ECS secret delivery; restricted Atlas 27017 path and "
    "allowlist; private authenticated EOS HTTP readback; live rollback.\n"
    "Task IN_PROGRESS, PR #419 DRAFT, production BLOCKED."
)
KEY = "mwt12-durable-atlas-" + sha3_512(MILESTONE.encode()).hexdigest()[:32]
PROJECT_ID = re.compile(r"prj-[a-f0-9]{48}\Z")
TASK_ID = re.compile(r"ptk-[a-f0-9]{48}\Z")


class ActivityError(RuntimeError):
    """Fail-closed non-disclosing source milestone error."""


def require(condition: bool, code: str) -> None:
    """Deny malformed or unverified source identity."""
    if not condition:
        raise ActivityError(code)


def api(token: str, route: str, payload: dict | None = None) -> dict:
    """Use existing authenticated localhost EOS route, never direct MongoDB."""
    require(route.startswith("/") and not route.startswith("//")
            and ".." not in route and len(route) <= 600, "ACTIVITY_ROUTE_INVALID")
    headers = {"Authorization": "Bearer " + token, "X-Tenant-ID": TENANT,
               "Accept": "application/json", "Cache-Control": "no-store"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        headers.update({"Content-Type": "application/json",
                        "Idempotency-Key": KEY})
    try:
        with urlopen(Request(BASE + route, headers=headers, data=data,
                             method="POST" if data else "GET"), timeout=12) as res:
            require(res.status == (201 if data else 200),
                    "ACTIVITY_HTTP_STATUS_UNVERIFIED")
            raw = res.read(500001)
    except (HTTPError, URLError, OSError, TimeoutError):
        raise ActivityError("ACTIVITY_EOS_DENIED_OR_UNAVAILABLE") from None
    require(len(raw) <= 500000, "ACTIVITY_RESPONSE_OVERSIZED")
    try:
        result = json.loads(raw)
    except (UnicodeError, ValueError):
        raise ActivityError("ACTIVITY_RESPONSE_INVALID") from None
    require(isinstance(result, dict), "ACTIVITY_RESPONSE_INVALID")
    return result


def pages(token: str, route: str, page_size: int) -> list[dict]:
    """Bound discovery; never infer success from truncated lists."""
    found: list[dict] = []
    while len(found) < 1000:
        result = api(token, route + "?" + urlencode(
            {"limit": page_size, "offset": len(found)}))
        chunk = result.get("items")
        require(isinstance(chunk, list)
                and all(isinstance(x, dict) for x in chunk),
                "ACTIVITY_PAGE_INVALID")
        found.extend(chunk)
        if result.get("has_more") is False:
            return found
        require(result.get("has_more") is True and bool(chunk),
                "ACTIVITY_PAGINATION_INVALID")
    raise ActivityError("ACTIVITY_PAGINATION_LIMIT")


def sync(token: str) -> str:
    """Create one exact existing MW-T12 comment, or verify prior persisted one."""
    projects = pages(token, "", 100)
    matches = [p for p in projects if p.get("name") == FOUNDATION]
    require(len(matches) == 1, "FOUNDATION_IDENTITY_AMBIGUOUS")
    project = matches[0].get("project_id")
    require(isinstance(project, str) and PROJECT_ID.fullmatch(project) is not None,
            "FOUNDATION_ID_INVALID")
    tasks = pages(token, "/" + project + "/tasks", 100)
    chosen = [t for t in tasks if isinstance(t.get("title"), str)
              and t["title"].startswith("MW-T12")
              and "rollback" in t["title"].lower()]
    require(len(chosen) == 1, "MW_T12_TASK_IDENTITY_AMBIGUOUS")
    task = chosen[0].get("task_id")
    require(isinstance(task, str) and TASK_ID.fullmatch(task) is not None,
            "MW_T12_TASK_ID_INVALID")
    path = "/" + project + "/tasks/" + task + "/comments"

    def existing() -> dict | None:
        """Independently retrieve exact comment without accepting duplicates."""
        rows = pages(token, path, 100)
        hits = [row for row in rows if row.get("body") == MILESTONE]
        require(len(hits) <= 1, "ACTIVITY_DUPLICATE_RECORDS")
        return hits[0] if hits else None

    old = existing()
    if old:
        require(isinstance(old.get("comment_id"), str),
                "ACTIVITY_OLD_RECORD_INVALID")
        return "EXISTING_ACTIVITY_VERIFIED"
    created = api(token, path, {"body": MILESTONE, "mentions": []})
    record = created.get("comment", {})
    require(isinstance(record, dict) and record.get("body") == MILESTONE
            and record.get("project_id") == project
            and record.get("task_id") == task
            and isinstance(record.get("comment_id"), str),
            "ACTIVITY_POST_READBACK_INVALID")
    persisted = existing()
    require(persisted is not None
            and persisted.get("comment_id") == record["comment_id"],
            "ACTIVITY_INDEPENDENT_READBACK_FAILED")
    return "SAVED_AND_INDEPENDENTLY_VERIFIED"


def main(argv: list[str] | None = None) -> int:
    """Require explicit authorized EOS write; never change task status."""
    parser = argparse.ArgumentParser(description="MW-T12 source activity sync")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true",
                      help="Use an existing EOS bearer token at a hidden prompt")
    mode.add_argument("--browser", action="store_true",
                      help="Display milestone for the already-authenticated browser")
    args = parser.parse_args(argv)
    if args.browser:
        print("MW_T12_ACTIVITY=READY_FOR_EXISTING_BROWSER_SESSION")
        print("MW_T12_ACTIVITY_WRITE_EXECUTED=FALSE")
        print("MW_T12_TARGET=FOUNDATION_PROJECT_EXISTING_MW_T12_ACTIVITY")
        print("MW_T12_MILESTONE_BEGIN")
        print(MILESTONE)
        print("MW_T12_MILESTONE_END")
        print("MW_T12_NEXT=PASTE_SAVE_AND_REOPEN_IN_WILSY_OS")
        return 0
    token = getpass("EOS access token, not password or MFA code (hidden; Enter for browser instructions): ").strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        print("MW_T12_ACTIVITY=NO_BEARER_TOKEN_SUPPLIED")
        print("MW_T12_ACTIVITY_WRITE_EXECUTED=FALSE")
        print("MW_T12_NEXT=RUN_WITH_BROWSER_TO_USE_SIGNED_IN_WILSY_OS")
        return 2
    if re.fullmatch(r"[A-Za-z0-9._~+/=-]{20,8192}", token) is None:
        print("MW_T12_ACTIVITY=UNSUPPORTED_BEARER_INPUT")
        print("MW_T12_ACTIVITY_WRITE_EXECUTED=FALSE")
        print("MW_T12_NEXT=RUN_WITH_BROWSER_TO_USE_SIGNED_IN_WILSY_OS")
        return 2
    try:
        print("MW_T12_ACTIVITY=" + sync(token))
        print("MW_T12_TASK_STATE=UNCHANGED")
        print("MW_T12_PRODUCTION_AUTHORIZED=FALSE")
        return 0
    except ActivityError as error:
        print("MW_T12_ACTIVITY=FAIL_CLOSED")
        print("MW_T12_ERROR=" + str(error))
        return 2


if __name__ == "__main__":
    sys.exit(main())

# ARTIFACT: tools/eos/ops/mw_t12_activity_sync.py
# VERSION: v1.1.0-BROWSER-SESSION-ACTIVITY-FALLBACK
# AUTHORITY BOUNDARY: Existing audited task comment only.
# TENANT POSTURE: Explicit canonical WILSY scope; EOS owns authentication.
# FAIL-CLOSED POSTURE: Ambiguous source identities or readback deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
