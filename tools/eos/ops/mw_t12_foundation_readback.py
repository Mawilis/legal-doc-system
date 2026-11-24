""" 
TITLE: MW-T12 live Foundation project independent source readback.
VERSION: v1.3.0-CANONICAL-SESSION-TENANT-BINDING
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Verify, never mutate, an existing tenant-authorized Foundation
         project task and its previously posted engineering activity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/mw_t12_foundation_readback.py
COLLABORATION / OWNERSHIP: Existing Python EOS Projects router and read-only
                           Projects task, comment and event registries.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.3.0-CANONICAL-SESSION-TENANT-BINDING uses the verified
           persisted Founder tenant ID, not the public wilsy alias,
           for Projects and asserts bootstrap tenant and Owner capacity.
CHANGELOG: v1.3.0-CANONICAL-SESSION-TENANT-BINDING authenticates the
           supplied bearer on canonical GET /api/auth/verify-token before
           Projects reads; HTTP 401 is distinguished from Projects authority
           or entitlement denial without printing any identity or token.
CHANGELOG: v1.1.0-EXACT-HTTP-DENIAL-CLASSIFICATION distinguishes
           HTTP 401 (session authentication) from HTTP 403 (source IAM/
           selected capacity or entitlement), records only a bounded route
           category, and never logs response bodies or bearer values.
CHANGELOG: v1.0.0-EXACT-TASK-COMMENT-READBACK adds a fail-closed,
           independently repeated GET-only readback without any source writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Bearer token entered locally with getpass,
                           never printed or persisted. No raw response or
                           principal, comment body or database URI is logged.
TENANT BOUNDARY: Canonical wilsy persisted Founder tenant only; exact tenant assertions on every
                 page and every matched project/task/comment.
AUTHORITY BOUNDARY: Authenticated existing Owner's current Projects read IAM;
                    no credentials, membership, role or entitlement issued.
TRANSACTION BOUNDARY: Each read is a separate source-owned EOS GET transaction.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
from getpass import getpass
from hashlib import sha3_512
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

VERSION = "v1.3.0-CANONICAL-SESSION-TENANT-BINDING"
CANONICAL_TENANT_ID = "WILSYTENANT-4CD2FZ4O"
PROJECT_NAME = "WILSY OS — Unified Operating Platform Foundation"
TASK_NAME = "MW-T12 — Certify production readiness and rollback"
CHECKPOINT = "840b294865a102ede84f77e3fc83ce4dcaabec19"
PROJECT_ID = re.compile(r"prj-[0-9a-f]{48}\Z")
TASK_ID = re.compile(r"ptk-[0-9a-f]{48}\Z")
HEX_DIGEST = re.compile(r"[0-9a-f]{128}\Z")
MAX_PAGES = 60


class SourceReadbackDenied(RuntimeError):
    """Fail-closed redacted code for an authenticated source-read boundary.

    This exception never carries a bearer token, endpoint, identity, body,
    infrastructure location, or financial execution capability.
    """

    def __init__(self, code: str) -> None:
        """Retain only the stable bounded failure classification."""
        super().__init__(code)
        self.code = code


class _NoRedirect(HTTPRedirectHandler):
    """Forbid token-bearing redirects to any unverified destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Never propagate authenticated requests through HTTP redirects."""
        raise SourceReadbackDenied("UNEXPECTED_SOURCE_REDIRECT")


def _verify_base(base: str) -> str:
    """Confine the operator to the developer's local loopback EOS/Vite proxy."""
    parsed = urlsplit(base)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query or parsed.fragment
        or parsed.port not in {5173, 9095}
    ):
        raise SourceReadbackDenied("LOCAL_EOS_ENDPOINT_REQUIRED")
    return base.rstrip("/")


