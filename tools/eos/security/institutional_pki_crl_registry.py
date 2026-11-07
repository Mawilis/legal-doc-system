"""Durable, revision-guarded CRL anti-rollback projection and append-only events."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import re
from typing import Mapping

from pymongo.collection import Collection


CURRENTNESS_COLLECTION = "wilsy_institutional_pki_crl_currentness"
EVENT_COLLECTION = "wilsy_institutional_pki_crl_events"


class InstitutionalPKICRLRegistryError(RuntimeError):
    """Stable failure at the durable CRL currentness boundary."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class InstitutionalPKICRLCurrentnessRegistry:
    """Persist accepted issuer CRL sequence numbers under a caller-owned transaction."""

    def __init__(self, currentness: Collection, events: Collection) -> None:
        if currentness is None or events is None:
            raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_COLLECTIONS_REQUIRED")
        self._currentness = currentness
        self._events = events

    def ensure_indexes(self) -> None:
        self._currentness.create_index(
            [("issuer_subject_sha256", 1)],
            unique=True,
            name="uq_institutional_pki_crl_issuer",
        )
        self._events.create_index(
            [("event_id", 1)],
            unique=True,
            name="uq_institutional_pki_crl_event_id",
        )
        self._events.create_index(
            [("issuer_subject_sha256", 1), ("crl_number", 1)],
            unique=True,
            name="uq_institutional_pki_crl_issuer_number",
        )

    def observe_bundle(
        self,
        observations: Mapping[str, tuple[int, str]],
        *,
        actor_reference: str,
        observed_at: datetime,
        session: object,
    ) -> int:
        """Advance currentness and append events atomically in the caller's transaction."""
        if session is None:
            raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_CALLER_SESSION_REQUIRED")
        if not isinstance(observations, Mapping) or not observations:
            raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_OBSERVATIONS_REQUIRED")
        if not isinstance(actor_reference, str) or not actor_reference.strip() or len(actor_reference) > 256:
            raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_ACTOR_REFERENCE_INVALID")
        if type(observed_at) is not datetime or observed_at.tzinfo is None or observed_at.utcoffset() is None:
            raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_OBSERVATION_TIME_INVALID")
        instant = observed_at.astimezone(timezone.utc)
        advanced = 0
        for issuer_reference, value in sorted(observations.items()):
            if not isinstance(issuer_reference, str) or not re.fullmatch(r"[0-9a-f]{64}", issuer_reference):
                raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_ISSUER_REFERENCE_INVALID")
            if not isinstance(value, tuple) or len(value) != 2:
                raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_OBSERVATION_INVALID")
            crl_number, crl_fingerprint = value
            if type(crl_number) is not int or crl_number < 1:
                raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_NUMBER_INVALID")
            if not isinstance(crl_fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", crl_fingerprint):
                raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_FINGERPRINT_INVALID")
            current = self._currentness.find_one(
                {"issuer_subject_sha256": issuer_reference},
                session=session,
            )
            previous_number = None
            previous_fingerprint = None
            if current is not None:
                previous_number = current["crl_number"]
                previous_fingerprint = current["crl_fingerprint"]
                if crl_number < previous_number:
                    raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_ROLLBACK_REJECTED")
                if crl_number == previous_number:
                    if crl_fingerprint != previous_fingerprint:
                        raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_NUMBER_REUSE_REJECTED")
                    continue
                revision = current["revision"] + 1
                result = self._currentness.update_one(
                    {
                        "_id": current["_id"],
                        "revision": current["revision"],
                        "crl_number": previous_number,
                        "crl_fingerprint": previous_fingerprint,
                    },
                    {
                        "$set": {
                            "crl_number": crl_number,
                            "crl_fingerprint": crl_fingerprint,
                            "revision": revision,
                            "updated_at": instant,
                        }
                    },
                    session=session,
                )
                if result.modified_count != 1:
                    raise InstitutionalPKICRLRegistryError("INSTITUTIONAL_PKI_CRL_CONCURRENT_REVISION_CONFLICT")
            else:
                revision = 1
                self._currentness.insert_one(
                    {
                        "issuer_subject_sha256": issuer_reference,
                        "crl_number": crl_number,
                        "crl_fingerprint": crl_fingerprint,
                        "revision": revision,
                        "created_at": instant,
                        "updated_at": instant,
                    },
                    session=session,
                )
            event_id = sha256(
                f"{issuer_reference}|{crl_number}|{crl_fingerprint}".encode()
            ).hexdigest()
            self._events.insert_one(
                {
                    "event_id": event_id,
                    "issuer_subject_sha256": issuer_reference,
                    "crl_number": crl_number,
                    "crl_fingerprint": crl_fingerprint,
                    "previous_crl_number": previous_number,
                    "previous_crl_fingerprint": previous_fingerprint,
                    "revision": revision,
                    "event_type": "CRL_CURRENTNESS_ADVANCED",
                    "actor_reference": actor_reference.strip(),
                    "occurred_at": instant,
                },
                session=session,
            )
            advanced += 1
        return advanced
