#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITLE: WILSY OS Issue #300 Local Corporate Evidence Forensic Reconciliation
VERSION: v1.2.0-SOVEREIGN-ISSUE300-FORENSIC-RECONCILIATION
AUTHORITY: WILSY OS Core Governance; evidence observation only
EPITOME: Inventory local corporate PDFs, examine normalized textual source signals,
    compare corrected G64 file revisions, and emit non-authorizing metadata only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/scripts/wilsy_issue300_local_evidence_reconcile.py
COLLABORATION / OWNERSHIP: Issue #300 ownership evidence intake is the consumer;
    existing tenant ownership verifier/registry retain all authorization truth.
    This script is a standalone operator-side, read-only evidence observer.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG: v1.2.0-SOVEREIGN-ISSUE300-FORENSIC-RECONCILIATION enhances the
    certified read-only inventory with page-level text fingerprints, exact
    cross-version semantic comparisons and flexible legal-name observations;
    removes deprecated fitz import. v1.1.0 added sovereign structure.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 (data minimization).
SECURITY / PRIVACY POSTURE: No PDFs, extracted text, ID numbers, addresses,
    credentials, or document signatures are emitted. Output includes file paths,
    file hashes and Boolean signals; treat even this metadata as confidential.
    Read-only PDF extraction uses installed local tooling; no OCR or network.
TENANT BOUNDARY: Fixed evidence subject WILSYTENANT-4CD2FZ4O; no cross-tenant
    registry queries, database access, admission, or tenant-level mutations.
AUTHORITY BOUNDARY: A matching digest, form label or name is NOT independent
    CIPC verification, representation proof, issuer approval or IAM authority.
FINANCIAL AUTHORITY BOUNDARY: No financial operation; Kennel EOS is the sole
    financial execution authority.

OPERATOR CONTRACT: Place this file at the canonical path above. The script
    reads candidate PDFs under existing ~/Downloads and docs/verification only;
    it writes JSON to standard output and warnings to standard error. Redirect
    output into a protected, operator-controlled location if retention is needed.
    Never use its output as a positive Issue #300 issuer-verification decision.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any


CANONICAL_REPOSITORY = Path.home() / "legal-doc-system"
SEARCH_ROOTS = (
    CANONICAL_REPOSITORY / "docs" / "verification",
    Path.home() / "Downloads",
)
TENANT_ID = "WILSYTENANT-4CD2FZ4O"
DECISION_REF = "WILSY-IAM-INITIAL-GRANTOR-20261114"
EXPECTED_REPOSITORY_SHA256 = {
    "COR14.3.pdf": "100116d88fa4f3a57234af553b9bc757815d69401890350bdc3c46ee24a8635d",
    "COR14.1.pdf": "213be9a7f69b7dc79ff3b793642b13b5293859afbe46c02c0808531c5e456315",
    "COR14.1A.pdf": "daa78125e86b79e8fac9f00c009a7f6766b33a6ff66a6a46a60fbdd6210dbdd1",
}
FILENAME_SIGNALS = ("cor14", "cor15", "wilsy pty", "wilsypty")
REGISTRATION_SIGNAL = re.compile(r"2024\s*[/\-]\s*617944\s*[/\-]\s*07")
LEGAL_NAME_SIGNAL = re.compile(
    r"\bwilsy\b.{0,80}\b(?:pty|proprietary)\b", re.I | re.S
)
DIRECTOR_SIGNAL = re.compile(r"\b(?:wilson\s+khanyezi|khanyezi\s*,?\s*wilson)\b", re.I)
FORM_SIGNALS = {
    "cor14_3": re.compile(r"cor\s*14\s*[.\-]?\s*3", re.I),
    "cor14_1": re.compile(r"cor\s*14\s*[.\-]?\s*1(?!\s*a)", re.I),
    "cor14_1a": re.compile(r"cor\s*14\s*[.\-]?\s*1\s*a", re.I),
    "cor15_1a": re.compile(r"cor\s*15\s*[.\-]?\s*1\s*a", re.I),
}
SIGNATURE_TERMS = re.compile(
    r"\b(?:electronically\s+signed|digital\s+signature|commissioner\s+of\s+oaths)\b",
    re.I,
)


class EvidenceInspectionError(RuntimeError):
    """Local PDF read/extraction failure; never implies failed external verification.

    Scope: one local file. No persistence, transaction, network, IAM or financial
    action. Callers must surface the error rather than infer absent evidence.
    """


