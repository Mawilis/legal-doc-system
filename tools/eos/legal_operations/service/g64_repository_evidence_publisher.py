"""Publish immutable G64 evidence manifests to a dedicated Git branch.

TITLE: G64 Repository Evidence Publisher
VERSION: v1.0.0-G64-DEDICATED-BRANCH-PUBLISHER
AUTHORITY: Evidence export persistence only; never merges, deploys, or ratifies.
FAIL-CLOSED: Requires an explicit token, repository, base branch and dedicated export branch.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from typing import Any, Final
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

VERSION: Final[str] = "v1.0.0-G64-DEDICATED-BRANCH-PUBLISHER"
_ID: Final[re.Pattern[str]] = re.compile(r"g64-[0-9a-f]{40}\Z")
_API: Final[str] = "https://api.github.com"


class G64RepositoryPublishError(RuntimeError):
    """Bounded repository publication failure with a content-free code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _configuration() -> tuple[str, str, str, str]:
    token = os.environ.get("G64_REPOSITORY_EXPORT_TOKEN", "").strip()
    repository = os.environ.get("G64_REPOSITORY_EXPORT_REPOSITORY", "").strip()
    base_branch = os.environ.get("G64_REPOSITORY_EXPORT_BASE_BRANCH", "").strip()
    export_branch = os.environ.get("G64_REPOSITORY_EXPORT_BRANCH", "").strip()
    if not token or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise G64RepositoryPublishError("G64_REPOSITORY_PUBLISHER_NOT_CONFIGURED")
    if (
        not re.fullmatch(r"[A-Za-z0-9._/-]{1,100}", base_branch)
        or ".." in base_branch
        or "//" in base_branch
        or base_branch.endswith("/")
        or not re.fullmatch(r"g64-evidence/[A-Za-z0-9._/-]{1,100}", export_branch)
        or ".." in export_branch
        or "//" in export_branch
        or export_branch.endswith("/")
        or export_branch == base_branch
        or any(value.strip() != value or not value for value in (base_branch, export_branch))
    ):
        raise G64RepositoryPublishError("G64_REPOSITORY_BRANCH_POLICY_INVALID")
    return token, repository, base_branch, export_branch


def _request(
    *, method: str, url: str, token: str, body: dict[str, Any] | None = None
) -> tuple[int, dict[str, Any] | None]:
    data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "WILSY-G64-Evidence-Publisher",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read()
            if not raw:
                return response.status, None
            try:
                return response.status, json.loads(raw)
            except ValueError as error:
                raise G64RepositoryPublishError(
                    "G64_REPOSITORY_API_RESPONSE_INVALID"
                ) from error
    except HTTPError as error:
        try:
            raw = error.read()
            parsed = json.loads(raw) if raw else None
        except (OSError, ValueError):
            parsed = None
        return error.code, parsed
    except (OSError, URLError, TimeoutError) as error:
        raise G64RepositoryPublishError("G64_REPOSITORY_PUBLISHER_UNAVAILABLE") from error


