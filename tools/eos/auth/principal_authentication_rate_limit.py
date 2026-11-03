"""WILSY OS durable rate gate for tenant-neutral global principal authentication.

TITLE: WILSY OS Global Principal Authentication Rate Limit
VERSION: v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT
AUTHORITY: Request-density admission only for global principal password authentication.
EPITOME: Applies independent fixed-window budgets to normalized-email and
         transport-peer digests before global credential verification.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_authentication_rate_limit.py
COLLABORATION / OWNERSHIP:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd).
    Engineering collaborator: WILSY OS Core Systems Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT introduces atomic Mongo fixed-window
    counters for global email and transport-peer digests, bounded admission,
    TTL cleanup metadata and fail-closed persistence handling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    Raw email addresses and IP addresses are never persisted. Bucket identity
    uses SHA3-512 digests, deterministic canonical serialization and explicit
    dimensions. Forwarded headers are not accepted; the caller must supply the
    ASGI transport peer address, not an untrusted X-Forwarded-For value.
TENANT BOUNDARY:
    Global authentication is tenant-neutral. No tenant ID, alias, workspace,
    membership, role or permission is accepted or persisted by this gate.
AUTHORITY BOUNDARY:
    This module owns request-density admission only. It does not authenticate
    credentials, reveal account existence, create principals, issue challenges,
    manage MFA, authorize memberships, or issue sessions/tokens.
TRANSACTION BOUNDARY:
    Each dimension is one atomic Mongo find/update. The gate owns no session,
    transaction, retry, or index-creation lifecycle. Indexes are installed by
    canonical EOS application startup only.
FINANCIAL AUTHORITY BOUNDARY:
    No financial authority. Kennel EOS remains the exclusive financial execution
    authority.
"""

from __future__ import annotations

import hashlib
import ipaddress
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.principal_credential import normalize_principal_email


VERSION = "v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT"
COLLECTION = "principal_authentication_rate_limits"
DEFAULT_WINDOW = timedelta(minutes=15)
DEFAULT_EMAIL_MAX_REQUESTS = 5
DEFAULT_SOURCE_MAX_REQUESTS = 30


class PrincipalAuthenticationRateLimitError(RuntimeError):
    """Base fail-closed error for global-principal authentication throttling."""


class PrincipalAuthenticationRateLimited(PrincipalAuthenticationRateLimitError):
    """The normalized email or transport-peer request budget is exhausted."""


class PrincipalAuthenticationRateLimitUnavailable(PrincipalAuthenticationRateLimitError):
    """The durable rate-limit authority is unavailable or corrupt."""


def _utc(value: datetime) -> datetime:
    """Require one timezone-aware UTC observation instant."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _canonical_source_address(value: object) -> str:
    """Canonicalize the direct ASGI transport peer without proxy-header inference."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_SOURCE_INVALID")
    try:
        return ipaddress.ip_address(value).compressed
    except ValueError as error:
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_SOURCE_INVALID") from error


def _window_start(observed_at: datetime, window: timedelta) -> datetime:
    """Floor one UTC instant to a deterministic fixed-window boundary."""
    seconds = int(window.total_seconds())
    epoch_seconds = int(observed_at.timestamp())
    return datetime.fromtimestamp(epoch_seconds - epoch_seconds % seconds, tz=timezone.utc)


def _digest(scope: str, subject: str, bucket_start: datetime) -> tuple[str, str]:
    """Return opaque subject and deterministic bucket digests."""
    subject_digest = hashlib.sha3_512(subject.encode("utf-8")).hexdigest()
    canonical = f"wilsy-global-principal-auth-rate-v1|{scope}|{subject_digest}|{bucket_start.isoformat()}"
    bucket_id = hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()
    return subject_digest, bucket_id


def _target(collection: Any | None) -> Any:
    """Resolve injected collection or the canonical EOS database lazily."""
    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _persisted_utc(value: object) -> datetime:
    """Normalize BSON naive UTC or already-aware UTC timestamps; reject other shapes."""
    if not isinstance(value, datetime):
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_STATE_INVALID")
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    if value.utcoffset() != timedelta(0):
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_STATE_INVALID")
    return value.astimezone(timezone.utc)


