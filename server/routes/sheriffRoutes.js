import { createRequire as _createRequire } from 'module';
const require = _createRequire(import.meta.url);
const express = require('express');

const router = express.Router();
router.get('/', (req, res) => res.json({ msg: 'Sheriff Route OK' }));
export default router;
