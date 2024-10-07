// instructionRoutes.js
const express = require('express');
const instructionController = require('../controllers/instructionController');
const authController = require('../controllers/authController');
const router = express.Router();

// Protected routes for instruction management
router.use(authController.protect);

router.post('/', instructionController.createInstruction);
router.get('/:instructionId', instructionController.getInstructionById);
router.get('/', instructionController.getAllInstructions);
router.put('/:instructionId', instructionController.updateInstruction);
router.delete('/:instructionId', instructionController.deleteInstruction);

module.exports = router;
