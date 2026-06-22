# WILSY OS Forensic Proof Lab

## Investor + Engineer Playbook

**Document status:** Production knowledge base draft  
**Lab status:** Forensic Proof Lab / Experimental  
**Account Command Center status:** Compact card pending  
**Current final-seal posture:** Review required  
**Backend seal authority:** Enabled  
**Browser seal authority:** Disabled  
**Current expected seal result:** `SEAL_BLOCKED_REVIEW_REQUIRED`

---

## 1. Executive Summary

The WILSY OS Forensic Proof Lab is an experimental evidence cockpit for proving the integrity posture of a tenant’s forensic audit chain. It gives operators, engineers, compliance teams, and investors a visible proof surface for Merkle-root evidence, receipt contracts, compliance bindings, and backend-owned seal decisions.

The lab does **not** allow the browser to certify immutable sealing. The browser can request a seal decision, display the result, export evidence, and show proof posture. Final seal authority remains with the backend route/auditor layer.

The current production-safe outcome is intentional:

> The backend receives a seal request, evaluates the safe receipt window, and truthfully blocks final sealing because the chain still contains review-required conditions.

Current backend decision:

```text
Seal status: SEAL_BLOCKED_REVIEW_REQUIRED

Blockers:
- CHAIN_NOT_VERIFIED
- REVIEW_RECEIPTS_PRESENT
- NOT_ALL_RECEIPTS_BACKEND_SEALED

Backend authority: TRUE
Browser authority: FALSE
Fallback authority: ROUTE_BACKEND_VERIFIER
Receipts: 250
Review receipts: 250
Sealed receipts: 0
Clause bindings: 1000
```

This is not prototype behavior. It is the correct production behavior for a compliance-grade proof system: the system refuses to pretend that an evidence window is sealed when backend verification says review is still required.

---

## 2. Why This Matters For Investors

Most workflow platforms can display documents, dashboards, and audit logs. WILSY OS is moving toward a higher-value layer: verifiable operating evidence.

The Forensic Proof Lab shows that WILSY OS can produce and inspect a compliance-aware evidence trail instead of relying only on UI state or database records. This matters because regulated customers need to prove:

1. What happened.
2. When it happened.
3. Which tenant it belonged to.
4. Which receipt or event represented it.
5. Which compliance frameworks were bound to it.
6. Whether the record was safe to seal.
7. Whether the proof decision came from backend authority, not browser-side decoration.

This lab demonstrates the foundation for investor-grade defensibility: WILSY OS is not just a productivity interface. It is building an evidence operating system for regulated work.

---

## 3. What The Lab Proves Today

### 3.1 Backend seal authority

The seal decision comes from:

```http
POST /api/forensics/merkle-auditor/seal-safe-window
```

The frontend does not compute or certify the seal. It sends a request and displays the backend decision.

### 3.2 Browser authority disabled

The frontend exposes and preserves the boundary:

```text
browserAuthority: false
```

This prevents false product claims. The browser can display proof. It cannot create final immutability.

### 3.3 Safe-window seal decision

The lab requests a bounded proof window, currently:

```json
{
  "limit": 250,
  "receiptLimit": 3
}
```

This avoids freezing the UI by replaying very large proof windows during normal showroom operation.

### 3.4 Truthful refusal to seal

When the backend sees unresolved review conditions, it returns:

```text
SEAL_BLOCKED_REVIEW_REQUIRED
```

This is a strength, not a failure. It means the system refuses to overstate integrity.

### 3.5 Evidence retained after HUD dismissal

The floating seal decision HUD can be dismissed, but the backend seal decision packet remains captured:

```js
{
  packetStillCaptured: true,
  hudVisible: false,
  sealStatus: "SEAL_BLOCKED_REVIEW_REQUIRED"
}
```

Operator UI control does not delete evidence.

---

## 4. Current Architecture

### 4.1 Backend route layer

Primary route file:

```text
server/routes/forensicRoutes.js
```

Production seal endpoint:

```http
POST /api/forensics/merkle-auditor/seal-safe-window
```

