"""WILSY OS repository-integrity and production-surface firewall.

TITLE: Changed Artifact Sovereign Contract Guard
VERSION: v1.2.0-CHANGED-BLOB-PYTHON-DOCSTRING-SEAL-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Validates exact Git snapshots, repository path policy, and complete
         sovereign metadata on changed production, test, and governance files.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/repository_integrity_guard.py
COLLABORATION / OWNERSHIP: Repository Integrity workflow and Python EOS governance owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
    v1.2.0-CHANGED-BLOB-PYTHON-DOCSTRING-SEAL-CERT normalizes Python
    docstring delimiters and equivalent governed date/privacy labels while
    preserving exact Git-blob, version, path, and seal checks.
    v1.1.0-CHANGED-BLOB-SOVEREIGN-SEAL-ENFORCEMENT validates complete text and
    JSON seal fields, exact changelog versions, canonical paths, and changed
    production, test, active governance, and source Git blobs.
    v1.0.0-CHANGED-GIT-BLOB-ARTIFACT-ENFORCEMENT validates changed committed
    Git blobs for complete, path-correct, version-aligned sovereign headers and seals.
COMPLIANCE: AGENTS.md v1.2.0; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Reads repository blobs and metadata only; no secrets,
    tenant records, external services, or production systems are accessed.
TENANT BOUNDARY: No tenant identity, record, or cross-tenant authority is accessed.
AUTHORITY BOUNDARY: Repository integrity evidence only; no runtime or business authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, settlement, or ledger authority.
TRANSACTION BOUNDARY: No database transaction or business persistence is performed.
FAIL-CLOSED POSTURE: Missing, divergent, or wrongly located artifact metadata fails.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import posixpath
import re
import subprocess
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
POLICY = ROOT / "tools/eos/governance/production_surface_policy.json"

BAD_CI = (
    re.compile(r'(?mi)^\s*run:\s*echo\s+["\']Security Logged["\']\s*$'),
    re.compile(r'(?mi)^\s*run:\s*echo\s+["\']Lint Logged["\']\s*$'),
)

ARTIFACT_SOURCE_SUFFIXES = frozenset(
    {
        ".cjs",
        ".js",
        ".jsx",
        ".mjs",
        ".py",
        ".sh",
        ".ts",
        ".tsx",
    }
)
ARTIFACT_DOCUMENT_SUFFIXES = frozenset(
    {
        ".md",
        ".yaml",
        ".yml",
    }
)
ARTIFACT_JSON_PATHS = frozenset(
    {
        "package.json",
        "tools/eos/governance/production_surface_policy.json",
    }
)
GENERATED_ARTIFACT_PATTERNS = (
    "package-lock.json",
    "**/package-lock.json",
    "**/*.lock",
    "**/__pycache__/**",
    "**/dist/**",
    "**/build/**",
    "**/coverage/**",
)
HISTORICAL_EVIDENCE_PATHS = frozenset(
    {
        "server/manifest.txt",
        "server/scripts/rollback-migration-production.patch",
        "docs/architecture/eos-runtime-database-consumer-inventory.md",
    }
)
HISTORICAL_EVIDENCE_PATTERNS = (
    "server/scripts/finalize-migration.js",
    "server/scripts/migrate-audit-legacy.js",
    "server/scripts/migrate-case-legacy.js",
    "server/scripts/migrate-documents-tenancy.js",
    "server/scripts/migrate-fixed.js",
    "server/scripts/migrate.js",
    "server/scripts/migration/**",
    "server/scripts/rollback-migration.js",
    "server/scripts/rollback-simple.js",
    "server/scripts/verify-migration-state-diagnostic.js",
    "server/scripts/verify-migration-state.js",
)
SOVEREIGN_VERSION = re.compile(r"v?\d+\.\d+\.\d+(?:-[A-Z0-9][A-Z0-9.-]*)?")


def _artifact_scope(path: str) -> str | None:
    """Return the changed-artifact contract for source and active governance paths.

    Tenant scope: repository paths only. Mutation: none. Authority: selects the
    structural validator and grants no runtime or business authority. Generated
    outputs and named retained historical evidence remain excluded so CI does
    not require source headers in generated or immutable evidence artifacts.
    """
    if path in HISTORICAL_EVIDENCE_PATHS or any(
        fnmatch.fnmatchcase(path, pattern)
        for pattern in HISTORICAL_EVIDENCE_PATTERNS
    ):
        return None
    if any(
        fnmatch.fnmatchcase(path, pattern)
        for pattern in GENERATED_ARTIFACT_PATTERNS
    ):
        return None

    suffix = PurePosixPath(path).suffix.lower()
    if path == "package.json" or path.endswith("/package.json"):
        return "json"
    if (
        path.startswith("tools/eos/governance/")
        and suffix == ".json"
    ):
        return "json"
    if suffix in ARTIFACT_SOURCE_SUFFIXES:
        return "text"
    if suffix not in ARTIFACT_DOCUMENT_SUFFIXES:
        return None
    if PurePosixPath(path).name == "AGENTS.md":
        return "text"
    if (
        path.startswith(".github/workflows/")
        or path.startswith("tools/eos/governance/")
        or path.startswith("docs/architecture/")
        or path in {"DEPLOYMENT.md", "GOVERNANCE.md"}
    ):
        return "text"
    return None


def _metadata_lines(content: str) -> list[str]:
    """Normalize comment and banner decoration while retaining metadata text."""
    normalized: list[str] = []
    for line in content.splitlines():
        value = line.strip()
        if value.startswith('"""') or value.startswith("'''"):
            value = value[3:].lstrip()
        value = re.sub(r"^\*\*(.+?):\*\*", r"\1:", value)
        value = re.sub(r"^(?:/\*+|\*/|//+|#+|\*+|<!--|-->)\s*", "", value)
        value = value.replace("║", " ").replace("╔", " ").replace("╗", " ")
        value = value.replace("╚", " ").replace("╝", " ").strip(" \t*│")
        normalized.append(value)
    return normalized


