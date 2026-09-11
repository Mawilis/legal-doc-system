"""Native Ed25519 adapter for the injected PRDCA cryptographic boundary.

TITLE: PRDCA Ed25519 Production Adapter
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3KR5
AUTHORITY: Wilsy OS Core Governance
EPITOME: Binds the frozen PRDCASigner and PRDCAKeyResolver protocols to the
         installed cryptography Ed25519 implementation without owning keys,
         persistence, deployment evidence, or runtime authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/prdca_ed25519.py
COLLABORATION / OWNERSHIP: PRDCA core consumes these adapters; deployment and
                            key-management authorities provide key objects.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3KR5 adds the native Ed25519
           signer and exact authority-key resolver adapter.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Private keys remain injected objects; no key
                            serialization, secret fetch, KMS, network, or
                            provider access occurs here.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Cryptographic signing and verification capability only;
                    this module does not issue deployment truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing backend, unknown key IDs, malformed messages,
                          malformed signatures, and invalid signatures reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
import re
from typing import Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from tools.eos.governance.prdca import PRDCAKeyResolver, PRDCASigner


_AUTHORITY_KEY_ID = re.compile(r"^prdca-key:[a-z0-9][a-z0-9._-]{0,63}$")


class PRDCAEd25519AdapterError(ValueError):
    """Fail-closed adapter boundary error."""


class CryptographyEd25519Signer(PRDCASigner):
    """Adapt an injected cryptography Ed25519 private-key object to PRDCA."""

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        if not isinstance(private_key, Ed25519PrivateKey):
            raise PRDCAEd25519AdapterError("M11P3KR5_ED25519_PRIVATE_KEY_REQUIRED")
        self._private_key = private_key

    def sign(self, message: bytes) -> bytes:
        """Return the native 64-byte Ed25519 signature for ``message``."""
        if not isinstance(message, bytes):
            raise PRDCAEd25519AdapterError("M11P3KR5_ED25519_MESSAGE_REQUIRED")
        signature = self._private_key.sign(message)
        if len(signature) != 64:
            raise PRDCAEd25519AdapterError("M11P3KR5_INVALID_SIGNATURE_LENGTH")
        return signature


class CryptographyEd25519KeyResolver(PRDCAKeyResolver):
    """Resolve exact authority key IDs to native Ed25519 verification callables."""

    def __init__(self, public_keys: Mapping[str, Ed25519PublicKey]) -> None:
        normalized: dict[str, Ed25519PublicKey] = {}
        for key_id, public_key in public_keys.items():
            if not isinstance(key_id, str) or _AUTHORITY_KEY_ID.fullmatch(key_id) is None:
                raise PRDCAEd25519AdapterError("M11P3KR5_INVALID_AUTHORITY_KEY_ID")
            if not isinstance(public_key, Ed25519PublicKey):
                raise PRDCAEd25519AdapterError("M11P3KR5_ED25519_PUBLIC_KEY_REQUIRED")
            normalized[key_id] = public_key
        self._public_keys = MappingProxyType(normalized)

    def resolve(self, authority_key_id: str) -> Callable[[bytes, bytes], bool]:
        """Return a verifier for one exact key ID; unknown IDs fail closed."""
        if not isinstance(authority_key_id, str) or _AUTHORITY_KEY_ID.fullmatch(authority_key_id) is None:
            raise KeyError(authority_key_id)
        public_key = self._public_keys[authority_key_id]

        def verify(message: bytes, signature: bytes) -> bool:
            if not isinstance(message, bytes) or not isinstance(signature, bytes) or len(signature) != 64:
                return False
            try:
                public_key.verify(signature, message)
            except (InvalidSignature, TypeError, ValueError):
                return False
            return True

        return verify


__all__ = [
    "CryptographyEd25519KeyResolver",
    "CryptographyEd25519Signer",
    "PRDCAEd25519AdapterError",
]


# ARTIFACT: prdca_ed25519.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3KR5
# AUTHORITY BOUNDARY: native Ed25519 capability adapter only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: unavailable, unknown, malformed, or invalid crypto rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
