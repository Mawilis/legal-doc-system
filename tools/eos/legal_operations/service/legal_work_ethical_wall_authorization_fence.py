"""G65/G77 shared MongoDB serialization fence for disclosure and revocation.

ENGINEERING PROPOSAL ONLY. This primitive grants no authority and must not be
used to enable disclosure until both call sites and deployment-owned indexes are
reviewed and certified against a replica set.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Final

from pymongo import ASCENDING

_SCOPE_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\Z")
FENCE_COLLECTION: Final[str] = "legal_ethical_wall_authorization_fences"
FENCE_INDEX_FIELDS: Final[tuple[tuple[str, int], ...]] = (
    ("tenant_id", 1),
    ("case_matter_id", 1),
    ("practitioner_principal_id", 1),
    ("policy_id", 1),
)
FENCE_INDEX_NAME: Final[str] = "uq_g65_wall_authorization_fence_scope"


def ensure_fence_index(collection: Any) -> None:
    """Provision the exact unique scope key through deployment-owned startup."""
    if collection is None:
        raise ValueError("G65_AUTHORIZATION_FENCE_COLLECTION_REQUIRED")
    collection.create_index(
        list(FENCE_INDEX_FIELDS),
        name=FENCE_INDEX_NAME,
        unique=True,
    )


class WallFenceUnavailable(PermissionError):
    """Content-free failure: no currentness proof was obtained."""

    def __init__(self, *, retryable: bool = False) -> None:
        self.retryable = retryable
        super().__init__("G65_AUTHORIZATION_FENCE_UNAVAILABLE")


def _scope_id(value: object) -> str:
    if type(value) is not str or _SCOPE_ID.fullmatch(value) is None:
        raise WallFenceUnavailable
    if value.casefold() in {"default", "global", "root", "*"}:
        raise WallFenceUnavailable
    return value


def _active_transaction(session: object) -> None:
    try:
        active = getattr(session, "in_transaction", False)
        active = active() if callable(active) else active
    except Exception as exc:
        raise WallFenceUnavailable from exc
    if active is not True:
        raise WallFenceUnavailable


@dataclass(frozen=True, slots=True)
class WallFenceToken:
    """Non-authorizing proof that this transaction wrote the shared scope fence."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    policy_id: str
    epoch: int


class CanonicalWallAuthorizationFence:
    """Force disclosure and revocation to write the same scope document.

    The deployment MUST provision a unique compound index matching
    FENCE_INDEX_FIELDS before use. Both disclosure and revocation must call
    contend() inside their own active transaction, before reading/updating wall
    evidence. The transaction must include the protected content read, and the
    content must not be returned until that transaction commits. A write conflict
    must abort and retry the WHOLE transaction from its beginning; never continue
    after a failed contend() or retry only the evidence lookup.

    This is a serialization primitive, not an authority decision. It does not
    establish issuer authority, institutional ratification, or policy validity.
    """

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise ValueError("G65_AUTHORIZATION_FENCE_COLLECTION_REQUIRED")
        self._collection = collection

    def contend(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        practitioner_principal_id: str,
        policy_id: str,
        session: object,
    ) -> WallFenceToken:
        """Acquire the same write-conflicting fence from either transaction path."""
        _active_transaction(session)
        tenant = _scope_id(tenant_id)
        matter = _scope_id(case_matter_id)
        principal = _scope_id(practitioner_principal_id)
        policy = _scope_id(policy_id)
        scope = {
            "tenant_id": tenant,
            "case_matter_id": matter,
            "practitioner_principal_id": principal,
            "policy_id": policy,
        }
        try:
            # This is deliberately a write, not a snapshot read. Concurrent
            # disclosure/revocation transactions for this exact scope contend
            # on the same document and MongoDB aborts one conflicting writer.
            result = self._collection.update_one(
                scope,
                {"$inc": {"epoch": 1}, "$setOnInsert": {**scope, "schema_version": 1}},
                upsert=True,
                session=session,
            )
            if result.matched_count != 1 and not result.upserted_id:
                raise WallFenceUnavailable
            current = self._collection.find_one(scope, session=session)
            if type(current) is not dict or type(current.get("epoch")) is not int or current["epoch"] < 1:
                raise WallFenceUnavailable
            if any(current.get(key) != value for key, value in scope.items()):
                raise WallFenceUnavailable
            return WallFenceToken(**scope, epoch=current["epoch"])
        except WallFenceUnavailable:
            raise
        except Exception as exc:
            # Preserve whether Mongo marks this as a transient transaction error.
            # The caller must abort and retry the WHOLE transaction when true.
            retryable = False
            try:
                retryable = bool(
                    getattr(exc, "has_error_label", lambda _label: False)(
                        "TransientTransactionError"
                    )
                ) or getattr(exc, "code", None) in {112, 251}
            except Exception:
                retryable = False
            raise WallFenceUnavailable(retryable=retryable) from exc


__all__ = [
    "FENCE_COLLECTION", "FENCE_INDEX_FIELDS", "FENCE_INDEX_NAME", "ensure_fence_index",
    "WallFenceUnavailable", "WallFenceToken", "CanonicalWallAuthorizationFence",
]
