const express = require('express');
const router = express.Router();
const controller = require('../controllers/returnController');
router.post('/dispatch-instructions/:id/returns/generate', controller.generateReturns);
module.exports = router;