Current behavior:

1. Receives tenant seal request.
2. Attempts backend auditor-owned seal workflow.
3. If the auditor method is unavailable, falls back to route-level backend verifier.
4. Builds a seal decision packet.
5. Returns receipt contract, blockers, seal status, authority boundary, and safe-window counts.

Current route fallback authority:

```text
ROUTE_BACKEND_VERIFIER
```

This fallback is acceptable for the lab because it is still server-side. It is not browser authority.

### 4.2 Backend auditor layer

Primary service file:

```text
server/services/ForensicMerkleAuditor.js
```

Long-term production target:

```js
forensicMerkleAuditor.sealSafeReceiptWindow()
```

The auditor should eventually own:

1. Full chain replay.
2. Receipt Merkle root verification.
3. Review receipt resolution.
4. Seal eligibility decision.
5. Immutable append-only seal persistence.
6. External WORM or QLDB-style anchor integration if required.

### 4.3 Frontend bridge layer

Primary bridge file:

```text
client/src/services/wilsyForensicMerkleClient.js
```

Important bridge function:

```js
sealWilsyMerkleSafeWindow()
```

Function role:

1. Calls the backend seal-safe-window endpoint.
2. Sends tenant, limit, receiptLimit, actor, and reason.
3. Returns the backend seal packet.
4. Does not compute proof in the browser.
5. Does not certify immutability in the browser.

### 4.4 Frontend lab UI

Primary UI file:

```text
client/src/components/chrome/WilsyForensicMerkleShowroom.jsx
```

Primary behaviors:

1. Displays the Forensic Proof Lab.
2. Shows evidence lanes:
   - Root witness
   - Clause bound
   - Seal decision
3. Provides command buttons:
   - Explain Review
   - Copy Regulator Pack
   - Export Evidence Bundle
   - Run Full Proof
   - Request Backend Seal
4. Shows backend seal decision copy in readable form.
5. Shows a floating seal decision HUD.
6. Allows HUD dismissal without deleting the captured packet.

### 4.5 CSS presentation layer

Primary CSS file:

```text
client/src/components/chrome/WilsyForensicMerkleShowroom.module.css
```

CSS responsibility:

1. Keep the seal HUD above the fold.
2. Prevent the panel from becoming a bottom-wall debug dump.
3. Make the seal decision readable with DevTools open.
4. Preserve boardroom-grade contrast and hierarchy.
5. Keep the lab visually aligned with WILSY OS command-center quality.

---

## 5. User-Facing Product Language

Use this language for investor demos:

> The Forensic Proof Lab shows WILSY OS refusing to certify an unsafe evidence window. The system asks the backend whether the current receipt window can be sealed. The backend returns a decision, explains the blockers, confirms that browser seal authority is disabled, and keeps the evidence packet available even if the operator dismisses the HUD.

Avoid this language:

```text
“The browser seals the chain.”
“The UI proves immutability.”
“The current chain is fully sealed.”
“The root is verified, so the evidence is final.”
```

Use this language instead:

```text
“The backend seal decision is blocked for review.”
“The proof window is evidence-bound but not final-sealed.”
“The browser displays the decision but does not certify the seal.”
“The route verifier is currently the backend authority fallback.”
“The auditor service should become the final seal workflow owner.”
```

---

## 6. Current Operator Workflow

### 6.1 Open the lab

Route:

```text
/wilsy-lab/forensic-merkle
```

### 6.2 Run audit

Click:

```text
RUN AUDIT
```

Expected result:

```text
Verified records: 250
Receipts logged: 250
Hash method: SHA3-512
Review required
```

### 6.3 Request backend seal decision

Click:

```text
REQUEST BACKEND SEAL
```

Expected command-layer copy:

```text
Backend seal blocked · 3 blockers · chain not verified · review receipts present · receipts not backend sealed · Backend authority confirmed · Browser authority disabled
```

Expected HUD:

```text
Backend Seal Decision

Seal blocked for review

Backend blockers:
chain not verified · review receipts present · receipts not backend sealed

Next action:
resolve review receipts · replay backend chain · confirm receipt Merkle root · retry after verified audit

Authority boundary:
Backend authority: TRUE
Browser authority: FALSE · Route backend verifier

Receipts 250 · Review 250 · Sealed 0 · Clauses 1000
```

### 6.4 Dismiss HUD

Click:

```text
×
```

Expected:

```text
HUD disappears.
Backend evidence packet remains captured.
```

---

## 7. Browser Smoke Tests

### 7.1 Showroom version proof

```js
const showroom = await import('/src/components/chrome/WilsyForensicMerkleShowroom.jsx?t=' + Date.now());

({
  version: showroom.WILSY_FORENSIC_MERKLE_SHOWROOM_VERSION,
  labStatus: showroom.WILSY_FORENSIC_PROOF_LAB_STATUS,
  accountStatus: showroom.WILSY_FORENSIC_ACCOUNT_INTEGRATION_STATUS
});
```

Expected:

```js
{
  labStatus: "FORENSIC_PROOF_LAB_EXPERIMENTAL",
  accountStatus: "ACCOUNT_COMMAND_CENTER_CARD_PENDING"
}
```

### 7.2 Seal client proof

```js
const bridge = await import('/src/services/wilsyForensicMerkleClient.js');

({
  version: bridge.WILSY_FORENSIC_MERKLE_CLIENT_VERSION,
  sealClient: typeof bridge.sealWilsyMerkleSafeWindow
});
```

Expected:

```js
{
  sealClient: "function"
}
```

### 7.3 Backend seal live proof

```js
const bridge = await import('/src/services/wilsyForensicMerkleClient.js');

const seal = await bridge.sealWilsyMerkleSafeWindow({
  tenantId: 'wilsy-sovereign-root',
  limit: 250,
  receiptLimit: 3,
  actor: 'wilsy-founder-console',
  reason: 'SAFE_WINDOW_SEAL_REQUEST'
});

({
  routeVersion: seal.routeVersion,
  sealWorkflowVersion: seal.sealWorkflowVersion,
  immutableSeal: seal.immutableSeal,
  sealStatus: seal.sealStatus,
  canSeal: seal.sealDecision?.canSeal,
  blockers: seal.sealDecision?.eligibility?.blockers,
  backendAuthority: seal.productionSeal?.backendAuthority,
  browserAuthority: seal.productionSeal?.browserAuthority,
  fallbackAuthority: seal.productionSeal?.fallbackAuthority,
  receiptCount: seal.receiptContract?.receiptCount,
  reviewReceiptCount: seal.receiptContract?.reviewReceiptCount,
  clausesAnchored: seal.receiptContract?.clausesAnchored,
  receiptsReturned: seal.receipts?.length
});
```

Expected:

```js
{
  routeVersion: "R18P1-PRODUCTION-SEAL-FALLBACK",
  sealWorkflowVersion: "R18P1-PRODUCTION-SEAL-FALLBACK",
  immutableSeal: false,
  sealStatus: "SEAL_BLOCKED_REVIEW_REQUIRED",
  canSeal: false,
  blockers: [
    "CHAIN_NOT_VERIFIED",
    "REVIEW_RECEIPTS_PRESENT",
    "NOT_ALL_RECEIPTS_BACKEND_SEALED"
  ],
  backendAuthority: true,
  browserAuthority: false,
  fallbackAuthority: "ROUTE_BACKEND_VERIFIER",
  receiptCount: 250,
  reviewReceiptCount: 250,
  clausesAnchored: 1000,
  receiptsReturned: 3
}
```

### 7.4 HUD visible after backend seal request

After clicking `REQUEST BACKEND SEAL`:

```js
const dock = document.querySelector('[data-wilsy-seal-decision-panel-mounted="R18U"]');
const box = dock?.getBoundingClientRect();

({
  mounted: Boolean(dock),
  position: getComputedStyle(dock).position,
  top: Math.round(box?.top || 0),
  right: Math.round(window.innerWidth - (box?.right || 0)),
  height: Math.round(box?.height || 0),
  visibleAboveFold: Boolean(box && box.top < window.innerHeight * 0.55)
});
```

