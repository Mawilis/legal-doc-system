/* eslint-disable */
import express from 'express';
import { onboardTenant, getTenantHealth } from '../../controllers/admin/TenantManagement.controller.js';

const router = express.Router();

router.post('/onboard', onboardTenant);
router.get('/health/:tenantId', getTenantHealth);

export default router;
