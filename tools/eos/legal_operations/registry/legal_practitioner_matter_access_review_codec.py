"""R65 infrastructure codec: canonical persistence and integrity.

No request admission, access issuance, IAM grants, or reassignment authority.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from hashlib import sha3_512
import hmac
import json
from typing import Any, Mapping

from tools.eos.legal_operations.domain.legal_practitioner_matter_access_review import (
    LegalPractitionerMatterAccessReview as Review,
    MatterAccessReviewBlocker,
    MatterAccessReviewDecision,
)


def serialize(review: Review, *, include_fingerprint: bool = True) -> dict[str, Any]:
    """Produce the exact original R65 persistence material."""
    result = {
        "schema": review.schema,
        "version": review.version,
        "review_request_id": review.review_request_id,
        "tenant_id": review.tenant_id,
        "case_matter_id": review.case_matter_id,
        "practitioner_principal_id": review.practitioner_principal_id,
        "requested_by_principal_id": review.requested_by_principal_id,
        "decision": MatterAccessReviewDecision(review.decision).value,
        "blockers": [MatterAccessReviewBlocker(v).value for v in review.blockers],
        "reason_reference": review.reason_reference,
        "idempotency_key": review.idempotency_key,
        "recorded_at": review.recorded_at.isoformat(),
    }
    if include_fingerprint:
        result["fingerprint"] = review.fingerprint
    return result


def fingerprint(review: Review) -> str:
    """Compute the original, deterministic SHA3-512 identity."""
    material = serialize(review, include_fingerprint=False)
    encoded = json.dumps(
        material, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return sha3_512(encoded).hexdigest()


def create_review(**values: Any) -> Review:
    """Construct an immutable review with its computed semantic identity."""
    if "fingerprint" in values:
        raise ValueError("R65_CALLER_FINGERPRINT_FORBIDDEN")
    candidate = Review(**{**values, "fingerprint": "0" * 128})
    return replace(candidate, fingerprint=fingerprint(candidate))


def verify_integrity(review: Review) -> bool:
    """Independently verify identity; object construction is not trust."""
    if type(review) is not Review:
        return False
    try:
        return hmac.compare_digest(review.fingerprint, fingerprint(review))
    except (TypeError, ValueError, AttributeError):
        return False


def hydrate(document: Mapping[str, Any]) -> Review:
    """Accept only the original exact schema and verified fingerprint."""
    allowed = {
        "schema", "version", "review_request_id", "tenant_id",
        "case_matter_id", "practitioner_principal_id",
        "requested_by_principal_id", "decision", "blockers",
        "reason_reference", "idempotency_key", "recorded_at",
        "fingerprint",
    }
    values = dict(document)
    values.pop("_id", None)
    if set(values) != allowed:
        raise ValueError("R65_PERSISTED_SHAPE_INVALID")
    if type(values["recorded_at"]) is not str:
        raise ValueError("R65_PERSISTED_TIME_INVALID")
    values["recorded_at"] = datetime.fromisoformat(values["recorded_at"])
    review = Review(**values)
    if not verify_integrity(review):
        raise ValueError("R65_PERSISTED_FINGERPRINT_INVALID")
    return review


__all__ = [
    "serialize", "fingerprint", "create_review",
    "verify_integrity", "hydrate",
]