def publish_repository_evidence(
    *, record_id: str, manifest_bytes: bytes, artifact_id: str | None = None
) -> dict[str, str]:
    """Create one immutable JSON artifact on a dedicated branch, never the base branch."""
    if not isinstance(record_id, str) or _ID.fullmatch(record_id) is None:
        raise G64RepositoryPublishError("G64_REPOSITORY_RECORD_ID_INVALID")
    if artifact_id is not None and (
        not isinstance(artifact_id, str) or _ARTIFACT_ID.fullmatch(artifact_id) is None
    ):
        raise G64RepositoryPublishError("G64_REPOSITORY_ARTIFACT_ID_INVALID")
    if not isinstance(manifest_bytes, bytes) or not manifest_bytes:
        raise G64RepositoryPublishError("G64_REPOSITORY_MANIFEST_INVALID")
    try:
        manifest = json.loads(manifest_bytes)
    except (ValueError, UnicodeDecodeError) as error:
        raise G64RepositoryPublishError("G64_REPOSITORY_MANIFEST_INVALID") from error
    if (
        not isinstance(manifest, dict)
        or manifest.get("record_id") != record_id
        or manifest.get("ratification_complete") is not False
        or manifest.get("permits_operational_access") is not False
        or manifest.get("constitutes_ratification") is not False
        or manifest.get("institution_binding_status")
        != "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION"
        or manifest.get("ratifier_authority_status")
        != "UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION"
    ):
        raise G64RepositoryPublishError("G64_REPOSITORY_MANIFEST_AUTHORITY_INVALID")
    claimed_digest = manifest.get("manifest_sha3_512")
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha3_512"}
    canonical = json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")
    if (
        not isinstance(claimed_digest, str)
        or claimed_digest != hashlib.sha3_512(canonical).hexdigest()
    ):
        raise G64RepositoryPublishError("G64_REPOSITORY_MANIFEST_FINGERPRINT_INVALID")

    token, repository, base_branch, export_branch = _configuration()
    encoded_repo = quote(repository, safe="/")
    base_url = f"{_API}/repos/{encoded_repo}"
    ref_path = f"/git/ref/heads/{quote(export_branch, safe='/')}"
    status_code, ref = _request(
        method="GET", url=base_url + ref_path, token=token
    )
    if status_code == 404:
        base_status, base_ref = _request(
            method="GET",
            url=base_url + f"/git/ref/heads/{quote(base_branch, safe='/')}",
            token=token,
        )
        if base_status != 200 or not isinstance(base_ref, dict):
            raise G64RepositoryPublishError("G64_REPOSITORY_BASE_BRANCH_UNAVAILABLE")
        base_object = base_ref.get("object")
        base_sha = base_object.get("sha") if isinstance(base_object, dict) else None
        if not isinstance(base_sha, str) or not base_sha:
            raise G64RepositoryPublishError("G64_REPOSITORY_BASE_REF_INVALID")
        create_status, created = _request(
            method="POST",
            url=base_url + "/git/refs",
            token=token,
            body={"ref": f"refs/heads/{export_branch}", "sha": base_sha},
        )
        if create_status not in (201, 422):
            raise G64RepositoryPublishError("G64_REPOSITORY_EXPORT_BRANCH_CREATE_FAILED")
        status_code, ref = _request(
            method="GET", url=base_url + ref_path, token=token
        )
    if status_code != 200 or not isinstance(ref, dict):
        raise G64RepositoryPublishError("G64_REPOSITORY_EXPORT_BRANCH_UNAVAILABLE")

    path = (
        f"encryption-evidence/g64-ratification-workspaces/{record_id}/{artifact_id}.json"
        if artifact_id is not None
        else f"encryption-evidence/g64-ratification-workspaces/{record_id}.json"
    )
    contents_url = f"{base_url}/contents/{quote(path, safe='/')}"
    branch_query = f"?ref={quote(export_branch, safe='')}"
    file_status, existing = _request(
        method="GET", url=contents_url + branch_query, token=token
    )
    content_b64 = base64.b64encode(manifest_bytes).decode("ascii")
    if file_status == 200 and isinstance(existing, dict):
        try:
            existing_bytes = base64.b64decode(existing.get("content", ""), validate=False)
        except (ValueError, TypeError):
            raise G64RepositoryPublishError("G64_REPOSITORY_EXISTING_ARTIFACT_INVALID")
        if existing_bytes == manifest_bytes:
            return {
                "status": "ALREADY_PUBLISHED",
                "repository": repository,
                "branch": export_branch,
                "path": path,
                "blob_sha": str(existing.get("sha", "")),
            }
        raise G64RepositoryPublishError("G64_REPOSITORY_IMMUTABLE_ARTIFACT_CONFLICT")
    if file_status != 404:
        raise G64RepositoryPublishError("G64_REPOSITORY_ARTIFACT_LOOKUP_FAILED")

    put_status, result = _request(
        method="PUT",
        url=contents_url,
        token=token,
        body={
            "message": f"Persist non-authorizing G64 evidence {record_id}",
            "content": content_b64,
            "branch": export_branch,
        },
    )
    if put_status not in (200, 201) or not isinstance(result, dict):
        raise G64RepositoryPublishError("G64_REPOSITORY_ARTIFACT_PUBLISH_FAILED")
    commit = result.get("commit", {})
    return {
        "status": "PUBLISHED",
        "repository": repository,
        "branch": export_branch,
        "path": path,
        "commit_sha": str(commit.get("sha", "")),
    }
