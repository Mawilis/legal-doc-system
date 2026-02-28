/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ COURT ROUTES - COMPLETE SA JUDICIAL MANAGEMENT API                                    ║
  ║ R4.5M/year operational savings | Jurisdiction AI | Appeal Routing                     ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/courtRoutes.js
 * VERSION: 1.0.0-PRODUCTION
 * CREATED: 2026-02-28
 */

import express from 'express';
import {
  createCourt,
  getCourt,
  updateCourt,
  listCourts,
  checkJurisdiction,
  getAppealRoute,
  addJudicialOfficer,
  getHierarchy,
  getCourtStats,
  addPracticeDirective
} from '../controllers/courtController.js';
import { authenticate } from '../middleware/auth.js';
import { extractTenant } from '../middleware/tenantContext.js';
import { rateLimiter } from '../middleware/rateLimiter.js';
import { validateRequest } from '../middleware/requestValidator.js';

const router = express.Router();

// Apply common middleware
router.use(extractTenant);
router.use(authenticate({ required: true }));

// Rate limiting
const standardLimiter = rateLimiter({ mode: 'standard' });
const strictLimiter = rateLimiter({ mode: 'strict' });

/**
 * @openapi
 * /api/courts:
 *   post:
 *     summary: Create a new court
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - category
 *               - name
 *             properties:
 *               category:
 *                 type: string
 *               name:
 *                 type: string
 *               tier:
 *                 type: string
 *     responses:
 *       201:
 *         description: Court created successfully
 */
router.post('/', standardLimiter, createCourt);

/**
 * @openapi
 * /api/courts:
 *   get:
 *     summary: List courts with filtering
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     parameters:
 *       - in: query
 *         name: tier
 *         schema:
 *           type: string
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *       - in: query
 *         name: province
 *         schema:
 *           type: string
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *     responses:
 *       200:
 *         description: List of courts
 */
router.get('/', standardLimiter, listCourts);

/**
 * @openapi
 * /api/courts/hierarchy:
 *   get:
 *     summary: Get full court hierarchy
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     responses:
 *       200:
 *         description: Court hierarchy tree
 */
router.get('/hierarchy', standardLimiter, getHierarchy);

/**
 * @openapi
 * /api/courts/stats:
 *   get:
 *     summary: Get court statistics
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     responses:
 *       200:
 *         description: Court statistics
 */
router.get('/stats', standardLimiter, getCourtStats);

/**
 * @openapi
 * /api/courts/{courtId}:
 *   get:
 *     summary: Get court by ID
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     parameters:
 *       - in: path
 *         name: courtId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Court details
 */
router.get('/:courtId', standardLimiter, getCourt);

/**
 * @openapi
 * /api/courts/{courtId}:
 *   put:
 *     summary: Update court
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     parameters:
 *       - in: path
 *         name: courtId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *     responses:
 *       200:
 *         description: Court updated
 */
router.put('/:courtId', standardLimiter, updateCourt);

/**
 * @openapi
 * /api/courts/{courtId}/appeal-route:
 *   get:
 *     summary: Get appeal route for a court
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     parameters:
 *       - in: path
 *         name: courtId
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Appeal route
 */
router.get('/:courtId/appeal-route', standardLimiter, getAppealRoute);

/**
 * @openapi
 * /api/courts/{courtId}/judicial-officers:
 *   post:
 *     summary: Add judicial officer to court
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     parameters:
 *       - in: path
 *         name: courtId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *               - title
 *             properties:
 *               name:
 *                 type: string
 *               title:
 *                 type: string
 *               appointmentDate:
 *                 type: string
 *                 format: date
 *     responses:
 *       201:
 *         description: Judicial officer added
 */
router.post('/:courtId/judicial-officers', standardLimiter, addJudicialOfficer);

/**
 * @openapi
 * /api/courts/{courtId}/practice-directives:
 *   post:
 *     summary: Add practice directive to court
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     parameters:
 *       - in: path
 *         name: courtId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - title
 *               - summary
 *             properties:
 *               title:
 *                 type: string
 *               summary:
 *                 type: string
 *               documentUrl:
 *                 type: string
 *     responses:
 *       201:
 *         description: Practice directive added
 */
router.post('/:courtId/practice-directives', standardLimiter, addPracticeDirective);

/**
 * @openapi
 * /api/courts/jurisdiction/check:
 *   post:
 *     summary: Check jurisdiction for a case
 *     tags: [Courts]
 *     security:
 *       - bearerAuth: []
 *       - tenantAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - type
 *             properties:
 *               type:
 *                 type: string
 *                 enum: [civil, criminal, constitutional, labour, land, electoral]
 *               value:
 *                 type: number
 *               location:
 *                 type: object
 *               isAppeal:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Jurisdiction check results
 */
router.post('/jurisdiction/check', strictLimiter, checkJurisdiction);

export default router;
