"""Direct certificate for dedicated acceptance-instrument content identity.

TITLE: Legal Client Matter Acceptance Instrument Content Certificate
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove opaque deterministic references, strict byte/media bounds,
         immutable metadata integrity and absence of unrelated authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_content.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes direct adversarial certification.
TENANT BOUNDARY: Synthetic exact tenant/matter scope only.
AUTHORITY BOUNDARY: Content identity only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from dataclasses import fields
from datetime import datetime, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_content import (
    CONTENT_FIELDS,
    MAX_CONTENT_BYTES,
    LegalClientMatterAcceptanceInstrumentContent,
    LegalClientMatterAcceptanceInstrumentContentError,
    register_legal_client_matter_acceptance_instrument_content,
)


NOW = datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)
BYTES = b"Canonical client review terms."


def make(**changes: object) -> LegalClientMatterAcceptanceInstrumentContent:
    values: dict[str, object] = dict(tenant_id="tenant-one", case_matter_id="matter-one", instrument_id="instrument-one", instrument_version="1.0.0", content=BYTES, media_type="text/markdown", registered_at=NOW)
    values.update(changes)
    return register_legal_client_matter_acceptance_instrument_content(**values)  # type: ignore[arg-type]


def test_exact_scope_digest_and_opaque_deterministic_reference() -> None:
    first = make()
    second = make()
    assert first == second
    assert first.content_fingerprint == hashlib.sha3_512(BYTES).hexdigest()
    assert first.content_reference.startswith("legal-client-acceptance-instrument:")
    assert "tenant-one" not in first.content_reference
    assert "matter-one" not in first.content_reference
    assert first.content_length == len(BYTES)


def test_scope_version_and_bytes_each_change_reference() -> None:
    base = make()
    assert make(tenant_id="tenant-two").content_reference != base.content_reference
    assert make(case_matter_id="matter-two").content_reference != base.content_reference
    assert make(instrument_id="instrument-two").content_reference != base.content_reference
    assert make(instrument_version="2.0.0").content_reference != base.content_reference
    assert make(content=b"Different").content_reference != base.content_reference


@pytest.mark.parametrize("content", [b"", b"x" * (MAX_CONTENT_BYTES + 1), bytearray(b"x")])
def test_invalid_bytes_reject(content: object) -> None:
    with pytest.raises(LegalClientMatterAcceptanceInstrumentContentError):
        make(content=content)


@pytest.mark.parametrize("media_type", ["application/pdf", "text/html", " text/plain", ""])
def test_unsupported_or_noncanonical_media_rejects(media_type: str) -> None:
    with pytest.raises(LegalClientMatterAcceptanceInstrumentContentError):
        make(media_type=media_type)


def test_strict_round_trip_and_corruption_rejection() -> None:
    value = make()
    assert LegalClientMatterAcceptanceInstrumentContent.from_dict(value.to_dict()) == value
    assert set(value.to_dict()) == CONTENT_FIELDS
    for field, replacement in (("fingerprint", "0" * 128), ("content_reference", "forged"), ("content_length", 1)):
        payload = value.to_dict()
        payload[field] = replacement
        with pytest.raises(LegalClientMatterAcceptanceInstrumentContentError):
            LegalClientMatterAcceptanceInstrumentContent.from_dict(payload)
    payload = value.to_dict()
    payload["document_id"] = "forbidden"
    with pytest.raises(LegalClientMatterAcceptanceInstrumentContentError):
        LegalClientMatterAcceptanceInstrumentContent.from_dict(payload)


def test_domain_has_no_unrelated_authority_fields() -> None:
    names = {field.name for field in fields(LegalClientMatterAcceptanceInstrumentContent)}
    assert not names & {"document_id", "party_id", "approval_id", "acceptance_id", "engagement_id", "representation_id", "invoice_id", "payment_id", "settlement_id", "ai_confidence"}


# ARTIFACT: test_legal_client_matter_acceptance_instrument_content.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT-CERT
# AUTHORITY BOUNDARY: direct pure-domain certificate only
# TENANT POSTURE: exact synthetic tenant/matter scope
# FAIL-CLOSED POSTURE: forged, malformed, oversized and authority-bearing values reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
