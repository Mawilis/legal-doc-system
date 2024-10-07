const express = require('express');
const passwordController = require('../controllers/passwordController');
const router = express.Router();

router.post('/request-reset', passwordController.requestPasswordReset);
router.post('/reset/:token', passwordController.resetPassword);

module.exports = router;
