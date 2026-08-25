/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Conversation History Routes (Kennel Phase 5)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/routes/conversationHistoryRoutes.js
 * Version:        v5.0.0-KENNEL-PHASE5
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Tenant‑scoped conversation history endpoints for the
 *                 Wilsy OS AI dock. Replaces localStorage with durable,
 *                 auditable, and isolated storage per tenant.
 * Classification: Production Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated history move to server.
 *   - AI Engineering – Phase 5: routes and controller integration.
 *
 * Change Log:
 *   2026-08-04 v5.0.0-KENNEL-PHASE5 — Initial creation; full CRUD for threads.
 *
 * Forensic Relationships:
 *   Upstream:   controllers/conversationHistoryController.js
 *   Downstream: client/src/components/intelligence/wilsyAIConversationHistoryEngine.js
 *   Kennel:     tenantGuard, sovereignAuthenticate
 *
 * Certification Seal: PRODUCTION_READY_v5.0.0-KENNEL-PHASE5
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import express from 'express';
import { sovereignAuthenticate } from '../middleware/auth.js';
import { tenantGuard } from '../middleware/tenantGuard.js';
import * as conversationController from '../controllers/conversationHistoryController.js';

const router = express.Router();

// ────────────────────────────────────────────────────────────────────────────
// 🏛️ SOVEREIGN ROUTES — All require authentication and tenant isolation
// ────────────────────────────────────────────────────────────────────────────

/**
 * GET /api/ai/conversations
 * @description Retrieve all conversation threads for the current tenant.
 * @returns {Object} { threads: Array }
 * @collaboration Wilsy AI dock, tenant isolation.
 */
router.get(
  '/',
  sovereignAuthenticate,
  tenantGuard,
  conversationController.getThreads
);

/**
 * POST /api/ai/conversations
 * @description Create a new conversation thread for the current tenant.
 * @body { title, workspace, createdAt, updatedAt, turns? }
 * @returns {Object} { thread: Object }
 * @collaboration Wilsy AI "New Chat" action.
 */
router.post(
  '/',
  sovereignAuthenticate,
  tenantGuard,
  conversationController.createThread
);

/**
 * PUT /api/ai/conversations/:id
 * @description Update an existing thread (add a turn, update metadata).
 * @body { title, workspace, turns, updatedAt }
 * @returns {Object} { thread: Object }
 * @collaboration Wilsy AI turn persistence.
 */
router.put(
  '/:id',
  sovereignAuthenticate,
  tenantGuard,
  conversationController.updateThread
);

/**
 * DELETE /api/ai/conversations
 * @description Delete all conversation threads for the current tenant.
 * @returns {Object} { success: true, message: string }
 * @collaboration Wilsy AI "Clear History" action.
 */
router.delete(
  '/',
  sovereignAuthenticate,
  tenantGuard,
  conversationController.clearThreads
);

/**
 * DELETE /api/ai/conversations/:id
 * @description Delete a single conversation thread.
 * @returns {Object} { success: true, message: string }
 * @collaboration Wilsy AI thread deletion.
 */
router.delete(
  '/:id',
  sovereignAuthenticate,
  tenantGuard,
  conversationController.deleteThread
);

export default router;

/*
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — Routes v5.0.0-KENNEL-PHASE5
 * ═══════════════════════════════════════════════════════════════════════════════
 * All routes enforce authentication and tenant isolation.
 * Next: implement the controller logic in conversationHistoryController.js.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
