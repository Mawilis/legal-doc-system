import { createRequire as _createRequire } from 'module';
const require = _createRequire(import.meta.url);
const express = require('express');

const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    status: 'active',
    message: 'Firm management API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// Add more routes as needed

export default router;