def validate_artifact_contract(path: str, contents: str) -> None:
    """Fail closed unless an applicable changed artifact carries a complete seal.

    The supplied text is decoded from the exact Git blob selected by a commit
    or index snapshot. Tenant scope is limited to repository path metadata;
    mutation, persistence, idempotency, and business transactions are absent.
    The function grants no runtime, IAM, financial, payment, or settlement
    authority. It raises IntegrityFailure for malformed or divergent metadata.
    """
    scope = _artifact_scope(path)
    if scope is None:
        return

    expected_path = f"/Users/wilsonkhanyezi/legal-doc-system/{path}"

    def version_token_present(value: str, version: str) -> bool:
        token = re.compile(
            r"(?<![A-Za-z0-9.-])" + re.escape(version) + r"(?![A-Za-z0-9.-])"
        )
        return token.search(value) is not None

    if scope == "json":
        try:
            data = json.loads(contents)
        except json.JSONDecodeError as exc:
            raise IntegrityFailure(f"{path}: invalid JSON artifact") from exc
        metadata = data.get("sovereign_artifact") or data.get("wilsyArtifact")
        if not isinstance(metadata, dict):
            raise IntegrityFailure(f"{path}: missing sovereign_artifact metadata")

        aliases = {
            "canonical_path": ("canonical_path", "canonicalPath"),
            "security_privacy_posture": (
                "security_privacy_posture",
                "securityPrivacyPosture",
            ),
            "tenant_boundary": ("tenant_boundary", "tenantBoundary"),
            "authority_boundary": ("authority_boundary", "authorityBoundary"),
            "financial_authority_boundary": (
                "financial_authority_boundary",
                "financialAuthority",
            ),
            "fail_closed_posture": ("fail_closed_posture", "failClosedPosture"),
            "end_seal": ("end_seal", "seal"),
        }

        def metadata_value(key: str) -> object:
            for candidate in aliases.get(key, (key,)):
                value = metadata.get(candidate)
                if value:
                    return value
            return None

        required = (
            "title",
            "version",
            "authority",
            "epitome",
            "canonical_path",
            "ownership",
            "updated",
            "changelog",
            "compliance",
            "security_privacy_posture",
            "tenant_boundary",
            "authority_boundary",
            "financial_authority_boundary",
            "fail_closed_posture",
            "end_seal",
        )
        missing = [key for key in required if not metadata_value(key)]
        if missing:
            raise IntegrityFailure(
                f"{path}: missing sovereign metadata: {', '.join(missing)}"
            )

        version = str(metadata_value("version"))
        if not SOVEREIGN_VERSION.fullmatch(version):
            raise IntegrityFailure(f"{path}: invalid semantic artifact version")
        if metadata_value("canonical_path") != expected_path:
            raise IntegrityFailure(f"{path}: canonical artifact path mismatch")

        changelog = str(metadata_value("changelog"))
        if not version_token_present(changelog, version):
            raise IntegrityFailure(
                f"{path}: current version is absent from the changelog"
            )

        seal = str(metadata_value("end_seal"))
        seal_requirements = {
            "ARTIFACT": r"(?i)\bARTIFACT:\s*\S",
            "VERSION": r"(?i)\bVERSION:\s*\S",
            "AUTHORITY BOUNDARY": r"(?i)\bAUTHORITY BOUNDARY:\s*\S",
            "TENANT POSTURE": r"(?i)\bTENANT POSTURE:\s*\S",
            "FAIL-CLOSED POSTURE": r"(?i)\bFAIL-CLOSED POSTURE:\s*\S",
            "FINANCIAL EXECUTION AUTHORITY": (
                r"(?i)\bFINANCIAL EXECUTION AUTHORITY:\s*\S"
            ),
        }
        missing_seal = [
            label
            for label, pattern in seal_requirements.items()
            if not re.search(pattern, seal)
        ]
        if missing_seal:
            raise IntegrityFailure(
                f"{path}: incomplete sovereign JSON end seal: "
                + ", ".join(missing_seal)
            )
        seal_version = re.search(r"(?i)\bVERSION:\s*(\S+)", seal)
        if (
            seal_version is None
            or seal_version.group(1).rstrip("*|;,") != version
        ):
            raise IntegrityFailure(
                f"{path}: JSON header and end-seal versions differ"
            )
        if not seal.rstrip().endswith("END OF WILSY OS SOVEREIGN ARTIFACT"):
            raise IntegrityFailure(f"{path}: explicit sovereign JSON end seal is missing")
        return

    lines = _metadata_lines(contents)
    header = lines[:100]
    header_text = "\n".join(header)
    requirements = {
        "TITLE": r"(?im)^TITLE:\s*\S",
        "VERSION": r"(?im)^VERSION:\s*\S",
        "AUTHORITY": r"(?im)^AUTHORITY:\s*\S",
        "EPITOME": r"(?im)^EPITOME:\s*\S",
        "ABSOLUTE CANONICAL PATH": r"(?im)^ABSOLUTE CANONICAL PATH:",
        "COLLABORATION / OWNERSHIP": (
            r"(?im)^COLLABORATION[^:]*:\s*\S|^OWNERSHIP:\s*\S"
        ),
        "CERTIFICATION / UPDATE DATE": (
            r"(?im)^CERTIFICATION(?:\s*/\s*|\s+OR\s+)UPDATE DATE:\s*\S|^UPDATE DATE:\s*\S"
        ),
        "CHANGELOG": r"(?im)^CHANGELOG:",
        "COMPLIANCE": r"(?im)^COMPLIANCE:\s*\S",
        "SECURITY / PRIVACY POSTURE": (
            r"(?im)^SECURITY(?:\s*/\s*PRIVACY)?\s+POSTURE:\s*\S"
            r"|^PRIVACY POSTURE:\s*\S"
        ),
        "TENANT BOUNDARY / POSTURE": r"(?im)^TENANT (?:BOUNDARY|POSTURE):\s*\S",
        "AUTHORITY BOUNDARY": r"(?im)^AUTHORITY BOUNDARY:\s*\S",
        "FINANCIAL AUTHORITY BOUNDARY": (
            r"(?im)^FINANCIAL (?:AUTHORITY|EXECUTION AUTHORITY) BOUNDARY:\s*\S"
            r"|^FINANCIAL AUTHORITY:\s*\S"
        ),
    }
    missing = [
        name
        for name, pattern in requirements.items()
        if not re.search(pattern, header_text)
    ]
    if missing:
        raise IntegrityFailure(
            f"{path}: missing sovereign header fields: {', '.join(missing)}"
        )

    version_match = re.search(r"(?im)^VERSION:\s*(\S+)", header_text)
    if version_match is None:
        raise IntegrityFailure(f"{path}: sovereign header version is missing")
    version = version_match.group(1).rstrip("*|")
    if not SOVEREIGN_VERSION.fullmatch(version):
        raise IntegrityFailure(f"{path}: invalid semantic artifact version {version!r}")

    changelog_index = next(
        index
        for index, line in enumerate(header)
        if line.upper().startswith("CHANGELOG:")
    )
    changelog_lines = [header[changelog_index].partition(":")[2]]
    for line in header[changelog_index + 1 : changelog_index + 24]:
        if re.match(
            r"(?i)^(?:TITLE|VERSION|AUTHORITY|EPITOME|ABSOLUTE CANONICAL PATH|"
            r"COLLABORATION|OWNERSHIP|CERTIFICATION|UPDATE DATE|COMPLIANCE|"
            r"SECURITY|PRIVACY|TENANT|FINANCIAL|TRANSACTION|FAIL-CLOSED|ARTIFACT):",
            line,
        ):
            break
        changelog_lines.append(line)
    if not version_token_present("\n".join(changelog_lines), version):
        raise IntegrityFailure(
            f"{path}: current version is absent from the header changelog"
        )

    canonical_index = next(
        index
        for index, line in enumerate(header)
        if line.upper().startswith("ABSOLUTE CANONICAL PATH:")
    )
    canonical_segments = [
        header[canonical_index].partition(":")[2],
    ]
    for line in header[canonical_index + 1 : canonical_index + 12]:
        if re.match(r"^[A-Z][A-Z /-]*:", line, re.IGNORECASE):
            break
        if line.strip():
            canonical_segments.append(line.strip())
    canonical_value = re.sub(r"\s+", "", "".join(canonical_segments))
    if re.sub(r"\s+", "", expected_path) not in canonical_value:
        raise IntegrityFailure(f"{path}: canonical artifact path mismatch")

    terminal_line = next((line for line in reversed(lines) if line.strip()), "")
    if not terminal_line.endswith("END OF WILSY OS SOVEREIGN ARTIFACT"):
        raise IntegrityFailure(f"{path}: terminal sovereign end seal is missing")

    artifact_index = next(
        (
            index
            for index in range(len(lines) - 1, max(-1, len(lines) - 41), -1)
            if re.match(r"(?i)^ARTIFACT:\s*\S", lines[index])
        ),
        None,
    )
    if artifact_index is None:
        raise IntegrityFailure(f"{path}: sovereign end-seal artifact is missing")
    seal_text = "\n".join(lines[artifact_index:])
    seal_requirements = {
        "ARTIFACT": r"(?im)^ARTIFACT:\s*\S",
        "VERSION": r"(?im)^VERSION:\s*\S",
        "AUTHORITY BOUNDARY": r"(?im)^AUTHORITY BOUNDARY:\s*\S",
        "TENANT POSTURE": r"(?im)^TENANT POSTURE:\s*\S",
        "FAIL-CLOSED POSTURE": r"(?im)^FAIL-CLOSED POSTURE:\s*\S",
        "FINANCIAL EXECUTION AUTHORITY": (
            r"(?im)^FINANCIAL EXECUTION AUTHORITY:\s*\S"
        ),
    }
    missing_seal = [
        label
        for label, pattern in seal_requirements.items()
        if not re.search(pattern, seal_text)
    ]
    if missing_seal:
        raise IntegrityFailure(
            f"{path}: incomplete sovereign end seal: {', '.join(missing_seal)}"
        )

    seal_versions = re.findall(r"(?im)^VERSION:\s*(\S+)", seal_text)
    if not seal_versions or seal_versions[-1].rstrip("*|;,") != version:
        raise IntegrityFailure(f"{path}: header and end-seal versions differ")


