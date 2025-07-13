const express = require('express');
const {
    createInstruction,
    getAllInstructions,
    getInstructionById,
    updateInstruction,
    deleteInstruction,
} = require('../controllers/instructionController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated to modular auth import

const router = express.Router();

router.use(protect);

/**
 * @swagger
 * /api/instructions:
 *   post:
 *     summary: Create a new instruction
 *     description: Creates a new instruction entry in the system.
 *     tags:
 *       - Instructions
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - title
 *               - content
 *             properties:
 *               title:
 *                 type: string
 *                 example: Safety Protocol
 *               content:
 *                 type: string
 *                 example: Always wear protective gear when entering the lab.
 *     responses:
 *       201:
 *         description: Instruction created successfully.
 *       400:
 *         description: Bad request. Invalid or missing data.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 * 
 *   get:
 *     summary: Get all instructions
 *     description: Retrieves a list of all instructions.
 *     tags:
 *       - Instructions
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of instructions retrieved successfully.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router
    .route('/')
    .post(createInstruction)
    .get(getAllInstructions);

/**
 * @swagger
 * /api/instructions/{id}:
 *   get:
 *     summary: Get an instruction by ID
 *     description: Retrieves a specific instruction by its ID.
 *     tags:
 *       - Instructions
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The ID of the instruction.
 *     responses:
 *       200:
 *         description: Instruction retrieved successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       404:
 *         description: Instruction not found.
 * 
 *   put:
 *     summary: Update an instruction
 *     description: Updates the details of an existing instruction.
 *     tags:
 *       - Instructions
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The ID of the instruction.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               title:
 *                 type: string
 *                 example: Updated Safety Protocol
 *               content:
 *                 type: string
 *                 example: Updated instruction content here.
 *     responses:
 *       200:
 *         description: Instruction updated successfully.
 *       400:
 *         description: Bad request. Invalid data or ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       404:
 *         description: Instruction not found.
 * 
 *   delete:
 *     summary: Delete an instruction
 *     description: Deletes an instruction by its ID (admin only).
 *     tags:
 *       - Instructions
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: The ID of the instruction.
 *     responses:
 *       200:
 *         description: Instruction deleted successfully.
 *       400:
 *         description: Bad request. Invalid ID.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 *       403:
 *         description: Forbidden. Admin access required.
 *       404:
 *         description: Instruction not found.
 */
router
    .route('/:id')
    .get(getInstructionById)
    .put(updateInstruction)
    .delete(authorize('admin'), deleteInstruction);

module.exports = router;
