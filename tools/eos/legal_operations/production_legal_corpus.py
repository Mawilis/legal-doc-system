"""Canonical WILSY OS production legal-corpus draft.

TITLE: WILSY OS Required Platform Legal Corpus Drafts
VERSION: v1.3.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-RUNTIME-CATALOG
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines the first substantive institutional Charter draft as an
         immutable, server-digested legal-document value without provisioning,
         approval, acceptance, signature, or commercial execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/production_legal_corpus.py
COLLABORATION / OWNERSHIP: Legal counsel and governed approval authorities own
                            review and approval; LegalDocumentRegistry owns
                            later durable persistence.
CERTIFICATION / UPDATE DATE: 2026-09-20
CHANGELOG: v1.3.0 preserves all historical and reviewed-successor values and
           adds one pure source-owned eleven-value runtime catalog/resolver;
           no document value, digest, authority, or persistence semantics change.
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


VERSION: Final[str] = "v1.3.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-RUNTIME-CATALOG"
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


DRAFT_AUTHORING_TIMESTAMP: Final[datetime] = datetime(2026, 9, 19, tzinfo=timezone.utc)
REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP: Final[datetime] = datetime(
    2026, 9, 19, 12, 0, tzinfo=timezone.utc
)

USER_TERMS_CONTENT: Final[str] = """WILSY OS USER TERMS

1. Scope and relationship to the Institutional Charter

These User Terms are a substantive draft for governed review. They describe
general use of WILSY OS within the principles of the WILSY OS Institutional
Charter. They are not a master subscription agreement, order form, data
processing agreement, service-level schedule, employment agreement, or grant
of signing authority. A later approved document may refine a subject only
through its own governed scope and version.

2. Authenticated accounts and responsible use

Access is provided to an authenticated person through the identity controls
made available by WILSY OS. The person using an account is responsible for
protecting credentials, authenticators, recovery material, and active
sessions; reporting suspected compromise through the authenticated support or
security contact mechanism; and ensuring that activity attributed to the
account is not knowingly permitted to continue when unauthorised. Authentication
establishes a presented identity. It does not establish every permission or
authority needed for an operation.

3. Tenant and organisation context

WILSY OS may operate across distinct tenant, organisation, matter, case,
workflow, district, or other institutional scopes. A user must select and use
only a scope to which the authenticated authority grants access. A tenant
owner, administrator, or super-administrator does not automatically become an
authorised signatory, legal representative, counsel, financial approver, or
execution operator. User acknowledgement or acceptance is attributable to the
user and is not an organisation signature or organisation-binding authority.

4. Permissions and permitted access

Permitted access is limited to the roles, permissions, assignments, and
resource boundaries granted by the relevant WILSY OS authority. Users must
not bypass a permission check, infer access from a visible identifier, query
another tenant, or use a client projection as proof of a missing authority.
Absence, conflict, or stale state must be reported or fail closed rather than
being replaced with an invented success.

5. Assistance, decisions, and evidence

WILSY OS may provide retrieval, organisation, analysis, drafting, explanation,
recommendation, and other tool assistance. Model output is not legal advice,
legal authority, approval, signatory authority, service evidence, execution,
payment, or settlement. Users remain responsible for consequential decisions,
source review, lawful instructions, and confirmation that an action was
actually performed by its designated authority. A provider response, browser
display, model result, location, timestamp, or uploaded image is not
self-authenticating WILSY OS truth.

6. User content and institutional integrity

Users must submit only content they are lawfully entitled and authorised to
submit. Content should be accurate to the user's knowledge, appropriately
scoped, and handled with care where it contains personal, confidential,
privileged, or legally sensitive information. Users must not alter, suppress,
fabricate, backdate, replay divergently, or misrepresent records, evidence,
workflow state, service events, invoices, payments, approvals, or settlement.
Immutable or append-only evidence may remain preserved when a user later asks
to remove a projection or account association.

7. Prohibited circumvention and misuse

Users must not use WILSY OS for unlawful access, credential theft, malware,
destructive activity, unauthorised scraping, resource exhaustion, security
probing, impersonation, fraud, harassment, threats, rights-infringing
content, or evasion of monitoring and access controls. The Acceptable Use
Policy draft supplies additional security and misuse boundaries. Users must
not treat AI output as fabricated legal evidence, bypass approval or signature
controls, or ask a non-Kennel surface to invent financial execution or
settlement truth.

8. Integrations, availability, and technical limitations

Third-party integrations, models, payment networks, courier systems, devices,
and other providers may supply capability, transport, standards, or observed
data. They do not become canonical WILSY OS authorities merely because they
return a response. Integrations may be unavailable, delayed, rate-limited,
incorrect, or changed. WILSY OS does not make an unstated uptime or service
level promise in this draft. Users must use the designated recovery and support
path when a result is unavailable or ambiguous.

9. Intellectual property and lawful compliance

Users retain whatever rights they lawfully hold in submitted material, subject
to the permissions necessary to operate the selected workflow and preserve
required evidence. WILSY OS platform materials, interface elements, and
governed records remain subject to the rights and permissions applicable to
their source; this draft does not invent a corporate ownership statement or
transfer rights that a later approved instrument has not defined. Users must
comply with applicable law, professional duties, court or regulator orders,
confidentiality obligations, and their own institutional policies.

10. Suspension, cessation, and version succession

Access may be restricted or suspended to protect security, tenant isolation,
records, people, or lawful operations. Suspension does not by itself delete
immutable evidence or decide a disputed legal issue. A user may stop using a
service, but historical authority and evidence remain governed by their own
retention and lifecycle rules. Version succession must identify the
predecessor, effective point, and governed review state; a newer draft does
not silently rewrite an older record.

11. Review boundary and governing framework

These texts are marked DRAFT_REVIEW_REQUIRED. They have not been approved,
accepted, signed, or made organisation-binding. Their intended review is
aligned to the laws and courts of South Africa (ZA) without inventing a
registered entity, registration number, address, regulator approval, or
commercial term. Questions, rights requests, security reports, and legal
concerns should use the authenticated support, legal, privacy, or security
contact mechanism made available by WILSY OS.
"""


ACCEPTABLE_USE_CONTENT: Final[str] = """WILSY OS ACCEPTABLE USE POLICY

1. Purpose and draft boundary

This Acceptable Use Policy is a substantive DRAFT_REVIEW_REQUIRED document
for the WILSY OS platform. It operates consistently with the Institutional
Charter and describes prohibited misuse of platform capability. It is not an
approved contract, commercial order, organisation signature, financial
authority, or substitute for a specific law, court order, or professional
duty.

2. Lawful and authorised use

Use WILSY OS only for lawful, authorised institutional work and only within
the tenant, organisation, matter, case, workflow, district, and permission
boundaries granted to the authenticated principal. Do not use another
person's credentials, tokens, recovery material, session, or device assertion.
Do not infer authority from a role label, tenant ownership, SUPER_ADMIN access,
an administrator badge, or a successful login. Authentication is not blanket
authorisation.