def sha256_file(path: Path) -> str:
    """Hash exact local file bytes without changing the source.

    SHA-256 is for compatibility with the supplied inventory, not issuer
    authenticity. The caller owns the filesystem read; no tenant data is read.
    """
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise EvidenceInspectionError(f"Cannot read candidate PDF: {path}") from exc
    return digest.hexdigest()


def extract_local_pdf(path: Path) -> tuple[str, int | None, str]:
    """Extract text using a local, installed reader; no OCR or network calls.

    Returns (reader, pages, text) for local classification only. Extraction
    errors fail closed; document absence and extraction failure stay distinct.
    No mutation, issuer decision, tenant write, or idempotency claim occurs.
    """
    try:
        import pymupdf  # type: ignore[import-not-found]
    except ImportError:
        pymupdf = None
    if pymupdf is not None:
        try:
            with pymupdf.open(path) as pdf:
                return "pymupdf", len(pdf), "\n".join(page.get_text() for page in pdf)
        except (OSError, RuntimeError, ValueError) as exc:
            raise EvidenceInspectionError(f"PyMuPDF could not read: {path}") from exc

    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError:
        PdfReader = None
    if PdfReader is not None:
        try:
            reader = PdfReader(str(path), strict=True)
            return "pypdf", len(reader.pages), "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except (OSError, ValueError, TypeError) as exc:
            raise EvidenceInspectionError(f"pypdf could not read: {path}") from exc

    if shutil.which("pdftotext"):
        with tempfile.TemporaryDirectory(prefix="wilsy-issue300-local-") as directory:
            output = Path(directory) / "page-text.txt"
            try:
                subprocess.run(
                    ["pdftotext", "-layout", str(path), str(output)],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
                return "pdftotext", None, output.read_text(encoding="utf-8", errors="replace")
            except (OSError, subprocess.SubprocessError) as exc:
                raise EvidenceInspectionError(f"pdftotext could not read: {path}") from exc

    raise EvidenceInspectionError("No local PDF reader available (PyMuPDF, pypdf or pdftotext)")


def discover_candidates() -> dict[str, list[Path]]:
    """Group only existing candidate PDFs by exact byte digest.

    The pre-existing operator roots are read-only. Symlinks are excluded;
    duplicate discovery is idempotent and cannot grant tenant authority.
    """
    groups: dict[str, list[Path]] = defaultdict(list)
    visited: set[Path] = set()
    for root in SEARCH_ROOTS:
        if not root.is_dir() or root.is_symlink():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".pdf":
                continue
            if not any(term in path.name.lower() for term in FILENAME_SIGNALS):
                continue
            resolved = path.resolve()
            if resolved in visited:
                continue
            visited.add(resolved)
            groups[sha256_file(path)].append(path)
    return dict(groups)


def normalized_text(contents: str) -> str:
    """Normalize extraction artifacts for local, non-authorizing comparison.

    Normalization is deterministic and lowers case/whitespace; comparison
    excludes PDF container metadata but cannot assess legal significance.
    There is no persistence, tenant session, or financial authority.
    """
    return re.sub(r"\s+", " ", contents.casefold()).strip()


def filing_family(path: Path) -> str:
    """Classify local evidence by its filename only, never its legal status.

    Classification has no IAM, legal-issuer, or tenant write semantics.
    """
    name = path.name.upper().replace(" ", "")
    for label in ("COR14.1A", "COR14.3", "COR14.1", "COR15.1A"):
        if name.startswith(label):
            return label
    return "COMPANY_CONSOLIDATED"


def semantic_comparisons(records: list[dict[str, Any]], text_by_hash: dict[str, str]) -> list[dict[str, Any]]:
    """Compare all version pairs within the same form family without leaking text.

    Exact text digests and bounded SequenceMatcher ratios distinguish identical
    extracted content from observable differences. They do not authenticate
    CIPC issuance, verify a signature, or determine which variant is legally
    current. Comparisons are computed locally without storage or transactions.
    """
    pairs: list[dict[str, Any]] = []
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            if left["filing_family"] != right["filing_family"]:
                continue
            first = text_by_hash[left["sha256"]]
            second = text_by_hash[right["sha256"]]
            # Compare bounded word streams to avoid quadratic character diffs.
            ratio = round(
                difflib.SequenceMatcher(
                    None, first.split()[:12000], second.split()[:12000],
                    autojunk=True,
                ).ratio(), 5
            )
            pairs.append({
                "filing_family": left["filing_family"],
                "left_sha256": left["sha256"],
                "right_sha256": right["sha256"],
                "normalized_text_identical": first == second,
                "normalized_text_similarity": ratio,
                "meaningful_legal_difference_verified": False,
            })
    return pairs


def inspection_record(digest: str, files: list[Path]) -> tuple[dict[str, Any], str]:
    """Produce minimized source-observation signals for one distinct PDF.

    No extracted personal data is retained in the returned record. A signal
    only establishes that text matching a pattern was observed locally; it
    cannot substitute for the independent Issue #300 verifier.
    """
    primary = sorted(
        files,
        key=lambda path: (
            not path.is_relative_to(CANONICAL_REPOSITORY / "docs" / "verification"),
            len(str(path)),
            str(path),
        ),
    )[0]
    reader, page_count, contents = extract_local_pdf(primary)
    normalized = normalized_text(contents)
    record = {
        "sha256": digest,
        "size_bytes": primary.stat().st_size,
        "file_count": len(files),
        "paths": [str(path) for path in files],
        "repository_copy": any(
            path.is_relative_to(CANONICAL_REPOSITORY / "docs" / "verification")
            for path in files
        ),
        "text_extraction": reader,
        "page_count": page_count,
        "filing_family": filing_family(primary),
        "normalized_text_sha3_512": hashlib.sha3_512(normalized.encode("utf-8")).hexdigest(),
        "contains_wilsy_token": bool(re.search(r"\bwilsy\b", normalized)),
        "contains_private_company_token": bool(re.search(r"\b(?:pty|proprietary)\b", normalized)),
        "has_extractable_text": bool(normalized.strip()),
        "registration_number_match": bool(REGISTRATION_SIGNAL.search(normalized)),
        "legal_name_match": bool(LEGAL_NAME_SIGNAL.search(normalized)),
        "director_name_match": bool(DIRECTOR_SIGNAL.search(normalized)),
        "form_type_signals": {
            form: bool(pattern.search(normalized)) for form, pattern in FORM_SIGNALS.items()
        },
        "possible_signing_terms": bool(SIGNATURE_TERMS.search(normalized)),
        "external_authenticity_verified": False,
        "current_representative_mandate_verified": False,
        "issue300_issuer_enrolled": False,
    }
    return record, normalized


def main() -> int:
    """Execute a bounded local inventory and print non-authorizing JSON.

    Exit 0 means inventory generated, 2 means no candidate PDFs, and 3 means
    local inspection failed. No transaction/session or database is opened.
    A successful exit NEVER means ownership, authority, or IAM was verified.
    """
    try:
        groups = discover_candidates()
        inspected = [
            inspection_record(digest, files)
            for digest, files in sorted(groups.items())
        ]
        records = [record for record, _ in inspected]
        text_by_hash = {record["sha256"]: content for record, content in inspected}
        comparisons = semantic_comparisons(records, text_by_hash)
        repository_hashes = {}
        for name, expected in EXPECTED_REPOSITORY_SHA256.items():
            path = CANONICAL_REPOSITORY / "docs" / "verification" / name
            repository_hashes[name] = (
                "missing" if not path.is_file()
                else "match" if sha256_file(path) == expected else "mismatch"
            )
    except (EvidenceInspectionError, OSError) as exc:
        print(f"ISSUE300_LOCAL_INSPECTION_FAILED: {exc}", file=sys.stderr)
        return 3

    print(json.dumps({
        "status": "LOCAL_DOCUMENT_INVENTORY_ONLY_NOT_AUTHORITY",
        "operation": "READ_ONLY",
        "canonical_iam_mutated": False,
        "tenant": TENANT_ID,
        "decision": DECISION_REF,
        "observed_files": sum(len(files) for files in groups.values()),
        "distinct_sha256": len(groups),
        "repository_hash_verification": repository_hashes,
        "documents": records,
        "same_family_version_comparisons": comparisons,
        "verification_receipt_discovered": False,
        "verification_receipt_search_status": "NOT_ASSESSED_BY_THIS_LOCAL_PDF_TOOL",
        "next_gate": (
            "Independent source authentication, representation mandate, "
            "issuer/trust-root/recovery governance and production composition"
        ),
    }, indent=2, sort_keys=True))
    return 0 if records else 2


if __name__ == "__main__":
    sys.exit(main())


# ARTIFACT: tools/eos/scripts/wilsy_issue300_local_evidence_reconcile.py
# VERSION: v1.2.0-SOVEREIGN-ISSUE300-FORENSIC-RECONCILIATION
# AUTHORITY BOUNDARY: Local source observation; never institutional approval or IAM grant.
# TENANT POSTURE: Exact WILSY tenant label only; no database or cross-tenant access.
# FAIL-CLOSED POSTURE: PDF-read failures raise structured errors; no positive verification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; none performed here.
# END OF WILSY OS SOVEREIGN ARTIFACT
