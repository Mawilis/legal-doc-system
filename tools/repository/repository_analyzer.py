#!/usr/bin/env python3
"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Performance Deterministic Source Code Repository Analyzer and Index Engine.
    Scans workspace file topologies to extract structural code entities, routes,
    components, and service boundaries for the Wilsy OS Engineering Core.

Biblical Scale & Architecture:
    Built to index massive telemetry graphs and architectural layers across 
    billion-dollar systems. Employs optimized regular expressions, deterministic
    path filtering, and strong structural mapping barriers to ensure zero memory bloat
    and completely safe, read-only system sweeps. No child's place.

Collaboration & Maintenance:
    - [Safety]: Enforces zero mutation of target code assets. Blocks scanning of unauthorized or sensitive directories.
    - [Performance]: Leverages pre-compiled search vectors and lightweight streaming iterators.
    - [Compliance]: Adheres strictly to the structural indexing manifest of Wilsy OS.

===============================================================================
"""

from __future__ import annotations

import argparse
import logging
import pathlib
import re
from collections.abc import Iterable

# Initialize institutional logger
logger = logging.getLogger("wilsy.repository.repository_analyzer")

SOURCE_EXTENSIONS = {
    ".cjs",
    ".js",
    ".jsx",
    ".mjs",
    ".ts",
    ".tsx",
}

IGNORED_PARTS = {
    ".git",
    ".next",
    ".vite",
    ".wilsy-backup-vault",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
}

INDEX_OPTIONS = {
    "ai",
    "classes",
    "components",
    "controllers",
    "crm",
    "dependencies",
    "directories",
    "files",
    "functions",
    "hooks",
    "knowledge-base",
    "middleware",
    "models",
    "payload-builders",
    "pdf",
    "receipts",
    "renderer",
    "request-builders",
    "response-builders",
    "routes",
    "security",
    "services",
    "template",
    "utilities",
}


def should_scan_path(path: pathlib.Path) -> bool:
    """
    Determines if the given target filesystem node should be admitted into the index pipeline.
    
    Collaboration Comment:
    Filters out non-source extensions and blacklisted operational directories (e.g., node_modules, .git).
    Prevents memory overflows and deep-tree traversal deadlocks.
    """
    # Architectural Guard: Absolute avoidance of hidden files or prohibited runtimes
    return path.suffix in SOURCE_EXTENSIONS and not any(
        part in IGNORED_PARTS or part.startswith(".")
        for part in path.parts
    )


def unique_sorted(values: Iterable[str]) -> list[str]:
    """
    Deduplicates and sorts extracted elements into a stable, deterministic list structure.
    
    Collaboration Comment:
    Guarantees that index reports remain completely identical across multiple sweeps
    if the codebase content has not mutated.
    """
    return sorted({str(value) for value in values if str(value).strip()})


def find_matches(content: str, option: str) -> list[str]:
    """
    Executes deep regex token scanning against file buffers to identify explicit component boundaries.
    
    Collaboration Comment:
    Each structural option matches against optimized syntax signatures. Update these regex patterns
    whenever new semantic patterns are adopted in the client or server specifications.
    """
    # Defensive programming guard
    if not content or not option:
        return []

    if option == "functions":
        return re.findall(r"(?:function|async\s+function)\s+([A-Za-z_$][\w$]*)\s*\(", content)

    if option == "classes":
        return re.findall(r"class\s+([A-Za-z_$][\w$]*)", content)

    if option == "components":
        matches = re.findall(
            r"(?:function|const)\s+([A-Z][A-Za-z0-9_$]*)\s*(?:=|\()",
            content,
        )
        memo_matches = re.findall(
            r"const\s+([A-Z][A-Za-z0-9_$]*)\s*=\s*(?:React\.)?(?:memo|forwardRef)\b",
            content,
        )
        return [*matches, *memo_matches]

    if option == "hooks":
        return re.findall(
            r"(?:function|const)\s+(use[A-Z][A-Za-z0-9_$]*)\s*(?:=|\()",
            content,
        )

    if option == "routes":
        return [
            f"{receiver}.{method}('{route}')"
            for receiver, method, route in re.findall(
                r"\b(app|router|express)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
                content,
            )
        ]

    if option in {"services", "controllers", "models"}:
        return re.findall(r"class\s+([A-Za-z_$][\w$]*(?:Service|Controller|Model))\b", content)

    if option == "middleware":
        return re.findall(
            r"(?:function|const)\s+([A-Za-z_$][\w$]*(?:Middleware|Guard|Auth))\b",
            content,
        )

    if option in {
        "utilities",
        "payload-builders",
        "request-builders",
        "response-builders",
        "renderer",
        "template",
    }:
        return re.findall(r"const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(", content)

    if option == "dependencies":
        imports = re.findall(r"import\s+(?:[^'\"]+\s+from\s+)?['\"]([^'\"]+)['\"]", content)
        requires = re.findall(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)", content)
        return [*imports, *requires]

    if option in {"ai", "crm", "knowledge-base", "pdf", "receipts", "security"}:
        keyword = option.replace("-", " ")
        if keyword in content.lower() or option in content.lower():
            return [option]

    return []


def analyze_repository(root_dir: pathlib.Path, options: Iterable[str]) -> dict[str, list[str]]:
    """
    Orchestrates the global recursive mapping sweep of the target repository workspace root.
    
    Collaboration Comment:
    Tracks file-level topology metrics and routes data streams into the matching engine.
    Gracefully handles encoding anomalies to prevent scanning process collapse.
    """
    requested = set(options)
    if "all" in requested:
        requested = set(INDEX_OPTIONS)

    results: dict[str, list[str]] = {option: [] for option in sorted(requested)}
    
    # Architectural Guard: Verify path resolution and baseline access authority
    if not root_dir.exists():
        logger.error(f"Execution Aborted: Root target directory does not exist: {root_dir}")
        raise FileNotFoundError(f"Repository target root path not found: {root_dir}")

    files = [path for path in root_dir.rglob("*") if path.is_file() and should_scan_path(path)]
    logger.info(f"Identified {len(files)} clean source candidates for compilation mapping.")

    for path in files:
        try:
            relative_path = path.relative_to(root_dir).as_posix()
            content = path.read_text(encoding="utf-8", errors="ignore")

            if "files" in results:
                results["files"].append(relative_path)

            if "directories" in results:
                results["directories"].append(path.parent.relative_to(root_dir).as_posix())

            for option in results:
                if option in {"directories", "files"}:
                    continue

                for match in find_matches(content, option):
                    results[option].append(f"{match} :: {relative_path}")
        except Exception as file_err:
            logger.warning(f"Skipping potentially corrupt node reference {path}: {file_err}")
            continue

    return {
        option: unique_sorted(matches)
        for option, matches in results.items()
    }


def print_markdown(results: dict[str, list[str]]) -> None:
    """
    Renders the compiled index mapping matrix into clean, high-readability markdown telemetry layout sequences.
    
    Collaboration Comment:
    Formats output streams clearly to enable simple terminal redirection into architectural artifacts.
    """
    for option, matches in results.items():
        print(f"# {option.upper()}")
        if not matches:
            print("- NONE")
        else:
            for match in matches:
                print(f"- {match}")
        print()


def main() -> None:
    """
    CLI execution entry point managing boundary flag processing and argument validation routines.
    """
    # Setup standard logging layout for high-throughput visualization
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Wilsy OS Repository Analyzer Engine")
    parser.add_argument("--root", default=".", help="Repository workspace root framework path to analyze")
    
    for option in sorted(INDEX_OPTIONS):
        parser.add_argument(f"--{option}", action="store_true", help=f"Compile granular index list for {option}")
    parser.add_argument("--all", action="store_true", help="Compile all system intelligence indexes comprehensively")

    args = parser.parse_args()
    requested = [
        option
        for option in [*sorted(INDEX_OPTIONS), "all"]
        if getattr(args, option.replace("-", "_"), False)
    ]

    if not requested:
        parser.error("Execution Bound Violation: At least one structural index scanning option must be provided.")

    root_dir = pathlib.Path(args.root).resolve()
    
    try:
        scan_matrix = analyze_repository(root_dir, requested)
        print_markdown(scan_matrix)
    except Exception as run_err:
        logger.critical(f"Fatal kernel failure during active repository scan routines: {run_err}")
        raise SystemExit(1) from run_err


if __name__ == "__main__":
    main()