3. Access, isolation, and security abuse

Prohibited activity includes bypassing tenant isolation; enumerating or
disclosing another tenant's records; unauthorised access or privilege
elevation; credential capture; token theft; malware; ransomware; destructive
commands; data poisoning; denial-of-service; resource exhaustion; unauthorised
scraping; automated traffic that defeats rate or safety controls; security
probing or vulnerability testing without an expressly authorised scope; and
interference with audit, identity, evidence, or availability controls.

4. Deception, content, and harm

Do not impersonate a person or institution, commit fraud, mislead a court,
regulator, client, tenant, provider, or operator, or submit content known to be
unlawful, rights-infringing, malicious, threatening, harassing, exploitative,
or intended to facilitate harm. Do not use the platform to target people with
unlawful discrimination, threats, stalking, or exploitation. These boundaries
do not create a general censorship rule for lawful institutional work; they
protect people, records, security, and legal operations.

5. Truth, evidence, and governed transitions

Never fabricate, alter, backdate, delete, replay divergently, or conceal legal,
operational, service, custody, approval, invoice, payment, execution,
settlement, or audit truth. A provider response, uploaded file, location,
model answer, browser state, or integration callback is evidence or capability,
not automatically canonical WILSY OS truth. Attempts are not completed
services; invoices are not payments; payments are not settlement.

6. AI and authority boundaries

AI assistance may retrieve, summarise, analyse, draft, classify, or recommend.
It may be inaccurate, incomplete, stale, or unsuitable. AI output is not legal
advice, legal authority, approval, signatory authority, service evidence,
execution, or settlement. Do not present model output as a signed instrument,
approved record, or real-world event. Tool access is capability, not authority.

7. Approval, signature, and financial circumvention

Do not bypass document review, approval, signature verification, acceptance,
release-authorisation, or operator transaction controls. Do not submit a
signature or authority representation for another person. Do not ask a client,
browser, provider, model, or integration to mark a document approved, a user
as an authorised signatory, a payment as executed, or a balance as settled.
Kennel EOS remains the exclusive financial execution and settlement authority
where the platform constitution assigns that boundary.

8. Secrets, reporting, and enforcement

Do not disclose passwords, private keys, passphrases, recovery codes, tokens,
or other secrets in content, logs, prompts, tickets, or integrations. Report
suspected vulnerability, abuse, compromise, or unsafe content through the
authenticated security or support mechanism made available by WILSY OS. WILSY
OS may monitor bounded security and integrity signals, preserve evidence,
restrict access, suspend a session, or require review when necessary to protect
people, tenants, records, or lawful operations. Enforcement decisions remain
subject to the designated authority and applicable law.

9. Review and versioning

This policy is DRAFT_REVIEW_REQUIRED and has not been approved, accepted,
signed, or made organisation-binding. Future approved versions must identify
their predecessor, effective point, and review authority. The policy does not
invent a corporate registration, contact address, regulator certification,
service-level guarantee, or commercial promise. Concerns should use the
authenticated support, legal, privacy, or security contact mechanism provided
by WILSY OS.
"""


PRIVACY_NOTICE_CONTENT: Final[str] = """WILSY OS PRIVACY NOTICE

1. Scope and draft status

This POPIA-aware Privacy Notice is a substantive DRAFT_REVIEW_REQUIRED text
for review in the South African (ZA) context. It describes categories,
purposes, boundaries, safeguards, and rights without claiming a completed
registration, a named Information Officer, a fixed retention period, or a
specific cross-border location. It is not an approved data-processing
agreement or a promise that overrides a lawful obligation.

2. Information that may be handled

Depending on the authorised workflow, WILSY OS may handle account, identity,
contact, authentication, membership, role, permission, tenant, organisation,
matter, case, instruction, process, custody, workflow, document, audit,
acceptance, evidence, billing-eligibility, and operational information. It may
also receive device, session, security, usage, diagnostic, trace, availability,
and integration information. AI-enabled workflows may handle the prompt,
selected context, retrieved records, tool events, model response, provenance,
and user feedback required by their configured contract.

3. Sources and purposes

Information may come from the authenticated person, an authorised institution,
platform services, security controls, connected capability providers, or
governed records. Purposes may include authentication, tenant isolation,
service delivery, workflow coordination, document and evidence integrity,
security and fraud prevention, support, troubleshooting, auditability,
operational reporting, product improvement, bounded analytics, and compliance
with lawful duties. A purpose must remain proportionate, scoped, and
consistent with the relevant authority; a client or model cannot silently
expand it.

4. Grounds and institutional boundaries

Processing grounds will be assessed for the relevant activity, including lawful
service delivery, a legal obligation, legitimate institutional purpose, or
another ground available under applicable law. This draft does not treat
blanket consent as the answer to every processing activity. Tenant and
organisation boundaries are enforced independently from identity and are not
overridden by a convenient provider response or an AI suggestion.

5. Operators, providers, and AI capability

WILSY OS may use operators, hosting, security, communications, storage,
analytics, model, or other service providers as capabilities within governed
contracts and instructions. A model or provider may retrieve, transport,
transform, or analyse information; it is not the canonical WILSY OS authority
for legal, lifecycle, evidence, approval, execution, payment, or settlement
truth. A provider response does not prove that WILSY performed or authorised
an action. Appropriate contractual, technical, and organisational boundaries
must be evaluated for each provider.

6. Cross-border and security posture

Information may be processed or supported across jurisdictions where a lawful
and governed arrangement permits it. This draft does not invent a provider
location or transfer mechanism. WILSY OS should apply access control,
authentication, least privilege, tenant isolation, secure transport, storage
protection, logging, monitoring, integrity checks, incident handling, and
redaction appropriate to the information. Security safeguards reduce risk but
do not promise that every incident is impossible.

7. Retention, immutable records, and rights

Information should be retained only for a lawful, documented, and necessary
purpose, subject to the applicable lifecycle and evidence rules. Immutable,
append-only, legal, audit, approval, acceptance, or transaction evidence may
need to remain preserved even when a projection, account association, or
ordinary copy is removed. Subject to applicable law and lawful limitations, a
person may have rights to access, correction, objection, deletion, restriction,
or another appropriate remedy. A request may be limited where retention,
privilege, security, third-party rights, or evidence integrity requires it.

8. AI transparency and sensitive information

AI processing must distinguish OBSERVED FACT from DERIVED SIGNAL, AI INFERENCE,
RECOMMENDATION, AUTHORIZATION, and EXECUTION. Model output may be inaccurate,
incomplete, or stale and is not legal advice or evidence by itself. Users must
consider whether sensitive, confidential, privileged, or personal information
is necessary before submitting it to an AI-enabled workflow and must use the
configured platform controls. Consequential decisions remain subject to human
review and the designated authority.

