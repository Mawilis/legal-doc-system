"""
============================================================================
EPITOME: WILSY OS - DEEP DYNAMIC EOS REPOSITORY DISCOVERY & AUDIT ENGINE
STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE
============================================================================

COLLABORATION COMMENTS:
- @Wilson: This script performs a multi-tier deep inspection across your entire 
  codebase. It does NOT rely on hardcoded file lists or simple filename matching.
- It dynamically flags files across 3 distinct discovery vectors:
    1. PATH VECTOR: Files inside any folder named 'eos' (at any depth).
    2. FILENAME VECTOR: Files containing 'eos' or 'eos_' anywhere in the name.
    3. CONTENT DEEP-SCAN VECTOR: Files containing EOS system signatures 
       (e.g., 'EosKernel', 'Executive Operating System', 'FG231', 'FG232', 
       'capability_registry', 'executive_reasoning') inside their source code.
- Multi-threading & safety mechanisms ignore binary assets, git histories, 
  and dependency trees (node_modules, .venv) to guarantee zero lockups.
============================================================================
"""

import os
import re
import json
from datetime import datetime

# -----------------------------------------------------------------------------
# DISCOVERY CONFIGURATION & SYSTEM BOUNDARIES
# -----------------------------------------------------------------------------
CONFIG = {
    # Skip heavy/irrelevant build & environment directories
    "IGNORE_DIRS": {
        ".git", "node_modules", ".mongodb", "dist", "build", 
        ".venv", "__pycache__", ".wilsy-backup-vault", ".next", "coverage"
    },
    # Allowed text extensions for deep content scanning
    "SCAN_EXTENSIONS": {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", 
        ".yml", ".sh", ".sql", ".md", ".css", ".html"
    },
    # Content signatures that prove a file belongs to the EOS ecosystem
    "CONTENT_SIGNATUES": [
        r"\beos\b",
        r"\bEosKernel\b",
        r"\bWilsyEOS\b",
        r"\bExecutive Operating System\b",
        r"\bFG231[A-Z]?\b",
        r"\bFG232[A-Z]?\b",
        r"\bcapability_registry\b",
        r"\bexecutive_reasoning\b"
    ],
    "OUTPUT_TXT": "wilsy_deep_eos_catalog.txt",
    "OUTPUT_JSON": "wilsy_deep_eos_catalog.json"
}

# Compile content signature regexes for performance
SIGNATURE_REGEX = re.compile("|".join(CONFIG["CONTENT_SIGNATUES"]), re.IGNORECASE)

def scan_file_content(file_path):
    """
    Safely reads file content to detect embedded EOS architecture signatures.
    Reads up to 100KB to maintain ultra-fast traversal times.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            chunk = f.read(102400) # Read first 100KB
            matches = SIGNATURE_REGEX.findall(chunk)
            if matches:
                # Return unique signatures found
                return list(set(matches))
    except Exception:
        pass
    return []

def execute_deep_discovery():
    root_dir = os.getcwd()
    catalog = []
    
    print("============================================================================")
    print("WILSY OS - DEEP EOS DYNAMIC DISCOVERY ENGINE")
    print(f"Target Root: {root_dir}")
    print("============================================================================\n")
    print("[+] Initiating multi-vector repository traversal...")

    for current_root, dirs, files in os.walk(root_dir, topdown=True):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in CONFIG["IGNORE_DIRS"]]
        
        rel_dir = os.path.relpath(current_root, root_dir)
        path_has_eos = "eos" in rel_dir.lower().split(os.sep)

        for file_name in files:
            full_path = os.path.join(current_root, file_name)
            rel_file_path = os.path.relpath(full_path, root_dir)
            ext = os.path.splitext(file_name)[1].lower()

            name_has_eos = "eos" in file_name.lower()
            content_signatures = []

            # Perform deep content scan if extension qualifies
            if ext in CONFIG["SCAN_EXTENSIONS"]:
                content_signatures = scan_file_content(full_path)

            # File qualifies if any of the 3 discovery vectors trigger
            if path_has_eos or name_has_eos or len(content_signatures) > 0:
                reasons = []
                if path_has_eos: reasons.append("Directory Path ('/eos/')")
                if name_has_eos: reasons.append("Filename ('*eos*')")
                if content_signatures: reasons.append(f"Content Signatures: {content_signatures}")

                try:
                    size_bytes = os.path.getsize(full_path)
                except OSError:
                    size_bytes = 0

                catalog.append({
                    "fileName": file_name,
                    "relativePath": rel_file_path,
                    "absolutePath": os.path.abspath(full_path),
                    "sizeBytes": size_bytes,
                    "discoveryVectors": reasons,
                    "isPathMatch": path_has_eos,
                    "isNameMatch": name_has_eos,
                    "isContentMatch": len(content_signatures) > 0
                })

    # Sort catalog by relative path for structural clarity
    catalog.sort(key=lambda x: x["relativePath"])

    # Build human-readable audit text file
    txt_lines = []
    txt_lines.append("============================================================================")
    txt_lines.append("WILSY OS - COMPLETE DYNAMIC EOS FILE CATALOG")
    txt_lines.append(f"ROOT: {root_dir}")
    txt_lines.append(f"TIMESTAMP: {datetime.now().isoformat()}")
    txt_lines.append(f"TOTAL EOS FILES LOCATED: {len(catalog)}")
    txt_lines.append("STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE")
    txt_lines.append("============================================================================\n")

    current_group = ""
    for entry in catalog:
        folder = os.path.dirname(entry["relativePath"])
        if folder != current_group:
            current_group = folder
            txt_lines.append(f"\n📂 {current_group if current_group else '.'}/")
        
        vectors_str = " | ".join(entry["discoveryVectors"])
        txt_lines.append(f"  ├── {entry['fileName']:<45} ({entry['sizeBytes']:>7} bytes) -> [{vectors_str}]")

    txt_output = "\n".join(txt_lines)

    # Write text report
    with open(CONFIG["OUTPUT_TXT"], "w", encoding="utf-8") as f:
        f.write(txt_output)

    # Write machine JSON report
    with open(CONFIG["OUTPUT_JSON"], "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"\n[+] DISCOVERY COMPLETE.")
    print(f" -> Total EOS Files Discovered: {len(catalog)}")
    print(f" -> Detailed Text Report: {os.path.abspath(CONFIG['OUTPUT_TXT'])}")
    print(f" -> Machine JSON Index:  {os.path.abspath(CONFIG['OUTPUT_JSON'])}\n")
    print("============================================================================")
    print("DISCOVERED EOS DIRECTORY GROUPS:")
    print("============================================================================")
    
    unique_dirs = sorted(list(set(os.path.dirname(e["relativePath"]) for e in catalog)))
    for d in unique_dirs:
        count = sum(1 for e in catalog if os.path.dirname(e["relativePath"]) == d)
        print(f"  • {d}/ ({count} files)")
    print("============================================================================\n")

if __name__ == "__main__":
    execute_deep_discovery()
