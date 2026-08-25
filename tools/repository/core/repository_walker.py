#!/usr/bin/env python3
"""
========================================================================================
WILSY OS ENTERPRISE PLATFORM - REPOSITORY WALKER & TOPOLOGY SCANNER
========================================================================================
Architect: Wilson Khanyezi | Founder & Lead SaaS Architect
System: Wilsy OS (Billion-Dollar Legal & Enterprise Intelligence Platform)
Module: tools/repository/core/repository_walker.py

COLLABORATION & GOVERNANCE NOTES:
----------------------------------------------------------------------------------------
- Purpose: Enforces complete visibility across full-stack target directories including
  client-side React/JSX components, server-side Node.js enterprise microservices, and
  Python kernel subsystems.
- Non-Negotiable: Production-ready code, zero truncations, explicit whitelist filters,
  and graceful handling of missing or locked directories.
- Architectural Standard: Enterprise-grade depth tracking, standard ignore patterns,
  and deterministic output formatting.
========================================================================================
"""

import os
import sys
from pathlib import Path
from typing import Set


# --------------------------------------------------------------------------------------
# SYSTEM CONFIGURATION & WHITELIST POLICIES
# --------------------------------------------------------------------------------------
TARGET_DIRECTORIES: Set[str] = {"client", "server", "tools"}
ALLOWED_EXTENSIONS: Set[str] = {
    ".js", ".jsx", ".ts", ".tsx", ".py", ".json", ".mjs", ".css", ".scss"
}
IGNORED_DIRS: Set[str] = {
    "node_modules", "build", "dist", ".git", "__pycache__", ".next", ".cache", "coverage"
}


def scan_wilsy_architecture(root_path_str: str = ".") -> None:
    """
    Executes an un-truncated, enterprise-grade directory walk starting from root_path.
    
    Evaluates system tree structures for Wilsy OS, explicitly displaying client-side 
    JSX components, backend JS microservices, and internal Python tooling while filtering 
    ephemeral artifacts (node_modules, build caches).

    Args:
        root_path_str (str): Target directory path to commence scanning. Defaults to standard root (".").
    
    Raises:
        FileNotFoundError: If the specified root path does not exist on the filesystem.
    """
    root_path = Path(root_path_str).resolve()

    if not root_path.exists():
        print(f"[ERROR] Target path '{root_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"========================================================================")
    print(f" WILSY OS - ENTERPRISE TOPOLOGY SCANNER")
    print(f" Root Path: {root_path}")
    print(f" Whitelist Targets: {', '.join(sorted(TARGET_DIRECTORIES))}")
    print(f"========================================================================\n")

    # Walk the tree deterministically
    for current_dir, dirs, files in os.walk(root_path):
        # In-place filtering of ignored directories to prevent deep traversal into dependencies
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]
        
        # Sort directories and files for deterministic output ordering
        dirs.sort()
        files.sort()

        rel_path = Path(current_dir).relative_to(root_path)
        depth = len(rel_path.parts)

        # Print root folder header
        if depth == 0:
            print(f"├── 📁 {root_path.name}/")
            continue

        # Ensure top-level isolation: only traverse target architecture directories
        if depth == 1 and rel_path.parts[0] not in TARGET_DIRECTORIES:
            continue

        # Generate visual tree indent depth
        indent = "│   " * (depth - 1)
        dir_name = Path(current_dir).name
        print(f"{indent}├── 📁 {dir_name}/")

        # Process valid full-stack source code files
        for file in files:
            file_ext = Path(file).suffix.lower()
            if file_ext in ALLOWED_EXTENSIONS or file.endswith(".config.js"):
                print(f"{indent}│   └── 📄 {file}")


if __name__ == "__main__":
    # Execute full architecture scan against project root
    scan_wilsy_architecture(".")