9. Support, complaints, and changes

Questions, access or correction requests, privacy concerns, and complaints
should use the authenticated support, legal, or privacy contact mechanism made
available by WILSY OS. An Information Regulator reference may be added through
governed review when its current official pathway is verified; this draft does
not invent a named officer or mailbox. Children or minors are not assigned an
unsupported eligibility rule here; any applicable safeguards require review.
This notice may change through explicit version succession and review.

10. Review boundary

This text is DRAFT_REVIEW_REQUIRED. It has not been approved, accepted,
signed, or made organisation-binding, and it does not create a commercial,
financial, or signatory authority.
"""


AI_ASSISTANCE_NOTICE_CONTENT: Final[str] = """WILSY OS AI ASSISTANCE NOTICE

1. Purpose and draft status

This AI Assistance Notice is a substantive DRAFT_REVIEW_REQUIRED document for
review. It explains the limits of AI-enabled capability in WILSY OS. It is not
legal advice, a model warranty, an approval, a signature, a service record, a
financial instruction, or an organisation-binding agreement.

2. Assistance is not institutional authority

AI may assist with retrieval, summarisation, analysis, drafting, translation,
classification, explanation, search, workflow suggestions, or next-action
recommendations. It does not autonomously become an institutional authority.
The governing distinctions remain:

OBSERVED FACT != DERIVED SIGNAL != AI INFERENCE != RECOMMENDATION
!= AUTHORIZATION != EXECUTION.

AI output may be inaccurate, incomplete, ambiguous, stale, biased, or based on
an unsuitable source. It must not be represented as legal advice, an approved
document, a valid signature, proof of service, a verified identity, a payment,
or settlement truth. Human users and designated authorities remain responsible
for consequential decisions and actual actions.

3. Source, context, and tenant boundaries

An AI response is bounded by the source records, permissions, tenant,
organisation, matter, case, workflow, jurisdiction, and context made
available to it. Retrieval or tool access does not grant access to records
outside those boundaries. A model must not select a tenant, elevate a role,
infer organisation authority, or disclose another tenant's information. If
source context is unavailable, conflicting, or stale, the result must be
treated as unavailable or requiring review rather than invented.

4. Human review and consequential use

Before relying on an output, a user must inspect the relevant source, check the
scope and date, consider uncertainty, and obtain the review or approval
required by the applicable workflow. AI cannot approve a legal corpus, create
signatory authority, accept terms for an organisation, certify a service event,
release funds, execute a payment, or mark a balance settled. A recommendation
is not permission, and a generated draft is not an executed instrument.

5. Tools, providers, and model changes

Tools and external model providers may supply capability, transport, retrieval,
or analysis. They do not become canonical WILSY OS authorities because they
returned a response. Providers and models may change, fail, be unavailable,
or produce different output. WILSY OS should preserve bounded provenance,
usage, invocation, and audit information where the configured contract
requires it, without treating a provider response as canonical business,
legal, lifecycle, evidence, payment, or settlement truth.

6. Information handling and confidentiality

Users must consider whether personal, confidential, privileged, security,
client, matter, or legally sensitive information is necessary before entering
it into an AI-enabled workflow. Use the platform's configured access,
redaction, retention, and provider controls. Do not submit secrets, private
keys, passphrases, recovery material, or another person's information without
lawful authority. Processing by a model or capability provider must remain
within the relevant governed purpose and privacy boundary.

7. Provenance, reporting, and misuse

Generated text should not be detached from the source and context needed to
evaluate it. Users should report materially incorrect, unsafe, discriminatory,
confidentiality-threatening, or misleading output through the authenticated
support, legal, privacy, or security contact mechanism made available by
WILSY OS. Do not use prompts, tools, or model output to bypass approval,
signature, audit, tenant, security, or Kennel financial boundaries.

8. Version and review boundary

Models, providers, retrieval sources, and controls may evolve. A material
change should identify its version and review state. This notice is
DRAFT_REVIEW_REQUIRED; it has not been approved, accepted, signed, or made
organisation-binding. It creates no commercial, financial, signatory, or
execution authority.
"""


ADMIN_RESPONSIBILITY_NOTICE_CONTENT: Final[str] = """WILSY OS ADMINISTRATOR RESPONSIBILITY NOTICE

1. Scope and draft status

This Administrator Responsibility Notice is a substantive
DRAFT_REVIEW_REQUIRED document for privileged and administrative users. It
describes elevated operational responsibility under the Institutional Charter.
It is not a corporate mandate, a signatory appointment, a service-level
promise, a commercial agreement, or financial execution authority.

2. Privilege is responsibility, not signature authority

Administrative access permits bounded platform operations; it does not by
itself make a person an authorised signatory, legal representative, counsel,
financial approver, or organisation owner. In particular:

SUPER_ADMIN != AUTHORISED_SIGNATORY.

A tenant owner, administrator, or membership manager is not automatically
authorised to bind an organisation, accept a commercial agreement, approve a
legal corpus, sign on behalf of another person, release funds, or declare
settlement. Authority must come from its designated governed source.

3. Least privilege and membership management

Administrators should grant the minimum role and permission needed for a
defined task, review access regularly, remove access when a person leaves or
changes responsibility, and avoid shared accounts. Role changes, invitations,
offboarding, recovery, integration credentials, and privileged actions should
remain attributable and auditable. A visible client state does not replace
server-side permission or tenant validation.

4. Tenant isolation and sensitive records

Administrators must preserve tenant, organisation, matter, case, district,
workflow, and evidence boundaries. They must not browse, export, disclose, or
alter another scope without a separately governed purpose. Legal, personal,
confidential, security, and operational records require careful handling,
least-privilege access, secure credentials, appropriate support channels, and
preservation of material audit evidence.

5. Configuration and integration responsibility

Administrators are responsible for reviewing configuration, webhooks, API
clients, automation, provider credentials, retention settings, and access
assignments within their granted scope. External integrations and providers
are capabilities, not canonical WILSY OS authorities. A provider response,
model recommendation, browser action, or automation result does not prove that
WILSY authorised or executed an operation.

6. AI and legal-operation boundaries

AI or administrative tooling may retrieve, analyse, draft, or recommend; it
does not create approval, review completion, signatory authority, acceptance,
organisation binding, service evidence, execution, payment, or settlement.
Administrators must not ask a model or tool to bypass a permission, alter
evidence, manufacture a legal fact, or conceal uncertainty. User acceptance is
an acknowledgement attributable to that user, not an organisation signature.

7. Financial and approval boundaries

Administrators must not bypass document review, approval, signature, acceptance,
release-authorisation, or transaction controls. APPROVED is not RELEASE
AUTHORIZED, EXECUTED, or SETTLED. Kennel EOS remains the exclusive authority
for financial execution and settlement truth where the platform constitution
assigns that boundary. No administrator action in this document changes that
rule or authorises a bank, provider, payment destination, paid state, or
settled state.

