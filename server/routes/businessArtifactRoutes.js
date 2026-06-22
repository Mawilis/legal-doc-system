/* eslint-disable */
/**
 * WILSY OS - BUSINESS ARTIFACT ROUTES [V1.3.0-SECURE-BROWSER-INGRESS]
 * Absolute Path: /Users/wilsonkhanyezi/legal-doc-system/server/routes/businessArtifactRoutes.js
 */

import express from 'express';
import { generateSovereignArtifact } from '../controllers/artifactController.js';
import { verifyBusinessArtifactIngress } from '../middleware/businessArtifactIngress.js';

const router = express.Router();

/**
 * @function businessArtifactHealth
 * @description Reports secure business artifact route health.
 * @returns {import('express').Router} Express router.
 * @collaboration Gives a lightweight proof that the secure browser ingress route is mounted.
 */
router.get('/health', (_req, res) => {
  res.json({
    success: true,
    service: 'WILSY_BUSINESS_ARTIFACT_INGRESS',
    version: '1.3.0',
    status: 'ONLINE',
  });
});

/**
 * @function postBusinessArtifactPdf
 * @description Generates sealed business artifact PDFs through verified browser-safe artifact ingress.
 * @returns {import('express').Router} Express router.
 * @collaboration Separates browser proof admission from server-side HMAC artifact sealing without bypassing Wilsy OS security.
 */
router.post(
  '/pdf',
  express.json({ limit: '25mb', strict: true }),
  express.urlencoded({ extended: true, limit: '25mb' }),
  verifyBusinessArtifactIngress,
  generateSovereignArtifact
);

export default router;