class IntegrityFailure(RuntimeError):
    """Represent a fail-closed repository governance violation."""



def git(*args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args],
        stderr=subprocess.PIPE,
    )


def git_text(*args: str) -> str:
    return git(*args).decode(
        "utf-8",
        errors="strict",
    ).strip()


def load_policy() -> dict[str, Any]:
    data = json.loads(
        POLICY.read_text(
            encoding="utf-8"
        )
    )

    if data.get("version") != 1:
        raise IntegrityFailure(
            "unsupported production-surface policy version"
        )

    return data


def index_entries() -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}

    for record in git(
        "ls-files",
        "-s",
        "-z",
    ).split(b"\0"):
        if not record:
            continue

        meta, raw_path = record.split(
            b"\t",
            1,
        )

        mode, oid, stage = meta.decode(
            "ascii"
        ).split()

        if stage != "0":
            raise IntegrityFailure(
                "non-zero Git index stage"
            )

        path = raw_path.decode(
            "utf-8",
            errors="strict",
        )

        entries[path] = (
            mode,
            oid,
        )

    return entries


def tree_entries(
    commit: str,
) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}

    for record in git(
        "ls-tree",
        "-r",
        "-z",
        commit,
    ).split(b"\0"):
        if not record:
            continue

        meta, raw_path = record.split(
            b"\t",
            1,
        )

        mode, kind, oid = meta.decode(
            "ascii"
        ).split()

        if kind != "blob":
            continue

        path = raw_path.decode(
            "utf-8",
            errors="strict",
        )

        entries[path] = (
            mode,
            oid,
        )

    return entries