class PrincipalAuthenticationRateLimit:
    """Durable dual-dimension rate gate for tenant-neutral global credential attempts.

    The email budget prevents distributed guessing against one account. The
    transport-peer budget limits one source from spraying many accounts. The
    caller supplies the direct ASGI peer address; proxy headers are excluded.
    Both counters are incremented before admission is decided, so blocked
    attempts remain durable within the active window.
    """

    def __init__(
        self,
        collection: Any | None = None,
        *,
        window: timedelta = DEFAULT_WINDOW,
        email_max_requests: int = DEFAULT_EMAIL_MAX_REQUESTS,
        source_max_requests: int = DEFAULT_SOURCE_MAX_REQUESTS,
    ) -> None:
        """Bind one collection and validated fixed-window policy."""
        if not isinstance(window, timedelta) or not timedelta(minutes=1) <= window <= timedelta(hours=24):
            raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_WINDOW_INVALID")
        for value in (email_max_requests, source_max_requests):
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
                raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_LIMIT_INVALID")
        self._collection = collection
        self._window = window
        self._email_max_requests = email_max_requests
        self._source_max_requests = source_max_requests

    def ensure_indexes(self) -> None:
        """Create lookup and TTL indexes during canonical application startup only."""
        source = _target(self._collection)
        try:
            source.create_index(
                [("scope", ASCENDING), ("subject_digest", ASCENDING), ("bucket_start", ASCENDING)],
                unique=True,
                name="principal_auth_rate_scope_subject_window_unique",
            )
            source.create_index(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=0,
                name="principal_auth_rate_expiry_ttl",
            )
        except PyMongoError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_INDEX_CREATION_FAILED"
            ) from error

    def _consume(
        self,
        *,
        scope: str,
        subject: str,
        observed_at: datetime,
        maximum: int,
    ) -> int:
        """Atomically increment one opaque dimension bucket and validate its persisted identity."""
        start = _window_start(observed_at, self._window)
        subject_digest, bucket_id = _digest(scope, subject, start)
        expires_at = start + self._window + timedelta(minutes=1)
        document = {
            "_id": bucket_id,
            "scope": scope,
            "subject_digest": subject_digest,
            "bucket_start": start,
            "expires_at": expires_at,
        }
        source = _target(self._collection)
        try:
            row = source.find_one_and_update(
                {"_id": bucket_id},
                {
                    "$setOnInsert": document,
                    "$inc": {"count": 1},
                },
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError:
            try:
                row = source.find_one_and_update(
                    {"_id": bucket_id},
                    {"$inc": {"count": 1}},
                    upsert=False,
                    return_document=ReturnDocument.AFTER,
                )
            except PyMongoError as error:
                raise PrincipalAuthenticationRateLimitUnavailable(
                    "PRINCIPAL_AUTH_RATE_WRITE_FAILED"
                ) from error
        except PyMongoError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_WRITE_FAILED"
            ) from error
        if not isinstance(row, dict):
            raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_STATE_INVALID")
        persisted_start = _persisted_utc(row.get("bucket_start"))
        count = row.get("count")
        if (
            row.get("_id") != bucket_id
            or row.get("scope") != scope
            or row.get("subject_digest") != subject_digest
            or persisted_start != start
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count < 1
        ):
            raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_STATE_MISMATCH")
        return count

    def require_allowed(
        self,
        *,
        email: str,
        source_address: str,
        observed_at: datetime,
    ) -> None:
        """Consume both global rate budgets or reject before credential lookup.

        Email is normalized using the canonical principal credential rule.
        The source address must be the direct ASGI connection peer. No tenant,
        account lookup, credential verifier, membership or role is consulted.
        """
        try:
            normalized_email = normalize_principal_email(email)
        except ValueError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_EMAIL_INVALID"
            ) from error
        source = _canonical_source_address(source_address)
        observed = _utc(observed_at)
        email_count = self._consume(
            scope="EMAIL",
            subject=normalized_email,
            observed_at=observed,
            maximum=self._email_max_requests,
        )
        source_count = self._consume(
            scope="SOURCE",
            subject=source,
            observed_at=observed,
            maximum=self._source_max_requests,
        )
        if email_count > self._email_max_requests or source_count > self._source_max_requests:
            raise PrincipalAuthenticationRateLimited("PRINCIPAL_AUTH_RATE_LIMITED")


__all__ = [
    "VERSION",
    "COLLECTION",
    "DEFAULT_WINDOW",
    "DEFAULT_EMAIL_MAX_REQUESTS",
    "DEFAULT_SOURCE_MAX_REQUESTS",
    "PrincipalAuthenticationRateLimit",
    "PrincipalAuthenticationRateLimitError",
    "PrincipalAuthenticationRateLimited",
    "PrincipalAuthenticationRateLimitUnavailable",
]

# ARTIFACT: principal_authentication_rate_limit.py
# VERSION: v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT
# AUTHORITY BOUNDARY: request-density admission only; no identity or authentication authority
# TENANT POSTURE: tenant-neutral email and transport-peer digest buckets
# FAIL-CLOSED POSTURE: invalid source, unavailable persistence, corrupt counters and exhausted budgets reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
