# WILSY Legal Operations — competitive benchmark and product strategy

**Research date:** 2 November 2026  
**Market focus:** South African sheriff/process-service workflows, with international process-serving platforms as capability benchmarks.  
**Status:** Public-source desk research; vendor claims are not independently audited.

## Executive position

WILSY should not try to win by claiming that it has GPS, photos, a mobile dashboard or digital returns. Competitors already market those capabilities. The defensible position is:

> **A South African legal-operations system that connects the instruction, canonical assignment, Deputy field work, evidence custody and Sheriff-controlled return workflow—with independently verifiable provenance and office-scoped authority.**

The product must support the authorised Sheriff and Deputy. It must never imply that a GPS fix, device signature or workflow status independently proves that service was legally valid. The authorised officer's evidence and return remain the operative legal acts.

## Competitor benchmark

| Competitor | Publicly marketed capabilities | Competitive threat |
|---|---|---|
| **Prosource PLDS (South Africa)** | Cloud legal-document workflow; law firms, correspondents, delivery agents and courts; real-time status; mobile app/web portal; GPS-stamped delivery confirmation; return-of-service capture; image attachments; notifications; per-matter audit history; correspondent/court linking and a marketed 15 km rule. | **Highest local workflow threat.** It is already tailored to South African legal-document delivery and markets the complete instruction-to-return chain. |
| **ServeManager (international)** | GPS service attempts; mobile app; maps/routes; electronic signatures; photos; affidavits/proofs; client collaboration; API/Zapier integrations; job/portfolio management and invoicing. Its current support material says the app syncs attempts, photos and signatures in real time. | **Strong operational benchmark.** It covers the daily process-server workflow and integrations, not merely evidence capture. |
| **ServeManager — October 2026 integrity updates** | October 1 update: in-app-only attempt photos, required current app version and automated GPS/time/photo checks. October 15 v1.22.4: fresh GPS at attempt/photo capture, rejects mock locations, shows GPS quality and photo metadata/distance, and restricts partner-job retries to the original failed media. | **Very high evidence-integrity bar.** WILSY's browser-key signature proves payload integrity, but does not yet match native GPS anti-spoofing, camera-only media capture or original-file retry controls. |
| **Proof** | Mobile job allocation and routing to nearby/available servers; exclusive job offer windows; mobile attempts, photo uploads, affidavits and client/server communications; browser-based client access. | **Strong network and distribution threat.** Its marketplace and routing network are as important as its mobile feature set. |

### Public sources

