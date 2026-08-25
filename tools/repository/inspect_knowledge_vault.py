#!/usr/bin/env python3
import sys
from pathlib import Path

def inspect_vault_architecture():
    root = Path("/Users/wilsonkhanyezi/legal-doc-system")
    target_jsx = root / "client/src/components/knowledge/WilsyKnowledgeBaseVault.jsx"
    target_css = root / "client/src/components/knowledge/WilsyKnowledgeBaseVault.module.css"

    if not target_jsx.exists():
        print(f"ERROR: Mandatory file target missing at {target_jsx}", file=sys.stderr)
        sys.exit(1)

    print("=== WILSY OS KERNEL DIAGNOSTIC: JSX STRUCTURAL SCAN ===")
    jsx_lines = target_jsx.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(jsx_lines, 1):
        print(f"JSX_{idx:04d}: {line}")

    if target_css.exists():
        print("\n=== WILSY OS KERNEL DIAGNOSTIC: CSS MODULE SCAN ===")
        css_lines = target_css.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(css_lines, 1):
            print(f"CSS_{idx:04d}: {line}")
    else:
        print("\nWARNING: CSS Module file not found at expected vector path.", file=sys.stderr)

if __name__ == "__main__":
    inspect_vault_architecture()
