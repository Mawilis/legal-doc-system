const express = require('express');
const {
    updateDetails,
    updatePassword,
} = require('../controllers/settingsController');
const { protect } = require('../middleware/auth');  // ✅ Updated path for modular auth

const router = express.Router();

router.use(protect);

/**
 * @swagger
 * /api/settings/updatedetails:
 *   put:
 *     summary: Update user details
 *     description: Updates the authenticated user's non-sensitive details (e.g., name, email).
 *     tags:
 *       - Settings
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *                 example: Jane Doe
 *               email:
 *                 type: string
 *                 format: email
 *                 example: jane.doe@example.com
 *     responses:
 *       200:
 *         description: User details updated successfully.
 *       400:
 *         description: Bad request. Invalid data.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router.put('/updatedetails', updateDetails);

/**
 * @swagger
 * /api/settings/updatepassword:
 *   put:
 *     summary: Update user password
 *     description: Updates the authenticated user's password securely.
 *     tags:
 *       - Settings
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - currentPassword
 *               - newPassword
 *             properties:
 *               currentPassword:
 *                 type: string
 *                 format: password
 *                 example: OldP@ssw0rd
 *               newPassword:
 *                 type: string
 *                 format: password
 *                 example: NewP@ssw0rd123
 *     responses:
 *       200:
 *         description: Password updated successfully.
 *       400:
 *         description: Bad request. Invalid password data.
 *       401:
 *         description: Unauthorized. Token is missing or invalid.
 */
router.put('/updatepassword', updatePassword);

module.exports = router;
