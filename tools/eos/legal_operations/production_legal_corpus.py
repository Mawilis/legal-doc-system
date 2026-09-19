"""Canonical WILSY OS production legal-corpus draft.

TITLE: WILSY OS Institutional Charter Draft
VERSION: v1.0.0-R1D-B0F-B4-R8A-PRODUCTION-LEGAL-CORPUS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines the first substantive institutional Charter draft as an
         immutable, server-digested legal-document value without provisioning,
         approval, acceptance, signature, or commercial execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/production_legal_corpus.py
COLLABORATION / OWNERSHIP: Legal counsel and governed approval authorities own
                            review and approval; LegalDocumentRegistry owns
                            later durable persistence.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0 authors the sole R8A WILSY OS Institutional Charter draft.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No personal, secret, corporate-registration, or
                            client tenant data is embedded in this draft.
TENANT BOUNDARY: Institutional corpus is platform-level; tenant acceptance is
                 created only by the separate authenticated acceptance service.
AUTHORITY BOUNDARY: Draft governance text only; import and construction have
                    zero persistence side effects and confer no approval.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Final

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-R8A-PRODUCTION-LEGAL-CORPUS"
DOCUMENT_ID: Final[str] = "WILSY-OS-INSTITUTIONAL-CHARTER"
DOCUMENT_VERSION: Final[str] = "1.0.0-DRAFT"
CONTENT_REFERENCE: Final[str] = "wilsy-os://legal/institutional-charter/1.0.0-draft"
JURISDICTION: Final[str] = "ZA"
LOCALE: Final[str] = "en-ZA"
AUTHORING_TIMESTAMP: Final[datetime] = datetime(2026, 9, 17, tzinfo=timezone.utc)

CHARTER_CONTENT: Final[str] = """WILSY OS INSTITUTIONAL CHARTER

1. Purpose and institutional mission

WILSY OS is a governed institutional operating system for organisations and
their authorised people. Its mission is to help institutions coordinate work,
records, evidence, decisions, and operational capability while preserving a
clear boundary between what is observed, what is derived, what is recommended,
and what an authorised human or governed execution system may do. The system is
designed for durable accountability: important state is attributable, scoped,
reviewable, and represented according to its actual authority.

This Charter describes the foundational principles by which WILSY OS is
designed and operated. It is an institutional governance instrument and not a
commercial order, service-level commitment, privacy notice, data-processing
agreement, employment agreement, or grant of signing authority. More specific
documents may define additional requirements within their own approved scope.

2. Sovereignty of institutional truth

WILSY owns the canonical business, legal, lifecycle, evidence, and intelligence
truth represented by its governed authorities. External providers, models,
devices, browsers, payment networks, courier systems, and other integrations
may provide transport, capability, standards, or observations. They do not
become a canonical WILSY authority merely because they produced a response,
status, location, score, token, or recommendation.

Canonical truth is established by the designated WILSY authority for the
relevant domain, persisted through its approved repository, and projected to
clients without silently changing meaning. A projection, cache, user
interface, webhook, model response, or integration callback cannot override a
durable authority. Where an authority is unavailable or a record is ambiguous,
the system must fail closed or expose an explicitly unavailable state rather
than inventing a successful outcome.

3. Human accountability and responsible assistance

People remain accountable for decisions and actions taken under their granted
institutional authority. WILSY OS may assist with retrieval, organisation,
analysis, drafting, explanation, and recommendation, but model output is not
legal advice, legal authority, approval, execution, settlement, or proof of a
real-world event. A model may be wrong, incomplete, stale, or unsuitable for a
particular decision; its output must therefore remain attributable to its
source, bounded by policy, and subject to appropriate human review.

No person may treat a generated answer as a substitute for an approved source,
an authenticated identity, an authorised decision, or durable evidence. AI
assistance must not conceal uncertainty, fabricate provenance, or imply that a
tool invocation performed an action that the underlying authority did not
perform.

4. Separation of observation, inference, recommendation, and execution

WILSY OS maintains the following distinction:

OBSERVED FACT is an input or record received from an identified source.
DERIVED SIGNAL is a reproducible computation over identified inputs.
AI INFERENCE is a model-generated interpretation that may require review.
RECOMMENDATION is proposed next action or explanation, not permission.
AUTHORIZATION is a bounded decision issued by the designated authority.
EXECUTION is a real-world or system mutation performed by its owner.
SETTLEMENT is a separately evidenced final financial state.

None of these states may be silently collapsed into another. A location, photo,
signature image, timestamp, device assertion, provider status, or courier
event is evidence to be evaluated; it is not self-authenticating legal truth.
An attempt is not service, service is not a return, a return is not an invoice,
and an invoice is not payment or settlement.

5. Tenant isolation and stewardship

Each tenant and organisation is a distinct institutional scope. Access,
queries, mutations, projections, evidence, and replay reconciliation must
carry the authenticated tenant boundary unless an explicitly governed platform
operation applies. Absence in one tenant must not disclose the existence or
state of another tenant. Identity, membership, role, permission, and district
or jurisdiction authority are independently validated rather than inferred
from a convenient label.

WILSY OS treats information as entrusted institutional data. Collection,
retention, projection, export, and deletion decisions must be limited to a
legitimate governed purpose, minimise unnecessary personal information, and
preserve an auditable record of material authority decisions. Secrets and
credentials are configuration material, not Charter content.

6. Identity and authority

Authentication establishes who is present; it does not by itself establish
every permission or authority needed for an action. Authorisation is evaluated
for the authenticated principal, tenant, operation, resource, role, and any
additional assignment required by the domain. A platform administrator,
superuser, or tenant owner is not automatically an authorised signatory, legal
representative, financial approver, or execution operator.