8. Incidents, escalation, and evidence preservation

Administrators should promptly use the authenticated security or support
mechanism for suspected compromise, unauthorised access, data loss, unsafe
automation, integrity conflict, or material policy breach. Preserve relevant
logs and immutable evidence; do not delete or rewrite records to conceal an
incident. Escalation does not itself determine legal liability or approval; the
designated authority must adjudicate the matter.

9. Version and review boundary

This notice is DRAFT_REVIEW_REQUIRED. It has not been approved, accepted,
signed, or made organisation-binding. Future versions must identify their
predecessor, effective point, and review authority. This draft invents no
corporate identity, registration, contact address, regulator certification,
commercial term, or financial authority.
"""


USER_TERMS_REVIEWED_SUCCESSOR_CONTENT: Final[str] = """WILSY OS USER TERMS

1. Scope and relationship to the Institutional Charter

These User Terms describe general use of WILSY OS within the principles of the
WILSY OS Institutional Charter. They are platform-use terms and are not a
master subscription agreement, order form, data processing agreement,
service-level schedule, employment agreement, or grant of signing authority.
A separate governed approval record is required before any version is treated
as effective for the scope stated in that record. A later version may refine a
subject only through its own governed scope, effective point, and succession
record.

2. Authenticated accounts and responsible use

Access is provided to an authenticated person through identity controls made
available by WILSY OS. The person using an account must protect credentials,
authenticators, recovery material, and active sessions; report suspected
compromise through the authenticated support or security mechanism; and stop
knowingly permitting unauthorised activity attributed to the account.
Authentication establishes a presented identity. It does not establish every
permission or authority needed for an operation.

3. Tenant and organisation context

WILSY OS may operate across distinct tenant, organisation, matter, case,
workflow, district, or other institutional scopes. A user must select and use
only a scope to which the authenticated authority grants access. A tenant
owner, administrator, or super-administrator does not automatically become an
authorised signatory, legal representative, counsel, financial approver, or
execution operator. User acknowledgement or acceptance is attributable to the
user and is not an organisation signature or organisation-binding authority.

4. Permissions and permitted access

Permitted access is limited to roles, permissions, assignments, and resource
boundaries granted by the relevant WILSY OS authority. Users must not bypass a
permission check, infer access from a visible identifier, query another
tenant, or use a client projection as proof of missing authority. Absence,
conflict, or stale state must be reported or fail closed rather than replaced
with an invented success.

5. Assistance, decisions, and evidence

WILSY OS may provide retrieval, organisation, analysis, explanation,
recommendation, and other tool assistance. Model output is not legal advice,
legal authority, a governed approval record, signatory authority, service
evidence, execution, payment, or settlement. Users remain responsible for
consequential decisions, source review, lawful instructions, and confirmation
that an action was performed by its designated authority. A provider response,
browser display, model result, location, timestamp, or uploaded image is not
self-authenticating WILSY OS truth.

6. User content and institutional integrity

Users must submit only content they are lawfully entitled and authorised to
submit. Content should be accurate to the user's knowledge, appropriately
scoped, and handled with care where it contains personal, confidential,
privileged, or legally sensitive information. Users must not alter, suppress,
fabricate, backdate, replay divergently, or misrepresent records, evidence,
workflow state, service events, invoices, payments, approvals, or settlement.
Immutable or append-only evidence may remain preserved when a projection or
account association is later removed.

7. Prohibited circumvention and misuse

Users must not use WILSY OS for unlawful access, credential theft, malware,
destructive activity, unauthorised scraping, resource exhaustion, security
probing, impersonation, fraud, harassment, threats, rights-infringing
content, or evasion of monitoring and access controls. The Acceptable Use
Policy supplies additional security and misuse boundaries. Users must not
treat AI output as fabricated legal evidence, bypass review or signature
controls, or ask a non-Kennel surface to invent financial execution or
settlement truth.

8. Integrations, availability, and technical limitations

Third-party integrations, models, payment networks, courier systems, devices,
and other providers may supply capability, transport, standards, or observed
data. They do not become canonical WILSY OS authorities merely because they
return a response. Integrations may be unavailable, delayed, rate-limited,
incorrect, or changed. No unstated uptime or service-level promise is made by
these terms. Users must use the designated recovery and support path when a
result is unavailable or ambiguous.

9. Intellectual property and lawful compliance

Users retain whatever rights they lawfully hold in submitted material, subject
to permissions necessary to operate the selected workflow and preserve
required evidence. WILSY OS platform materials, interface elements, and
governed records remain subject to rights applicable to their source; these
terms do not create a corporate ownership statement or transfer rights. Users
must comply with applicable law, professional duties, court or regulator
orders, confidentiality obligations, and their own institutional policies.

10. Suspension, cessation, and version succession

Access may be restricted or suspended to protect security, tenant isolation,
records, people, or lawful operations. Suspension does not by itself delete
immutable evidence or decide a disputed legal issue. Historical authority and
evidence remain governed by their own retention and lifecycle rules. Version
succession must identify the predecessor, effective point, and governing
record; a newer version does not silently rewrite an older record.

11. Governance contacts and lifecycle separation

Questions, rights requests, security reports, and legal concerns should use
the authenticated support, legal, privacy, or security contact mechanism made
available by WILSY OS. The existence of these terms does not itself create
acceptance, organisation binding, signatory authority, commercial obligation,
financial execution, or settlement. Each such outcome requires its separate
designated authority and durable evidence.
"""


ACCEPTABLE_USE_REVIEWED_SUCCESSOR_CONTENT: Final[str] = """WILSY OS ACCEPTABLE USE POLICY

1. Purpose and relationship to the Institutional Charter

This Acceptable Use Policy describes prohibited misuse of WILSY OS platform
capability and operates consistently with the Institutional Charter. It is
not a commercial order, organisation signature, financial authority, or
substitute for a specific law, court order, or professional duty. A separate
governed record determines the applicable scope and effective point.

2. Lawful and authorised use

Use WILSY OS only for lawful, authorised institutional work and only within
the tenant, organisation, matter, case, workflow, district, and permission
boundaries granted to the authenticated principal. Do not use another
person's credentials, tokens, recovery material, session, or device
assertion. Do not infer authority from a role label, tenant ownership,
SUPER_ADMIN access, an administrator badge, or a successful login.
Authentication is not blanket authorisation.

3. Access, isolation, and security abuse

Prohibited activity includes bypassing tenant isolation; enumerating or
disclosing another tenant's records; unauthorised access or privilege
elevation; credential capture; token theft; malware; ransomware; destructive
commands; data poisoning; denial-of-service; resource exhaustion;
unauthorised scraping; automated traffic that defeats rate or safety controls;
security probing or vulnerability testing without an expressly authorised
scope; and interference with audit, identity, evidence, or availability
controls.

