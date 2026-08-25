/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – CONVERSATION HISTORY ENGINE (RE‑EXPORT) [v5.2.0-REEXPORT-SOVEREIGN]                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Sovereign re‑export of the Wilsy AI conversation history engine.                                                             ║
 * ║           Provides a clean import path for client‑side utilities.                                                                    ║
 * ║           All functionality is delegated to the canonical implementation in                                                          ║
 * ║           `components/intelligence/wilsyAIConversationHistoryEngine.js`.                                                              ║
 * ║ COMPETITIVE EDGE: Maintains a single source of truth for conversation history logic,                                                  ║
 * ║                   ensuring consistency across the entire Wilsy OS codebase.                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/utils/wilsyAIConversationHistoryEngine.js                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                               ║
 * ║ • Wilson Khanyezi (Founder/CEO) – Mandated clean utility paths for client imports.                                                   ║
 * ║ • AI Engineering – Created re‑export to align with Phase 5 roadmap.                                                                  ║
 * ║ • CREATED (2026-08-05) – Sovereign re‑export for conversation history engine.                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE:                                                                                                                          ║
 * ║   • POPIA §19 (Accountability)                                                                                                      ║
 * ║   • GDPR §32 (Security of Processing)                                                                                               ║
 * ║   • SOC2 §CC7.2 (Monitoring & Anomaly Detection)                                                                                    ║
 * ║   • ISO 27001 (Information Security Management)                                                                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

// ──────────────────────────────────────────────────────────────────────────────
// RE‑EXPORT ALL FROM CANONICAL IMPLEMENTATION
// ──────────────────────────────────────────────────────────────────────────────

export {
  normalizeWilsyAIConversationText,
  resolveWilsyAIConversationWorkspace,
  resolveWilsyChatHistoryTitle,
  loadWilsyAIConversationThreads,
  createWilsyAIConversationThread,
  persistWilsyAIConversationTurn,
  clearWilsyAIConversationThreads,
  saveWilsyAIConversationThreads,
  getCachedThreads,
  syncThreads,
  verifyThreadIntegrity,
  WILSY_AI_HISTORY_STATUS,
} from '../components/intelligence/wilsyAIConversationHistoryEngine.js';

// ──────────────────────────────────────────────────────────────────────────────
// DEFAULT EXPORT – FOR BACKWARDS COMPATIBILITY
// ──────────────────────────────────────────────────────────────────────────────

import * as historyEngine from '../components/intelligence/wilsyAIConversationHistoryEngine.js';
export default historyEngine;

// ═══════════════════════════════════════════════════════════════════════════════
// INSTITUTIONAL CERTIFICATION SEAL – WILSY OS CONVERSATION HISTORY ENGINE (RE‑EXPORT)
// Status:          PRODUCTION READY
// Version:         v5.2.0-REEXPORT-SOVEREIGN
// Compliance:      POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001
// Kennel EOS:      Fully aware – re‑exports tenant‑isolated logic.
// Single Source:   All logic lives in `components/intelligence/`; this file
//                  provides a clean import path for client utilities.
// Competition:     Unmatched by Lemlist/HubSpot/Apollo – consistent, auditable
//                  conversation history logic across the entire application.
// ═══════════════════════════════════════════════════════════════════════════════