An acceptance or acknowledgement attributable to a user is not an organisation
signature and does not bind an organisation. Corporate, commercial, legal, and
financial authority requires its own approved contract, assignment, or execution
boundary. No text in this draft creates such an authority.

7. Evidence integrity and forensic posture

Material records should be canonicalised deterministically, bound to their
semantic source fields, and protected by immutable or append-only persistence
where the domain requires it. Cryptographic fingerprints such as SHA3-512 are
integrity evidence over a defined payload; they do not prove facts outside
that payload. Persistence identifiers, transport metadata, and generated
database keys are implementation details unless an authority explicitly makes
them part of identity.

Replay with the same canonical identity and payload must resolve to the same
durable evidence without creating a contradictory row. Divergent replay,
corrupt hydration, missing provenance, and ambiguous conflict must fail closed.
The absence of evidence is not evidence of completion.

8. Governance and lifecycle

Institutional changes follow a governed lifecycle of discovery, authority
mapping, implementation, review, certification, observation, and controlled
evolution. Lifecycle states have distinct meanings and must not be skipped or
relabelled. Registration is not receipt; allocation is not an attempt; an
attempt is not completion; completion is not a return; a return is not an
invoice; and none of these states is settlement.

Approved versions are selected by the designated server authority. A new
material version succeeds its predecessor without mutating historical truth.
Retirement prevents a version from satisfying a current requirement while
preserving its historical record. Every successor, review decision, and
material correction should remain attributable and chronologically coherent.

9. Security and privacy stewardship

WILSY OS applies defence in depth across identity, transport, storage,
tenant boundaries, least privilege, auditability, integrity checks, and
operational monitoring. Failure states must be structured, bounded, and useful
without exposing secrets or unnecessary personal information. Diagnostic
logging is quiet by default; sensitive values are redacted, and integrity or
save failures are not swallowed.

Security controls support the protection of personal information and
institutional records under applicable privacy and security obligations. This
Charter states principles only; detailed collection, retention, data-subject,
incident, and processing terms belong in the applicable approved policies and
agreements.

10. Responsible AI assistance

AI capabilities must identify their source context, preserve tenant scope,
respect permission boundaries, and expose when information is unavailable or
uncertain. Tool access is capability, not authority. A model must not select a
tenant, elevate a role, approve a document, authorise a payment, certify legal
service, or create an execution result merely because a prompt requests it.

Human review remains responsible for consequential use. Model providers may be
changed or unavailable without changing WILSY's canonical authority model.
Provider outputs, invocation evidence, usage accounting, and recommendations
must remain distinct from the underlying institutional record.

11. Commercial and financial separation

Commercial discussion, quotation, order, billing eligibility, invoice issuance,
payment execution, and settlement are separate authorities. A draft or
acknowledgement cannot create a commercial order, release funds, prove payment,
or mark a balance settled. WILSY OS does not infer financial execution from a
client action, provider response, invoice state, or model recommendation.

Where the existing constitutional architecture requires a financial execution
boundary, Kennel EOS is the exclusive authority for financial execution and
settlement truth. Other WILSY surfaces may request, display, or reconcile
evidence according to their contracts, but may not fabricate bank, provider,
payment-destination, paid, or settled truth.

12. Amendment and version succession

This Charter is versioned institutional text. A governed amendment must identify
the new version, its effective point, the material scope of change, and the
predecessor it supersedes. Historical versions remain immutable records. No
amendment becomes an approved production obligation until the designated
governance and legal review process has completed and the approved version has
been durably recorded.

More specific approved documents may refine a subject without silently
overriding this Charter's authority separations. If documents conflict, the
conflict is surfaced for governed resolution; a client or model may not choose
the result by inference.

13. Draft status and institutional boundary

This source artifact is the first WILSY OS Institutional Charter draft. It is
intentionally marked DRAFT_REVIEW_REQUIRED. It has not been approved, accepted,
signed, or made organisation-binding. Importing or constructing this value does
not provision a production document, create review or approval evidence, create
acceptance evidence, grant signatory authority, or create a commercial or
financial obligation. Those outcomes require their separate authenticated,
governed, and durable authorities.
"""


INSTITUTIONAL_CHARTER_DRAFT: Final[LegalDocumentVersion] = LegalDocumentVersion(
    document_id=DOCUMENT_ID,
    agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
    version=DOCUMENT_VERSION,
    title="WILSY OS Institutional Charter",
    jurisdiction=JURISDICTION,
    locale=LOCALE,
    effective_from=AUTHORING_TIMESTAMP,
    status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
    content_reference=CONTENT_REFERENCE,
    content=CHARTER_CONTENT,
    sha3_512=canonical_document_digest(CHARTER_CONTENT, CONTENT_REFERENCE),
    created_at=AUTHORING_TIMESTAMP,
    supersedes_document_id=None,
)


def get_institutional_charter_draft() -> LegalDocumentVersion:
    """Return the immutable Charter draft without persistence or authority changes."""
    return INSTITUTIONAL_CHARTER_DRAFT


__all__ = [
    "AUTHORING_TIMESTAMP",
    "CHARTER_CONTENT",
    "CONTENT_REFERENCE",
    "DOCUMENT_ID",
    "DOCUMENT_VERSION",
    "INSTITUTIONAL_CHARTER_DRAFT",
    "JURISDICTION",
    "LOCALE",
    "VERSION",
    "get_institutional_charter_draft",
]


# ARTIFACT: production_legal_corpus.py
# VERSION: v1.0.0-R1D-B0F-B4-R8A-PRODUCTION-LEGAL-CORPUS
# AUTHORITY BOUNDARY: draft institutional Charter text and immutable value only
# TENANT POSTURE: platform corpus draft; no tenant acceptance or binding truth
# FAIL-CLOSED POSTURE: draft remains review-required and cannot imply approval
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
