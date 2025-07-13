const express = require('express');
const {
    forgotPassword,
    resetPassword,
} = require('../controllers/passwordController');

const router = express.Router();

/**
 * @swagger
 * /api/password/forgotpassword:
 *   post:
 *     summary: Request a password reset
 *     description: Sends a password reset email to the user if the email exists in the system.
 *     tags:
 *       - Password
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *                 example: user@example.com
 *     responses:
 *       200:
 *         description: Password reset email sent (if account exists).
 *       400:
 *         description: Bad request. Missing or invalid email.
 */
router.post('/forgotpassword', forgotPassword);

/**
 * @swagger
 * /api/password/resetpassword/{resettoken}:
 *   put:
 *     summary: Reset password using token
 *     description: Resets the user's password using the provided reset token.
 *     tags:
 *       - Password
 *     parameters:
 *       - in: path
 *         name: resettoken
 *         required: true
 *         schema:
 *           type: string
 *         description: The password reset token sent via email.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - password
 *             properties:
 *               password:
 *                 type: string
 *                 format: password
 *                 example: NewSecureP@ssw0rd
 *     responses:
 *       200:
 *         description: Password reset successfully.
 *       400:
 *         description: Bad request. Invalid token or password.
 *       404:
 *         description: Reset token not found or expired.
 */
router.put('/resetpassword/:resettoken', resetPassword);

module.exports = router;
