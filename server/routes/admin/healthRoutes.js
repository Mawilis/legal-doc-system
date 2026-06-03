/* eslint-disable */
import express from 'express';
import { getSystemVitality } from '../../controllers/admin/SystemHealth.controller.js';

const router = express.Router();

router.get('/vitality', getSystemVitality);

export default router;