def blob(
    oid: str,
) -> bytes:
    return git(
        "cat-file",
        "blob",
        oid,
    )


def validate_path(
    path: str,
    allowed_top_level: set[str],
) -> None:
    if (
        not path
        or path.startswith("/")
        or "\\" in path
    ):
        raise IntegrityFailure(
            f"non-portable tracked path: {path!r}"
        )

    parts = PurePosixPath(
        path
    ).parts

    if not parts:
        raise IntegrityFailure(
            f"invalid tracked path: {path!r}"
        )

    if parts[0] not in allowed_top_level:
        raise IntegrityFailure(
            "unapproved top-level repository namespace: "
            f"{parts[0]!r}"
        )

    for part in parts:
        if part != part.strip():
            raise IntegrityFailure(
                f"whitespace-edge tracked path: {path!r}"
            )

        if "\u00a0" in part:
            raise IntegrityFailure(
                f"NBSP tracked path: {path!r}"
            )

        if any(
            unicodedata.category(ch) == "Cc"
            for ch in part
        ):
            raise IntegrityFailure(
                f"control-character tracked path: {path!r}"
            )


def target_exists(
    entries: dict[str, tuple[str, str]],
    target: str,
) -> bool:
    if target in entries:
        return True

    prefix = target.rstrip("/") + "/"

    return any(
        path.startswith(prefix)
        for path in entries
    )