4. Deception, content, and harm

Do not impersonate a person or institution, commit fraud, mislead a court,
regulator, client, tenant, provider, or operator, or submit content known to
be unlawful, rights-infringing, malicious, threatening, harassing,
exploitative, or intended to facilitate harm. Do not use the platform to
target people with unlawful discrimination, threats, stalking, or
exploitation. These boundaries protect people, records, security, and legal
operations without deciding a disputed legal issue.

5. Truth, evidence, and governed transitions

Never fabricate, alter, backdate, delete, replay divergently, or conceal
legal, operational, service, custody, review, approval, invoice, payment,
execution, settlement, or audit truth. A provider response, uploaded file,
location, model answer, browser state, or integration callback is evidence or
capability, not automatically canonical WILSY OS truth. Attempts are not
completed services; invoices are not payments; payments are not settlement.

6. AI and authority boundaries

AI assistance may retrieve, summarise, analyse, classify, or recommend. It
may be inaccurate, incomplete, stale, or unsuitable. AI output is not legal
advice, legal authority, a governed approval record, signatory authority,
service evidence, execution, or settlement. Do not present model output as a
signed instrument, authoritative record, or real-world event. Tool access is
capability, not authority.

7. Review, signature, and financial circumvention

Do not bypass document review, governed approval, signature verification,
acceptance, release-authorisation, or operator transaction controls. Do not
submit a signature or authority representation for another person. Do not ask
a client, browser, provider, model, or integration to mark a document as
effective, a user as an authorised signatory, a payment as executed, or a
balance as settled. Kennel EOS remains the exclusive financial execution and
settlement authority where the platform constitution assigns that boundary.

8. Secrets, reporting, and enforcement

Do not disclose passwords, private keys, passphrases, recovery codes, tokens,
or other secrets in content, logs, prompts, tickets, or integrations. Report
suspected vulnerability, abuse, compromise, or unsafe content through the
authenticated security or support mechanism made available by WILSY OS. WILSY
OS may monitor bounded security and integrity signals, preserve evidence,
restrict access, suspend a session, or require review when necessary. Such
enforcement does not itself determine legal liability or create financial
authority; the designated authority and applicable law govern those questions.

9. Version succession and contact boundary

Material changes identify their version, predecessor, effective point, and
governing record. Concerns should use the authenticated support, legal,
privacy, or security contact mechanism provided by WILSY OS. The existence of
this policy does not itself create organisation binding, signature authority,
commercial obligation, payment execution, or settlement truth.
"""


PRIVACY_NOTICE_REVIEWED_SUCCESSOR_CONTENT: Final[str] = """WILSY OS PRIVACY NOTICE

1. Scope and South African context

This POPIA-aware Privacy Notice describes information categories, purposes,
boundaries, safeguards, and rights relevant to WILSY OS in the South African
(ZA) context. It does not create a data-processing agreement or override a
lawful obligation. Processing and disclosure remain subject to the applicable
authority, purpose, and lifecycle record.

2. Information that may be handled

Depending on an authorised workflow, WILSY OS may handle account, identity,
contact, authentication, membership, role, permission, tenant,
organisation, matter, case, instruction, process, custody, workflow,
document, audit, acceptance, evidence, billing-eligibility, and operational
information. It may also receive device, session, security, usage,
diagnostic, trace, availability, and integration information. AI-enabled
workflows may handle prompts, selected context, retrieved records, tool
events, model responses, provenance, and feedback required by their governed
configuration.

3. Sources and purposes

Information may come from the authenticated person, an authorised institution,
platform services, security controls, connected capability providers, or
governed records. Purposes may include authentication, tenant isolation,
service delivery, workflow coordination, document and evidence integrity,
security and fraud prevention, support, troubleshooting, auditability,
operational reporting, product improvement, bounded analytics, and compliance
with lawful duties. A purpose must remain proportionate, scoped, and
consistent with its authority; a client or model cannot silently expand it.

4. Responsible-party and operator boundaries

WILSY OS determines the applicable responsible-party and operator roles for a
particular processing activity from the governing arrangement and instructions.
Hosting, security, communications, storage, analytics, model, and other
providers may act as operators or capabilities only within those arrangements.
A provider or model is not the canonical WILSY OS authority for legal,
lifecycle, evidence, review, approval, execution, payment, or settlement
truth. Concrete role allocation remains activity-specific and governed.

5. Lawful grounds and tenant boundaries

Processing grounds are assessed for the relevant activity, including lawful
service delivery, a legal obligation, a legitimate institutional purpose, or
another ground available under applicable law. Blanket consent is not treated
as the answer to every activity. Tenant and organisation boundaries are
enforced independently from identity and are not overridden by a provider
response or AI suggestion.

6. Cross-border processing and security safeguards

Information may be processed or supported across jurisdictions only where a
lawful and governed arrangement permits it. WILSY OS does not assert a
specific provider location or transfer country here. Access control,
authentication, least privilege, tenant isolation, secure transport, storage
protection, logging, monitoring, integrity checks, incident handling, and
redaction should be applied according to the information and governing
contract. Safeguards reduce risk but do not promise that every incident is
impossible.

7. Retention, immutable evidence, and rights

Information should be retained only for a lawful, documented, and necessary
purpose, subject to the applicable lifecycle and evidence rules. Immutable,
append-only, legal, audit, review, acceptance, or transaction evidence may
need to remain preserved even when a projection, account association, or
ordinary copy is removed. Subject to applicable law and lawful limitations, a
person may have rights to access, correction, objection, deletion,
restriction, or another appropriate remedy. A request may be limited where
retention, privilege, security, third-party rights, or evidence integrity
requires it.

8. AI transparency and sensitive information

AI processing distinguishes OBSERVED FACT from DERIVED SIGNAL, AI INFERENCE,
RECOMMENDATION, AUTHORIZATION, and EXECUTION. Model output may be inaccurate,
incomplete, or stale and is not legal advice or evidence by itself. Users
should consider whether sensitive, confidential, privileged, or personal
information is necessary before submitting it to an AI-enabled workflow and
must use configured platform controls. Consequential decisions remain subject
to human review and the designated authority.

9. Requests, complaints, and version succession

Questions, access or correction requests, privacy concerns, and complaints
should use the authenticated support, legal, or privacy contact mechanism made
available by WILSY OS. The Information Regulator of South Africa may be
contacted through its official published channels; no mailbox or officer is
created by this notice. Children or minors are not assigned an unsupported
eligibility rule here; applicable safeguards require activity-specific review.
Material changes identify their version, predecessor, effective point, and
governing record. This notice does not itself create commercial, financial,
signatory, acceptance, or organisation-binding authority.
"""


AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_CONTENT: Final[str] = """WILSY OS AI ASSISTANCE NOTICE

1. Purpose and authority boundary

