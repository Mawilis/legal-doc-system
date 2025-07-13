const express = require('express');
const { summarizeText } = require('../controllers/aiController');
const { protect } = require('../middleware/auth');  // ✅ Updated import path to match modular auth structure

const router = express.Router();

// AI summarization route, protected so only authenticated users can use it
/**
 * @swagger
 * /api/ai/summarize:
 *   post:
 *     summary: Summarize text using the AI summarization feature
 *     description: Accepts a text input and returns a summarized version using the AI engine.
 *     tags:
 *       - AI
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - text
 *             properties:
 *               text:
 *                 type: string
 *                 example: "This is a long paragraph of text that the AI will summarize for you."
 *     responses:
 *       200:
 *         description: Summarization successful. Returns the summarized text.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 summary:
 *                   type: string
 *                   example: "This is the summarized version of your text."
 *       400:
 *         description: Bad request. Input text is missing or invalid.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router.post('/summarize', protect, summarizeText);

module.exports = router;
