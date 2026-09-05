"""WILSY OS — PRE-TENANT BOOTSTRAP AUTHORITY

TITLE: Deployment-rooted tenant-owner bootstrap authority
VERSION: v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Verify the deployment-controlled provisioner allowlist.
EPITOME: Establishes non-circular, non-tenant authority evidence for a future
tenant-owner bootstrap operation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/pretenant_bootstrap_authority.py
COLLABORATION / OWNERSHIP: EOS auth domain owns verification; bootstrap orchestration consumes evidence.
SECURITY / PRIVACY POSTURE: Fail closed; configuration and identity values never enter errors.
TENANT BOUNDARY: Non-tenant authority; tenant context is intentionally excluded.
AUTHORITY BOUNDARY: Only deployment allowlisted authenticated principals may enter tenant-owner bootstrap.
FINANCIAL BOUNDARY: No financial or Kennel execution authority.
TRANSACTION BOUNDARY: No persistence, transaction, replay, or grant-consumption writes.
CERTIFICATION / UPDATE DATE: 2026-09-05
CHANGELOG: v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY — initial deployment-rooted verifier.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum

from tools.eos.auth.identity import SovereignIdentity

VERSION = "v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY"
TENANT_OWNER_BOOTSTRAP_OPERATION = "tenant_owner_bootstrap"
AUTHORITY_SOURCE_ID = "deployment_operator_provisioner_config"
_CONFIG_NAME = "WILSY_PRETENTANT_TENANT_PROVISIONER_PRINCIPAL_IDS"


class PretenantBootstrapAuthorityDenialCode(str, Enum):
    MALFORMED_IDENTITY = "MALFORMED_IDENTITY"
    MISSING_TRUSTED_AUTHORITY = "MISSING_TRUSTED_AUTHORITY"
    MALFORMED_TRUST_CONFIG = "MALFORMED_TRUST_CONFIG"
    PRINCIPAL_NOT_PROVISIONER = "PRINCIPAL_NOT_PROVISIONER"
    INTERNAL_INVARIANT_FRACTURE = "INTERNAL_INVARIANT_FRACTURE"


class PretenantBootstrapAuthorityError(Exception):
    """Bounded denial; never discloses principal or allowlist data."""

    def __init__(self, code: PretenantBootstrapAuthorityDenialCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class PretenantBootstrapAuthorityEvidence:
    """Immutable evidence; construction alone never grants authority."""

    principal_id: str
    operation: str
    authority_source: str


def _parse_provisioner_principal_ids(raw: str) -> frozenset[str]:
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG) from exc
    if not isinstance(parsed, list):
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG)
    if not parsed:
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MISSING_TRUSTED_AUTHORITY)
    values: list[str] = []
    for value in parsed:
        if not isinstance(value, str):
            raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG)
        if "\n" in value or "\r" in value:
            raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG)
        normalized = value.strip(" \t")
        if not normalized or normalized == "*":
            raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG)
        values.append(normalized)
    if len(set(values)) != len(values):
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG)
    return frozenset(values)


def verify_pretenant_bootstrap_authority(
    identity: SovereignIdentity,
) -> PretenantBootstrapAuthorityEvidence:
    """Verify authenticated identity against one trusted environment snapshot."""
    if not isinstance(identity, SovereignIdentity) or not isinstance(identity.identity_id, str) or not identity.identity_id:
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MALFORMED_IDENTITY)
    raw = os.environ.get(_CONFIG_NAME)
    if raw is None or not raw.strip():
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.MISSING_TRUSTED_AUTHORITY)
    provisioners = _parse_provisioner_principal_ids(raw)
    if identity.identity_id not in provisioners:
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.PRINCIPAL_NOT_PROVISIONER)
    evidence = PretenantBootstrapAuthorityEvidence(identity.identity_id, TENANT_OWNER_BOOTSTRAP_OPERATION, AUTHORITY_SOURCE_ID)
    if evidence.principal_id != identity.identity_id or evidence.operation != TENANT_OWNER_BOOTSTRAP_OPERATION or evidence.authority_source != AUTHORITY_SOURCE_ID:
        raise PretenantBootstrapAuthorityError(PretenantBootstrapAuthorityDenialCode.INTERNAL_INVARIANT_FRACTURE)
    return evidence


__all__ = ["TENANT_OWNER_BOOTSTRAP_OPERATION", "AUTHORITY_SOURCE_ID", "PretenantBootstrapAuthorityEvidence", "PretenantBootstrapAuthorityDenialCode", "PretenantBootstrapAuthorityError", "verify_pretenant_bootstrap_authority"]

# ARTIFACT: pretenant_bootstrap_authority.py
# VERSION: v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY
# AUTHORITY BOUNDARY: Deployment-rooted pre-tenant verification only.
# TENANT POSTURE: Non-tenant; no tenant-local authority.
# FAIL-CLOSED POSTURE: Missing, malformed, or unallowlisted identity denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