This AI Assistance Notice explains the limits of AI-enabled capability in
WILSY OS. It is not legal advice, a model warranty, a governed approval
record, a signature, a service record, a financial instruction, or an
organisation-binding agreement. The existence of this notice does not grant
an AI system, provider, tool, or user authority to act outside its governed
scope.

2. Assistance is not institutional authority

AI may assist with retrieval, summarisation, analysis, classification,
translation, drafting, explanation, search, workflow suggestions, or
next-action recommendations. It does not autonomously become an institutional
authority. The governing distinctions remain:

OBSERVED FACT != DERIVED SIGNAL != AI INFERENCE != RECOMMENDATION
!= AUTHORIZATION != EXECUTION.

AI output may be inaccurate, incomplete, ambiguous, stale, biased, or based on
an unsuitable source. It must not be represented as legal advice, an
authoritative record, a valid signature, proof of service, a verified
identity, a payment, or settlement truth. Human users and designated
authorities remain responsible for consequential decisions and actual actions.

3. Source, context, and tenant boundaries

An AI response is bounded by source records, permissions, tenant,
organisation, matter, case, workflow, jurisdiction, and context made
available to it. Retrieval or tool access does not grant access to records
outside those boundaries. A model must not select a tenant, elevate a role,
infer organisation authority, or disclose another tenant's information. If
source context is unavailable, conflicting, or stale, the result is
unavailable or requires review rather than an invented outcome.

4. Human review and consequential use

Before relying on an output, a user must inspect the relevant source, check
scope and date, consider uncertainty, and obtain the review or governed
decision required by the applicable workflow. AI cannot create a legal-corpus
approval, signatory authority, organisation acceptance, service evidence,
release of funds, payment execution, or settled balance. A recommendation is
not permission, and generated text is not an executed instrument.

5. Tools, providers, and model changes

Tools and external model providers may supply capability, transport,
retrieval, or analysis. They do not become canonical WILSY OS authorities
because they returned a response. Providers and models may change, fail, be
unavailable, or produce different output. WILSY OS should preserve bounded
provenance, usage, invocation, and audit information where the governing
configuration requires it, without treating a provider response as canonical
business, legal, lifecycle, evidence, payment, or settlement truth.

6. Information handling and confidentiality

Users must consider whether personal, confidential, privileged, security,
client, matter, or legally sensitive information is necessary before entering
it into an AI-enabled workflow. Use configured access, redaction, retention,
and provider controls. Do not submit secrets, private keys, passphrases,
recovery material, or another person's information without lawful authority.
Processing by a model or capability provider must remain within the relevant
governed purpose and privacy boundary.

7. Provenance, reporting, and misuse

Generated text should remain associated with the source and context needed to
evaluate it. Users should report materially incorrect, unsafe,
discriminatory, confidentiality-threatening, or misleading output through
the authenticated support, legal, privacy, or security contact mechanism made
available by WILSY OS. Do not use prompts, tools, or model output to bypass
review, signature, audit, tenant, security, or Kennel financial boundaries.

8. Version succession and lifecycle separation

Models, providers, retrieval sources, and controls may evolve. A material
change should identify its version, predecessor, effective point, and governing
record. This notice does not itself create approval, acceptance, signatory,
commercial, financial, execution, or settlement authority; each outcome
requires its separate designated authority and durable evidence.
"""


ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_CONTENT: Final[str] = """WILSY OS ADMINISTRATOR RESPONSIBILITY NOTICE

1. Scope and relationship to the Institutional Charter

This Administrator Responsibility Notice describes elevated operational
responsibility under the Institutional Charter. It is not a corporate mandate,
signatory appointment, service-level promise, commercial agreement, or
financial execution authority. A separate governed record determines the
scope, effective point, and authority applicable to an administrator.

2. Privilege is responsibility, not signature authority

Administrative access permits bounded platform operations; it does not by
itself make a person an authorised signatory, legal representative, counsel,
financial approver, or organisation owner. In particular:

SUPER_ADMIN != AUTHORISED_SIGNATORY.

A tenant owner, administrator, or membership manager is not automatically
authorised to bind an organisation, accept a commercial agreement, approve a
legal corpus, sign on behalf of another person, release funds, or declare
settlement. Authority must come from its designated governed source.

3. Least privilege and membership management

Administrators should grant the minimum role and permission needed for a
defined task, review access regularly, remove access when a person leaves or
changes responsibility, and avoid shared accounts. Role changes, invitations,
offboarding, recovery, integration credentials, and privileged actions should
remain attributable and auditable. A visible client state does not replace
server-side permission or tenant validation.

4. Tenant isolation and sensitive records

Administrators must preserve tenant, organisation, matter, case, district,
workflow, and evidence boundaries. They must not browse, export, disclose, or
alter another scope without a separately governed purpose. Legal, personal,
confidential, security, and operational records require careful handling,
least-privilege access, secure credentials, appropriate support channels, and
preservation of material audit evidence.

5. Configuration and integration responsibility

Administrators are responsible for reviewing configuration, webhooks, API
clients, automation, provider credentials, retention settings, and access
assignments within their granted scope. External integrations and providers
are capabilities, not canonical WILSY OS authorities. A provider response,
model recommendation, browser action, or automation result does not prove
that WILSY authorised or executed an operation.

6. AI and legal-operation boundaries

AI or administrative tooling may retrieve, analyse, explain, or recommend; it
does not create review completion, governed approval, signatory authority,
acceptance, organisation binding, service evidence, execution, payment, or
settlement. Administrators must not ask a model or tool to bypass a
permission, alter evidence, manufacture a legal fact, or conceal uncertainty.
User acceptance is an acknowledgement attributable to that user, not an
organisation signature.

7. Financial and review boundaries

Administrators must not bypass document review, governed approval, signature,
acceptance, release-authorisation, or transaction controls. A document
lifecycle state is not RELEASE AUTHORIZED, EXECUTED, or SETTLED. Kennel EOS remains the exclusive
authority for financial execution and settlement truth where the platform
constitution assigns that boundary. No administrator action changes that rule
or authorises a bank, provider, payment destination, paid state, or settled
state.

8. Incidents, escalation, and evidence preservation

Administrators should promptly use the authenticated security or support
mechanism for suspected compromise, unauthorised access, data loss, unsafe
automation, integrity conflict, or material policy breach. Preserve relevant
logs and immutable evidence; do not delete or rewrite records to conceal an
incident. Escalation does not itself determine legal liability or authority;
the designated authority must adjudicate the matter.

9. Version succession and contact boundary

