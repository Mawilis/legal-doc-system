const express = require('express');
const router = express.Router();
const controller = require('../controllers/attemptController');
router.post('/dispatch-instructions/:id/attempts', controller.createAttempt);
router.get('/dispatch-instructions/:id/attempts', controller.listAttempts);
module.exports = router;
