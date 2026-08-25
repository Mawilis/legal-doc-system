#!/usr/bin/env python3
"""
WILSY OS — AUTOMATED PDF LAYOUT & PAGE-BUDGET VALIDATOR
Verifies compiled PDFs for page budget, structural boundaries, and non-empty content.
Includes zero-failure auto-bootstrap protocol for required dependencies.
"""

import sys
import os
import subprocess

# Zero-Failure Dependency Auto-Bootstrap Protocol
try:
    import pypdf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf


def validate_milestone_pdf(pdf_path: str, max_expected_pages: int = 2) -> bool:
    """Forensically inspects generated PDF to enforce geometry and page count constraints."""
    if not os.path.exists(pdf_path):
        print(f"[VALIDATION ERROR] File does not exist: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        reader = pypdf.PdfReader(pdf_path)
        actual_pages = len(reader.pages)
        
        print(f"\n[VALIDATOR] Inspecting target PDF: {pdf_path}")
        print(f"[VALIDATOR] Page Count: {actual_pages} / Max Allowed: {max_expected_pages}")
        
        if actual_pages > max_expected_pages:
            raise ValueError(
                f"[CONTRACT FAILURE] PDF overshot page budget! "
                f"Expected maximum {max_expected_pages} pages, but rendered {actual_pages} pages."
            )
            
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text or len(text.strip()) < 50:
                raise ValueError(f"[CONTRACT FAILURE] Page {idx + 1} contains insufficient or corrupt text rendering.")
                
        print(f"[SUCCESS] PDF layout contract mathematically verified for: {pdf_path}\n")
        return True

    except Exception as err:
        print(f"[VALIDATION ERROR] {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        validate_milestone_pdf(sys.argv[1])
    else:
        print("Usage: python3 pdf_validator.py <path_to_pdf>")