Material changes identify the predecessor, effective point, and governing
record. Administrators should use the authenticated security, support, legal,
privacy, or security contact mechanism made available by WILSY OS. The
existence of this notice does not create corporate identity, registration,
signatory authority, commercial obligation, financial execution, or settlement
truth.
"""


def _platform_draft(
    *,
    document_id: str,
    agreement_type: LegalAgreementType,
    title: str,
    content_reference: str,
    content: str,
) -> LegalDocumentVersion:
    """Construct one immutable platform draft without persistence or authority."""
    return LegalDocumentVersion(
        document_id=document_id,
        agreement_type=agreement_type,
        version="1.0.0-DRAFT",
        title=title,
        jurisdiction="ZA",
        locale="en-ZA",
        effective_from=DRAFT_AUTHORING_TIMESTAMP,
        status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        content_reference=content_reference,
        content=content,
        sha3_512=canonical_document_digest(content, content_reference),
        created_at=DRAFT_AUTHORING_TIMESTAMP,
        supersedes_document_id=None,
    )


def _platform_reviewed_successor_draft(
    *,
    document_id: str,
    agreement_type: LegalAgreementType,
    title: str,
    content_reference: str,
    content: str,
    supersedes_document_id: str,
) -> LegalDocumentVersion:
    """Construct one human-directed successor value without persistence authority."""
    return LegalDocumentVersion(
        document_id=document_id,
        agreement_type=agreement_type,
        version="1.1.0-DRAFT",
        title=title,
        jurisdiction="ZA",
        locale="en-ZA",
        effective_from=REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP,
        status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        content_reference=content_reference,
        content=content,
        sha3_512=canonical_document_digest(content, content_reference),
        created_at=REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP,
        supersedes_document_id=supersedes_document_id,
    )


USER_TERMS_DRAFT: Final[LegalDocumentVersion] = _platform_draft(
    document_id="WILSY-OS-USER-TERMS",
    agreement_type=LegalAgreementType.USER_TERMS,
    title="WILSY OS User Terms",
    content_reference="wilsy-os://legal/user-terms/1.0.0-draft",
    content=USER_TERMS_CONTENT,
)
ACCEPTABLE_USE_DRAFT: Final[LegalDocumentVersion] = _platform_draft(
    document_id="WILSY-OS-ACCEPTABLE-USE",
    agreement_type=LegalAgreementType.ACCEPTABLE_USE,
    title="WILSY OS Acceptable Use Policy",
    content_reference="wilsy-os://legal/acceptable-use/1.0.0-draft",
    content=ACCEPTABLE_USE_CONTENT,
)
PRIVACY_NOTICE_DRAFT: Final[LegalDocumentVersion] = _platform_draft(
    document_id="WILSY-OS-PRIVACY-NOTICE",
    agreement_type=LegalAgreementType.PRIVACY_NOTICE,
    title="WILSY OS Privacy Notice",
    content_reference="wilsy-os://legal/privacy-notice/1.0.0-draft",
    content=PRIVACY_NOTICE_CONTENT,
)
AI_ASSISTANCE_NOTICE_DRAFT: Final[LegalDocumentVersion] = _platform_draft(
    document_id="WILSY-OS-AI-ASSISTANCE-NOTICE",
    agreement_type=LegalAgreementType.AI_ASSISTANCE_NOTICE,
    title="WILSY OS AI Assistance Notice",
    content_reference="wilsy-os://legal/ai-assistance-notice/1.0.0-draft",
    content=AI_ASSISTANCE_NOTICE_CONTENT,
)
ADMIN_RESPONSIBILITY_NOTICE_DRAFT: Final[LegalDocumentVersion] = _platform_draft(
    document_id="WILSY-OS-ADMIN-RESPONSIBILITY-NOTICE",
    agreement_type=LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE,
    title="WILSY OS Administrator Responsibility Notice",
    content_reference="wilsy-os://legal/admin-responsibility-notice/1.0.0-draft",
    content=ADMIN_RESPONSIBILITY_NOTICE_CONTENT,
)

USER_TERMS_REVIEWED_SUCCESSOR_DRAFT: Final[LegalDocumentVersion] = _platform_reviewed_successor_draft(
    document_id=USER_TERMS_DRAFT.document_id,
    agreement_type=USER_TERMS_DRAFT.agreement_type,
    title=USER_TERMS_DRAFT.title,
    content_reference="wilsy-os://legal/user-terms/1.1.0-draft",
    content=USER_TERMS_REVIEWED_SUCCESSOR_CONTENT,
    supersedes_document_id=USER_TERMS_DRAFT.document_id,
)
ACCEPTABLE_USE_REVIEWED_SUCCESSOR_DRAFT: Final[LegalDocumentVersion] = _platform_reviewed_successor_draft(
    document_id=ACCEPTABLE_USE_DRAFT.document_id,
    agreement_type=ACCEPTABLE_USE_DRAFT.agreement_type,
    title=ACCEPTABLE_USE_DRAFT.title,
    content_reference="wilsy-os://legal/acceptable-use/1.1.0-draft",
    content=ACCEPTABLE_USE_REVIEWED_SUCCESSOR_CONTENT,
    supersedes_document_id=ACCEPTABLE_USE_DRAFT.document_id,
)
PRIVACY_NOTICE_REVIEWED_SUCCESSOR_DRAFT: Final[LegalDocumentVersion] = _platform_reviewed_successor_draft(
    document_id=PRIVACY_NOTICE_DRAFT.document_id,
    agreement_type=PRIVACY_NOTICE_DRAFT.agreement_type,
    title=PRIVACY_NOTICE_DRAFT.title,
    content_reference="wilsy-os://legal/privacy-notice/1.1.0-draft",
    content=PRIVACY_NOTICE_REVIEWED_SUCCESSOR_CONTENT,
    supersedes_document_id=PRIVACY_NOTICE_DRAFT.document_id,
)
AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_DRAFT: Final[LegalDocumentVersion] = _platform_reviewed_successor_draft(
    document_id=AI_ASSISTANCE_NOTICE_DRAFT.document_id,
    agreement_type=AI_ASSISTANCE_NOTICE_DRAFT.agreement_type,
    title=AI_ASSISTANCE_NOTICE_DRAFT.title,
    content_reference="wilsy-os://legal/ai-assistance-notice/1.1.0-draft",
    content=AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_CONTENT,
    supersedes_document_id=AI_ASSISTANCE_NOTICE_DRAFT.document_id,
)
ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_DRAFT: Final[LegalDocumentVersion] = _platform_reviewed_successor_draft(
    document_id=ADMIN_RESPONSIBILITY_NOTICE_DRAFT.document_id,
    agreement_type=ADMIN_RESPONSIBILITY_NOTICE_DRAFT.agreement_type,
    title=ADMIN_RESPONSIBILITY_NOTICE_DRAFT.title,
    content_reference="wilsy-os://legal/admin-responsibility-notice/1.1.0-draft",
    content=ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_CONTENT,
    supersedes_document_id=ADMIN_RESPONSIBILITY_NOTICE_DRAFT.document_id,
)

PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS: Final[tuple[LegalDocumentVersion, ...]] = (
    USER_TERMS_REVIEWED_SUCCESSOR_DRAFT,
    ACCEPTABLE_USE_REVIEWED_SUCCESSOR_DRAFT,
    PRIVACY_NOTICE_REVIEWED_SUCCESSOR_DRAFT,
    AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_DRAFT,
    ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_DRAFT,
)

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


PLATFORM_LEGAL_CORPUS_DRAFTS: Final[tuple[LegalDocumentVersion, ...]] = (
    INSTITUTIONAL_CHARTER_DRAFT,
    USER_TERMS_DRAFT,
    ACCEPTABLE_USE_DRAFT,
    PRIVACY_NOTICE_DRAFT,
    AI_ASSISTANCE_NOTICE_DRAFT,
    ADMIN_RESPONSIBILITY_NOTICE_DRAFT,
)


class LegalCorpusCanonicalDraftResolutionError(ValueError):
    """Fail-closed error for exact source-owned runtime catalog resolution."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS: Final[tuple[LegalDocumentVersion, ...]] = (
    *PLATFORM_LEGAL_CORPUS_DRAFTS,
    *PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS,
)