def validate_snapshot(
    entries: dict[str, tuple[str, str]],
    changed: set[str],
) -> None:
    data = load_policy()

    allowed_top_level = {
        str(item)
        for item in data.get(
            "allowed_top_level",
            [],
        )
    }

    if not allowed_top_level:
        raise IntegrityFailure(
            "allowed_top_level policy is empty"
        )

    for path, (
        mode,
        oid,
    ) in entries.items():
        validate_path(
            path,
            allowed_top_level,
        )

        if mode == "120000":
            target = blob(
                oid
            ).decode(
                "utf-8",
                errors="strict",
            )

            if (
                not target
                or target.startswith("/")
                or "\\" in target
            ):
                raise IntegrityFailure(
                    f"non-portable symlink: {path!r} -> {target!r}"
                )

            resolved = posixpath.normpath(
                posixpath.join(
                    posixpath.dirname(path),
                    target,
                )
            )

            if (
                resolved == ".."
                or resolved.startswith("../")
            ):
                raise IntegrityFailure(
                    f"symlink escapes repository: {path!r}"
                )

            if not target_exists(
                entries,
                resolved,
            ):
                raise IntegrityFailure(
                    "symlink target absent from Git authority: "
                    f"{path!r} -> {target!r}"
                )

        if (
            path.startswith(
                ".github/workflows/"
            )
            and path.endswith(
                (
                    ".yml",
                    ".yaml",
                )
            )
        ):
            contents = blob(
                oid
            ).decode(
                "utf-8",
                errors="strict",
            )

            if any(
                pattern.search(contents)
                for pattern in BAD_CI
            ):
                raise IntegrityFailure(
                    f"placeholder CI enforcement: {path!r}"
                )

    for path in changed:
        current = entries.get(
            path
        )

        if current is None:
            continue

        mode, oid = current

        if mode != "120000" and _artifact_scope(path) is not None:
            try:
                artifact_text = blob(oid).decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise IntegrityFailure(
                    f"{path}: governed text artifact is not UTF-8"
                ) from exc
            validate_artifact_contract(path, artifact_text)

        if (
            path.endswith(".py")
            and mode == "100755"
            and not blob(oid).startswith(b"#!")
        ):
            raise IntegrityFailure(
                "executable Python without shebang: "
                f"{path!r}"
            )


