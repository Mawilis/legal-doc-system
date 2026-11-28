"""TITLE: WILSY OS HR03 Organization Source Accessibility Certificate
VERSION: v1.0.0-M03-HR03-A11Y-SOURCE-CERT
AUTHORITY: WILSY OS Core Governance
EPITOME: Guard high-contrast HR form colors and keyboard focus contracts at source level.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr03_organization_accessibility_contract.py
COLLABORATION / OWNERSHIP: WILSY OS People UX and HR engineering
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-M03-HR03-A11Y-SOURCE-CERT adds WCAG contrast source checks and keyboard focus selectors.
COMPLIANCE: WCAG 2.2 SC 1.4.3 and SC 2.4.7 source-level guards; not browser accessibility certification.
SECURITY / PRIVACY POSTURE: Static source only; no credentials or employee fixtures.
TENANT BOUNDARY: No tenant information accessed.
AUTHORITY BOUNDARY: Test-only contract; cannot create or authorize HR decisions.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2] / "client/src/components/hr"


def _luminance(color: str) -> float:
    """Compute sRGB relative luminance for a specified hex color."""
    channels = [int(color[index:index + 2], 16) / 255
                for index in (1, 3, 5)]
    linear = [(channel / 12.92 if channel <= 0.04045
               else ((channel + 0.055) / 1.055) ** 2.4)
              for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(fg: str, bg: str) -> float:
    """Calculate WCAG relative contrast, independent of DOM text-size inference."""
    first, second = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def _rules(filename: str, selector: str) -> str:
    """Return the last CSS rule for a specific, well-defined source selector."""
    source = (ROOT / filename).read_text(encoding="utf-8")
    found = list(re.finditer(
        re.escape(selector) + r"\s*\{([^{}]*)\}", source,
        flags=re.DOTALL,
    ))
    assert found, f"Missing accessibility selector {filename}: {selector}"
    return found[-1].group(1)


def _color(rule: str, property_name: str) -> str:
    """Extract an exact hex color declaration from the matched CSS rule."""
    matches = re.findall(
        r"(?:^|;)\s*" + re.escape(property_name) +
        r"\s*:\s*(#[0-9a-fA-F]{6})\b", rule,
    )
    assert matches, f"Missing explicit {property_name} color"
    return matches[-1].lower()


def test_department_labels_meet_wcag_aa_contrast():
    """Reject pale gold primary labels against the new white form background."""
    rule = _rules("HrDashboard.module.css",
                  ".peopleSurface .organizationDraftGrid label > span")
    fg = _color(rule, "color")
    assert _contrast(fg, "#ffffff") >= 4.5


def test_department_code_and_context_labels_meet_wcag_aa_contrast():
    """Readability remains explicit for generated-code and activity controls."""
    code = _rules("HrDashboard.module.css",
                  ".peopleSurface .organizationDraftGrid .organizationCodeField > label")
    assert _contrast(_color(code, "color"), "#ffffff") >= 4.5
    context = _rules("BusinessActivityContextWorkspace.module.css",
                     ".choices label")
    assert _contrast(_color(context, "color"), "#ffffff") >= 4.5
    lifecycle = _rules("OrganizationLifecycleWorkspace.module.css",
                       ".form label")
    assert _contrast(_color(lifecycle, "color"), "#fbfcff") >= 4.5


def test_keyboard_focus_visible_for_each_operational_surface():
    """A keyboard user must see focus indicators across the new HR controls."""
    expected = [
        ("HrDashboard.module.css",
         ".peopleSurface .organizationCodeHelp summary:focus-visible"),
        ("BusinessActivityContextWorkspace.module.css",
         ".context button:focus-visible"),
        ("OrganizationLifecycleWorkspace.module.css",
         ".lifecycle button:focus-visible"),
    ]
    for filename, selector in expected:
        rule = _rules(filename, selector)
        assert "outline:" in rule
        assert "none" not in rule


def test_form_uses_explicit_code_label_and_discrete_help():
    """The code field must not nest a second interactive button inside its label."""
    source = (ROOT / "HrDashboard.jsx").read_text(encoding="utf-8")
    assert 'htmlFor="wilsy-organization-record-code"' in source
    assert 'id="wilsy-organization-record-code"' in source
    assert '<details className={styles.organizationCodeHelp}>' in source
    assert "Editable suggestion, not a reserved code." not in source


# ARTIFACT: tests/unit/test_hr03_organization_accessibility_contract.py
# VERSION: v1.0.0-M03-HR03-A11Y-SOURCE-CERT
# AUTHORITY BOUNDARY: Source-level contrast and semantic test only.
# TENANT POSTURE: No tenant data or privileges.
# FAIL-CLOSED POSTURE: Any missing explicit accessible selector or label fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