def resolve_platform_legal_corpus_draft(
    document_id: str,
    version: str,
) -> LegalDocumentVersion:
    """Resolve one exact draft identity from the immutable source catalog.

    This pure platform resolver accepts only exact ``document_id`` and
    ``version`` identity, requires exactly one source value, and rejects every
    non-draft or unknown/ambiguous identity. It performs no I/O, authority
    issuance, persistence, or caller-content lookup.
    """
    matches = tuple(
        document
        for document in PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS
        if document.document_id == document_id and document.version == version
    )
    if not matches:
        raise LegalCorpusCanonicalDraftResolutionError("CANONICAL_DOCUMENT_UNKNOWN")
    if len(matches) != 1:
        raise LegalCorpusCanonicalDraftResolutionError("CANONICAL_DOCUMENT_DUPLICATE")
    document = matches[0]
    if document.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
        raise LegalCorpusCanonicalDraftResolutionError("NON_DRAFT_CANONICAL_SOURCE")
    return document


def get_user_terms_draft() -> LegalDocumentVersion:
    """Return the immutable User Terms draft without persistence or authority changes."""
    return USER_TERMS_DRAFT


def get_acceptable_use_draft() -> LegalDocumentVersion:
    """Return the immutable Acceptable Use draft without persistence or authority changes."""
    return ACCEPTABLE_USE_DRAFT


def get_privacy_notice_draft() -> LegalDocumentVersion:
    """Return the immutable Privacy Notice draft without persistence or authority changes."""
    return PRIVACY_NOTICE_DRAFT


def get_ai_assistance_notice_draft() -> LegalDocumentVersion:
    """Return the immutable AI Assistance Notice draft without persistence or authority changes."""
    return AI_ASSISTANCE_NOTICE_DRAFT


def get_admin_responsibility_notice_draft() -> LegalDocumentVersion:
    """Return the immutable Administrator Responsibility draft without persistence or authority changes."""
    return ADMIN_RESPONSIBILITY_NOTICE_DRAFT


def get_user_terms_reviewed_successor_draft() -> LegalDocumentVersion:
    """Return the human-directed User Terms successor without persistence authority."""
    return USER_TERMS_REVIEWED_SUCCESSOR_DRAFT


def get_acceptable_use_reviewed_successor_draft() -> LegalDocumentVersion:
    """Return the human-directed Acceptable Use successor without persistence authority."""
    return ACCEPTABLE_USE_REVIEWED_SUCCESSOR_DRAFT


def get_privacy_notice_reviewed_successor_draft() -> LegalDocumentVersion:
    """Return the human-directed Privacy Notice successor without persistence authority."""
    return PRIVACY_NOTICE_REVIEWED_SUCCESSOR_DRAFT


def get_ai_assistance_notice_reviewed_successor_draft() -> LegalDocumentVersion:
    """Return the human-directed AI Assistance successor without persistence authority."""
    return AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_DRAFT


def get_admin_responsibility_notice_reviewed_successor_draft() -> LegalDocumentVersion:
    """Return the human-directed Administrator Responsibility successor without persistence authority."""
    return ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_DRAFT


__all__ = [
    "AUTHORING_TIMESTAMP",
    "DRAFT_AUTHORING_TIMESTAMP",
    "REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP",
    "CHARTER_CONTENT",
    "CONTENT_REFERENCE",
    "DOCUMENT_ID",
    "DOCUMENT_VERSION",
    "INSTITUTIONAL_CHARTER_DRAFT",
    "USER_TERMS_CONTENT",
    "USER_TERMS_DRAFT",
    "ACCEPTABLE_USE_CONTENT",
    "ACCEPTABLE_USE_DRAFT",
    "PRIVACY_NOTICE_CONTENT",
    "PRIVACY_NOTICE_DRAFT",
    "AI_ASSISTANCE_NOTICE_CONTENT",
    "AI_ASSISTANCE_NOTICE_DRAFT",
    "ADMIN_RESPONSIBILITY_NOTICE_CONTENT",
    "ADMIN_RESPONSIBILITY_NOTICE_DRAFT",
    "USER_TERMS_REVIEWED_SUCCESSOR_CONTENT",
    "USER_TERMS_REVIEWED_SUCCESSOR_DRAFT",
    "ACCEPTABLE_USE_REVIEWED_SUCCESSOR_CONTENT",
    "ACCEPTABLE_USE_REVIEWED_SUCCESSOR_DRAFT",
    "PRIVACY_NOTICE_REVIEWED_SUCCESSOR_CONTENT",
    "PRIVACY_NOTICE_REVIEWED_SUCCESSOR_DRAFT",
    "AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_CONTENT",
    "AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_DRAFT",
    "ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_CONTENT",
    "ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_DRAFT",
    "JURISDICTION",
    "LOCALE",
    "PLATFORM_LEGAL_CORPUS_DRAFTS",
    "PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS",
    "PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS",
    "LegalCorpusCanonicalDraftResolutionError",
    "resolve_platform_legal_corpus_draft",
    "VERSION",
    "get_acceptable_use_draft",
    "get_admin_responsibility_notice_draft",
    "get_ai_assistance_notice_draft",
    "get_institutional_charter_draft",
    "get_privacy_notice_draft",
    "get_user_terms_draft",
    "get_acceptable_use_reviewed_successor_draft",
    "get_admin_responsibility_notice_reviewed_successor_draft",
    "get_ai_assistance_notice_reviewed_successor_draft",
    "get_privacy_notice_reviewed_successor_draft",
    "get_user_terms_reviewed_successor_draft",
]


# ARTIFACT: production_legal_corpus.py
# VERSION: v1.3.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-RUNTIME-CATALOG
# AUTHORITY BOUNDARY: historical drafts and human-directed successor values only
# TENANT POSTURE: platform corpus draft; no tenant acceptance or binding truth
# FAIL-CLOSED POSTURE: draft remains review-required and cannot imply approval
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
