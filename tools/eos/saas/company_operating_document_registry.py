"""TITLE: WILSY OS Company Operating Document Revision Registry.
VERSION: v1.1.1-FOUNDER-CURRENTNESS-UNAVAILABLE-DENIAL
AUTHORITY: Immutable company-document persistence and durable command replay.
EPITOME: Preserve revision lineage and independent publication evidence in
caller-owned Mongo transactions; never turn drafts into official policy.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/company_operating_document_registry.py
COLLABORATION / OWNERSHIP: Pure company_operating_document domain owns lifecycle;
HTTP owns current IAM and whole-transaction retry. Explicit operators/test
fixtures own index provisioning; ordinary reads never create indexes or data.
CERTIFICATION / UPDATE DATE: 2026-11-13
CHANGELOG: v1.1.1-FOUNDER-CURRENTNESS-UNAVAILABLE-DENIAL
translates durable Founder currentness/repository errors to a fail-closed
source-unavailable result without appending a revision or receipt.
CHANGELOG: v1.1.0-FOUNDER-STRATEGY-SOURCE-VERIFIED-RATIFICATION
adds distinct Founder-only create/submit/ratify actions, rechecking immutable
designation and active principal/tenant/capacity/IAM within the caller's
source transaction. Normal publication still denies self-approval.
CHANGELOG: v1.0.0-IMMUTABLE-COMPANY-DOCUMENT-REGISTRY adds bounded immutable
history, SHA3-512 lineage, exact command receipts and explicit index assurance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No logging, token storage, generic document upload,
financial mutation, generated content or in-place revision changes.
TENANT BOUNDARY: Exact canonical WILSY company tenant on every lookup and write.
AUTHORITY BOUNDARY: Caller must authorize each actor; this registry grants no
role, approval permission or publication privilege. Pure validated absence is
not-yet-published; persistence/integrity failures are never empty results.
TRANSACTION BOUNDARY: Active caller-owned session required on every data path.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime
from hmac import compare_digest
from pymongo.errors import PyMongoError
from typing import Any, Final, Mapping

from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.auth.founder_institutional_designation import (
    read_founder_designation, FounderDesignationRejected,
)
from tools.eos.saas.domain.company_operating_document import (
    CompanyDocumentClass, CompanyDocumentError, CompanyDocumentSection,
    CompanyDocumentState, CompanyOperatingDocumentRevision, instant, semantic_fingerprint,
    FOUNDER_RATIFICATION_REFERENCE,
)

VERSION: Final = "v1.1.1-FOUNDER-CURRENTNESS-UNAVAILABLE-DENIAL"
REVISION_COLLECTION: Final = "company_operating_document_revisions"
COMMAND_COLLECTION: Final = "company_operating_document_commands"
MAX_REVISIONS: Final = 1000
REVISION_INDEX: Final = "company_operating_document_revision_unique"
PUBLICATION_INDEX: Final = "company_operating_document_published_version_unique"
COMMAND_INDEX: Final = "company_operating_document_command_unique"


class CompanyOperatingDocumentRegistry:
    """Append-only registry with caller-owned transactions and no IAM authority.

    Indexed commands are durable exact replay. Reads are bounded and validate
    every revision; Mongo/transient errors deliberately propagate so the HTTP
    owner can retry the whole transaction from fresh state.
    """

    def __init__(self, database: Any) -> None:
        self.database = database
        self.revisions = database[REVISION_COLLECTION]
        self.commands = database[COMMAND_COLLECTION]

    def provision_indexes(self) -> None:
        """Provision declared unique indexes only under explicit operator authority.

        This is an administrative mutation, never called by ordinary HTTP reads
        or commands. Disposable certification invokes it on its owned database.
        """
        self.revisions.create_index(
            [("tenant_id", 1), ("classification", 1), ("revision", 1)],
            unique=True, name=REVISION_INDEX,
        )
        self.revisions.create_index(
            [("tenant_id", 1), ("classification", 1), ("document_version", 1)],
            unique=True, partialFilterExpression={"state": "PUBLISHED"}, name=PUBLICATION_INDEX,
        )
        self.commands.create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True, name=COMMAND_INDEX)

    def require_command_indexes(self) -> None:
        """Validate required write arbitration; never silently provision indexes."""
        revisions = self.revisions.index_information()
        commands = self.commands.index_information()
        expected = (
            (revisions, REVISION_INDEX, [("tenant_id", 1), ("classification", 1), ("revision", 1)]),
            (revisions, PUBLICATION_INDEX, [("tenant_id", 1), ("classification", 1), ("document_version", 1)]),
            (commands, COMMAND_INDEX, [("tenant_id", 1), ("idempotency_key", 1)]),
        )
        for actual, name, keys in expected:
            if actual.get(name, {}).get("unique") is not True or actual[name].get("key") != keys:
                raise CompanyDocumentError("COMPANY_DOCUMENT_INDEX_PROVISIONING_REQUIRED")
        if revisions[PUBLICATION_INDEX].get("partialFilterExpression") != {"state": "PUBLISHED"}:
            raise CompanyDocumentError("COMPANY_DOCUMENT_INDEX_PROVISIONING_REQUIRED")

    @staticmethod
    def _scope(tenant_id: str, classification: CompanyDocumentClass, session: Any) -> None:
        if tenant_id != WILSY_COMPANY_TENANT_ID or not isinstance(classification, CompanyDocumentClass):
            raise CompanyDocumentError("COMPANY_DOCUMENT_TENANT_DENIED")
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise CompanyDocumentError("COMPANY_DOCUMENT_CALLER_TRANSACTION_REQUIRED")

    def history(self, tenant_id: str, classification: CompanyDocumentClass, *, session: Any) -> tuple[CompanyOperatingDocumentRevision, ...]:
        """Read exact-company immutable history with full digest/lineage validation.

        At most 1000 revisions per classification are admitted. Excess history
        fails explicitly instead of presenting a partial or fabricated latest
        policy. No read, even lawful absence, provisions indexes or writes data.
        """
        self._scope(tenant_id, classification, session)
        rows = list(self.revisions.find(
            {"tenant_id": tenant_id, "classification": classification.value}, session=session,
        ).sort("revision", 1).limit(MAX_REVISIONS + 1).max_time_ms(5000))
        if len(rows) > MAX_REVISIONS:
            raise CompanyDocumentError("COMPANY_DOCUMENT_HISTORY_LIMIT_REACHED")
        result = tuple(CompanyOperatingDocumentRevision.from_dict(row) for row in rows)
        previous = None
        for number, revision in enumerate(result, start=1):
            if revision.tenant_id != tenant_id or revision.classification is not classification or revision.revision != number:
                raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
            if previous is not None and (
                revision.previous_fingerprint != previous.fingerprint
                or revision.recorded_at < previous.recorded_at
            ):
                raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
            if previous is None and revision.state is not CompanyDocumentState.DRAFT:
                raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
            if previous is not None:
                observed_at = datetime.fromisoformat(revision.recorded_at)
                if revision.state is CompanyDocumentState.SUBMITTED:
                    if previous.state is not CompanyDocumentState.DRAFT or revision.author_principal_id != previous.author_principal_id:
                        raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
                    expected = previous.submit(revision.author_principal_id, observed_at)
                    if revision != expected:
                        raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
                elif revision.state is CompanyDocumentState.PUBLISHED:
                    if previous.state is not CompanyDocumentState.SUBMITTED:
                        raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
                    if revision.approved_by_principal_id is None or revision.approval_reference is None or revision.effective_from is None:
                        raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
                    expected = previous.publish(revision.approved_by_principal_id, revision.approval_reference,
                                                revision.effective_from, observed_at)
                    if revision != expected:
                        raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
                elif previous.state is not CompanyDocumentState.PUBLISHED and revision.author_principal_id != previous.author_principal_id:
                    raise CompanyDocumentError("COMPANY_DOCUMENT_LINEAGE_INVALID")
            previous = revision
        return result

    def current(self, tenant_id: str, classification: CompanyDocumentClass, *,
                session: Any, now: datetime, review: bool = False) -> CompanyOperatingDocumentRevision | None:
        """Select current effective publication, or privileged latest review state.

        Caller must independently authorize review before setting review=True.
        Ordinary readers never receive draft/submitted content or future versions.
        """
        history = self.history(tenant_id, classification, session=session)
        if review:
            return history[-1] if history else None
        as_of = instant(now)
        return next((item for item in reversed(history)
                     if item.state is CompanyDocumentState.PUBLISHED
                     and item.effective_from is not None and item.effective_from <= as_of), None)

    def command(self, tenant_id: str, classification: CompanyDocumentClass, *, actor_id: str,
                action: str, payload: Mapping[str, Any], expected_revision: int,
                idempotency_key: str, now: datetime, session: Any) -> CompanyOperatingDocumentRevision:
        """Append one authorized lifecycle command or replay its exact receipt.

        The HTTP owner supplies an independently authorized actor. Same tenant,
        key and canonical actor/action/payload fingerprint yields exact replay;
        divergence fails closed. A stale expected revision never overwrites
        truth. Source data and receipt commit atomically in the caller session.
        """
        self._scope(tenant_id, classification, session)
        if not isinstance(actor_id, str) or not actor_id or actor_id != actor_id.strip():
            raise CompanyDocumentError("COMPANY_DOCUMENT_ACTOR_INVALID")
        if not isinstance(idempotency_key, str) or not idempotency_key or len(idempotency_key) > 160 or idempotency_key != idempotency_key.strip():
            raise CompanyDocumentError("COMPANY_DOCUMENT_IDEMPOTENCY_REQUIRED")
        if type(expected_revision) is not int or expected_revision < 0:
            raise CompanyDocumentError("COMPANY_DOCUMENT_EXPECTED_REVISION_INVALID")
        founder_actions = frozenset({"FOUNDER_CREATE_DRAFT", "FOUNDER_SUBMIT", "FOUNDER_RATIFY"})
        if action in founder_actions:
            if classification is not CompanyDocumentClass.STRATEGY:
                raise CompanyDocumentError("COMPANY_DOCUMENT_FOUNDER_STRATEGY_ONLY")
            try:
                evidence = read_founder_designation(
                    principal_id=actor_id, tenant_id=tenant_id,
                    database=self.database, session=session,
                )
            except (FounderDesignationRejected, RuntimeError, PyMongoError) as error:
                raise CompanyDocumentError("COMPANY_DOCUMENT_FOUNDER_SOURCE_UNAVAILABLE") from error
            if evidence is None or evidence.get("state") != "ACTIVE":
                raise CompanyDocumentError("COMPANY_DOCUMENT_FOUNDER_AUTHORITY_DENIED")
        expected_fields = {"CREATE_DRAFT": {"title", "document_version", "sections"},
                           "SUBMIT": set(), "PUBLISH": {"approval_reference", "effective_from"},
                           "FOUNDER_CREATE_DRAFT": {"title", "document_version", "sections"},
                           "FOUNDER_SUBMIT": set(), "FOUNDER_RATIFY": {"effective_from"}}
        if action not in expected_fields or set(payload) != expected_fields[action]:
            raise CompanyDocumentError("COMPANY_DOCUMENT_COMMAND_INVALID")
        canonical_payload = dict(payload)
        if action in {"PUBLISH", "FOUNDER_RATIFY"}:
            canonical_payload["effective_from"] = instant(canonical_payload["effective_from"])
        if action == "PUBLISH" and canonical_payload["approval_reference"] == FOUNDER_RATIFICATION_REFERENCE:
            raise CompanyDocumentError("COMPANY_DOCUMENT_FOUNDER_RATIFICATION_INVALID")
        request_fingerprint = semantic_fingerprint({
            "tenant_id": tenant_id, "classification": classification.value,
            "actor_id": actor_id, "action": action, "payload": canonical_payload,
            "expected_revision": expected_revision,
        })
        history = self.history(tenant_id, classification, session=session)
        receipt = self.commands.find_one({"tenant_id": tenant_id, "idempotency_key": idempotency_key}, session=session)
        if receipt is not None:
            existing = dict(receipt)
            existing.pop("_id", None)
            digest = existing.pop("fingerprint", None)
            if not isinstance(digest, str) or not compare_digest(digest, semantic_fingerprint(existing)):
                raise CompanyDocumentError("COMPANY_DOCUMENT_RECEIPT_INTEGRITY_INVALID")
            if existing.get("command_fingerprint") != request_fingerprint:
                raise CompanyDocumentError("COMPANY_DOCUMENT_IDEMPOTENCY_CONFLICT")
            match = next((item for item in history if item.revision == existing.get("response_revision")
                          and item.fingerprint == existing.get("response_fingerprint")), None)
            if match is None:
                raise CompanyDocumentError("COMPANY_DOCUMENT_RECEIPT_READBACK_INVALID")
            return match
        latest = history[-1] if history else None
        if expected_revision != (latest.revision if latest else 0):
            raise CompanyDocumentError("COMPANY_DOCUMENT_REVISION_CONFLICT")
        if len(history) >= MAX_REVISIONS:
            raise CompanyDocumentError("COMPANY_DOCUMENT_HISTORY_LIMIT_REACHED")
        if action in {"CREATE_DRAFT", "FOUNDER_CREATE_DRAFT"}:
            if latest is not None and latest.state is not CompanyDocumentState.PUBLISHED and latest.author_principal_id != actor_id:
                raise CompanyDocumentError("COMPANY_DOCUMENT_DRAFT_OWNER_REQUIRED")
            if any(item.state is CompanyDocumentState.PUBLISHED and item.document_version == payload["document_version"] for item in history):
                raise CompanyDocumentError("COMPANY_DOCUMENT_VERSION_ALREADY_PUBLISHED")
            try:
                sections = tuple(CompanyDocumentSection(**section) for section in payload["sections"])
            except (TypeError, KeyError) as error:
                raise CompanyDocumentError("COMPANY_DOCUMENT_SECTIONS_INVALID") from error
            record = CompanyOperatingDocumentRevision(
                tenant_id=tenant_id, classification=classification, document_version=payload["document_version"],
                revision=expected_revision + 1, state=CompanyDocumentState.DRAFT, title=payload["title"],
                sections=sections, author_principal_id=actor_id, recorded_at=instant(now),
                previous_fingerprint=latest.fingerprint if latest else None,
            )
        elif latest is None:
            raise CompanyDocumentError("COMPANY_DOCUMENT_REVISION_CONFLICT")
        elif action in {"SUBMIT", "FOUNDER_SUBMIT"}:
            record = latest.submit(actor_id, now)
        elif action == "FOUNDER_RATIFY":
            if latest.author_principal_id != actor_id:
                raise CompanyDocumentError("COMPANY_DOCUMENT_FOUNDER_AUTHOR_REQUIRED")
            record = latest.publish(actor_id, FOUNDER_RATIFICATION_REFERENCE,
                                    canonical_payload["effective_from"], now)
        else:
            if latest.author_principal_id == actor_id:
                raise CompanyDocumentError("COMPANY_DOCUMENT_INDEPENDENT_APPROVER_REQUIRED")
            record = latest.publish(actor_id, canonical_payload["approval_reference"],
                                    canonical_payload["effective_from"], now)
        if latest is not None and record.recorded_at < latest.recorded_at:
            raise CompanyDocumentError("COMPANY_DOCUMENT_TIME_INVALID")
        self.revisions.insert_one(record.to_dict(), session=session)
        receipt_payload = {
            "schema": "WILSY-COMPANY-OPERATING-DOCUMENT-COMMAND/V1", "tenant_id": tenant_id,
            "classification": classification.value, "idempotency_key": idempotency_key,
            "command_fingerprint": request_fingerprint, "response_revision": record.revision,
            "response_fingerprint": record.fingerprint,
        }
        self.commands.insert_one({**receipt_payload, "fingerprint": semantic_fingerprint(receipt_payload)}, session=session)
        return record


# ARTIFACT: company_operating_document_registry.py
# VERSION: v1.1.1-FOUNDER-CURRENTNESS-UNAVAILABLE-DENIAL
# AUTHORITY BOUNDARY: Append-only persistence/replay only; caller owns IAM.
# TENANT POSTURE: Exact canonical company tenant on every operation.
# FAIL-CLOSED POSTURE: Missing index, transaction, lineage or receipt truth rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
