const express = require('express');
const router = express.Router();
const controller = require('../controllers/dispatchInstructionController');

router.post('/dispatch-instructions', controller.createInstruction);
router.get('/dispatch-instructions', controller.listInstructions);
router.get('/dispatch-instructions/:id', controller.getInstruction);

module.exports = router;