Expected:

```js
{
  mounted: true,
  position: "fixed",
  visibleAboveFold: true
}
```

### 7.5 HUD dismiss keeps evidence

After clicking the HUD `×`:

```js
({
  packetStillCaptured: Boolean(window.__wilsyLastSealDecision),
  hudVisible: Boolean(document.querySelector('[data-wilsy-seal-decision-panel-mounted="R18U"]')),
  sealStatus: window.__wilsyLastSealDecision?.sealStatus
});
```

Expected:

```js
{
  packetStillCaptured: true,
  hudVisible: false,
  sealStatus: "SEAL_BLOCKED_REVIEW_REQUIRED"
}
```

---

## 8. Backend API Contract

### 8.1 Seal safe window endpoint

```http
POST /api/forensics/merkle-auditor/seal-safe-window
Content-Type: application/json
X-Tenant-Id: wilsy-sovereign-root
```

Payload:

```json
{
  "tenantId": "wilsy-sovereign-root",
  "limit": 250,
  "receiptLimit": 3,
  "actor": "wilsy-founder-console",
  "reason": "SAFE_WINDOW_SEAL_REQUEST"
}
```

Expected response fields:

```json
{
  "routeVersion": "R18P1-PRODUCTION-SEAL-FALLBACK",
  "sealWorkflowVersion": "R18P1-PRODUCTION-SEAL-FALLBACK",
  "immutableSeal": false,
  "sealStatus": "SEAL_BLOCKED_REVIEW_REQUIRED",
  "sealDecision": {
    "canSeal": false,
    "eligibility": {
      "blockers": [
        "CHAIN_NOT_VERIFIED",
        "REVIEW_RECEIPTS_PRESENT",
        "NOT_ALL_RECEIPTS_BACKEND_SEALED"
      ]
    }
  },
  "productionSeal": {
    "backendAuthority": true,
    "browserAuthority": false,
    "fallbackAuthority": "ROUTE_BACKEND_VERIFIER"
  },
  "receiptContract": {
    "receiptCount": 250,
    "reviewReceiptCount": 250,
    "clausesAnchored": 1000
  }
}
```

---

## 9. Engineering Rules

### 9.1 Browser rule

The browser may:

```text
Request a seal decision.
Display a seal decision.
Export a regulator pack.
Show human-readable blockers.
Keep evidence packet after dismiss.
```

The browser may not:

```text
Claim immutable seal.
Create final seal authority.
Override backend blockers.
Convert review-required into sealed.
Hide backend authority boundary.
```

### 9.2 Backend rule

The backend must:

```text
Own seal decisions.
Own chain replay.
Own receipt counts.
Own blocker logic.
Own authority boundary.
Return browserAuthority: false.
```

### 9.3 Account Command Center rule

Do not integrate the full lab as a normal account panel.

The current state must remain:

```text
Forensic Proof Lab / Experimental
Account Command Center card pending
```

Only later add a compact card with:

```text
Last proof status
Safe-window receipt count
Clause bindings
Download regulator pack
Open forensic lab
```

The compact card must not recreate the full forensic cockpit inside Account Command Center.

---

## 10. Current Known Limitation

The system currently blocks sealing because review conditions remain:

```text
CHAIN_NOT_VERIFIED
REVIEW_RECEIPTS_PRESENT
NOT_ALL_RECEIPTS_BACKEND_SEALED
```

This is not a failure. It is a correct safety state.

Before WILSY OS can claim final immutable seal for this evidence window, backend remediation must resolve:

1. Chain verification.
2. Review receipt status.
3. Backend-sealed receipt completeness.
4. Final auditor-owned seal method.
5. Optional external append-only/WORM anchoring.

---

## 11. Production Roadmap

### Phase 1 — Freeze the lab

Current status:

```text
Done.
```

Freeze as:

```text
Forensic Proof Lab / Experimental
```

