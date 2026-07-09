# Wilsy AI Inline Command Contract - FG108

## Protected baseline

FG108 established the Wilsy AI inline command contract for CRM Leads Proof Trail.

Runtime locks:

- p60k5q10fg108k-ai-inline-artifact-pdf-verified-stable
- p60k5q10fg108l4-ai-inline-command-dom-action-runtime-rescue-stable
- p60k5q10fg108l4-dom-action-runtime-verified-stable
- p60k5q10fg108m-final-ai-inline-artifact-regression-stable

## Contract

Wilsy AI responses in CRM Leads use one continuous typographic response surface. Inline actions appear inside the response and route into existing governed CRM workspace actions.

The surface must not introduce cards, rails, shelves, chips, mission panels, or a separate AI command canvas.

## Source surfaces

Frontend response surface:

    client/src/components/crm/lead/WilsyLeadOperatingRoom.jsx

AI Operator route:

    /api/wilsy/ai/operator/resolve

Artifact PDF route:

    /api/generate/pdf

Forbidden legacy route:

    /api/crm/leads/views/proof-pack/export/pdf

The forbidden legacy route must remain absent.

## DOM audit metadata

Every Wilsy AI inline command button rendered by the CRM Leads response surface must expose:

    data-wilsy-ai-response-surface="continuous_typographic"
    data-wilsy-ai-inline-command-router="FG107J"
    data-wilsy-ai-inline-command
    data-wilsy-ai-inline-command-action
    data-wilsy-ai-inline-command-route
    data-wilsy-ai-inline-command-id

## Required buttons

| Button | DOM command/action/id | Route context | Expected execution |
|---|---|---|---|
| Open Proof Trail | crm.leads.openProofTrail | crm.leads.openProofTrail | Opens Proof Trail |
| Open Sort Command | crm.leads.openSortCommand | crm.leads.openSortCommand | Opens Sort Command |
| Open Source Authority | crm.leads.openSourceAuthority | crm.leads.openSourceAuthority | Opens Source Authority |
| Open Artifact PDF control | open_artifact_pdf_control | crm.leads.openProofTrail | Calls governed Artifact PDF export |
| Open Evidence JSON control | open_evidence_json_control | crm.leads.openProofTrail | Downloads proof-pack JSON |
| Run proof before export | run_proof_before_export | crm.leads.openProofTrail | Returns user to Proof Trail proof workflow |

## Safety requirements

- No browser-side provider secrets.
- No silent mutation from inline AI links.
- PDF generation remains backend-governed through /api/generate/pdf.
- Evidence JSON remains proof-pack evidence export.
- Any future mutating AI action must use institutional headers and strike payload evidence.
- New AI capabilities must build on this contract, not bypass it.