- [Prosource PLDS](https://www.prosource.co.za/) — South African platform description, mobile access, GPS-stamped confirmation, return capture, audit and 15 km correspondent/court rules.
- [ServeManager mobile FAQ](https://support.servemanager.com/articles/mobile-app-faqs/) — mobile attempts, GPS/map tracking, photos, signatures and real-time sync.
- [ServeManager October 2026 safeguards](https://www.servemanager.com/blog/3413/new-safeguards-that-protect-honest-process-servers) — in-app photos and automated GPS/time/photo checks, dated 1 October 2026.
- [ServeManager Mobile App 1.22.4 release notes](https://www.servemanager.com/blog/3415/mobile-app-1-22-4-release-notes) — fresh GPS, mock-location rejection, GPS quality checks, photo GPS metadata and original-file-only retries, dated 15 October 2026.
- [ServeManager public pricing](https://app.servemanager.com/pricing) — public US-dollar volume tiers and advertised integrations/features; not a South African price benchmark.
- [Proof: how the platform works](https://help.proofserve.com/server/en/articles/7950703-how-does-proof-work) — location/availability-based job offers and mobile app.
- [Proof mobile app](https://help.proofserve.com/server/en/articles/8475023-how-do-i-download-the-proof-mobile-app) — attempts, photos, affidavits and client communications.

Public product pages describe vendor capabilities, not independent accuracy, legal admissibility, security or uptime. WILSY should not publish comparative performance claims without controlled testing.

## What WILSY has that can become a moat

1. **Canonical legal lifecycle:** connect instruction, current allocation, attempt, execution and return-of-service evidence rather than treating each GPS/photo event as a standalone job record.
2. **Authority-bound field work:** server-derived tenant, principal, Deputy and current-session scope; no caller-supplied Deputy identity.
3. **Signed evidence facts:** P-256 device-key proof plus a second signature over the exact attempt, grant, coordinates, accuracy and capture time. This detects post-signing payload changes.
4. **Purpose-limited collection:** explicit one-shot location capture, short-lived permission grant and append-only revocation; no continuous tracking.
5. **Office-aware disclosure:** Deputy personal visibility and Sheriff-office scoping that fails closed when the tenant has multiple offices but no office-specific binding.
6. **Audit and chain-of-custody:** immutable source fingerprints, exact replay rules, transaction boundaries and metadata-only access events.

These are architectural advantages, not yet proof of market leadership. They become a moat only after production operations, customer adoption, court-facing workflows and independent security testing are complete.

## Gaps that still prevent a credible “market leader” claim

| Gap | Why it matters | Required completion gate |
|---|---|---|
| Offline location capture and sync | Field work happens in poor-connectivity areas. Current GPS capture needs a live API round trip and is not an offline queue. | Device-signed offline event journal, bounded offline permit, replay-safe batch sync, clock/timestamp policy, conflict handling and real-device tests. |
| Retention, deletion and legal hold | GPS is personal information. No universal retention duration should be guessed. | Tenant-approved retention policy, per-record expiry, legal-hold/restriction events, scheduled deletion/de-identification, audit of purge and restoration controls. |
| Multi-office Sheriff authority | Tenant-level Sheriff role is not enough to identify which office may see which attempt. | Canonical Sheriff-principal-to-office binding with independent approval and adversarial cross-office tests. Current read path denies multi-office tenants. |
| Native capture integrity | Browser geolocation and a browser-held key do not attest that the physical GPS sensor or operating system is genuine. | Native mobile app, hardware-backed key where supported, in-app camera capture, media hashing and anti-tamper checks. |
| Complete returns workflow | GPS evidence must not be mistaken for a valid return or substitute for the Sheriff's statutory act. | Jurisdiction-aware return templates, authorised signing, review/approval, court filing/export and immutable amendment history. |
| Routing and address intelligence | Competitors market maps, route planning and address validation. | Verified address quality, district/court rules, safe route planning and measurable failed-service reduction. |
| Client and correspondent experience | Status visibility, notifications and integrations are now baseline. | Client/correspondent portal, consent-aware notifications, API/webhooks, export and integration governance. |
| Production operations | Green unit tests are not production proof. | Load, latency, availability, backup/restore, incident response, security review and pilot acceptance. |

## Privacy and legal design constraint

POPIA section 14 says personal information must not be retained longer than necessary for the collection/processing purpose, subject to specified legal, lawful-function, contractual and consent grounds. It also requires destruction/deletion or de-identification when retention is no longer authorised, and recognises restriction where information must be retained for proof.

Source: [POPIA section 14 — Retention and restriction of records](https://popia.co.za/section-14-retention-and-restriction-of-records/).

Therefore:
- Do not hard-code an arbitrary 1-, 3-, 5- or 7-year GPS retention period.
- Require each tenant to approve a documented retention basis and duration with South African legal/privacy review.
- Treat permission withdrawal as stopping future collection; do not silently erase evidence that must lawfully be retained for proof.
- Support legal hold/restriction and log every access, export, purge and restoration.
- Keep location collection one-shot and attempt-bound. Do not add continuous employee tracking as a default.

This document is product research, not legal advice or a finding that WILSY or any competitor complies with POPIA.

## Recommended 90-day execution sequence

### Days 0–30: close trust and governance gaps
- Complete the durable location registry, signed GPS payload, permission/revocation lifecycle and authenticated API.
- Implement tenant retention policy + expiry + legal hold + auditable purge before production location data is enabled.
- Implement Sheriff principal-to-office binding; remove the single-office-only temporary gate.
- Implement offline signed event queue and replay-safe sync.
- Complete Mongo replica-set transaction tests and cross-tenant/cross-office tests.

### Days 31–60: close field-work parity gaps
- Build native iOS/Android capture or a managed PWA with tested offline persistence.
- Capture photos in-app; hash media at capture; prohibit arbitrary camera-roll substitution where operationally appropriate.
- Add route planning, address validation and district/court assignment constraints.
- Complete return-of-service templates, authorised signing and review workflow.

### Days 61–90: win distribution and measurable outcomes
- Launch client and correspondent portals with permissioned status and evidence views.
- Add webhooks/API integrations and reliable notifications.
- Pilot with a small number of Sheriff offices and instructing firms; measure completion time, failed attempts, return corrections, evidence disputes and support burden.
- Publish only independently measured performance and security results.

## Product KPIs

- Median time from accepted instruction to first attempt.
- Median time from final attempt to reviewed return of service.
- First-attempt completion rate, segmented by district and address quality.
- Return correction/rejection rate.
- GPS evidence signature verification failure rate.
- Offline queue sync success and duplicate/replay rejection rate.
- Evidence access/export audit completeness.
- Retention-policy compliance and purge latency.
- Cross-office access denials and confirmed zero unauthorised disclosures.
- Pilot customer activation, weekly active Deputies, customer retention and cost per completed matter.

## Competitive strategy

**Do not copy the whole competitor surface at once.** Win the high-trust legal-operational core first: canonical workflow, verified authority, evidence integrity, privacy and return-of-service correctness. Then close mobile/offline parity and distribution. This gives WILSY a credible route to compete with Prosource locally and with ServeManager/Proof on field operations—without making unsupported claims about legal validity or competitor weakness.

---
**Document owner:** WILSY Legal Operations Product & Engineering  
**Version:** v1.0.0 — 2026-11-02
