/* eslint-disable */
import express from 'express';
import { getTenantWorkspace } from '../../controllers/tenant/ClientPortal.controller.js';

const router = express.Router();

router.get('/workspace/:tenantId', getTenantWorkspace);

export default router;
