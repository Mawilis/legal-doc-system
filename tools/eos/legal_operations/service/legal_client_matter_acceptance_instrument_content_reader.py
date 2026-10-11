"""Production reader for dedicated acceptance-instrument content.

TITLE: Legal Client Matter Acceptance Instrument Content Reader
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-READER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adapt the certified dedicated content registry to the existing
         client-acceptance ContentReader capability without bypassing delivery checks.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_client_matter_acceptance_instrument_content_reader.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes exact tenant/session registry reads.
TENANT BOUNDARY: Tenant and reference are supplied only by server orchestration.
AUTHORITY BOUNDARY: Storage adaptation only; no content delivery or acceptance authority.
TRANSACTION BOUNDARY: The registry requires the caller-owned active transaction.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, foreign, corrupt or unavailable content rejects.
"""
from __future__ import annotations

from typing import Any, Final

from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_content_registry import read_content
from tools.eos.legal_operations.service.legal_client_acceptance_content_service import StoredContent


VERSION: Final[str] = "v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-READER"


class LegalClientMatterAcceptanceInstrumentContentReader:
    """Resolve only dedicated, integrity-verified acceptance content bytes."""

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise TypeError("CLIENT_ACCEPTANCE_CONTENT_READER_COLLECTION_REQUIRED")
        self._collection = collection

    def read(self, content_reference: str, *, tenant_id: str, session: Any) -> StoredContent:
        """Return canonical media and bytes from one exact tenant-scoped row."""
        metadata, content = read_content(tenant_id, content_reference, self._collection, session=session)
        return StoredContent(content=content, media_type=metadata.media_type)


__all__ = ["VERSION", "LegalClientMatterAcceptanceInstrumentContentReader"]

# ARTIFACT: legal_client_matter_acceptance_instrument_content_reader.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-READER
# AUTHORITY BOUNDARY: dedicated registry-to-ContentReader adaptation only
# TENANT POSTURE: exact server-derived tenant/reference scope
# FAIL-CLOSED POSTURE: missing, foreign, corrupt and untransactional reads reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
