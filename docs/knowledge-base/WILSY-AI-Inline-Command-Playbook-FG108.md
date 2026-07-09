# WILSY OS AI Inline Command Playbook - FG108

Document class: Investor, user, and engineering knowledge base  
Product surface: CRM Leads Proof Trail + Wilsy AI Operator Kernel  
Baseline: FG108M final runtime regression verified  
Owner: Wilsy OS  
Prepared for: Investors, tenant users, operators, auditors, and future engineers  

---

## 1. Executive summary

Wilsy OS now has a verified AI inline command contract for CRM Leads Proof Trail.

Wilsy AI can answer inside the working surface and expose governed inline actions that execute real product operations without creating disconnected AI panels or static suggestion cards.

FG108 proved this production loop:

    User question
    -> Wilsy AI Operator Kernel
    -> continuous typographic response
    -> inline command links
    -> audited DOM command/action metadata
    -> governed frontend router
    -> Artifact PDF export through /api/generate/pdf
    -> Evidence JSON handoff
    -> runtime regression proof

This gives Wilsy OS a foundation for an AI operator that is useful, auditable, expandable, and safe.

---

## 2. Why this matters

Most SaaS AI features are bolted on as chat boxes, side panels, prompt cards, and static suggestions. Wilsy OS is building a different pattern.

Wilsy AI operates inside the actual workspace. The user asks a question in context, receives a direct answer, and sees inline command links embedded in the same response. These command links route into existing governed product actions.

Investors see proof that Wilsy AI can route governed action, not just produce text. Users keep answers and next steps inside the real workspace. Engineers get a strict contract for adding future AI capability.

---

## 3. Protected runtime baseline

Current protected runtime baseline:

    p60k5q10fg108k-ai-inline-artifact-pdf-verified-stable
    p60k5q10fg108l4-ai-inline-command-dom-action-runtime-rescue-stable
    p60k5q10fg108l4-dom-action-runtime-verified-stable
    p60k5q10fg108m-final-ai-inline-artifact-regression-stable

FG108M final regression verified:

    pass: true
    allButtonsClicked: true
    artifactPdfRouteUsed: true
    artifactPdfDownloaded: true
    evidenceJsonDownloaded: true
    noOldProofPackPdfRoute: true
    noErrorBoundary: true
    noLinkReferenceCrash: true
    noQuestionReferenceError: true
    noDockMapCrash: true
    noSec403Hdr: true
    noSealMismatch: true

---

## 4. Product doctrine

The Wilsy AI surface must remain a single continuous typographic response surface.

Do not add AI cards, AI rails, AI shelves, AI chips, AI mission panels, AI command canvases, static suggestion blocks, or separate AI sidebars.

Do use flowing response text, inline command links, existing workspace actions, auditable DOM metadata, governed backend routes, and evidence receipts.

---

## 5. Runtime contract

Operator Kernel response links become frontend inline command buttons inside:

    client/src/components/crm/lead/WilsyLeadOperatingRoom.jsx

The AI response surface must expose:

    data-wilsy-ai-response-surface="continuous_typographic"

Each inline command button must expose:

    data-wilsy-ai-inline-command-router="FG107J"
    data-wilsy-ai-inline-command
    data-wilsy-ai-inline-command-action
    data-wilsy-ai-inline-command-route
    data-wilsy-ai-inline-command-id

This makes the command visible to browser proof scripts, QA automation, future smoke harnesses, engineers reviewing runtime state, and auditors validating action posture.

---

## 6. Required inline commands

| Button | DOM command/action/id | Route context | Execution |
|---|---|---|---|
| Open Proof Trail | crm.leads.openProofTrail | crm.leads.openProofTrail | Opens Proof Trail |
| Open Sort Command | crm.leads.openSortCommand | crm.leads.openSortCommand | Opens Sort Command |
| Open Source Authority | crm.leads.openSourceAuthority | crm.leads.openSourceAuthority | Opens Source Authority |
| Open Artifact PDF control | open_artifact_pdf_control | crm.leads.openProofTrail | Generates governed Artifact PDF |
| Open Evidence JSON control | open_evidence_json_control | crm.leads.openProofTrail | Downloads proof-pack JSON |
| Run proof before export | run_proof_before_export | crm.leads.openProofTrail | Returns to Proof Trail workflow |

---

## 7. PDF and evidence route contract

The governed Artifact PDF route is:

    /api/generate/pdf

The Evidence JSON control uses the proof-pack JSON handoff from the CRM Proof Trail packet.

The forbidden legacy PDF route is:

    /api/crm/leads/views/proof-pack/export/pdf

That route must remain absent. Do not recreate it.

---

## 8. Backend posture

Wilsy AI route posture:

    /api/wilsy/ai/health
    /api/wilsy/ai/context/resolve
    /api/wilsy/ai/operator/resolve

Artifact generation posture:

    POST /api/generate/pdf

The AI operator route must remain evidence-aware. Any future write action must carry institutional headers and strike payload evidence.

---

## 9. User workflow

A user in CRM Leads Proof Trail can ask:

    In CRM Leads Proof Trail, which governed Artifact PDF control should I use?

Wilsy AI responds with a Proof Trail answer and exposes inline commands.

The user can then click:

    Open Artifact PDF control
    Open Evidence JSON control
    Run proof before export

The PDF control generates a governed PDF through /api/generate/pdf.

The JSON control downloads the portable proof-pack evidence file.

---

## 10. Investor interpretation

FG108 proves a repeatable operating pattern:

    Context-aware AI
    + governed inline actions
    + product-native execution
    + evidence export
    + DOM audit metadata
    + regression proof

This is a foundation for a universal Wilsy AI operator across CRM, meetings, calendar, documents, finance, evidence, and future operating surfaces.

The commercial value is not the chat response alone. The value is AI becoming an accountable action layer inside the OS.

---

## 11. Engineering rules for future AI capabilities

Any new inline command must:

1. Stay inside the continuous typographic response.
2. Expose DOM-auditable command/action/id/route metadata.
3. Route into an existing governed workspace action.
4. Avoid silent mutation.
5. Use /api/generate/pdf for artifact PDF generation.
6. Preserve the forbidden old route absence.
7. Preserve institutional headers and strike payload evidence for backend actions.
8. Include browser proof before being tagged stable.
9. Include a rollback path.
10. Avoid adding new static AI cards, panels, shelves, or chips.

---

## 12. Regression checklist

Before tagging any future AI inline command capability, prove:

    inputMounted: true
    surfaceStillMounted: true
    buttonsSeeded: true
    allButtonsClicked: true
    noErrorBoundary: true
    noLinkReferenceCrash: true
    noQuestionReferenceError: true
    noDockMapCrash: true
    noSec403Hdr: true
    noSealMismatch: true
    noOldProofPackPdfRoute: true
    artifactPdfRouteUsed: true
    artifactPdfDownloaded: true
    evidenceJsonDownloaded: true
    DOM action metadata audited: true
    pass: true

---

## 13. Known source files

    client/src/components/crm/lead/WilsyLeadOperatingRoom.jsx
    server/routes/wilsyAiRoutes.js
    server/services/wilsyAI/wilsyAIOperatorModelService.js
    server/services/wilsyAI/wilsyAICRMLeadsViewpointIntelligenceService.js
    server/routes/artifactRoutes.js
    server/controllers/artifactController.js
    scripts/wilsy-ai-operator-proof-harness.js

---

## 14. Operating principle

Wilsy AI must become a production operator, not a decorative chatbot.

The inline command contract is the bridge:

    answer -> action -> evidence -> proof -> next workflow

That loop is the Wilsy OS advantage.