def staged_changed() -> set[str]:
    return {
        item.decode(
            "utf-8",
            errors="strict",
        )
        for item in git(
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMR",
            "-z",
        ).split(b"\0")
        if item
    }


def commit_changed(
    commit: str,
) -> set[str]:
    parents = git_text(
        "show",
        "-s",
        "--format=%P",
        commit,
    ).split()

    if parents:
        raw = git(
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            "-z",
            parents[0],
            commit,
        )
    else:
        raw = git(
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "--diff-filter=ACMR",
            "-r",
            "-z",
            commit,
        )

    return {
        item.decode(
            "utf-8",
            errors="strict",
        )
        for item in raw.split(b"\0")
        if item
    }


def validate_public_status(surface: str = "worktree") -> None:
    if surface == "worktree":
        read = lambda path: (ROOT / path).read_text(encoding="utf-8")
    elif surface == "index":
        read = lambda path: git("show", f":{path}").decode("utf-8")
    else:
        read = lambda path: git("show", f"{surface}:{path}").decode("utf-8")
    try:
        sys.path.insert(0, str(ROOT))
        from tools.eos.governance.public_status import validate_text
        validate_text(read("README.md"), read("tools/eos/governance/public_project_status.json"))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise IntegrityFailure("public README status drift: " + str(exc)) from exc


def classify(
    path: str,
) -> str:
    data = load_policy()

    result = str(
        data.get(
            "default",
            "UNCLASSIFIED",
        )
    )

    for rule in data.get(
        "rules",
        [],
    ):
        pattern = str(
            rule["pattern"]
        )

        if fnmatch.fnmatchcase(
            path,
            pattern,
        ):
            result = str(
                rule["class"]
            )

    return result


def main() -> int:
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(
        required=True
    )

    mode.add_argument(
        "--staged",
        action="store_true",
    )

    mode.add_argument(
        "--commit",
    )

    mode.add_argument(
        "--classify",
        nargs="+",
        metavar="PATH",
    )

    mode.add_argument(
        "--assert-retained",
        nargs="+",
        metavar="PATH",
    )

    args = parser.parse_args()

    try:
        if args.staged:
            validate_public_status("index")
            validate_snapshot(
                index_entries(),
                staged_changed(),
            )

            print(
                "WILSY_REPOSITORY_INTEGRITY=PASS"
            )
            print(
                "AUTHORITY_SURFACE=INDEX"
            )

        elif args.commit:
            validate_public_status(args.commit)
            validate_snapshot(
                tree_entries(
                    args.commit
                ),
                commit_changed(
                    args.commit
                ),
            )

            print(
                "WILSY_REPOSITORY_INTEGRITY=PASS"
            )
            print(
                "AUTHORITY_SURFACE=COMMIT:"
                + args.commit
            )

        elif args.classify:
            for path in args.classify:
                print(
                    path
                    + "\t"
                    + classify(path)
                )

        else:
            data = load_policy()

            allowed = {
                str(item)
                for item in data.get(
                    "expensive_certification_allowed",
                    [],
                )
            }

            blocked: list[str] = []

            for path in args.assert_retained:
                classification = classify(
                    path
                )

                print(
                    path
                    + "\t"
                    + classification
                )

                if classification not in allowed:
                    blocked.append(
                        path
                        + "="
                        + classification
                    )

            if blocked:
                raise IntegrityFailure(
                    "expensive certification forbidden before "
                    "RETAIN/SOVEREIGN classification: "
                    + ", ".join(blocked)
                )

            print(
                "WILSY_PRODUCTION_SURFACE_AUTHORITY=PASS"
            )

        return 0

    except (
        IntegrityFailure,
        OSError,
        UnicodeError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
    ) as exc:
        print(
            "WILSY_REPOSITORY_INTEGRITY=FAIL: "
            + str(exc),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )


# ARTIFACT: Changed Artifact Sovereign Contract Guard
# VERSION: v1.2.0-CHANGED-BLOB-PYTHON-DOCSTRING-SEAL-CERT
# AUTHORITY BOUNDARY: Repository integrity evidence only; no runtime or business authority.
# TENANT POSTURE: No tenant identity, records, or cross-tenant authority are accessed.
# FAIL-CLOSED POSTURE: Missing, divergent, or wrongly located artifact metadata fails.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively owns execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