def _page(client, base: str, token: str, path: str) -> dict:
    """Perform one no-cache, no-redirect, tenant-scoped GET with fail-closed JSON."""
    if not path.startswith("/api/projects") or ".." in path or "//" in path:
        raise SourceReadbackDenied("UNTRUSTED_SOURCE_PATH")
    request = Request(
        base + path,
        method="GET",
        headers={
            "Authorization": "Bearer " + token,
            "X-Tenant-ID": CANONICAL_TENANT_ID,
            "Accept": "application/json",
            "Cache-Control": "no-store, no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with client.open(request, timeout=18) as response:
            if response.status != 200:
                raise SourceReadbackDenied("EOS_READ_HTTP_NON_200")
            payload = response.read(1024 * 1024 + 1)
            if len(payload) > 1024 * 1024:
                raise SourceReadbackDenied("EOS_SOURCE_PAGE_OVERSIZED")
    except HTTPError as error:
        if error.code == 401:
            raise SourceReadbackDenied("EXISTING_EOS_SESSION_AUTHENTICATION_REQUIRED") from None
        if error.code == 403:
            raise SourceReadbackDenied("EXISTING_PROJECTS_READ_PERMISSION_OR_CAPACITY_DENIED") from None
        if error.code == 404:
            raise SourceReadbackDenied("SOURCE_ROUTE_OR_RECORD_NOT_FOUND") from None
        if error.code == 503:
            raise SourceReadbackDenied("EOS_SOURCE_UNAVAILABLE") from None
        raise SourceReadbackDenied("EOS_SOURCE_HTTP_FAILURE") from None
    except (TimeoutError, URLError):
        raise SourceReadbackDenied("EOS_SOURCE_TRANSPORT_FAILURE") from None
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, ValueError):
        raise SourceReadbackDenied("EOS_SOURCE_RESPONSE_INVALID") from None
    if not isinstance(value, dict):
        raise SourceReadbackDenied("EOS_SOURCE_RESPONSE_INVALID")
    return value


def _list_all(client, base: str, token: str, route: str, schema: str,
              limit: int) -> list[dict]:
    """Verify every bounded EOS page and reject incomplete or drifting results."""
    result: list[dict] = []
    offset = 0
    principal = None
    for _ in range(MAX_PAGES):
        response = _page(client, base, token, route + "?" + urlencode({
            "limit": limit, "offset": offset,
        }))
        if response.get("schema") != schema or response.get("tenant_id") != CANONICAL_TENANT_ID:
            raise SourceReadbackDenied("SOURCE_ENVELOPE_INVALID")
        if not isinstance(response.get("principal_id"), str) or not response["principal_id"]:
            raise SourceReadbackDenied("SOURCE_PRINCIPAL_INVALID")
        if principal is None:
            principal = response["principal_id"]
        elif principal != response["principal_id"]:
            raise SourceReadbackDenied("SOURCE_PRINCIPAL_CHANGED")
        items = response.get("items")
        if (not isinstance(items, list) or len(items) > limit
                or response.get("offset") != offset
                or response.get("limit") != limit
                or type(response.get("has_more")) is not bool
                or any(not isinstance(item, dict) for item in items)):
            raise SourceReadbackDenied("SOURCE_PAGE_CONTRACT_INVALID")
        result.extend(items)
        if not response["has_more"]:
            return result
        next_offset = response.get("next_offset")
        if (type(next_offset) is not int or next_offset != offset + len(items)
                or next_offset <= offset):
            raise SourceReadbackDenied("SOURCE_PAGINATION_INVALID")
        offset = next_offset
    raise SourceReadbackDenied("SOURCE_PAGINATION_BOUND_EXCEEDED")


def _identify_exact(items: list[dict], key: str, title: str, code: str) -> dict:
    """Accept exactly one matching source record; no first-match fallback."""
    matching = [item for item in items if item.get(key) == title]
    if len(matching) != 1:
        raise SourceReadbackDenied(code)
    return matching[0]


def _snapshot(client, base: str, token: str) -> dict:
    """Independently rediscover original project/task and immutable activity."""
    projects = _list_all(
        client, base, token, "/api/projects",
        "WILSY-PROJECT-LIST/V1", 100,
    )
    project = _identify_exact(
        projects, "name", PROJECT_NAME, "FOUNDATION_PROJECT_NOT_UNIQUE_OR_MISSING",
    )
    project_id = project.get("project_id")
    if (not isinstance(project_id, str) or not PROJECT_ID.fullmatch(project_id)
            or project.get("tenant_id") != CANONICAL_TENANT_ID):
        raise SourceReadbackDenied("FOUNDATION_PROJECT_BINDING_INVALID")

    route = "/api/projects/" + project_id
    tasks = _list_all(
        client, base, token, route + "/tasks",
        "WILSY-PROJECT-TASK-LIST/V1", 100,
    )
    task = _identify_exact(tasks, "title", TASK_NAME, "MW_T12_TASK_NOT_UNIQUE_OR_MISSING")
    task_id = task.get("task_id")
    if (not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id)
            or task.get("project_id") != project_id
            or task.get("tenant_id") != CANONICAL_TENANT_ID
            or task.get("status") != "IN_PROGRESS"
            or type(task.get("revision")) is not int
            or task["revision"] < 1):
        raise SourceReadbackDenied("MW_T12_TASK_SOURCE_STATE_INVALID")

    exact = route + "/tasks/" + task_id
    comments = _list_all(
        client, base, token, exact + "/comments",
        "WILSY-PROJECT-COMMENT-LIST/V1", 100,
    )
    events = _list_all(
        client, base, token, exact + "/events",
        "WILSY-PROJECT-TASK-EVENT-LIST/V1", 100,
    )
    if not events:
        raise SourceReadbackDenied("MW_T12_AUDIT_EVENTS_UNAVAILABLE")
    matches = [
        comment for comment in comments
        if isinstance(comment.get("body"), str)
        and CHECKPOINT in comment["body"]
        and "23/23" in comment["body"]
    ]
    if len(matches) != 1:
        raise SourceReadbackDenied("MW_T12_CHECKPOINT_COMMENT_NOT_UNIQUE_OR_MISSING")
    comment = matches[0]
    if (comment.get("tenant_id") != CANONICAL_TENANT_ID
            or comment.get("project_id") != project_id
            or comment.get("task_id") != task_id
            or not isinstance(comment.get("comment_id"), str)
            or not comment["comment_id"]
            or not isinstance(comment.get("created_at"), str)
            or not comment["created_at"]
            or not isinstance(comment.get("author_principal_id"), str)
            or not comment["author_principal_id"]
            or not isinstance(comment.get("fingerprint"), str)
            or not HEX_DIGEST.fullmatch(comment["fingerprint"])):
        raise SourceReadbackDenied("MW_T12_COMMENT_SOURCE_BINDING_INVALID")
    normalized = comment["body"].upper().replace("_", " ").replace("-", " ")
    if not any(word in normalized for word in ("NOT CERTIFIED", "ROLLBACK")):
        raise SourceReadbackDenied("MW_T12_ROLLBACK_STATE_NOT_RECORDED")
    # Digest protects the cross-request comparison without exposing source text.
    semantic = {
        "schema": comment.get("schema"), "tenant_id": CANONICAL_TENANT_ID,
        "project_id": project_id, "task_id": task_id,
        "comment_id": comment["comment_id"],
        "fingerprint": comment["fingerprint"],
        "created_at": comment["created_at"],
        "task_revision": task["revision"], "task_status": task["status"],
    }
    fingerprint = sha3_512(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {"project": project_id, "task": task_id, "comment": comment["comment_id"],
            "source_revision": task["revision"], "receipt_digest": fingerprint,
            "events_count": len(events)}


def _verify_identity(client, base: str, token: str) -> None:
    """Verify bearer on canonical EOS auth, without disclosing private values."""
    request = Request(
        base + "/api/auth/verify-token", method="GET",
        headers={"Authorization": "Bearer " + token, "X-Tenant-ID": CANONICAL_TENANT_ID,
                 "Accept": "application/json", "Cache-Control": "no-store"},
    )
    try:
        with client.open(request, timeout=18) as response:
            if response.status != 200:
                raise SourceReadbackDenied("EOS_IDENTITY_VERIFY_RESPONSE_INVALID")
            body = response.read(16385)
            if len(body) > 16384:
                raise SourceReadbackDenied("EOS_IDENTITY_VERIFY_RESPONSE_INVALID")
    except HTTPError as error:
        codes = {
            401: "EOS_BEARER_REJECTED_BY_CANONICAL_AUTH",
            403: "EOS_IDENTITY_VERIFY_DENIED",
            404: "EOS_AUTH_VERIFY_ROUTE_NOT_MOUNTED",
            503: "EOS_IDENTITY_VERIFY_SOURCE_UNAVAILABLE",
        }
        raise SourceReadbackDenied(codes.get(error.code, "EOS_IDENTITY_VERIFY_HTTP_FAILURE")) from None
    except (TimeoutError, URLError):
        raise SourceReadbackDenied("EOS_IDENTITY_VERIFY_TRANSPORT_FAILURE") from None
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise SourceReadbackDenied("EOS_IDENTITY_VERIFY_RESPONSE_INVALID") from None
    if (not isinstance(payload, dict) or payload.get("success") is not True
            or payload.get("status") != "VERIFIED"
            or not isinstance(payload.get("user"), dict)
            or not isinstance(payload["user"].get("id"), str)
            or not payload["user"]["id"]):
        raise SourceReadbackDenied("EOS_IDENTITY_VERIFY_RESPONSE_INVALID")


def _verify_workspace_scope(client, base: str, token: str) -> None:
    """Verify that EOS selected the existing Founder tenant and Owner capacity."""
    request = Request(
        base + "/api/auth/workspace-bootstrap", method="GET",
        headers={"Authorization": "Bearer " + token,
                 "X-Tenant-ID": CANONICAL_TENANT_ID,
                 "Accept": "application/json", "Cache-Control": "no-store"},
    )
    try:
        with client.open(request, timeout=18) as response:
            if response.status != 200:
                raise SourceReadbackDenied("EOS_WORKSPACE_BOOTSTRAP_RESPONSE_INVALID")
            body = response.read(65537)
            if len(body) > 65536:
                raise SourceReadbackDenied("EOS_WORKSPACE_BOOTSTRAP_RESPONSE_INVALID")
    except HTTPError as error:
        codes = {
            401: "EOS_WORKSPACE_SESSION_AUTHENTICATION_REQUIRED",
            403: "EOS_WORKSPACE_BOOTSTRAP_DENIED",
            503: "EOS_WORKSPACE_BOOTSTRAP_SOURCE_UNAVAILABLE",
        }
        raise SourceReadbackDenied(codes.get(error.code, "EOS_WORKSPACE_BOOTSTRAP_HTTP_FAILURE")) from None
    except (TimeoutError, URLError):
        raise SourceReadbackDenied("EOS_WORKSPACE_BOOTSTRAP_TRANSPORT_FAILURE") from None
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise SourceReadbackDenied("EOS_WORKSPACE_BOOTSTRAP_RESPONSE_INVALID") from None
    workspace = payload.get("workspace") if isinstance(payload, dict) else None
    if (not isinstance(payload, dict) or payload.get("status") != "READY"
            or not isinstance(workspace, dict)
            or workspace.get("tenantId") != CANONICAL_TENANT_ID):
        raise SourceReadbackDenied("EOS_WORKSPACE_SELECTED_TENANT_MISMATCH")
    if workspace.get("businessRole") != "tenant_owner":
        raise SourceReadbackDenied("EOS_WORKSPACE_OWNER_CAPACITY_NOT_SELECTED")


def verify(base: str, token: str) -> dict:
    """Preflight canonical bearer identity and re-GET current source evidence."""
    opener = build_opener(_NoRedirect)
    _verify_identity(opener, base, token)
    _verify_workspace_scope(opener, base, token)
    first = _snapshot(opener, base, token)
    second = _snapshot(opener, base, token)
    if first != second:
        raise SourceReadbackDenied("MW_T12_INDEPENDENT_READBACK_DRIFT")
    return {
        "source_revision": first["source_revision"],
        "events_count": first["events_count"],
        "receipt_digest": first["receipt_digest"],
    }


def main() -> int:
    """Accept operator-only local session credential; emit redacted gate output."""
    parser = argparse.ArgumentParser(description="MW-T12 existing EOS source GET readback")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--base-url", default="http://127.0.0.1:5173")
    args = parser.parse_args()
    try:
        base = _verify_base(args.base_url)
        if args.check == args.run:
            raise SourceReadbackDenied("SELECT_EXACTLY_ONE_CHECK_OR_RUN")
        if args.check:
            print("MW_T12_GATE0_OPERATOR=READY")
            print("MW_T12_GATE0_READBACK_EXECUTED=FALSE")
            return 0
        token = getpass("Existing authenticated EOS access token (hidden): ").strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
        if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
            token = token[1:-1]
        if any(char.isspace() for char in token):
            raise SourceReadbackDenied("BEARER_TOKEN_FORMAT_INVALID")
        if not token or len(token) > 8192 or "\n" in token:
            raise SourceReadbackDenied("AUTHENTICATED_SESSION_TOKEN_REQUIRED")
        result = verify(base, token)
        print("MW_T12_GATE0_SOURCE_READBACK=VERIFIED")
        print("MW_T12_GATE0_INDEPENDENT_REOPEN=VERIFIED")
        print("MW_T12_GATE0_TASK_STATUS=IN_PROGRESS")
        print("MW_T12_GATE0_TASK_REVISION=" + str(result["source_revision"]))
        print("MW_T12_GATE0_AUDIT_EVENTS_PRESENT=TRUE")
        print("MW_T12_GATE0_COMMENT_FINGERPRINT_SHA3_512=" + result["receipt_digest"])
        print("MW_T12_INFRASTRUCTURE_ROLLBACK_CERTIFIED=FALSE")
        print("MW_T12_PRODUCTION_RELEASE_AUTHORIZED=FALSE")
        return 0
    except (SourceReadbackDenied, KeyboardInterrupt) as error:
        code = error.code if isinstance(error, SourceReadbackDenied) else "OPERATOR_INTERRUPTED"
        print("MW_T12_GATE0_SOURCE_READBACK=NOT_VERIFIED")
        print("MW_T12_GATE0_FAILURE=" + code)
        print("MW_T12_INFRASTRUCTURE_ROLLBACK_CERTIFIED=FALSE")
        print("MW_T12_PRODUCTION_RELEASE_AUTHORIZED=FALSE")
        return 2


if __name__ == "__main__":
    sys.exit(main())

# ARTIFACT: tools/eos/ops/mw_t12_foundation_readback.py
# VERSION: v1.3.0-CANONICAL-SESSION-TENANT-BINDING
# AUTHORITY BOUNDARY: Strictly GET-only existing Python EOS Projects source.
# TENANT POSTURE: Canonical wilsy Founder persisted tenant ID, exact principal.
# FAIL-CLOSED POSTURE: No unique project, task, checkpoint or independent
#                      matching EOS readback means NO certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
