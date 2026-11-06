"""WILSY OS durable failure throttling for tenant-neutral global principal authentication.

TITLE: WILSY OS Global Principal Authentication Failure Throttle
VERSION: v1.1.0-GLOBAL-PRINCIPAL-FAILURE-THROTTLE
AUTHORITY: Request admission and failed-authentication throttling only.
EPITOME: Records failed credential attempts against opaque normalized-email
         and direct transport-peer buckets; checks admission before credential
         verification and clears the email failure bucket only after success.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_authentication_rate_limit.py
COLLABORATION / OWNERSHIP:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd).
    Engineering collaborator: WILSY OS Core Systems Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.1.0-GLOBAL-PRINCIPAL-FAILURE-THROTTLE changes counters from all-request
    consumption to failure-only recording, checks without mutation, resets
    only the authenticated email bucket after success, and returns bounded
    retry-after guidance. This avoids counting successful logins as failures.
    v1.0.0-GLOBAL-PRINCIPAL-AUTH-RATE-LIMIT introduced opaque dual-dimension
    fixed-window counters and startup-owned indexes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    Raw email addresses and IP addresses are never persisted. Bucket identity
    uses SHA3-512 digests and deterministic canonical serialization. Forwarded
    headers are not accepted; callers supply the direct ASGI transport peer.
TENANT BOUNDARY:
    Global authentication is tenant-neutral. No tenant, workspace, membership,
    role or permission is accepted or persisted by this throttle.
AUTHORITY BOUNDARY:
    This module does not authenticate credentials, determine account existence,
    create principals, issue challenges, manage MFA, authorize memberships,
    issue sessions/tokens, send notifications, or declare a security incident.
TRANSACTION BOUNDARY:
    Each bucket mutation is one atomic Mongo update. Indexes are installed by
    canonical EOS startup. The caller owns HTTP response, event/outbox routing,
    and any larger transaction.
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


VERSION = "v1.1.0-GLOBAL-PRINCIPAL-FAILURE-THROTTLE"
COLLECTION = "principal_authentication_rate_limits"
DEFAULT_WINDOW = timedelta(minutes=15)
DEFAULT_EMAIL_MAX_FAILURES = 5
DEFAULT_SOURCE_MAX_FAILURES = 30


class PrincipalAuthenticationRateLimitError(RuntimeError):
    """Base fail-closed error for global-principal authentication throttling."""


class PrincipalAuthenticationRateLimited(PrincipalAuthenticationRateLimitError):
    """The email or source failure budget is exhausted for the active window.

    retry_after_seconds is bounded by the remaining fixed-window lifetime.
    The value is transport guidance only; it does not expose account existence.
    """

    def __init__(self, retry_after_seconds: int) -> None:
        """Create a bounded retry response without exposing the affected dimension."""
        self.retry_after_seconds = max(1, min(int(retry_after_seconds), 86400))
        super().__init__("PRINCIPAL_AUTH_RATE_LIMITED")


class PrincipalAuthenticationRateLimitUnavailable(PrincipalAuthenticationRateLimitError):
    """The durable rate-limit authority is unavailable or corrupt."""


def _utc(value: datetime) -> datetime:
    """Require one timezone-aware UTC observation instant."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _canonical_source_address(value: object) -> str:
    """Canonicalize the direct ASGI transport peer without proxy-header inference."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise PrincipalAuthenticationRateLimitUnavailable("PRINCIPAL_AUTH_RATE_SOURCE_INVALID")
    try:
        return ipaddress.ip_address(value).compressed
    except ValueError as error:
        raise PrincipalAuthenticationRateLimitUnavailable(
            "PRINCIPAL_AUTH_RATE_SOURCE_INVALID"
        ) from error


def _window_start(observed_at: datetime, window: timedelta) -> datetime:
    """Floor one UTC instant to a deterministic fixed-window boundary."""
    seconds = int(window.total_seconds())
    epoch_seconds = int(observed_at.timestamp())
    return datetime.fromtimestamp(epoch_seconds - epoch_seconds % seconds, tz=timezone.utc)


def _digest(scope: str, subject: str, bucket_start: datetime) -> tuple[str, str]:
    """Return opaque subject and deterministic bucket digests."""
    subject_digest = hashlib.sha3_512(subject.encode("utf-8")).hexdigest()
    canonical = (
        f"wilsy-global-principal-auth-rate-v1|{scope}|"
        f"{subject_digest}|{bucket_start.isoformat()}"
    )
    bucket_id = hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()
    return subject_digest, bucket_id


def _target(collection: Any | None) -> Any:
    """Resolve injected collection or the canonical EOS database lazily."""
    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise PrincipalAuthenticationRateLimitUnavailable(
            "PRINCIPAL_AUTH_RATE_DATABASE_UNAVAILABLE"
        )
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
    """Durable failure-only throttle for global principal credential attempts.

    Call require_allowed before credential verification. Call record_failure
    only after a credential failure, including a syntactically valid but
    unregistered email. Call record_success only after successful credential
    verification; it clears that normalized email's failure bucket but leaves
    the source bucket intact to preserve password-spray protection.

    The email bucket protects one principal from distributed guessing. The
    source bucket limits one direct transport peer across many email addresses.
    Unknown and known email addresses receive the same admission behavior.
    """

    def __init__(
        self,
        collection: Any | None = None,
        *,
        window: timedelta = DEFAULT_WINDOW,
        email_max_failures: int = DEFAULT_EMAIL_MAX_FAILURES,
        source_max_failures: int = DEFAULT_SOURCE_MAX_FAILURES,
    ) -> None:
        """Bind one collection and validated fixed-window failure policy."""
        if (
            not isinstance(window, timedelta)
            or not timedelta(minutes=1) <= window <= timedelta(hours=24)
        ):
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_WINDOW_INVALID"
            )
        for value in (email_max_failures, source_max_failures):
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
                raise PrincipalAuthenticationRateLimitUnavailable(
                    "PRINCIPAL_AUTH_RATE_LIMIT_INVALID"
                )
        self._collection = collection
        self._window = window
        self._email_max_failures = email_max_failures
        self._source_max_failures = source_max_failures

    def ensure_indexes(self) -> None:
        """Create unique bucket and TTL indexes during canonical startup only."""
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

    def _identity(
        self,
        *,
        scope: str,
        subject: str,
        observed_at: datetime,
    ) -> tuple[str, str, datetime]:
        """Derive the exact opaque bucket identity for one dimension."""
        start = _window_start(observed_at, self._window)
        subject_digest, bucket_id = _digest(scope, subject, start)
        return subject_digest, bucket_id, start

    def _read_count(
        self,
        *,
        scope: str,
        subject: str,
        observed_at: datetime,
    ) -> int:
        """Read and validate one bucket without changing its failure count."""
        subject_digest, bucket_id, start = self._identity(
            scope=scope,
            subject=subject,
            observed_at=observed_at,
        )
        try:
            row = _target(self._collection).find_one({"_id": bucket_id})
        except PyMongoError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_READ_FAILED"
            ) from error
        if row is None:
            return 0
        count = row.get("count")
        if (
            row.get("_id") != bucket_id
            or row.get("scope") != scope
            or row.get("subject_digest") != subject_digest
            or _persisted_utc(row.get("bucket_start")) != start
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count < 0
        ):
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_STATE_MISMATCH"
            )
        return count

    def _record_failure_dimension(
        self,
        *,
        scope: str,
        subject: str,
        observed_at: datetime,
    ) -> int:
        """Atomically increment one opaque failure bucket."""
        subject_digest, bucket_id, start = self._identity(
            scope=scope,
            subject=subject,
            observed_at=observed_at,
        )
        document = {
            "_id": bucket_id,
            "scope": scope,
            "subject_digest": subject_digest,
            "bucket_start": start,
            "expires_at": start + self._window + timedelta(minutes=1),
        }
        source = _target(self._collection)
        try:
            row = source.find_one_and_update(
                {"_id": bucket_id},
                {"$setOnInsert": document, "$inc": {"count": 1}},
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
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_STATE_INVALID"
            )
        count = row.get("count")
        if (
            row.get("_id") != bucket_id
            or row.get("scope") != scope
            or row.get("subject_digest") != subject_digest
            or _persisted_utc(row.get("bucket_start")) != start
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count < 1
        ):
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_STATE_MISMATCH"
            )
        return count

    def require_allowed(
        self,
        *,
        email: str,
        source_address: str,
        observed_at: datetime,
    ) -> None:
        """Reject exhausted email/source budgets without counting a successful attempt.

        The caller must invoke record_failure after failed credential
        verification. A valid password attempt is not counted as a failure.
        retry_after_seconds is identical in meaning regardless of which
        dimension exhausted its budget.
        """
        try:
            normalized_email = normalize_principal_email(email)
        except ValueError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_EMAIL_INVALID"
            ) from error
        source = _canonical_source_address(source_address)
        observed = _utc(observed_at)
        email_count = self._read_count(
            scope="EMAIL_FAILURE",
            subject=normalized_email,
            observed_at=observed,
        )
        source_count = self._read_count(
            scope="SOURCE_FAILURE",
            subject=source,
            observed_at=observed,
        )
        retry_after = max(
            1,
            int(
                (
                    _window_start(observed, self._window)
                    + self._window
                    - observed
                ).total_seconds()
            ),
        )
        if (
            email_count >= self._email_max_failures
            or source_count >= self._source_max_failures
        ):
            raise PrincipalAuthenticationRateLimited(retry_after)

    def record_failure(
        self,
        *,
        email: str,
        source_address: str,
        observed_at: datetime,
    ) -> tuple[int, int]:
        """Record one failed password attempt against email and source budgets.

        Email is normalized before hashing. Unknown but syntactically valid
        addresses are counted identically to registered addresses. The method
        does not send notifications or reveal whether a principal exists.
        """
        try:
            normalized_email = normalize_principal_email(email)
        except ValueError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_EMAIL_INVALID"
            ) from error
        source = _canonical_source_address(source_address)
        observed = _utc(observed_at)
        email_count = self._record_failure_dimension(
            scope="EMAIL_FAILURE",
            subject=normalized_email,
            observed_at=observed,
        )
        source_count = self._record_failure_dimension(
            scope="SOURCE_FAILURE",
            subject=source,
            observed_at=observed,
        )
        return email_count, source_count

    def record_success(self, *, email: str, observed_at: datetime) -> None:
        """Clear only the successful normalized email's current failure bucket.

        Source-wide failures are retained because a source may still be spraying
        other accounts. This method must be called only after credential success.
        """
        try:
            normalized_email = normalize_principal_email(email)
        except ValueError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_EMAIL_INVALID"
            ) from error
        observed = _utc(observed_at)
        _subject_digest, bucket_id, _start = self._identity(
            scope="EMAIL_FAILURE",
            subject=normalized_email,
            observed_at=observed,
        )
        try:
            _target(self._collection).delete_one({"_id": bucket_id})
        except PyMongoError as error:
            raise PrincipalAuthenticationRateLimitUnavailable(
                "PRINCIPAL_AUTH_RATE_RESET_FAILED"
            ) from error


__all__ = [
    "VERSION",
    "COLLECTION",
    "DEFAULT_WINDOW",
    "DEFAULT_EMAIL_MAX_FAILURES",
    "DEFAULT_SOURCE_MAX_FAILURES",
    "PrincipalAuthenticationRateLimit",
    "PrincipalAuthenticationRateLimitError",
    "PrincipalAuthenticationRateLimited",
    "PrincipalAuthenticationRateLimitUnavailable",
]

# ARTIFACT: principal_authentication_rate_limit.py
# VERSION: v1.1.0-GLOBAL-PRINCIPAL-FAILURE-THROTTLE
# AUTHORITY BOUNDARY: failure throttling only; no identity or session authority
# TENANT POSTURE: tenant-neutral normalized-email and source failure buckets
# FAIL-CLOSED POSTURE: corrupt state, unavailable persistence and exhausted budgets reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
