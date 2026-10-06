"""WILSY OS CLI package boundary.

TITLE: WILSY OS CLI Package Boundary
VERSION: v1.0.1-D15G-CLI-LAZY-PACKAGE-BOUNDARY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Keeps the CLI package importable without eagerly importing legacy
         command surfaces whose optional dependencies may be unavailable, while
         preserving compatibility names through bounded lazy resolution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/cli/__init__.py
COLLABORATION / OWNERSHIP: Python EOS CLI package boundary only. Individual CLI
                           modules retain ownership of their runtime semantics.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.0.1-D15G-CLI-LAZY-PACKAGE-BOUNDARY — Declares the lazy compatibility
    exports only to static type checkers so Pyright can validate __all__ without
    creating runtime attributes that would bypass module __getattr__. Runtime
    lazy import behavior and failure semantics are unchanged.
  v1.0.0-D15G-CLI-LAZY-PACKAGE-BOUNDARY — Replaces unconditional package-time
    imports with lazy compatibility resolution so independent CLI submodules can
    be imported and certified without being coupled to unrelated legacy doctor
    wiring. No command, auth, tenant, persistence, or financial semantics change.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001 awareness.
SECURITY / PRIVACY POSTURE: Import-only package boundary; no secrets, persistence,
                            network calls, token issuance, or logging occur here.
TENANT BOUNDARY: None. This module performs no tenant lookup or mutation.
AUTHORITY BOUNDARY: Package import orchestration only; it grants no application,
                    authentication, authorization, legal, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Final


VERSION: Final[str] = "v1.0.1-D15G-CLI-LAZY-PACKAGE-BOUNDARY"

__all__ = [
    "CLICommands",
    "CLIStatus",
    "CLIDoctor",
    "CLIReport",
]

if TYPE_CHECKING:
    # Static declarations only. These names must remain unbound at runtime so
    # module __getattr__ retains sole ownership of lazy compatibility loading.
    CLICommands: Any
    CLIStatus: Any
    CLIDoctor: Any
    CLIReport: Any

_LAZY_EXPORTS: Final[dict[str, tuple[str, str]]] = {
    "CLICommands": ("tools.eos.cli.commands", "CLICommands"),
    "CLIStatus": ("tools.eos.cli.status", "CLIStatus"),
    "CLIDoctor": ("tools.eos.cli.doctor", "CLIDoctor"),
    "CLIReport": ("tools.eos.cli.report", "CLIReport"),
}


def __getattr__(name: str) -> Any:
    """Resolve one legacy package export only when explicitly requested.

    Authority:
        Import compatibility only. Resolution never creates runtime authority,
        performs authentication, or mutates state.

    Failure semantics:
        Unknown names raise AttributeError. A requested legacy export whose own
        module is structurally invalid propagates that import failure rather
        than making unrelated CLI submodule imports fail at package import time.

    Tenant and transaction semantics:
        None. No database, tenant, session, or transaction access occurs.

    Financial boundary:
        None. Kennel EOS remains the exclusive financial execution authority.
    """
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = target
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return deterministic package discovery including lazy compatibility names."""
    return sorted(set(globals()) | set(__all__))


# ARTIFACT: tools/eos/cli/__init__.py
# VERSION: v1.0.1-D15G-CLI-LAZY-PACKAGE-BOUNDARY
# AUTHORITY BOUNDARY: import-only lazy CLI package compatibility boundary
# TENANT POSTURE: none; no tenant read, projection, or mutation
# FAIL-CLOSED POSTURE: unknown names fail; requested broken legacy exports propagate their own import failure without poisoning unrelated submodules
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
