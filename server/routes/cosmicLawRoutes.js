import { createRequire as _createRequire } from 'module';
const require = _createRequire(import.meta.url);
const express = require('express');

const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    status: 'active',
    message: 'Cosmic law enforcement API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

export default router;
