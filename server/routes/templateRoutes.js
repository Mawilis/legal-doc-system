const express = require('express');
const {
    createTemplate,
    getAllTemplates,
    getTemplateById,
    updateTemplate,
    deleteTemplate,
} = require('../controllers/templateController');
const { protect, authorize } = require('../middleware/auth');  // ✅ Updated modular auth

const router = express.Router();

// All routes require admin privileges
router.use(protect);
router.use(authorize('admin'));

/**
 * @swagger
 * /api/templates:
 *   post:
 *     summary: Create a new document template
 *     tags:
 *       - Templates
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *               - description
 *               - fields
 *             properties:
 *               name:
 *                 type: string
 *                 example: Court Filing Template
 *               description:
 *                 type: string
 *                 example: Template for standard court filings
 *               fields:
 *                 type: array
 *                 items:
 *                   type: object
 *                   required:
 *                     - name
 *                     - label
 *                     - fieldType
 *                   properties:
 *                     name:
 *                       type: string
 *                       example: plaintiff_name
 *                     label:
 *                       type: string
 *                       example: Plaintiff Name
 *                     fieldType:
 *                       type: string
 *                       enum: [text, textarea, date, number, dropdown]
 *                       example: text
 *                     options:
 *                       type: array
 *                       items:
 *                         type: string
 *                     required:
 *                       type: boolean
 *     responses:
 *       201:
 *         description: Template created successfully.
 *       400:
 *         description: Bad request. Validation failed.
 *   get:
 *     summary: Retrieve all templates
 *     tags:
 *       - Templates
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of templates retrieved successfully.
 */
router.route('/')
    .post(createTemplate)
    .get(getAllTemplates);

/**
 * @swagger
 * /api/templates/{id}:
 *   get:
 *     summary: Get a single template by ID
 *     tags:
 *       - Templates
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Template retrieved successfully.
 *       404:
 *         description: Template not found.
 *   put:
 *     summary: Update a template
 *     tags:
 *       - Templates
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *               description:
 *                 type: string
 *               fields:
 *                 type: array
 *                 items:
 *                   type: object
 *     responses:
 *       200:
 *         description: Template updated successfully.
 *       403:
 *         description: Unauthorized to update.
 *       404:
 *         description: Template not found.
 *   delete:
 *     summary: Delete a template
 *     tags:
 *       - Templates
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Template deleted successfully.
 *       403:
 *         description: Unauthorized to delete.
 *       404:
 *         description: Template not found.
 */
router.route('/:id')
    .get(getTemplateById)
    .put(updateTemplate)
    .delete(deleteTemplate);

module.exports = router;
