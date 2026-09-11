"""TITLE: Accounts Payable Provider Selection Decision.
VERSION: v1.0.0-M11-P5-R1B-AP2D-R1.
AUTHORITY: Kennel EOS AP provider-selection authority.
EPITOME: Immutable provider selection for one exact AP authority slot.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/accounts_payable_provider_selection_decision.py
COLLABORATION / OWNERSHIP: Kennel EOS AP provider-selection domain; AP2D orchestration constructs this fact.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes deterministic authority-slot identity and immutable selected-provider evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers only; no secrets or provider transport.
TENANT BOUNDARY: Every decision carries an exact tenant identity in its authority slot.
AUTHORITY BOUNDARY: Provider selection evidence only; no policy lookup, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS owns later command execution; this fact does not move money.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Mapping, cast


_FINGERPRINT_PATTERN = re.compile(r"[0-9a-f]{128}")


class AccountsPayableProviderSelectionDecisionError(ValueError):
    """Raised when immutable AP provider-selection evidence is malformed."""


def _require_text(name: str, value: object) -> str:
    """Require a non-empty textual authority field without normalizing it."""
    if not isinstance(value, str) or not value.strip():
        raise AccountsPayableProviderSelectionDecisionError(f"{name} is invalid")
    return value


def _require_fingerprint(name: str, value: object) -> str:
    """Require the canonical lowercase SHA3-512 hexadecimal representation."""
    text = _require_text(name, value)
    if _FINGERPRINT_PATTERN.fullmatch(text) is None:
        raise AccountsPayableProviderSelectionDecisionError(f"{name} is invalid")
    return text


def _digest(payload: Mapping[str, object]) -> str:
    """Hash deterministic canonical JSON using SHA3-512."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class AccountsPayableProviderSelectionDecision:
    """Immutable AP selection fact for one request, runtime binding, and policy slot.

    The constructor accepts ``selected_provider`` as value material because the
    object records a completed decision.  It does not confer selection authority;
    AP2D orchestration must prove request durability, explicit currentness, exact
    policy provenance, and eligibility before constructing or persisting it.
    """

    tenant_id: str
    execution_request_id: str
    execution_request_fingerprint: str
    runtime_binding_id: str
    runtime_binding_revision: int
    runtime_binding_fingerprint: str
    provider_policy_id: str
    provider_policy_revision: int
    provider_policy_fingerprint: str
    selected_provider: str
    selection_decision_id: str = field(init=False, default="")
    selection_decision_fingerprint: str = field(init=False, default="")

    def __post_init__(self) -> None:
        """Validate intrinsic shape and derive immutable identifiers deterministically."""
        for name in (
            "tenant_id",
            "execution_request_id",
            "runtime_binding_id",
            "provider_policy_id",
            "selected_provider",
        ):
            _require_text(name, getattr(self, name))
        for name in (
            "execution_request_fingerprint",
            "runtime_binding_fingerprint",
            "provider_policy_fingerprint",
        ):
            _require_fingerprint(name, getattr(self, name))
        for name in ("runtime_binding_revision", "provider_policy_revision"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise AccountsPayableProviderSelectionDecisionError(f"{name} is invalid")

        expected_id = self.derive_selection_decision_id()
        object.__setattr__(self, "selection_decision_id", expected_id)

        expected_fingerprint = self.derive_fingerprint()
        object.__setattr__(self, "selection_decision_fingerprint", expected_fingerprint)

    def authority_slot_payload(self) -> dict[str, object]:
        """Return the canonical slot material, deliberately excluding the provider result."""
        return {
            "tenant_id": self.tenant_id,
            "execution_request_id": self.execution_request_id,
            "execution_request_fingerprint": self.execution_request_fingerprint,
            "runtime_binding_id": self.runtime_binding_id,
            "runtime_binding_revision": self.runtime_binding_revision,
            "runtime_binding_fingerprint": self.runtime_binding_fingerprint,
            "provider_policy_id": self.provider_policy_id,
            "provider_policy_revision": self.provider_policy_revision,
            "provider_policy_fingerprint": self.provider_policy_fingerprint,
        }

    def derive_selection_decision_id(self) -> str:
        """Derive the deterministic decision identity from authority-slot material only."""
        return _digest(self.authority_slot_payload())

    def decision_payload(self) -> dict[str, object]:
        """Return every immutable decision field used by the decision fingerprint."""
        return {
            "selection_decision_id": self.selection_decision_id,
            "tenant_id": self.tenant_id,
            "execution_request_id": self.execution_request_id,
            "execution_request_fingerprint": self.execution_request_fingerprint,
            "runtime_binding_id": self.runtime_binding_id,
            "runtime_binding_revision": self.runtime_binding_revision,
            "runtime_binding_fingerprint": self.runtime_binding_fingerprint,
            "provider_policy_id": self.provider_policy_id,
            "provider_policy_revision": self.provider_policy_revision,
            "provider_policy_fingerprint": self.provider_policy_fingerprint,
            "selected_provider": self.selected_provider,
        }

    def derive_fingerprint(self) -> str:
        """Derive the deterministic SHA3-512 fingerprint of the full decision payload."""
        return _digest(self.decision_payload())

    def to_persisted(self) -> dict[str, object]:
        """Return the complete immutable decision document for a future registry."""
        return {**self.decision_payload(), "selection_decision_fingerprint": self.selection_decision_fingerprint}

    @classmethod
    def from_persisted(cls, row: Mapping[str, object]) -> "AccountsPayableProviderSelectionDecision":
        """Reconstruct a decision from its canonical document without external I/O."""
        values = cast(dict[str, Any], dict(row))
        stored_id = values.pop("selection_decision_id", None)
        stored_fingerprint = values.pop("selection_decision_fingerprint", None)
        value = cls(**values)
        if stored_id != value.selection_decision_id:
            raise AccountsPayableProviderSelectionDecisionError("selection_decision_id is invalid")
        if stored_fingerprint != value.selection_decision_fingerprint:
            raise AccountsPayableProviderSelectionDecisionError("selection_decision_fingerprint is invalid")
        return value


# ARTIFACT: accounts_payable_provider_selection_decision.py
# VERSION: v1.0.0-M11-P5-R1B-AP2D-R1
# AUTHORITY BOUNDARY: AP provider selection evidence only; no execution or settlement
# TENANT POSTURE: exact tenant-scoped authority-slot provenance
# FAIL-CLOSED POSTURE: malformed, divergent, or non-canonical evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