### Phase 2 — Document investor and engineering contract

Current status:

```text
This playbook.
```

### Phase 3 — Add compact Account Command Center card

Do not integrate the full lab.

Add only a compact card:

```text
Last proof status: Review required
Safe-window receipts: 250
Clause bindings: 1000
Backend authority: true
Browser authority: false
Actions:
- Download regulator pack
- Open forensic lab
```

### Phase 4 — Auditor-owned seal service

Move final seal workflow into:

```text
server/services/ForensicMerkleAuditor.js
```

Target function:

```js
sealSafeReceiptWindow()
```

Route fallback should remain for resilience, but final authority should become auditor-owned.

### Phase 5 — External append-only anchor

Add optional external anchor layer:

```text
WORM storage
QLDB-style journal
S3 Object Lock
External timestamp authority
```

### Phase 6 — Regulator-grade export

Regulator pack should include:

```text
Seal status
Receipt manifest
Receipt Merkle root
Backend blockers
Clause bindings
Tenant id
Actor
Timestamp
Route/auditor version
Browser authority disabled proof
```

---

## 12. Investor Narrative

WILSY OS is building a compliance operating layer where work is not merely completed but evidenced.

The Forensic Proof Lab demonstrates a key product principle:

> The system must be willing to say “not sealed yet” when evidence is not safe to certify.

That is valuable for regulated customers because false certainty is dangerous. WILSY OS is designed to expose proof posture, identify blockers, preserve evidence packets, and keep final proof authority in backend-controlled services.

This gives WILSY OS a differentiated foundation for:

```text
Legal operations
Compliance operations
Audit trails
Regulator packs
Enterprise governance
Tenant-specific forensic records
Founder/operator proof dashboards
```

---

## 13. Engineer Acceptance Criteria

The feature is acceptable only if all these remain true:

```text
[ ] The lab route loads.
[ ] RUN AUDIT returns proof data.
[ ] REQUEST BACKEND SEAL calls the backend endpoint.
[ ] Backend returns SEAL_BLOCKED_REVIEW_REQUIRED.
[ ] Browser authority is false.
[ ] Backend authority is true.
[ ] HUD opens after backend seal request.
[ ] HUD is dismissible.
[ ] Evidence packet remains after dismiss.
[ ] Command copy is human-readable.
[ ] Full raw blockers remain available in the packet.
[ ] The lab remains experimental.
[ ] Account Command Center integration remains pending.
```

---

## 14. Guard And Build Commands

Run from repo root:

```bash
cd /Users/wilsonkhanyezi/legal-doc-system

node scripts/wilsy-secret-guard.js server/routes/forensicRoutes.js
node scripts/wilsy-documentation-guard.js server/routes/forensicRoutes.js
node --check server/routes/forensicRoutes.js

node scripts/wilsy-secret-guard.js client/src/services/wilsyForensicMerkleClient.js
node scripts/wilsy-documentation-guard.js client/src/services/wilsyForensicMerkleClient.js

node scripts/wilsy-secret-guard.js client/src/components/chrome/WilsyForensicMerkleShowroom.jsx
node scripts/wilsy-documentation-guard.js client/src/components/chrome/WilsyForensicMerkleShowroom.jsx

node scripts/wilsy-secret-guard.js client/src/components/chrome/WilsyForensicMerkleShowroom.module.css

if [ -f scripts/wilsy-chrome-mandate-guard.js ]; then
  node scripts/wilsy-chrome-mandate-guard.js client/src/components/chrome/WilsyForensicMerkleShowroom.jsx
fi

cd client
npm run build
```

---

## 15. Current Freeze Statement

The current Forensic Proof Lab should be frozen as:

```text
WILSY OS Forensic Proof Lab
Status: Experimental
Purpose: Backend-owned evidence proof and seal-decision cockpit
Account Command Center status: Compact card pending
Final seal authority: Backend only
Browser seal authority: Disabled
Current seal result: Review required
Reason: Chain not verified, review receipts present, not all receipts backend sealed
```
