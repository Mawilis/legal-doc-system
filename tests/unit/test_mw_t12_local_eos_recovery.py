"""TITLE: MW-T12 isolated Headquarters recovery evidence certificate.
VERSION: v1.0.0-FOUR-VIEWPORT-EVIDENCE-FAIL-CLOSED-TEST
AUTHORITY: WILSY OS Core Governance; synthetic test-only proof.
EPITOME: Certify the existing local recovery operator checks authenticated
         browser evidence for every Headquarters viewport before success.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_local_eos_recovery.py
COLLABORATION / OWNERSHIP: The MW-T12 operator owns loopback replica lifecycle;
         Playwright owns assertions, network evidence and screen captures.
CERTIFICATION / UPDATE DATE: 2026-11-24.
CHANGELOG: v1.0.0-FOUR-VIEWPORT-EVIDENCE-FAIL-CLOSED-TEST adds synthetic
           positive, missing viewport, browser failure, foreign fixture,
           missing authenticated readback and absent screenshot tests.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real tokens, users, tenants or work records.
TENANT BOUNDARY: Only temporary test fixture artifacts are used.
AUTHORITY BOUNDARY: Tests evidence admission, not production rollback or IAM.
FINANCIAL AUTHORITY BOUNDARY: No financial execution.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.eos.ops.mw_t12_local_eos_recovery import (
    MWRecoveryError,
    _verify_headquarters_evidence,
)

VIEWPORTS = ((1440, 900), (1760, 1000), (1024, 900), (390, 844))


def _evidence(directory: Path) -> None:
    """Create the exact expected synthetic browser-proof surface."""
    for width, height in VIEWPORTS:
        name = f"headquarters-{width}"
        (directory / f"{name}-network.json").write_text(
            json.dumps({
                "viewport": {"width": width, "height": height},
                "fixture": "DISPOSABLE_SYNTHETIC_SESSION",
                "founderMfaAcceptance": False,
                "network": [
                    {"path": "/api/my-work", "method": "GET", "status": 200},
                ],
                "browserErrors": [],
            }),
            encoding="utf-8",
        )
        for suffix in ("", "-ai-companion", "-record", "-readback"):
            (directory / f"{name}{suffix}.png").write_bytes(b"synthetic-test-pixel")


def test_complete_four_viewport_authenticated_evidence_admitted(tmp_path: Path) -> None:
    """Evidence emitted by all four browser widths admits recovery readback."""
    _evidence(tmp_path)
    _verify_headquarters_evidence(tmp_path)


@pytest.mark.parametrize("missing", [
    "headquarters-390-network.json",
    "headquarters-1440-readback.png",
])
def test_missing_browser_evidence_fails_closed(tmp_path: Path, missing: str) -> None:
    """Missing responsive or readback artifacts cannot certify MW-T12."""
    _evidence(tmp_path)
    (tmp_path / missing).unlink()
    with pytest.raises(MWRecoveryError, match="HEADQUARTERS_"):
        _verify_headquarters_evidence(tmp_path)


@pytest.mark.parametrize("field,value", [
    ("browserErrors", ["TypeError"]),
    ("fixture", "CANONICAL_WILSY_TENANT"),
    ("founderMfaAcceptance", True),
    ("network", [{"path": "/api/my-work", "method": "GET", "status": 403}]),
    ("viewport", {"width": 300, "height": 844}),
])
def test_invalid_or_unverified_browser_proof_rejected(
    tmp_path: Path, field: str, value: object,
) -> None:
    """Malformed, unauthorized or mislabelled evidence never passes."""
    _evidence(tmp_path)
    path = tmp_path / "headquarters-390-network.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document[field] = value
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(MWRecoveryError, match="HEADQUARTERS_"):
        _verify_headquarters_evidence(tmp_path)


def test_corrupted_browser_network_record_rejected(tmp_path: Path) -> None:
    """Invalid JSON must fail without inventing a successful readback."""
    _evidence(tmp_path)
    (tmp_path / "headquarters-1024-network.json").write_text(
        "{malformed", encoding="utf-8",
    )
    with pytest.raises(MWRecoveryError, match="HEADQUARTERS_NETWORK_EVIDENCE_INVALID"):
        _verify_headquarters_evidence(tmp_path)


# ARTIFACT: tests/unit/test_mw_t12_local_eos_recovery.py
# VERSION: v1.0.0-FOUR-VIEWPORT-EVIDENCE-FAIL-CLOSED-TEST
# AUTHORITY BOUNDARY: Disposable test data and read-only certificate.
# TENANT POSTURE: No canonical WILSY database, actor or credentials.
# FAIL-CLOSED POSTURE: Missing or invalid proof denies certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
