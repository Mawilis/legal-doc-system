"""WILSY OS repository-integrity and production-surface firewall."""

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

ROOT = Path(__file__).resolve().parents[3]
POLICY = ROOT / "tools/eos/governance/production_surface_policy.json"

BAD_CI = (
    re.compile(r'(?mi)^\s*run:\s*echo\s+["\']Security Logged["\']\s*$'),
    re.compile(r'(?mi)^\s*run:\s*echo\s+["\']Lint Logged["\']\s*$'),
)


class IntegrityFailure(RuntimeError):
    pass


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


def load_policy() -> dict[str, object]:
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
